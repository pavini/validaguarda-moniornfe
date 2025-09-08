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
                # Extract archive and find XML files
                if self._archive_service.can_extract(request.file_path):
                    # Create temporary extraction directory
                    import tempfile
                    with tempfile.TemporaryDirectory() as temp_dir:
                        temp_path = Path(temp_dir)
                        
                        self._log_repository.log_info(f"Extraindo arquivo: {request.filename}")
                        extracted_files = self._archive_service.extract_archive(request.file_path, temp_path)
                        
                        # Find XML files in extracted content
                        for extracted_file in extracted_files:
                            if extracted_file.suffix.lower() == '.xml':
                                # Copy to a permanent location or process immediately
                                xml_files.append(extracted_file)
                        
                        self._log_repository.log_info(f"Arquivos XML encontrados no arquivo: {len(xml_files)}")
                else:
                    self._log_repository.log_warning(f"Formato de arquivo não suportado: {request.filename}")
            else:
                self._log_repository.log_warning(f"Tipo de arquivo não processável: {request.filename}")
                
        except Exception as e:
            self._log_repository.log_error(f"Erro ao obter arquivos XML: {request.filename}", e)
        
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