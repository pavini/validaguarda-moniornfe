from pathlib import Path
from typing import Dict, Any, Callable, Optional

# Domain
from domain.services.nfe_validation_service import NFEValidationService

# Application
from application.interfaces.repositories import IConfigurationRepository, ILogRepository
from application.interfaces.services import (
    IFileMonitorService, IArchiveService, IAPIService, 
    IFileOrganizerService, IXMLSchemaService
)
from application.use_cases.validate_nfe_use_case import ValidateNFeUseCase
from application.use_cases.process_file_use_case import ProcessFileUseCase

# Infrastructure
from infrastructure.data_access.qsettings_config_repository import QSettingsConfigRepository
from infrastructure.data_access.console_log_repository import ConsoleLogRepository
from infrastructure.external_services.validanfe_api_service import ValidaNFeAPIService
from infrastructure.external_services.xml_schema_service import XMLSchemaService
from infrastructure.file_system.watchdog_monitor_service import WatchdogMonitorService
from infrastructure.file_system.archive_extractor_service import ArchiveExtractorService
from infrastructure.file_system.file_organizer_service import FileOrganizerService

# Presentation
from presentation.viewmodels.main_view_model import MainViewModel


class DependencyContainer:
    """Dependency injection container for the application"""
    
    def __init__(self, schemas_folder: Optional[Path] = None):
        self._services: Dict[str, Any] = {}
        self._singletons: Dict[str, Any] = {}
        self._factories: Dict[str, Callable] = {}
        
        # Store configuration
        self._schemas_folder = schemas_folder
        
        # Register all services
        self._register_services()
    
    def _register_services(self):
        """Register all services and their dependencies"""
        
        # === Repositories ===
        self._register_singleton('config_repository', lambda: QSettingsConfigRepository())
        self._register_singleton('log_repository', lambda: ConsoleLogRepository())
        
        # === Domain Services ===
        self._register_singleton('nfe_validation_service', lambda: NFEValidationService())
        
        # === Infrastructure Services ===
        self._register_singleton('api_service', lambda: ValidaNFeAPIService())
        self._register_singleton('file_monitor_service', lambda: WatchdogMonitorService())
        self._register_singleton('archive_service', lambda: ArchiveExtractorService())
        self._register_singleton('file_organizer_service', lambda: FileOrganizerService())
        self._register_singleton(
            'xml_schema_service', 
            lambda: XMLSchemaService(self._schemas_folder)
        )
        
        # === Use Cases ===
        self._register_factory(
            'validate_nfe_use_case',
            lambda: ValidateNFeUseCase(
                validation_service=self.get('nfe_validation_service'),
                schema_service=self.get('xml_schema_service'),
                api_service=self.get('api_service'),
                config_repository=self.get('config_repository'),
                log_repository=self.get('log_repository')
            )
        )
        
        self._register_factory(
            'process_file_use_case',
            lambda: ProcessFileUseCase(
                validate_nfe_use_case=self.get('validate_nfe_use_case'),
                archive_service=self.get('archive_service'),
                file_organizer_service=self.get('file_organizer_service'),
                config_repository=self.get('config_repository'),
                log_repository=self.get('log_repository')
            )
        )
        
        # === ViewModels ===
        self._register_factory(
            'main_view_model',
            lambda: MainViewModel(
                config_repository=self.get('config_repository'),
                file_monitor_service=self.get('file_monitor_service'),
                process_file_use_case=self.get('process_file_use_case')
            )
        )
    
    def _register_singleton(self, name: str, factory: Callable):
        """Register a singleton service"""
        self._factories[name] = factory
    
    def _register_factory(self, name: str, factory: Callable):
        """Register a factory service (creates new instance each time)"""
        self._services[name] = factory
    
    def get(self, service_name: str) -> Any:
        """Get a service instance"""
        # Check if it's a singleton
        if service_name in self._singletons:
            return self._singletons[service_name]
        
        # Check if it's a registered factory (singleton)
        if service_name in self._factories:
            instance = self._factories[service_name]()
            self._singletons[service_name] = instance
            return instance
        
        # Check if it's a regular service factory
        if service_name in self._services:
            return self._services[service_name]()
        
        raise ValueError(f"Service '{service_name}' not registered")
    
    def initialize_services(self) -> bool:
        """Initialize critical services"""
        try:
            print("🔧 Inicializando serviços...")
            
            # Initialize XML Schema Service
            xml_schema_service = self.get('xml_schema_service')
            schemas_loaded = xml_schema_service.load_schemas()
            
            if not schemas_loaded:
                print("⚠️  Schemas XSD não foram carregados - validação de schema não funcionará")
            
            # Initialize log repository
            log_repo = self.get('log_repository')
            log_repo.log_info("Container de dependências inicializado")
            
            print("✅ Serviços inicializados com sucesso")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao inicializar serviços: {e}")
            return False
    
    def cleanup(self):
        """Cleanup all services"""
        try:
            # Stop file monitoring if active
            file_monitor = self._singletons.get('file_monitor_service')
            if file_monitor:
                file_monitor.stop_monitoring()
            
            # Clear all singletons
            self._singletons.clear()
            
            print("🧹 Limpeza de serviços concluída")
            
        except Exception as e:
            print(f"⚠️  Erro na limpeza de serviços: {e}")
    
    def get_service_info(self) -> Dict[str, str]:
        """Get information about registered services"""
        info = {}
        
        # Singletons
        for name in self._factories.keys():
            status = "Inicializado" if name in self._singletons else "Não inicializado"
            info[name] = f"Singleton - {status}"
        
        # Factories
        for name in self._services.keys():
            info[name] = "Factory - Nova instância a cada chamada"
        
        return info