from dataclasses import dataclass
from datetime import datetime
from typing import List
from pathlib import Path
import time

from ..interfaces.repositories import IConfigurationRepository, ILogRepository
from ..interfaces.services import IArchiveService, IFileOrganizerService
from ..dtos.file_processing_dto import FileProcessingRequest, FileProcessingResponse
from domain.entities.nfe_document import NFEDocument
from domain.entities.validation_result import ValidationResult
from .validate_nfe_use_case import ValidateNFeUseCase, ValidateNFeUseCaseRequest


@dataclass
class ProcessFileUseCaseRequest:
    """Request for file processing use case"""
    file_path: Path
    process_archives: bool = True
    validate_schema: bool = True
    send_to_api: bool = True
    organize_output: bool = True


class ProcessFileUseCase:
    """Use case for processing files (XML or archives containing XML)"""
    
    def __init__(
        self,
        validate_nfe_use_case: ValidateNFeUseCase,
        archive_service: IArchiveService,
        file_organizer_service: IFileOrganizerService,
        config_repository: IConfigurationRepository,
        log_repository: ILogRepository
    ):
        self._validate_nfe_use_case = validate_nfe_use_case
        self._archive_service = archive_service
        self._file_organizer_service = file_organizer_service
        self._config_repository = config_repository
        self._log_repository = log_repository
        self._result_callback = None
    
    def set_result_callback(self, callback):
        """Set callback function to be called when each result is ready"""
        self._result_callback = callback
    
    def execute(self, request: ProcessFileUseCaseRequest) -> FileProcessingResponse:
        """Execute file processing"""
        start_time = time.time()
        
        # Create processing request DTO
        processing_request = FileProcessingRequest(
            file_path=request.file_path,
            process_archives=request.process_archives,
            validate_schema=request.validate_schema,
            send_to_api=request.send_to_api,
            organize_output=request.organize_output
        )
        
        try:
            self._log_repository.log_info(f"Iniciando processamento: {request.file_path.name}")
            
            # Get list of XML files to process
            xml_files = self._get_xml_files_to_process(processing_request)
            
            if not xml_files:
                # No XML files found
                end_time = time.time()
                processing_time_ms = (end_time - start_time) * 1000
                
                self._log_repository.log_warning(f"Nenhum arquivo XML encontrado para processar: {request.file_path.name}")
                
                return FileProcessingResponse(
                    request=processing_request,
                    results=[],
                    processed_at=datetime.now(),
                    processing_time_ms=processing_time_ms,
                    success=True,
                    error_message="Nenhum arquivo XML encontrado"
                )
            
            # Process each XML file
            validation_results = []
            
            for xml_file in xml_files:
                nfe_document = NFEDocument(file_path=xml_file)
                
                validate_request = ValidateNFeUseCaseRequest(
                    document=nfe_document,
                    validate_schema=request.validate_schema,
                    send_to_api=request.send_to_api
                )
                
                validate_response = self._validate_nfe_use_case.execute(validate_request)
                validation_results.append(validate_response.validation_result)
                
                # Call callback immediately if available (for real-time UI updates)
                if self._result_callback:
                    self._result_callback(validate_response.validation_result)
                
                # Organize file if requested
                if request.organize_output:
                    self._organize_processed_file(xml_file, validate_response.validation_result)
            
            # Calculate total processing time
            end_time = time.time()
            processing_time_ms = (end_time - start_time) * 1000
            
            # Check overall success
            success = all(result.is_valid for result in validation_results)
            
            self._log_repository.log_info(
                f"Processamento concluído: {request.file_path.name} - "
                f"{len(validation_results)} arquivo(s), "
                f"{len([r for r in validation_results if r.is_valid])} sucesso(s)"
            )
            
            # Clean up temporary XML files
            self._cleanup_temp_xml_files()
            
            return FileProcessingResponse(
                request=processing_request,
                results=validation_results,
                processed_at=datetime.now(),
                processing_time_ms=processing_time_ms,
                success=True,
                error_message=None
            )
            
        except Exception as e:
            end_time = time.time()
            processing_time_ms = (end_time - start_time) * 1000
            
            self._log_repository.log_error(f"Erro durante processamento: {request.file_path.name}", e)
            
            # Clean up temporary XML files even on error
            self._cleanup_temp_xml_files()
            
            return FileProcessingResponse(
                request=processing_request,
                results=[],
                processed_at=datetime.now(),
                processing_time_ms=processing_time_ms,
                success=False,
                error_message=str(e)
            )
    
    def _get_xml_files_to_process(self, request: FileProcessingRequest) -> List[Path]:
        """Get list of XML files to process from file or archive"""
        xml_files = []
        
        try:
            if request.is_xml:
                # Single XML file
                if request.file_path.exists():
                    xml_files.append(request.file_path)
                    self._log_repository.log_debug(f"Arquivo XML encontrado: {request.filename}")
                
            elif request.is_archive and request.process_archives:
                # Extract archive and copy XML files to permanent location
                if self._archive_service.can_extract(request.file_path):
                    xml_files = self._extract_and_copy_xml_files(request.file_path)
                else:
                    self._log_repository.log_warning(f"Formato de arquivo não suportado: {request.filename}")
            else:
                self._log_repository.log_warning(f"Tipo de arquivo não processável: {request.filename}")
                
        except Exception as e:
            self._log_repository.log_error(f"Erro ao obter arquivos XML: {request.filename}", e)
        
        return xml_files
    
    def _extract_and_copy_xml_files(self, archive_path: Path) -> List[Path]:
        """Extract archive and copy XML files to permanent location"""
        xml_files = []
        
        try:
            # Create temporary extraction directory
            import tempfile
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                self._log_repository.log_info(f"Extraindo arquivo: {archive_path.name}")
                extracted_files = self._archive_service.extract_archive(archive_path, temp_path)
                
                # Get output directory from configuration
                config = self._config_repository.load_configuration()
                if not config.output_path:
                    raise ValueError("Pasta de saída não configurada")
                
                output_path = Path(config.output_path)
                temp_xml_dir = output_path / "temp_xml"
                temp_xml_dir.mkdir(parents=True, exist_ok=True)
                
                # Find and copy XML files to permanent location
                for extracted_file in extracted_files:
                    if extracted_file.suffix.lower() == '.xml':
                        # Create unique filename to avoid conflicts
                        import uuid
                        unique_prefix = str(uuid.uuid4())[:8]
                        permanent_filename = f"{unique_prefix}_{extracted_file.name}"
                        permanent_path = temp_xml_dir / permanent_filename
                        
                        # Copy file to permanent location
                        import shutil
                        shutil.copy2(extracted_file, permanent_path)
                        xml_files.append(permanent_path)
                        
                        self._log_repository.log_debug(f"XML copiado para: {permanent_path}")
                
                self._log_repository.log_info(f"Arquivos XML encontrados no arquivo: {len(xml_files)}")
                
                # Store extracted file paths for cleanup later
                if hasattr(self, '_temp_xml_files'):
                    self._temp_xml_files.extend(xml_files)
                else:
                    self._temp_xml_files = xml_files.copy()
                    
        except Exception as e:
            self._log_repository.log_error(f"Erro ao extrair arquivos XML de: {archive_path.name}", e)
            # Clean up any partial files
            for xml_file in xml_files:
                try:
                    if xml_file.exists():
                        xml_file.unlink()
                except:
                    pass
            xml_files = []
        
        return xml_files
    
    def _organize_processed_file(self, file_path: Path, validation_result: ValidationResult):
        """Organize processed file based on validation result"""
        try:
            config = self._config_repository.load_configuration()
            
            if config.output_path and config.auto_organize:
                success = self._file_organizer_service.organize_processed_file(
                    file_path, validation_result, config.output_path
                )
                
                if success:
                    self._log_repository.log_debug(f"Arquivo organizado: {file_path.name}")
                else:
                    self._log_repository.log_warning(f"Falha ao organizar arquivo: {file_path.name}")
                    
        except Exception as e:
            self._log_repository.log_error(f"Erro ao organizar arquivo: {file_path.name}", e)
    
    def _cleanup_temp_xml_files(self):
        """Clean up temporary XML files created during archive extraction"""
        if hasattr(self, '_temp_xml_files'):
            for xml_file in self._temp_xml_files:
                try:
                    if xml_file.exists():
                        xml_file.unlink()
                        self._log_repository.log_debug(f"Arquivo temporário removido: {xml_file.name}")
                except Exception as e:
                    self._log_repository.log_warning(f"Erro ao remover arquivo temporário {xml_file.name}: {e}")
            
            # Clean up temp directory if empty
            try:
                if self._temp_xml_files:
                    temp_xml_dir = self._temp_xml_files[0].parent
                    if temp_xml_dir.exists() and not any(temp_xml_dir.iterdir()):
                        temp_xml_dir.rmdir()
                        self._log_repository.log_debug(f"Diretório temporário removido: {temp_xml_dir}")
            except Exception as e:
                self._log_repository.log_debug(f"Erro ao remover diretório temporário: {e}")
            
            self._temp_xml_files = []