import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Optional, Callable, Dict
import uuid
from datetime import datetime

from domain.entities.processing_session import ProcessingSession, ProcessingState
from domain.entities.validation_result import ValidationResult
from application.use_cases.process_file_use_case import ProcessFileUseCase, ProcessFileUseCaseRequest
from application.interfaces.repositories import ILogRepository


class ParallelProcessingService:
    """Service for parallel processing of files with thread safety"""
    
    def __init__(
        self,
        process_file_use_case: ProcessFileUseCase,
        log_repository: ILogRepository,
        max_threads: int = 10
    ):
        self._process_file_use_case = process_file_use_case
        self._log_repository = log_repository
        self._max_threads = max_threads
        self._executor: Optional[ThreadPoolExecutor] = None
        self._active_sessions: Dict[str, ProcessingSession] = {}
        self._session_lock = threading.Lock()
        
        # Callbacks
        self._progress_callback: Optional[Callable] = None
        self._result_callback: Optional[Callable] = None
    
    def set_progress_callback(self, callback: Callable[[str, int, int], None]):
        """Set callback for progress updates: (session_id, processed, total)"""
        self._progress_callback = callback
    
    def set_result_callback(self, callback: Callable[[ValidationResult, str], None]):
        """Set callback for individual results: (result, thread_id)"""
        self._result_callback = callback
    
    def start_parallel_processing(
        self, 
        file_paths: List[Path],
        process_archives: bool = True,
        validate_schema: bool = True,
        send_to_api: bool = True,
        organize_output: bool = True
    ) -> str:
        """Start parallel processing of multiple files"""
        
        # Create processing session
        session = ProcessingSession(max_parallel_threads=self._max_threads)
        
        # Add files to session
        for file_path in file_paths:
            session.add_file(file_path, ProcessingState.PENDING)
        
        # Store session
        with self._session_lock:
            self._active_sessions[session.session_id] = session
        
        # Start thread pool if not already running
        if self._executor is None:
            self._executor = ThreadPoolExecutor(max_workers=self._max_threads, thread_name_prefix="NFE-Worker")
        
        self._log_repository.log_info(f"🚀 Iniciando processamento paralelo: {len(file_paths)} arquivo(s), sessão {session.session_id}")
        
        # Submit processing tasks
        futures = []
        for file_path in file_paths:
            future = self._executor.submit(
                self._process_single_file,
                session.session_id,
                file_path,
                ProcessFileUseCaseRequest(
                    file_path=file_path,
                    process_archives=process_archives,
                    validate_schema=validate_schema,
                    send_to_api=send_to_api,
                    organize_output=organize_output
                )
            )
            futures.append(future)
        
        # Monitor completion in background thread
        monitoring_thread = threading.Thread(
            target=self._monitor_session_completion,
            args=(session.session_id, futures),
            daemon=True
        )
        monitoring_thread.start()
        
        return session.session_id
    
    def _process_single_file(self, session_id: str, file_path: Path, request: ProcessFileUseCaseRequest):
        """Process a single file within a session"""
        thread_id = threading.current_thread().name
        start_time = time.time()
        
        # Get session
        with self._session_lock:
            session = self._active_sessions.get(session_id)
            if not session:
                return
        
        try:
            # Mark file as being processed
            session.mark_file_processing(file_path, thread_id)
            
            self._log_repository.log_info(f"[{thread_id}] 🔄 Iniciando processamento: {file_path.name}")
            
            # Process the file
            response = self._process_file_use_case.execute(request)
            
            # Process each result immediately and call callbacks
            for result in response.results:
                try:
                    # Call main result callback immediately for each result
                    if self._result_callback:
                        self._result_callback(result, thread_id)
                        
                except Exception as e:
                    self._log_repository.log_error(f"Erro no callback de resultado: {e}")
            
            # Update progress after processing
            try:
                if self._progress_callback:
                    completed_count = len(session.get_completed_files()) + 1  # +1 for current
                    total_count = len(session.files)
                    self._progress_callback(session_id, completed_count, total_count)
            except Exception as e:
                self._log_repository.log_error(f"Erro no callback de progresso: {e}")
            
            # Mark as completed
            if response.success:
                session.mark_file_completed(file_path)
                processing_time = (time.time() - start_time) * 1000
                self._log_repository.log_info(f"[{thread_id}] ✅ Concluído: {file_path.name} ({processing_time:.1f}ms)")
            else:
                error_msg = response.error_message or "Processamento falhou"
                session.mark_file_error(file_path, error_msg)
                self._log_repository.log_error(f"[{thread_id}] ❌ Falhou: {file_path.name} - {error_msg}")
            
        except Exception as e:
            # Mark as error
            session.mark_file_error(file_path, str(e))
            self._log_repository.log_error(f"[{thread_id}] ❌ Erro: {file_path.name} - {e}")
    
    def _monitor_session_completion(self, session_id: str, futures: List):
        """Monitor session completion and cleanup"""
        try:
            # Wait for all futures to complete
            for future in as_completed(futures):
                try:
                    future.result()  # Get result to catch any exceptions
                except Exception as e:
                    self._log_repository.log_error(f"Erro em thread de processamento: {e}")
            
            # Session completed
            with self._session_lock:
                session = self._active_sessions.get(session_id)
                if session:
                    summary = session.get_processing_summary()
                    self._log_repository.log_info(
                        f"🏁 Sessão {session_id} concluída: "
                        f"{summary['completed']} sucesso(s), {summary['errors']} erro(s)"
                    )
                    
                    # Final progress callback
                    if self._progress_callback:
                        self._progress_callback(session_id, summary['completed'] + summary['errors'], summary['total'])
                    
                    # Cleanup session after a delay
                    cleanup_thread = threading.Thread(
                        target=self._cleanup_session_delayed,
                        args=(session_id,),
                        daemon=True
                    )
                    cleanup_thread.start()
                    
        except Exception as e:
            self._log_repository.log_error(f"Erro no monitoramento de sessão {session_id}: {e}")
    
    def _cleanup_session_delayed(self, session_id: str, delay_seconds: int = 5):
        """Clean up session after a delay to ensure all operations complete"""
        try:
            time.sleep(delay_seconds)
            
            with self._session_lock:
                session = self._active_sessions.pop(session_id, None)
                if session:
                    # Force cleanup of any remaining temp files
                    try:
                        self._process_file_use_case.force_cleanup_temp_files()
                    except Exception as e:
                        self._log_repository.log_warning(f"Erro na limpeza final dos arquivos temporários: {e}")
                    
                    # Clean up temp directory if it was created
                    session.cleanup_temp_directory()
                    self._log_repository.log_debug(f"🧹 Sessão {session_id} removida")
                    
        except Exception as e:
            self._log_repository.log_error(f"Erro na limpeza da sessão {session_id}: {e}")
    
    def get_session_status(self, session_id: str) -> Optional[Dict]:
        """Get current status of a processing session"""
        with self._session_lock:
            session = self._active_sessions.get(session_id)
            if session:
                summary = session.get_processing_summary()
                return {
                    'session_id': session_id,
                    'created_at': session.created_at,
                    'is_complete': session.is_complete(),
                    'summary': summary,
                    'active_files': len(session.get_active_files()),
                    'max_threads': session.max_parallel_threads
                }
        return None
    
    def stop_all_processing(self):
        """Stop all processing and clean up"""
        if self._executor:
            self._log_repository.log_info("🛑 Parando processamento paralelo...")
            self._executor.shutdown(wait=True)
            self._executor = None
        
        # Clean up all sessions
        with self._session_lock:
            for session in self._active_sessions.values():
                session.cleanup_temp_directory()
            self._active_sessions.clear()
    
    def __del__(self):
        """Cleanup on destruction"""
        self.stop_all_processing()