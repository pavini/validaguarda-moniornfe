from dataclasses import dataclass, field
from datetime import datetime
from typing import Set, Dict, Optional
from pathlib import Path
from enum import Enum
import uuid


class ProcessingState(Enum):
    PENDING = "pending"
    EXTRACTING = "extracting"
    EXTRACTED = "extracted"
    PROCESSING = "processing"
    PROCESSED = "processed"
    CLEANUP_READY = "cleanup_ready"
    ERROR = "error"


@dataclass
class FileProcessingState:
    """Represents the processing state of an individual file"""
    file_path: Path
    state: ProcessingState
    thread_id: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
    def mark_processing(self, thread_id: str):
        """Mark file as being processed by a specific thread"""
        self.state = ProcessingState.PROCESSING
        self.thread_id = thread_id
        self.started_at = datetime.now()
    
    def mark_completed(self):
        """Mark file as processing completed"""
        self.state = ProcessingState.PROCESSED
        self.completed_at = datetime.now()
    
    def mark_error(self, error: str):
        """Mark file as having processing error"""
        self.state = ProcessingState.ERROR
        self.error_message = error
        self.completed_at = datetime.now()
    
    @property
    def is_active(self) -> bool:
        """Check if file is currently being processed"""
        return self.state in [ProcessingState.PROCESSING, ProcessingState.EXTRACTING]
    
    @property
    def processing_time_ms(self) -> Optional[float]:
        """Get processing time in milliseconds"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds() * 1000
        return None


@dataclass
class ProcessingSession:
    """Manages a processing session with multiple files and parallel execution"""
    session_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    created_at: datetime = field(default_factory=datetime.now)
    temp_directory: Optional[Path] = None
    files: Dict[str, FileProcessingState] = field(default_factory=dict)
    max_parallel_threads: int = 10
    
    def add_file(self, file_path: Path, state: ProcessingState = ProcessingState.PENDING):
        """Add a file to the processing session"""
        file_key = str(file_path)
        self.files[file_key] = FileProcessingState(
            file_path=file_path,
            state=state
        )
        return file_key
    
    def get_file_state(self, file_path: Path) -> Optional[FileProcessingState]:
        """Get the processing state of a file"""
        return self.files.get(str(file_path))
    
    def mark_file_processing(self, file_path: Path, thread_id: str):
        """Mark a file as being processed by a thread"""
        file_state = self.get_file_state(file_path)
        if file_state:
            file_state.mark_processing(thread_id)
    
    def mark_file_completed(self, file_path: Path):
        """Mark a file as processing completed"""
        file_state = self.get_file_state(file_path)
        if file_state:
            file_state.mark_completed()
    
    def mark_file_error(self, file_path: Path, error: str):
        """Mark a file as having an error"""
        file_state = self.get_file_state(file_path)
        if file_state:
            file_state.mark_error(error)
    
    def get_active_files(self) -> Set[str]:
        """Get set of files currently being processed"""
        return {
            file_key for file_key, file_state in self.files.items()
            if file_state.is_active
        }
    
    def get_pending_files(self) -> Set[str]:
        """Get set of files waiting to be processed"""
        return {
            file_key for file_key, file_state in self.files.items()
            if file_state.state == ProcessingState.PENDING
        }
    
    def get_completed_files(self) -> Set[str]:
        """Get set of files that completed processing"""
        return {
            file_key for file_key, file_state in self.files.items()
            if file_state.state in [ProcessingState.PROCESSED, ProcessingState.ERROR]
        }
    
    def can_start_processing(self) -> bool:
        """Check if we can start processing more files (within thread limit)"""
        active_count = len(self.get_active_files())
        return active_count < self.max_parallel_threads
    
    def get_processing_summary(self) -> Dict[str, int]:
        """Get summary of processing states"""
        summary = {
            'total': len(self.files),
            'pending': 0,
            'processing': 0,
            'completed': 0,
            'errors': 0
        }
        
        for file_state in self.files.values():
            if file_state.state == ProcessingState.PENDING:
                summary['pending'] += 1
            elif file_state.state == ProcessingState.PROCESSING:
                summary['processing'] += 1
            elif file_state.state == ProcessingState.PROCESSED:
                summary['completed'] += 1
            elif file_state.state == ProcessingState.ERROR:
                summary['errors'] += 1
        
        return summary
    
    def is_complete(self) -> bool:
        """Check if all files have been processed"""
        return len(self.get_completed_files()) == len(self.files)
    
    def cleanup_temp_directory(self):
        """Clean up temporary directory if safe to do so"""
        if self.temp_directory and self.temp_directory.exists():
            # Only cleanup if no files are actively being processed
            if not self.get_active_files():
                try:
                    import shutil
                    shutil.rmtree(self.temp_directory)
                except Exception:
                    pass  # Ignore cleanup errors