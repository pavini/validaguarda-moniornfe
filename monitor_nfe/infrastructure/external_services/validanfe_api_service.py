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
            
            # Log API request details for debugging
            print(f"[ValidaNFeAPIService] API Request: {url}")
            print(f"[ValidaNFeAPIService] Headers: {{'X-API-KEY': '[TOKEN]'}}")
            print(f"[ValidaNFeAPIService] Sending as multipart/form-data with xmlFile field")
            print(f"[ValidaNFeAPIService] XML content length: {len(xml_content)} chars")
            print(f"[ValidaNFeAPIService] XML starts with: {xml_content[:100]}...")
            print(f"[ValidaNFeAPIService] File name: {document.filename}")
            
            # Make API request with retry logic
            response = self._make_request_with_retry(url, files, headers)
            
            # Log response for debugging
            print(f"[ValidaNFeAPIService] API Response: {response.status_code}")
            print(f"[ValidaNFeAPIService] Response headers: {dict(response.headers)}")
            if response.text:
                print(f"[ValidaNFeAPIService] Response text (first 300 chars): {response.text[:300]}")
            else:
                print(f"[ValidaNFeAPIService] Response has no text content")
            
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
                # API error - handle specific status codes
                if response.status_code == 401:
                    error_message = "Token inválido/expirado"
                elif response.status_code == 400:
                    error_message = f"Validação falhou: {response.text[:100] if response.text else 'Dados inválidos'}"
                elif response.status_code == 404:
                    error_message = "Endpoint não encontrado (404) - Verifique a URL da API"
                elif response.status_code == 409:
                    # NFe já existe - isso pode ser considerado sucesso
                    return APIResponse(
                        success=True,
                        message="NFe já foi enviada anteriormente",
                        data={"raw_response": response.text[:200]} if response.text else None,
                        status_code=response.status_code,
                        response_time_ms=response_time_ms
                    )
                elif response.status_code == 429:
                    error_message = "API sobrecarregada - tente novamente mais tarde"
                elif response.status_code == 500:
                    error_message = "Erro interno do servidor (500)"
                elif response.status_code == 502:
                    error_message = "Bad Gateway (502) - Servidor indisponível temporariamente"
                elif response.status_code == 503:
                    error_message = "Service Unavailable (503) - Servidor sobrecarregado temporariamente"
                elif response.status_code == 504:
                    error_message = "Gateway Timeout (504) - Timeout no servidor"
                else:
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
    
    def _make_request_with_retry(self, url, files, headers, max_retries=3):
        """Make HTTP request with retry logic for temporary server errors"""
        import time
        
        for attempt in range(max_retries + 1):
            try:
                print(f"[ValidaNFeAPIService] 🌐 Tentativa {attempt + 1}/{max_retries + 1}")
                response = requests.post(url, files=files, headers=headers, timeout=30)
                
                # If success or permanent error, return immediately
                if response.status_code < 500 or response.status_code in [500]:
                    return response
                
                # If temporary error (502, 503, 504) and not last attempt, retry
                if response.status_code in [502, 503, 504] and attempt < max_retries:
                    wait_time = (2 ** attempt)  # Exponential backoff: 1s, 2s, 4s
                    print(f"[ValidaNFeAPIService] ⏰ HTTP {response.status_code} - Retry em {wait_time}s...")
                    print(f"[ValidaNFeAPIService]    Motivo: {response.text[:100] if response.text else 'Servidor indisponível'}")
                    time.sleep(wait_time)
                    continue
                
                return response
                
            except requests.exceptions.Timeout:
                if attempt < max_retries:
                    wait_time = (2 ** attempt)
                    print(f"[ValidaNFeAPIService] ⏰ Timeout - Retry em {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    raise
            
            except requests.exceptions.ConnectionError as e:
                if attempt < max_retries and ("connection" in str(e).lower() or "reset" in str(e).lower()):
                    wait_time = (2 ** attempt)
                    print(f"[ValidaNFeAPIService] ⏰ Erro de conexão - Retry em {wait_time}s...")
                    print(f"[ValidaNFeAPIService]    Motivo: {str(e)[:100]}")
                    time.sleep(wait_time)
                    continue
                else:
                    raise
        
        # Should not reach here
        return response