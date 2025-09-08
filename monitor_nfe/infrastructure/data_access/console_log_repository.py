import logging
import sys
from datetime import datetime
from typing import Optional

from application.interfaces.repositories import ILogRepository


class ConsoleLogRepository(ILogRepository):
    """Log repository implementation using Python logging to console"""
    
    def __init__(self, log_level: str = "INFO"):
        self._logger = logging.getLogger("MonitorNFe")
        self._setup_logger(log_level)
    
    def _setup_logger(self, log_level: str):
        """Setup logger configuration"""
        # Clear any existing handlers
        self._logger.handlers.clear()
        
        # Set level
        level = getattr(logging, log_level.upper(), logging.INFO)
        self._logger.setLevel(level)
        
        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        
        # Add handler to logger
        self._logger.addHandler(console_handler)
    
    def log_info(self, message: str):
        """Log informational message"""
        self._logger.info(message)
    
    def log_warning(self, message: str):
        """Log warning message"""
        self._logger.warning(message)
    
    def log_error(self, message: str, exception: Optional[Exception] = None):
        """Log error message"""
        if exception:
            self._logger.error(f"{message}: {str(exception)}", exc_info=True)
        else:
            self._logger.error(message)
    
    def log_debug(self, message: str):
        """Log debug message"""
        self._logger.debug(message)
    
    def set_log_level(self, log_level: str):
        """Update log level"""
        level = getattr(logging, log_level.upper(), logging.INFO)
        self._logger.setLevel(level)
        for handler in self._logger.handlers:
            handler.setLevel(level)