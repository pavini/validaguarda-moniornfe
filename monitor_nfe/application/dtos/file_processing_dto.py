from dataclasses import dataclass
from typing import Optional, List
from pathlib import Path
from datetime import datetime

from domain.entities.validation_result import ValidationResult


@dataclass
class FileProcessingRequest:
    """DTO for file processing requests"""
    file_path: Path
    process_archives: bool = True
    validate_schema: bool = True
    send_to_api: bool = True
    organize_output: bool = True
    
    @property
    def filename(self) -> str:
        return self.file_path.name
    
    @property
    def is_xml(self) -> bool:
        return self.file_path.suffix.lower() == '.xml'
    
    @property
    def is_archive(self) -> bool:
        return self.file_path.suffix.lower() in ['.zip', '.rar', '.7z']


@dataclass
class FileProcessingResponse:
    """DTO for file processing responses"""
    request: FileProcessingRequest
    results: List[ValidationResult]
    processed_at: datetime
    processing_time_ms: float
    success: bool
    error_message: Optional[str] = None
    
    @property
    def has_errors(self) -> bool:
        return not self.success or any(not result.is_valid for result in self.results)
    
    @property
    def total_files_processed(self) -> int:
        return len(self.results)
    
    @property
    def successful_validations(self) -> List[ValidationResult]:
        return [r for r in self.results if r.is_valid]
    
    @property
    def failed_validations(self) -> List[ValidationResult]:
        return [r for r in self.results if not r.is_valid]


@dataclass
class MonitoringStatus:
    """DTO for monitoring status information"""
    is_active: bool
    monitor_folder: Optional[str] = None
    output_folder: Optional[str] = None
    files_processed: int = 0
    files_successful: int = 0
    files_failed: int = 0
    started_at: Optional[datetime] = None
    last_activity: Optional[datetime] = None
    
    @property
    def success_rate(self) -> float:
        if self.files_processed == 0:
            return 0.0
        return (self.files_successful / self.files_processed) * 100
    
    @property
    def uptime_minutes(self) -> int:
        if not self.started_at:
            return 0
        return int((datetime.now() - self.started_at).total_seconds() / 60)