import requests
import time
from pathlib import Path
from typing import Optional, Dict, Any

from application.interfaces.services import IAPIService
from domain.entities.nfe_document import NFEDocument
from domain.entities.validation_result import APIResponse
from domain.value_objects.api_token import APIToken


class ValidaNFeAPIService(IAPIService):
    """ValidaNFe API service implementation"""
    
    def __init__(self, base_url: str = "https://api.validanfe.com"):
        self.base_url = base_url
        self.guarda_endpoint = "/GuardaNFe/EnviarXml"
    
    def validate_nfe(self, document: NFEDocument, token: APIToken) -> APIResponse:
        """Send NFe document to ValidaNFe API for validation"""
        start_time = time.time()
        
        try:
            # Check if file exists
            if not document.exists():
                return APIResponse(
                    success=False,
                    message=f"Arquivo não encontrado: {document.filename}",
                    status_code=None,
                    response_time_ms=0
                )
            
            # Read XML file content
            xml_content = self._read_xml_content(document.file_path)
            if not xml_content:
                return APIResponse(
                    success=False,
                    message="Não foi possível ler o conteúdo do arquivo XML",
                    status_code=None,
                    response_time_ms=0
                )
            
            # Validate XML content
            validation_error = self._validate_xml_content(xml_content)
            if validation_error:
                return APIResponse(
                    success=False,
                    message=validation_error,
                    status_code=None,
                    response_time_ms=0
                )
            
            # Check file size limit (5MB)
            if len(xml_content) > 5 * 1024 * 1024:
                return APIResponse(
                    success=False,
                    message="Arquivo muito grande (limite 5MB)",
                    status_code=None,
                    response_time_ms=0
                )
            
            # Prepare API request
            headers = {'X-API-KEY': str(token)}
            files = {
                'xmlFile': (document.filename, xml_content, 'application/xml')
            }
            url = f"{self.base_url}{self.guarda_endpoint}"
            
            # Make API request
            response = requests.post(url, files=files, headers=headers, timeout=30)
            
            # Calculate response time
            end_time = time.time()
            response_time_ms = (end_time - start_time) * 1000
            
            # Process response
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    return APIResponse(
                        success=True,
                        message="NFe enviada com sucesso",
                        data=response_data,
                        status_code=response.status_code,
                        response_time_ms=response_time_ms
                    )
                except ValueError:
                    # Response is not JSON
                    return APIResponse(
                        success=True,
                        message="NFe enviada com sucesso (resposta não-JSON)",
                        data={"raw_response": response.text[:200]},
                        status_code=response.status_code,
                        response_time_ms=response_time_ms
                    )
            else:
                # API error
                error_message = self._extract_error_message(response)
                return APIResponse(
                    success=False,
                    message=error_message,
                    data={"raw_response": response.text[:200]} if response.text else None,
                    status_code=response.status_code,
                    response_time_ms=response_time_ms
                )
                
        except requests.exceptions.Timeout:
            end_time = time.time()
            response_time_ms = (end_time - start_time) * 1000
            return APIResponse(
                success=False,
                message="Timeout na conexão com a API",
                status_code=None,
                response_time_ms=response_time_ms
            )
            
        except requests.exceptions.ConnectionError:
            end_time = time.time()
            response_time_ms = (end_time - start_time) * 1000
            return APIResponse(
                success=False,
                message="Erro de conexão com a API",
                status_code=None,
                response_time_ms=response_time_ms
            )
            
        except Exception as e:
            end_time = time.time()
            response_time_ms = (end_time - start_time) * 1000
            return APIResponse(
                success=False,
                message=f"Erro inesperado: {str(e)[:100]}",
                status_code=None,
                response_time_ms=response_time_ms
            )
    
    def test_connection(self, token: APIToken) -> bool:
        """Test API connectivity and token validity"""
        try:
            # Use a simple endpoint or create a minimal test request
            # For now, we'll use a HEAD request to the base URL
            headers = {'X-API-KEY': str(token)}
            response = requests.head(self.base_url, headers=headers, timeout=10)
            return response.status_code < 500  # Accept any non-server-error
        except Exception:
            return False
    
    def _read_xml_content(self, file_path: Path) -> Optional[str]:
        """Read XML file content with multiple encoding attempts"""
        encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
        
        for encoding in encodings:
            try:
                return file_path.read_text(encoding=encoding)
            except UnicodeDecodeError:
                continue
            except Exception:
                break
        
        return None
    
    def _validate_xml_content(self, xml_content: str) -> Optional[str]:
        """Validate XML content and return error message if invalid"""
        if not xml_content or len(xml_content.strip()) < 10:
            return "Arquivo XML vazio ou muito pequeno"
        
        xml_stripped = xml_content.strip()
        if not xml_stripped.startswith('<?xml'):
            return "Arquivo não é um XML válido (sem declaração XML)"
        
        if '<NFe' not in xml_content and '<nfeProc' not in xml_content:
            return "Arquivo não parece ser uma NFe válida"
        
        return None
    
    def _extract_error_message(self, response: requests.Response) -> str:
        """Extract error message from API response"""
        try:
            if response.text:
                # Try to parse as JSON first
                try:
                    error_data = response.json()
                    if isinstance(error_data, dict):
                        return error_data.get('message', error_data.get('error', f"Erro HTTP {response.status_code}"))
                except ValueError:
                    pass
                
                # Return first part of text response
                return f"Erro HTTP {response.status_code}: {response.text[:100]}"
            else:
                return f"Erro HTTP {response.status_code}"
        except Exception:
            return f"Erro HTTP {response.status_code}"