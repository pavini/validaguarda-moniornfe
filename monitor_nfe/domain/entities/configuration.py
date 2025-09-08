from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class Configuration:
    """Entity representing application configuration"""
    monitor_folder: Optional[str] = None
    output_folder: Optional[str] = None
    token: Optional[str] = None
    auto_organize: bool = True
    log_level: str = "INFO"
    
    @property
    def monitor_path(self) -> Optional[Path]:
        """Get monitor folder as Path object"""
        return Path(self.monitor_folder) if self.monitor_folder else None
    
    @property
    def output_path(self) -> Optional[Path]:
        """Get output folder as Path object"""
        return Path(self.output_folder) if self.output_folder else None
    
    @property
    def processed_path(self) -> Optional[Path]:
        """Get processed files folder path"""
        return self.output_path / "processed" if self.output_path else None
    
    @property
    def errors_path(self) -> Optional[Path]:
        """Get error files folder path"""
        return self.output_path / "errors" if self.output_path else None
    
    @property
    def logs_path(self) -> Optional[Path]:
        """Get logs folder path"""
        return self.output_path / "logs" if self.output_path else None
    
    def is_valid(self) -> bool:
        """Check if configuration is valid for operation"""
        return (self.monitor_folder is not None and 
                self.output_folder is not None and
                self.token is not None and
                len(self.token.strip()) > 0)
    
    def ensure_folders_exist(self) -> bool:
        """Create output folder structure if it doesn't exist"""
        if not self.output_path:
            return False
        
        try:
            folders = [self.processed_path, self.errors_path, self.logs_path]
            for folder in folders:
                if folder:
                    folder.mkdir(parents=True, exist_ok=True)
            return True
        except Exception:
            return False