from datetime import datetime
from pathlib import Path
from typing import List, Optional, Callable
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication

from application.dtos.file_processing_dto import MonitoringStatus
from application.use_cases.process_file_use_case import ProcessFileUseCase, ProcessFileUseCaseRequest
from application.interfaces.repositories import IConfigurationRepository
from application.interfaces.services import IFileMonitorService
from domain.entities.configuration import Configuration
from domain.entities.validation_result import ValidationResult


class MainViewModel(QObject):
    """ViewModel for main window following MVVM pattern"""
    
    # Signals for UI updates
    monitoring_started = Signal(str)  # folder path
    monitoring_stopped = Signal()
    file_processed = Signal(str, bool)  # filename, success
    status_updated = Signal(str)  # status message
    configuration_changed = Signal()
    validation_result_added = Signal(object)  # ValidationResult
    
    def __init__(
        self,
        config_repository: IConfigurationRepository,
        file_monitor_service: IFileMonitorService,
        process_file_use_case: ProcessFileUseCase
    ):
        super().__init__()
        
        self._config_repository = config_repository
        self._file_monitor_service = file_monitor_service
        self._process_file_use_case = process_file_use_case
        
        # State
        self._configuration: Configuration = Configuration()
        self._monitoring_status = MonitoringStatus(is_active=False)
        self._validation_results: List[ValidationResult] = []
        
        # Load initial configuration
        self.load_configuration()
    
    # Properties
    @property
    def configuration(self) -> Configuration:
        """Get current configuration"""
        return self._configuration
    
    @property
    def monitoring_status(self) -> MonitoringStatus:
        """Get current monitoring status"""
        return self._monitoring_status
    
    @property
    def validation_results(self) -> List[ValidationResult]:
        """Get validation results"""
        return self._validation_results.copy()
    
    @property
    def is_monitoring_active(self) -> bool:
        """Check if monitoring is active"""
        return self._monitoring_status.is_active
    
    @property
    def can_start_monitoring(self) -> bool:
        """Check if monitoring can be started"""
        return (not self._monitoring_status.is_active and 
                self._configuration.is_valid())
    
    # Configuration management
    def load_configuration(self):
        """Load configuration from repository"""
        try:
            self._configuration = self._config_repository.load_configuration()
            self.configuration_changed.emit()
            self.status_updated.emit("Configuração carregada")
        except Exception as e:
            self.status_updated.emit(f"Erro ao carregar configuração: {e}")
    
    def save_configuration(self, config: Configuration) -> bool:
        """Save configuration to repository"""
        try:
            success = self._config_repository.save_configuration(config)
            if success:
                self._configuration = config
                self.configuration_changed.emit()
                self.status_updated.emit("Configuração salva com sucesso")
                return True
            else:
                self.status_updated.emit("Erro ao salvar configuração")
                return False
        except Exception as e:
            self.status_updated.emit(f"Erro ao salvar configuração: {e}")
            return False
    
    # Monitoring operations
    def start_monitoring(self) -> bool:
        """Start file monitoring"""
        try:
            if not self.can_start_monitoring:
                self.status_updated.emit("Não é possível iniciar monitoramento - verifique configuração")
                return False
            
            monitor_path = self._configuration.monitor_path
            if not monitor_path or not monitor_path.exists():
                self.status_updated.emit("Pasta de monitoramento não existe")
                return False
            
            # Start monitoring
            self._file_monitor_service.start_monitoring(
                monitor_path,
                self._on_file_detected
            )
            
            # Update status
            self._monitoring_status = MonitoringStatus(
                is_active=True,
                monitor_folder=str(monitor_path),
                output_folder=str(self._configuration.output_path) if self._configuration.output_path else None,
                started_at=datetime.now()
            )
            
            self.monitoring_started.emit(str(monitor_path))
            self.status_updated.emit(f"Monitoramento iniciado: {monitor_path}")
            
            # Perform initial scan of existing files
            self._perform_initial_scan(monitor_path)
            
            return True
            
        except Exception as e:
            self.status_updated.emit(f"Erro ao iniciar monitoramento: {e}")
            return False
    
    def stop_monitoring(self):
        """Stop file monitoring"""
        try:
            self._file_monitor_service.stop_monitoring()
            
            # Update status
            self._monitoring_status = MonitoringStatus(is_active=False)
            
            self.monitoring_stopped.emit()
            self.status_updated.emit("Monitoramento parado")
            
        except Exception as e:
            self.status_updated.emit(f"Erro ao parar monitoramento: {e}")
    
    # File processing
    def process_file_manually(self, file_path: Path) -> bool:
        """Process a file manually"""
        try:
            request = ProcessFileUseCaseRequest(
                file_path=file_path,
                process_archives=True,
                validate_schema=True,
                send_to_api=True,
                organize_output=self._configuration.auto_organize
            )
            
            # Set up real-time callback for individual results
            def on_result_ready(result: ValidationResult):
                """Callback called when each individual result is ready"""
                self._validation_results.append(result)
                self.validation_result_added.emit(result)
                
                # Update statistics immediately
                self._monitoring_status.files_processed += 1
                if result.is_valid:
                    self._monitoring_status.files_successful += 1
                else:
                    self._monitoring_status.files_failed += 1
                
                # Force UI update immediately
                QApplication.processEvents()
            
            # Add callback to use case if it supports it
            if hasattr(self._process_file_use_case, 'set_result_callback'):
                self._process_file_use_case.set_result_callback(on_result_ready)
            
            response = self._process_file_use_case.execute(request)
            
            # If use case doesn't support callbacks, fall back to batch processing
            if not hasattr(self._process_file_use_case, 'set_result_callback'):
                for result in response.results:
                    on_result_ready(result)
            
            # Notify UI about file completion
            success = response.success and not response.has_errors
            self.file_processed.emit(file_path.name, success)
            
            if success:
                self.status_updated.emit(f"✅ Arquivo processado: {file_path.name}")
            else:
                error_msg = response.error_message or "Falha no processamento"
                self.status_updated.emit(f"❌ Arquivo processado: {file_path.name}")
                self.status_updated.emit(f"ℹ️  Erro no processamento: {error_msg}")
            
            return success
            
        except Exception as e:
            self.status_updated.emit(f"Erro ao processar arquivo: {e}")
            return False
    
    def clear_results(self):
        """Clear all validation results"""
        self._validation_results.clear()
        self._monitoring_status.files_processed = 0
        self._monitoring_status.files_successful = 0
        self._monitoring_status.files_failed = 0
        self.status_updated.emit("Resultados limpos")
    
    def get_result_summary(self) -> dict:
        """Get summary of validation results"""
        total = len(self._validation_results)
        successful = sum(1 for r in self._validation_results if r.is_valid)
        failed = total - successful
        
        return {
            'total': total,
            'successful': successful,
            'failed': failed,
            'success_rate': (successful / total * 100) if total > 0 else 0
        }
    
    # Private methods
    def _on_file_detected(self, file_path: Path):
        """Handle file detection from monitoring service"""
        try:
            self.status_updated.emit(f"Arquivo detectado: {file_path.name}")
            self._monitoring_status.last_activity = datetime.now()
            
            # Process the file
            self.process_file_manually(file_path)
            
        except Exception as e:
            self.status_updated.emit(f"Erro ao processar arquivo detectado: {e}")
    
    def _update_processing_statistics(self, results: List[ValidationResult]):
        """Update processing statistics (only used when callback is not supported)"""
        for result in results:
            # Only update if not already updated via callback
            if not hasattr(self._process_file_use_case, 'set_result_callback'):
                self._monitoring_status.files_processed += 1
                
                if result.is_valid:
                    self._monitoring_status.files_successful += 1
                else:
                    self._monitoring_status.files_failed += 1
    
    # Utility methods
    def get_monitoring_uptime_minutes(self) -> int:
        """Get monitoring uptime in minutes"""
        if not self._monitoring_status.started_at:
            return 0
        return int((datetime.now() - self._monitoring_status.started_at).total_seconds() / 60)
    
    def _perform_initial_scan(self, monitor_path: Path):
        """Perform initial scan of existing files in monitor folder"""
        try:
            self.status_updated.emit("🔍 Iniciando varredura de arquivos existentes...")
            
            # Supported file extensions
            extensions = {'.xml', '.zip', '.rar', '.7z'}
            files_found = []
            
            # Scan folder recursively for supported files
            def scan_directory(directory: Path):
                try:
                    for item in directory.iterdir():
                        if item.is_file() and item.suffix.lower() in extensions:
                            files_found.append(item)
                        elif item.is_dir():
                            # Recursively scan subdirectories
                            scan_directory(item)
                except PermissionError:
                    self.status_updated.emit(f"⚠️  Sem permissão para acessar: {directory}")
                except Exception as e:
                    self.status_updated.emit(f"⚠️  Erro ao varrer {directory}: {e}")
            
            # Start scanning
            scan_directory(monitor_path)
            
            if files_found:
                self.status_updated.emit(f"📁 {len(files_found)} arquivo(s) encontrado(s) - iniciando processamento...")
                
                # Process each file found - with real-time UI updates
                for i, file_path in enumerate(files_found, 1):
                    if self._monitoring_status.is_active:  # Check if still monitoring
                        try:
                            # Show progress immediately
                            progress_msg = f"📄 [{i}/{len(files_found)}] Processando: {file_path.name}"
                            self.status_updated.emit(progress_msg)
                            
                            # Force immediate UI update
                            QApplication.processEvents()
                            
                            # Process the file (now with real-time callback support)
                            success = self.process_file_manually(file_path)
                            
                            # Show completion status immediately
                            if success:
                                self.status_updated.emit(f"✅ [{i}/{len(files_found)}] Concluído: {file_path.name}")
                            else:
                                self.status_updated.emit(f"❌ [{i}/{len(files_found)}] Falhou: {file_path.name}")
                            
                            # Force UI update after completion
                            QApplication.processEvents()
                            
                        except Exception as e:
                            self.status_updated.emit(f"❌ [{i}/{len(files_found)}] Erro: {file_path.name} - {e}")
                            QApplication.processEvents()
                    else:
                        break  # Stop if monitoring was stopped
                
                self.status_updated.emit(f"✅ Varredura inicial concluída - {len(files_found)} arquivo(s) processado(s)")
            else:
                self.status_updated.emit("📁 Nenhum arquivo encontrado na pasta de monitoramento")
                
        except Exception as e:
            self.status_updated.emit(f"❌ Erro na varredura inicial: {e}")