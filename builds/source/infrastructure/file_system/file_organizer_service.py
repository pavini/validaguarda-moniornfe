import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

from application.interfaces.services import IFileOrganizerService
from domain.entities.validation_result import ValidationResult


class FileOrganizerService(IFileOrganizerService):
    """File organization service implementation"""
    
    def organize_processed_file(self, file_path: Path, validation_result: ValidationResult, 
                              output_folder: Path) -> bool:
        """Move processed file to appropriate folder based on validation result"""
        try:
            if not file_path.exists():
                print(f"❌ Arquivo não existe para organização: {file_path}")
                return False
            
            # Determine target folder based on validation result
            if validation_result.is_valid:
                target_folder = output_folder / "processed"
            else:
                # Check if error should go to reprocess or permanent errors
                if self._should_reprocess(validation_result):
                    target_folder = output_folder / "reprocess"
                else:
                    target_folder = output_folder / "errors"
            
            # Ensure target folder exists
            target_folder.mkdir(parents=True, exist_ok=True)
            
            # Generate unique filename if file already exists
            target_path = self._get_unique_target_path(target_folder, file_path)
            
            # Move the file
            shutil.move(str(file_path), str(target_path))
            
            # Create a processing log file with details
            self._create_processing_log(target_path, validation_result, output_folder)
            
            print(f"📁 Arquivo organizado: {file_path.name} -> {target_folder.name}/{target_path.name}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao organizar arquivo {file_path.name}: {e}")
            return False
    
    def create_output_structure(self, output_folder: Path) -> bool:
        """Create output folder structure (processed, errors, logs)"""
        try:
            folders = ['processed', 'errors', 'reprocess', 'logs']
            
            for folder_name in folders:
                folder_path = output_folder / folder_name
                folder_path.mkdir(parents=True, exist_ok=True)
            
            print(f"📁 Estrutura de pastas criada: {output_folder}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao criar estrutura de pastas: {e}")
            return False
    
    def _get_unique_target_path(self, target_folder: Path, source_file: Path) -> Path:
        """Generate a unique target path to avoid overwriting existing files"""
        base_name = source_file.stem
        extension = source_file.suffix
        target_path = target_folder / source_file.name
        
        if not target_path.exists():
            return target_path
        
        # Generate unique name with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        counter = 1
        
        while True:
            unique_name = f"{base_name}_{timestamp}_{counter:03d}{extension}"
            unique_path = target_folder / unique_name
            
            if not unique_path.exists():
                return unique_path
            
            counter += 1
            
            # Safety check to avoid infinite loop
            if counter > 999:
                unique_name = f"{base_name}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}{extension}"
                return target_folder / unique_name
    
    def _create_processing_log(self, file_path: Path, validation_result: ValidationResult, 
                             output_folder: Path):
        """Create a log file with processing details"""
        try:
            logs_folder = output_folder / "logs"
            logs_folder.mkdir(parents=True, exist_ok=True)
            
            # Create log filename based on original file
            log_filename = f"{file_path.stem}_processing.log"
            log_path = logs_folder / log_filename
            
            # Prepare log content
            log_lines = [
                f"Processamento NFe - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                f"Arquivo: {file_path.name}",
                f"Caminho original: {validation_result.document_path}",
                f"Status: {validation_result.status.value}",
                f"Válido: {'Sim' if validation_result.is_valid else 'Não'}",
                f"Chave NFe: {validation_result.nfe_key or 'Não encontrada'}",
                f"Schema válido: {'Sim' if validation_result.schema_valid else 'Não'}",
                f"Assinatura válida: {'Sim' if validation_result.signature_valid else 'Não'}",
                f"Tempo de processamento: {validation_result.processing_time_ms or 0:.1f} ms",
                "",
                "=== ERROS ENCONTRADOS ==="
            ]
            
            if validation_result.has_errors:
                for i, error in enumerate(validation_result.errors, 1):
                    log_lines.extend([
                        f"{i}. {error}",
                        ""
                    ])
            else:
                log_lines.append("Nenhum erro encontrado")
            
            # Add API response if available
            if validation_result.api_response:
                log_lines.extend([
                    "",
                    "=== RESPOSTA DA API ===",
                    f"Sucesso: {'Sim' if validation_result.api_response.success else 'Não'}",
                    f"Mensagem: {validation_result.api_response.message}",
                    f"Status HTTP: {validation_result.api_response.status_code or 'N/A'}",
                    f"Tempo de resposta: {validation_result.api_response.response_time_ms or 0:.1f} ms"
                ])
                
                if validation_result.api_response.data:
                    log_lines.extend([
                        f"Dados adicionais: {validation_result.api_response.data}"
                    ])
            
            # Write log file
            with open(log_path, 'w', encoding='utf-8') as log_file:
                log_file.write('\n'.join(log_lines))
            
        except Exception as e:
            print(f"⚠️  Erro ao criar log de processamento: {e}")
            # Don't raise exception as this is not critical for the main operation
    
    def _should_reprocess(self, validation_result: ValidationResult) -> bool:
        """Determine if file should go to reprocess folder based on error type"""
        # Only files that fail should be considered for reprocessing
        if validation_result.is_valid:
            return False
        
        # Check each error to determine if it's temporary/retryable
        for error in validation_result.errors:
            if error.error_type.value == 'api':
                # Permanent errors that should NOT be reprocessed
                permanent_keywords = [
                    'já existe', 'already exists', 'duplicate',  # File already processed
                    'assinatura', 'signature', 'digital',        # Signature issues
                    'schema', 'xsd', 'xml malformado'           # Structure issues
                ]
                
                # Temporary errors that SHOULD be reprocessed
                temporary_keywords = [
                    'servidor', 'server', 'timeout', 'internal',
                    'connection', 'network', 'unavailable', 
                    'service temporarily', 'try again'
                ]
                
                error_msg_lower = error.message.lower()
                
                # Check if it's a permanent error
                if any(keyword in error_msg_lower for keyword in permanent_keywords):
                    return False
                
                # Check if it's a temporary error
                if any(keyword in error_msg_lower for keyword in temporary_keywords):
                    return True
        
        # Default: if unsure, send to reprocess (better to retry than lose)
        return True