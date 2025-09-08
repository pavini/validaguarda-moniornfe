import zipfile
import tempfile
import shutil
from pathlib import Path
from typing import List

from application.interfaces.services import IArchiveService


class ArchiveExtractorService(IArchiveService):
    """Archive extraction service implementation"""
    
    def __init__(self):
        self._supported_extensions = {'.zip', '.rar', '.7z'}
    
    def extract_archive(self, archive_path: Path, extract_to: Path) -> List[Path]:
        """Extract archive and return list of extracted files"""
        extracted_files = []
        
        try:
            if not archive_path.exists():
                raise FileNotFoundError(f"Arquivo não encontrado: {archive_path}")
            
            if not self.can_extract(archive_path):
                raise ValueError(f"Formato de arquivo não suportado: {archive_path.suffix}")
            
            # Ensure extraction directory exists
            extract_to.mkdir(parents=True, exist_ok=True)
            
            # Extract based on file type
            if archive_path.suffix.lower() == '.zip':
                extracted_files = self._extract_zip(archive_path, extract_to)
            elif archive_path.suffix.lower() in ['.rar', '.7z']:
                # For now, we'll focus on ZIP files as they are most common
                # RAR and 7Z support would require additional libraries
                raise NotImplementedError(f"Extração de arquivos {archive_path.suffix} não implementada ainda")
            
            print(f"✅ Arquivo extraído: {archive_path.name}")
            print(f"   Arquivos extraídos: {len(extracted_files)}")
            
            return extracted_files
            
        except Exception as e:
            print(f"❌ Erro na extração: {archive_path.name} - {e}")
            raise
    
    def can_extract(self, file_path: Path) -> bool:
        """Check if file is a supported archive format"""
        return file_path.suffix.lower() in self._supported_extensions
    
    def _extract_zip(self, zip_path: Path, extract_to: Path) -> List[Path]:
        """Extract ZIP file and return list of extracted files"""
        extracted_files = []
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Get list of all files in the archive
                file_list = zip_ref.namelist()
                
                print(f"   Arquivos no ZIP: {len(file_list)}")
                
                # Extract all files
                for file_info in zip_ref.infolist():
                    # Skip directories
                    if file_info.is_dir():
                        continue
                    
                    try:
                        # Extract the file
                        extracted_path = extract_to / file_info.filename
                        
                        # Ensure parent directory exists
                        extracted_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        # Extract file content
                        with zip_ref.open(file_info) as source, open(extracted_path, 'wb') as target:
                            shutil.copyfileobj(source, target)
                        
                        # Set file permissions if available
                        if hasattr(file_info, 'external_attr') and file_info.external_attr:
                            extracted_path.chmod(file_info.external_attr >> 16)
                        
                        extracted_files.append(extracted_path)
                        print(f"     ✓ {file_info.filename}")
                        
                    except Exception as e:
                        print(f"     ❌ Erro ao extrair {file_info.filename}: {e}")
                        continue
                
        except zipfile.BadZipFile:
            raise ValueError(f"Arquivo ZIP corrompido ou inválido: {zip_path.name}")
        except Exception as e:
            raise RuntimeError(f"Erro na extração do ZIP: {e}")
        
        return extracted_files
    
    def get_supported_extensions(self) -> List[str]:
        """Get list of supported archive extensions"""
        return list(self._supported_extensions)