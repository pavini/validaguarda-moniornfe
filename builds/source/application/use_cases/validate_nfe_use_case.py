from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import time

from ..interfaces.repositories import IConfigurationRepository, ILogRepository
from ..interfaces.services import IAPIService, IXMLSchemaService
from domain.entities.nfe_document import NFEDocument
from domain.entities.validation_result import ValidationResult, ValidationStatus, ValidationType
from domain.services.nfe_validation_service import INFEValidationService
from domain.value_objects.api_token import APIToken


@dataclass
class ValidateNFeUseCaseRequest:
    """Request for NFe validation use case"""
    document: NFEDocument
    validate_schema: bool = True
    send_to_api: bool = True


@dataclass
class ValidateNFeUseCaseResponse:
    """Response from NFe validation use case"""
    validation_result: ValidationResult
    processing_time_ms: float
    success: bool


class ValidateNFeUseCase:
    """Use case for validating NFe documents"""
    
    def __init__(
        self,
        validation_service: INFEValidationService,
        schema_service: IXMLSchemaService,
        api_service: IAPIService,
        config_repository: IConfigurationRepository,
        log_repository: ILogRepository
    ):
        self._validation_service = validation_service
        self._schema_service = schema_service
        self._api_service = api_service
        self._config_repository = config_repository
        self._log_repository = log_repository
    
    def execute(self, request: ValidateNFeUseCaseRequest) -> ValidateNFeUseCaseResponse:
        """Execute NFe validation"""
        start_time = time.time()
        
        try:
            # Create initial validation result
            result = ValidationResult(
                document_path=str(request.document.file_path),
                status=ValidationStatus.SUCCESS
            )
            
            self._log_repository.log_info(f"Iniciando validação: {request.document.filename}")
            
            # Step 1: Basic structure validation
            structure_result = self._validation_service.validate_structure(request.document)
            result.errors.extend(structure_result.errors)
            result.nfe_key = structure_result.nfe_key
            
            if structure_result.has_errors:
                result.status = ValidationStatus.FAILED
                self._log_repository.log_warning(f"Falha na validação estrutural: {request.document.filename}")
            
            # Step 2: Detect document type
            document_type = self._validation_service.detect_document_type(request.document)
            request.document.document_type = document_type
            
            # Step 3: Schema validation (if requested and structure is valid)
            if request.validate_schema and not structure_result.has_errors:
                if self._schema_service.has_schemas_loaded():
                    schema_result = self._schema_service.validate_against_schema(request.document)
                    result.errors.extend(schema_result.errors)
                    result.schema_valid = schema_result.status == ValidationStatus.SUCCESS
                    
                    if schema_result.has_errors:
                        result.status = ValidationStatus.FAILED
                        self._log_repository.log_warning(f"Falha na validação de schema: {request.document.filename}")
                else:
                    self._log_repository.log_warning("Schemas XSD não carregados - pulando validação de schema")
            
            # Step 4: API validation (if requested and no critical errors)
            if request.send_to_api and result.status != ValidationStatus.ERROR:
                config = self._config_repository.load_configuration()
                
                if config.token:
                    try:
                        api_token = APIToken.from_string(config.token)
                        if api_token:
                            api_response = self._api_service.validate_nfe(request.document, api_token)
                            
                            result.add_api_response(
                                success=api_response.success,
                                message=api_response.message,
                                data=api_response.data,
                                status_code=api_response.status_code,
                                response_time_ms=api_response.response_time_ms
                            )
                            
                            if api_response.is_error:
                                self._log_repository.log_error(f"Erro na API: {api_response.message}")
                        else:
                            self._log_repository.log_error("Token de API inválido")
                    except ValueError as e:
                        self._log_repository.log_error(f"Erro no token da API: {e}")
                else:
                    self._log_repository.log_warning("Token da API não configurado")
            
            # Calculate processing time
            end_time = time.time()
            processing_time_ms = (end_time - start_time) * 1000
            result.processing_time_ms = processing_time_ms
            
            # Log final result
            if result.is_valid:
                self._log_repository.log_info(f"Validação concluída com sucesso: {request.document.filename}")
            else:
                self._log_repository.log_warning(f"Validação falhou: {request.document.filename} - {result.error_count} erro(s)")
            
            return ValidateNFeUseCaseResponse(
                validation_result=result,
                processing_time_ms=processing_time_ms,
                success=True
            )
            
        except Exception as e:
            # Handle unexpected errors
            end_time = time.time()
            processing_time_ms = (end_time - start_time) * 1000
            
            self._log_repository.log_error(f"Erro inesperado durante validação: {request.document.filename}", e)
            
            error_result = ValidationResult(
                document_path=str(request.document.file_path),
                status=ValidationStatus.ERROR,
                processing_time_ms=processing_time_ms
            )
            error_result.add_error(
                ValidationType.STRUCTURE,
                "Erro inesperado durante validação",
                str(e)
            )
            
            return ValidateNFeUseCaseResponse(
                validation_result=error_result,
                processing_time_ms=processing_time_ms,
                success=False
            )