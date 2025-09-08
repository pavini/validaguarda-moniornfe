from abc import ABC, abstractmethod
from typing import Optional

from domain.entities.configuration import Configuration


class IConfigurationRepository(ABC):
    """Interface for configuration persistence"""
    
    @abstractmethod
    def load_configuration(self) -> Configuration:
        """Load configuration from storage"""
        pass
    
    @abstractmethod
    def save_configuration(self, config: Configuration) -> bool:
        """Save configuration to storage"""
        pass
    
    @abstractmethod
    def get_value(self, key: str, default=None):
        """Get a specific configuration value"""
        pass
    
    @abstractmethod
    def set_value(self, key: str, value) -> bool:
        """Set a specific configuration value"""
        pass


class ILogRepository(ABC):
    """Interface for logging operations"""
    
    @abstractmethod
    def log_info(self, message: str):
        """Log informational message"""
        pass
    
    @abstractmethod
    def log_warning(self, message: str):
        """Log warning message"""
        pass
    
    @abstractmethod
    def log_error(self, message: str, exception: Optional[Exception] = None):
        """Log error message"""
        pass
    
    @abstractmethod
    def log_debug(self, message: str):
        """Log debug message"""
        pass