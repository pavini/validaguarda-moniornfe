from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum


class ValidationStatus(Enum):
    SUCCESS = "success"
    FAILED = "failed"
    ERROR = "error"
    SKIPPED = "skipped"


class ValidationType(Enum):
    SCHEMA = "schema"
    API = "api"
    SIGNATURE = "signature"
    STRUCTURE = "structure"


@dataclass
class ValidationError:
    """Represents a validation error"""
    error_type: ValidationType
    message: str
    details: Optional[str] = None
    line_number: Optional[int] = None
    
    def __str__(self) -> str:
        base = f"[{self.error_type.value.upper()}] {self.message}"
        if self.line_number:
            base += f" (linha {self.line_number})"
        if self.details:
            base += f" - {self.details}"
        return base


@dataclass
class APIResponse:
    """Represents API response data"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    status_code: Optional[int] = None
    response_time_ms: Optional[float] = None
    
    @property
    def is_error(self) -> bool:
        return not self.success or (self.status_code and self.status_code >= 400)


@dataclass
class ValidationResult:
    """Entity representing the result of NFe validation"""
    document_path: str
    status: ValidationStatus
    validated_at: datetime = field(default_factory=datetime.now)
    errors: List[ValidationError] = field(default_factory=list)
    api_response: Optional[APIResponse] = None
    schema_valid: bool = False
    signature_valid: bool = False
    processing_time_ms: Optional[float] = None
    nfe_key: Optional[str] = None
    
    @property
    def is_valid(self) -> bool:
        return self.status == ValidationStatus.SUCCESS and len(self.errors) == 0
    
    @property
    def has_errors(self) -> bool:
        return len(self.errors) > 0
    
    @property
    def error_count(self) -> int:
        return len(self.errors)
    
    @property
    def schema_errors(self) -> List[ValidationError]:
        return [e for e in self.errors if e.error_type == ValidationType.SCHEMA]
    
    @property
    def api_errors(self) -> List[ValidationError]:
        return [e for e in self.errors if e.error_type == ValidationType.API]
    
    def add_error(self, error_type: ValidationType, message: str, 
                  details: Optional[str] = None, line_number: Optional[int] = None):
        """Add a validation error"""
        error = ValidationError(error_type, message, details, line_number)
        self.errors.append(error)
        if self.status == ValidationStatus.SUCCESS:
            self.status = ValidationStatus.FAILED
    
    def add_api_response(self, success: bool, message: str, 
                        data: Optional[Dict[str, Any]] = None,
                        status_code: Optional[int] = None,
                        response_time_ms: Optional[float] = None):
        """Add API response data"""
        self.api_response = APIResponse(
            success=success,
            message=message,
            data=data,
            status_code=status_code,
            response_time_ms=response_time_ms
        )
        
        if not success and self.status == ValidationStatus.SUCCESS:
            self.status = ValidationStatus.FAILED
            self.add_error(ValidationType.API, message)
    
    def get_summary(self) -> str:
        """Get a human-readable summary of the validation result"""
        if self.is_valid:
            return f"✅ Validação bem-sucedida para {self.document_path}"
        
        error_summary = f"❌ {self.error_count} erro(s) encontrado(s)"
        if self.schema_errors:
            error_summary += f" | Schema: {len(self.schema_errors)}"
        if self.api_errors:
            error_summary += f" | API: {len(self.api_errors)}"
        
        return error_summary