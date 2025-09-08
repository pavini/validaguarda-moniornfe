from PySide6.QtCore import QSettings

from application.interfaces.repositories import IConfigurationRepository
from domain.entities.configuration import Configuration


class QSettingsConfigRepository(IConfigurationRepository):
    """Configuration repository implementation using QSettings"""
    
    def __init__(self, organization: str = "ValidateCh", application: str = "MonitorNFe"):
        self._settings = QSettings(organization, application)
    
    def load_configuration(self) -> Configuration:
        """Load configuration from QSettings"""
        return Configuration(
            monitor_folder=self._settings.value('monitor_folder', None),
            output_folder=self._settings.value('output_folder', None),
            token=self._settings.value('token', None),
            auto_organize=self._settings.value('auto_organize', True, type=bool),
            log_level=self._settings.value('log_level', 'INFO')
        )
    
    def save_configuration(self, config: Configuration) -> bool:
        """Save configuration to QSettings"""
        try:
            self._settings.setValue('monitor_folder', config.monitor_folder)
            self._settings.setValue('output_folder', config.output_folder)
            self._settings.setValue('token', config.token)
            self._settings.setValue('auto_organize', config.auto_organize)
            self._settings.setValue('log_level', config.log_level)
            self._settings.sync()
            return True
        except Exception:
            return False
    
    def get_value(self, key: str, default=None):
        """Get a specific configuration value"""
        return self._settings.value(key, default)
    
    def set_value(self, key: str, value) -> bool:
        """Set a specific configuration value"""
        try:
            self._settings.setValue(key, value)
            self._settings.sync()
            return True
        except Exception:
            return False