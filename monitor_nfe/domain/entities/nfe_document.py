from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from pathlib import Path
from enum import Enum


class NFEType(Enum):
    NFE = "nfe"
    PROC_NFE = "procNFe"
    UNKNOWN = "unknown"


class ProcessingStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    PROCESSED = "processed"
    ERROR = "error"
    SKIPPED = "skipped"


@dataclass
class NFEDocument:
    """Entity representing an NFe document"""
    file_path: Path
    nfe_key: Optional[str] = None
    document_type: NFEType = NFEType.UNKNOWN
    file_size: int = 0
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.modified_at is None:
            self.modified_at = self.created_at
            
        if self.file_path.exists():
            stat = self.file_path.stat()
            self.file_size = stat.st_size
            self.modified_at = datetime.fromtimestamp(stat.st_mtime)
    
    @property
    def filename(self) -> str:
        return self.file_path.name
    
    @property
    def extension(self) -> str:
        return self.file_path.suffix.lower()
    
    @property
    def is_xml(self) -> bool:
        return self.extension == '.xml'
    
    @property
    def is_archive(self) -> bool:
        return self.extension in ['.zip', '.rar', '.7z']
    
    def exists(self) -> bool:
        return self.file_path.exists()