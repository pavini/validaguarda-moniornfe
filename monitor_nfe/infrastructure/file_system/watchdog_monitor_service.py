import time
from pathlib import Path
from typing import Callable, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

from application.interfaces.services import IFileMonitorService


class NFEFileHandler(FileSystemEventHandler):
    """File system event handler for NFe files"""
    
    def __init__(self, callback: Callable[[Path], None]):
        super().__init__()
        self.callback = callback
        self._supported_extensions = {'.xml', '.zip', '.rar', '.7z'}
    
    def on_created(self, event: FileSystemEvent):
        """Handle file creation events"""
        if not event.is_directory:
            self._process_file_event(Path(event.src_path))
    
    def on_modified(self, event: FileSystemEvent):
        """Handle file modification events"""
        if not event.is_directory:
            # Add a small delay to ensure file is fully written
            time.sleep(0.5)
            self._process_file_event(Path(event.src_path))
    
    def on_moved(self, event: FileSystemEvent):
        """Handle file move events"""
        if not event.is_directory and hasattr(event, 'dest_path'):
            self._process_file_event(Path(event.dest_path))
    
    def _process_file_event(self, file_path: Path):
        """Process file system event for supported file types"""
        try:
            # Check if file has supported extension
            if file_path.suffix.lower() in self._supported_extensions:
                # Check if file exists and has content (to avoid processing incomplete files)
                if file_path.exists() and file_path.stat().st_size > 0:
                    self.callback(file_path)
        except Exception as e:
            # Log error but don't crash the monitor
            print(f"Erro ao processar evento de arquivo {file_path}: {e}")


class WatchdogMonitorService(IFileMonitorService):
    """File monitoring service implementation using Watchdog"""
    
    def __init__(self):
        self._observer: Optional[Observer] = None
        self._monitoring_path: Optional[Path] = None
        self._callback: Optional[Callable[[Path], None]] = None
    
    def start_monitoring(self, folder_path: Path, callback: Callable[[Path], None]):
        """Start monitoring a folder for file changes"""
        # Stop any existing monitoring
        self.stop_monitoring()
        
        try:
            if not folder_path.exists():
                raise ValueError(f"Pasta de monitoramento não existe: {folder_path}")
            
            if not folder_path.is_dir():
                raise ValueError(f"Caminho especificado não é uma pasta: {folder_path}")
            
            # Create event handler
            event_handler = NFEFileHandler(callback)
            
            # Create and configure observer
            self._observer = Observer()
            self._observer.schedule(
                event_handler,
                str(folder_path),
                recursive=True  # Monitor subfolders too
            )
            
            # Start monitoring
            self._observer.start()
            
            # Store monitoring info
            self._monitoring_path = folder_path
            self._callback = callback
            
            print(f"✅ Monitoramento iniciado: {folder_path}")
            print(f"   Monitorando subpastas: Sim")
            print(f"   Tipos suportados: XML, ZIP, RAR, 7Z")
            
        except Exception as e:
            print(f"❌ Erro ao iniciar monitoramento: {e}")
            self.stop_monitoring()
            raise
    
    def stop_monitoring(self):
        """Stop file system monitoring"""
        if self._observer and self._observer.is_alive():
            try:
                self._observer.stop()
                self._observer.join(timeout=5)  # Wait up to 5 seconds for clean shutdown
                print("🛑 Monitoramento parado")
            except Exception as e:
                print(f"⚠️  Erro ao parar monitoramento: {e}")
        
        self._observer = None
        self._monitoring_path = None
        self._callback = None
    
    def is_monitoring(self) -> bool:
        """Check if monitoring is active"""
        return (self._observer is not None and 
                self._observer.is_alive() and
                self._monitoring_path is not None)
    
    @property
    def monitoring_path(self) -> Optional[Path]:
        """Get current monitoring path"""
        return self._monitoring_path
    
    def __del__(self):
        """Cleanup on destruction"""
        self.stop_monitoring()