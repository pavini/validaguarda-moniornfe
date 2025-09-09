#!/usr/bin/env python3
"""
Simulação completa do envio como feito no aplicativo principal
"""
from pathlib import Path
import requests
import re
import time

def extract_nfe_key(xml_content):
    """Extract NFe key from XML content - exata replica do código principal"""
    try:
        # Try to extract chNFe from XML
        # Look for chNFe tag
        match = re.search(r'<chNFe>([^<]+)</chNFe>', xml_content)
        if match:
            return match.group(1)
        
        # Alternative: look for Id attribute
        match = re.search(r'Id="NFe(\d{44})"', xml_content)
        if match:
            return match.group(1)
            
        # Alternative: try to extract from infNFe Id
        match = re.search(r'<infNFe[^>]*Id="NFe(\d{44})"', xml_content)
        if match:
            return match.group(1)
        
        return None
    except Exception:
        return None

def send_nfe_like_main_app(xml_file_path, token):
    """
    Simular exatamente como o aplicativo principal envia NFe
    Baseado no código do monitor_nfe/main.py:771-888
    """
    try:
        base_url = "https://api.validanfe.com"
        guarda_endpoint = "/GuardaNFe/EnviarXml"
        
        print(f"=== SIMULAÇÃO COMPLETA DO APLICATIVO PRINCIPAL ===")
        print(f"Token: {token[:20]}..." if token else "Token: NÃO FORNECIDO")
        
        if not token:
            return {"success": False, "message": "Token não configurado"}
        
        # Check if file exists
        file_path = Path(xml_file_path)
        if not file_path.exists():
            return {"success": False, "message": f"Arquivo não encontrado: {file_path.name}"}
        
        print(f"Arquivo: {file_path}")
        print(f"Tamanho: {file_path.stat().st_size} bytes")
        
        # Read XML file with better error handling
        try:
            xml_content = file_path.read_text(encoding='utf-8')
            print("✅ Lido com UTF-8")
        except UnicodeDecodeError:
            try:
                # Try with latin-1 encoding if utf-8 fails
                xml_content = file_path.read_text(encoding='latin-1')
                print("✅ Lido com latin-1")
            except Exception as e:
                return {"success": False, "message": f"Erro de encoding: {str(e)[:50]}..."}
        except Exception as e:
            return {"success": False, "message": f"Erro na leitura: {str(e)[:50]}..."}
        
        # Validate XML content
        if not xml_content or len(xml_content.strip()) < 10:
            return {"success": False, "message": "Arquivo XML vazio ou muito pequeno"}
        
        # Basic XML validation - must start with <?xml and contain <NFe or <nfeProc
        xml_stripped = xml_content.strip()
        if not xml_stripped.startswith('<?xml'):
            return {"success": False, "message": "Arquivo não é um XML válido (sem declaração XML)"}
        
        if '<NFe' not in xml_content and '<nfeProc' not in xml_content:
            return {"success": False, "message": "Arquivo não parece ser uma NFe válida"}
        
        print("✅ Validações básicas passaram")
        
        # Extract NFe key from XML if possible
        nfe_chave = extract_nfe_key(xml_content)
        
        # Prepare headers (ValidaNFe uses X-API-KEY with multipart/form-data)
        headers = {
            'X-API-KEY': token
            # Don't set Content-Type - let requests set it for multipart
        }
        
        # Prepare multipart form data (like .NET example)
        files = {
            'xmlFile': (file_path.name, xml_content, 'application/xml')
        }
        
        # Make API request
        url = f"{base_url}{guarda_endpoint}"
        
        # Log API request details for debugging
        print(f"\nAPI Request: {url}")
        print(f"Headers: {{'X-API-KEY': '[TOKEN]'}}")
        print(f"Sending as multipart/form-data with xmlFile field")
        print(f"XML content length: {len(xml_content)} chars")
        print(f"XML starts with: {xml_content[:100]}...")
        print(f"NFe key: {nfe_chave[:20]}..." if nfe_chave else "NFe key: (não encontrada)")
        
        # Check file size
        if len(xml_content) > 5 * 1024 * 1024:  # 5MB limit
            return {"success": False, "message": "Arquivo muito grande (limite 5MB)"}
        
        print(f"\n🚀 Enviando requisição...")
        start_time = time.time()
        
        try:
            response = requests.post(url, files=files, headers=headers, timeout=30)
        except requests.exceptions.Timeout:
            return {"success": False, "message": "Timeout na API"}
        except requests.exceptions.ConnectionError:
            return {"success": False, "message": "Erro de conexão"}
        except Exception as e:
            return {"success": False, "message": f"Erro na requisição: {str(e)[:100]}"}
        
        end_time = time.time()
        response_time = (end_time - start_time) * 1000
        
        # Log response for debugging
        print(f"\n=== RESPOSTA DA API ===")
        print(f"Status Code: {response.status_code}")
        print(f"Tempo de resposta: {response_time:.2f}ms")
        print(f"Headers de resposta: {dict(response.headers)}")
        
        if response.text:
            print(f"Response body (primeiros 300 chars):")
            print(response.text[:300])
        
        # Handle response
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"✅ JSON parseado: {result}")
                return {
                    "success": True, 
                    "message": "Enviado ✅",
                    "data": result
                }
            except Exception:
                print("⚠️ Resposta não é JSON válido")
                return {"success": True, "message": "Enviado com sucesso [OK] (resposta não-JSON)"}
        elif response.status_code == 401:
            return {"success": False, "message": "Token inválido/expirado ✗"}
        elif response.status_code == 400:
            try:
                error_text = response.text
                print(f"❌ Erro 400: {error_text}")
                return {"success": False, "message": f"Validação falhou: {error_text[:100]}..."}
            except:
                return {"success": False, "message": "Erro 400: Dados inválidos"}
        elif response.status_code == 404:
            return {"success": False, "message": "Endpoint não encontrado (404) - Verifique a URL da API"}
        elif response.status_code == 409:
            return {"success": True, "message": "NFe já existe ⚠️"}
        elif response.status_code == 429:
            return {"success": False, "message": "API sobrecarregada - tente novamente ⏰"}
        elif response.status_code == 500:
            return {"success": False, "message": "Erro interno do servidor (500)"}
        else:
            return {"success": False, "message": f"HTTP {response.status_code}: {response.text[:100] if response.text else 'Sem conteúdo'}"}
            
    except Exception as e:
        return {"success": False, "message": f"Erro inesperado: {str(e)[:100]}"}

def main():
    print("=== TESTE COMPLETO DE SIMULAÇÃO ===")
    
    xml_file = "xml-teste.xml"
    
    # Pedir token se não fornecido como argumento
    import sys
    if len(sys.argv) > 1:
        token = sys.argv[1]
    else:
        token = input("Digite o token da API (ou ENTER para usar um token de teste): ").strip()
        if not token:
            token = "TOKEN_DE_TESTE_PARA_DEBUG"
    
    result = send_nfe_like_main_app(xml_file, token)
    
    print(f"\n=== RESULTADO FINAL ===")
    print(f"Sucesso: {result['success']}")
    print(f"Mensagem: {result['message']}")
    if 'data' in result:
        print(f"Dados: {result['data']}")

if __name__ == "__main__":
    main()