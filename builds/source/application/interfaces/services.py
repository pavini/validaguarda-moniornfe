from abc import ABC, abstractmethod
from typing import List, Optional, Callable
from pathlib import Path

from domain.entities.nfe_document import NFEDocument
from domain.entities.validation_result import ValidationResult, APIResponse
from domain.value_objects.api_token import APIToken


class IFileMonitorService(ABC):
    """Interface for file system monitoring"""
    
    @abstractmethod
    def start_monitoring(self, folder_path: Path, callback: Callable[[Path], None]):
        """Start monitoring a folder for file changes"""
        pass
    
    @abstractmethod
    def stop_monitoring(self):
        """Stop file system monitoring"""
        pass
    
    @abstractmethod
    def is_monitoring(self) -> bool:
        """Check if monitoring is active"""
        pass


class IArchiveService(ABC):
    """Interface for archive extraction operations"""
    
    @abstractmethod
    def extract_archive(self, archive_path: Path, extract_to: Path) -> List[Path]:
        """Extract archive and return list of extracted files"""
        pass
    
    @abstractmethod
    def can_extract(self, file_path: Path) -> bool:
        """Check if file is a supported archive format"""
        pass


class IAPIService(ABC):
    """Interface for external API communication"""
    
    @abstractmethod
    def validate_nfe(self, document: NFEDocument, token: APIToken) -> APIResponse:
        """Send NFe document to external API for validation"""
        pass
    
    @abstractmethod
    def test_connection(self, token: APIToken) -> bool:
        """Test API connectivity and token validity"""
        pass


class IFileOrganizerService(ABC):
    """Interface for file organization operations"""
    
    @abstractmethod
    def organize_processed_file(self, file_path: Path, validation_result: ValidationResult, 
                              output_folder: Path) -> bool:
        """Move processed file to appropriate folder based on validation result"""
        pass
    
    @abstractmethod
    def create_output_structure(self, output_folder: Path) -> bool:
        """Create output folder structure (processed, errors, logs)"""
        pass


class IXMLSchemaService(ABC):
    """Interface for XML schema validation"""
    
    @abstractmethod
    def load_schemas(self) -> bool:
        """Load XSD schemas for validation"""
        pass
    
    @abstractmethod
    def validate_against_schema(self, document: NFEDocument) -> ValidationResult:
        """Validate XML document against loaded schemas"""
        pass
    
    @abstractmethod
    def has_schemas_loaded(self) -> bool:
        """Check if schemas are loaded and ready"""
        pass


class IParallelProcessingService(ABC):
    """Interface for parallel processing operations"""
    
    @abstractmethod
    def process_files_in_parallel(self, files: List[NFEDocument], 
                                 processor_func: Callable[[NFEDocument], ValidationResult],
                                 max_workers: Optional[int] = None) -> List[ValidationResult]:
        """Process multiple files in parallel"""
        pass