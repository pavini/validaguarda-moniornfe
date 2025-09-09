#!/usr/bin/env python3
"""
Testar ambas as implementações da API para comparar
"""
import sys
from pathlib import Path
import requests
import time

# Adicionar caminho
sys.path.append('./monitor_nfe')

def test_both_api_implementations():
    """Testar tanto o ValidaNFeAPIService quanto o método do main.py"""
    
    print("=" * 80)
    print("🔍 TESTE COMPARATIVO DAS IMPLEMENTAÇÕES DE API")
    print("=" * 80)
    
    xml_file = Path("xml-problematico.xml")
    
    if not xml_file.exists():
        print("❌ Arquivo xml-problematico.xml não encontrado")
        return
    
    # Pedir token
    token = input("Digite o token da ValidaNFe API (ou ENTER para usar token de teste): ").strip()
    if not token:
        token = "TOKEN_DE_TESTE"
        print("⚠️  Usando token de teste")
    
    print(f"\n🧪 TESTE 1: IMPLEMENTAÇÃO DO MAIN.PY (send_nfe)")
    print("=" * 80)
    
    try:
        # Simular o método send_nfe do main.py
        result_main = test_main_py_implementation(xml_file, token)
        print(f"✅ Implementação main.py concluída:")
        print(f"   Sucesso: {result_main.get('success', False)}")
        print(f"   Mensagem: {result_main.get('message', 'N/A')}")
        
    except Exception as e:
        print(f"❌ ERRO na implementação main.py: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n🧪 TESTE 2: VALIDANFE API SERVICE (melhorado)")
    print("=" * 80)
    
    try:
        # Testar ValidaNFeAPIService
        result_service = test_validanfe_api_service(xml_file, token)
        print(f"✅ ValidaNFeAPIService concluído:")
        print(f"   Sucesso: {result_service.success}")
        print(f"   Mensagem: {result_service.message}")
        print(f"   Status Code: {result_service.status_code}")
        print(f"   Tempo: {result_service.response_time_ms:.2f}ms")
        
    except Exception as e:
        print(f"❌ ERRO no ValidaNFeAPIService: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n📊 COMPARAÇÃO DE RESULTADOS")
    print("=" * 80)
    
    try:
        print("Main.py:")
        print(f"   Sucesso: {result_main.get('success', False)}")
        print(f"   Mensagem: {result_main.get('message', 'ERRO')}")
        
        print("ValidaNFeAPIService:")
        print(f"   Sucesso: {result_service.success}")
        print(f"   Mensagem: {result_service.message}")
        print(f"   Status: {result_service.status_code}")
        
        # Comparar resultados
        if result_main.get('success') == result_service.success:
            print("✅ Ambas implementações retornaram o mesmo resultado")
        else:
            print("⚠️  Implementações retornaram resultados diferentes!")
            
    except:
        print("❌ Erro na comparação - uma ou ambas implementações falharam")

def test_main_py_implementation(xml_file, token):
    """Simular exatamente o método send_nfe do main.py"""
    print("Executando lógica do main.py send_nfe...")
    
    try:
        if not token:
            return {"success": False, "message": "Token não configurado"}
        
        # Check if file exists
        file_path = Path(xml_file)
        if not file_path.exists():
            return {"success": False, "message": f"Arquivo não encontrado: {file_path.name}"}
        
        # Read XML file with better error handling
        try:
            xml_content = file_path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            try:
                # Try with latin-1 encoding if utf-8 fails
                xml_content = file_path.read_text(encoding='latin-1')
            except Exception as e:
                return {"success": False, "message": f"Erro de encoding: {str(e)[:50]}..."}
        except Exception as e:
            return {"success": False, "message": f"Erro na leitura: {str(e)[:50]}..."}
        
        # Validate XML content
        if not xml_content or len(xml_content.strip()) < 10:
            return {"success": False, "message": "Arquivo XML vazio ou muito pequeno"}
        
        # Basic XML validation
        xml_stripped = xml_content.strip()
        if not xml_stripped.startswith('<?xml'):
            return {"success": False, "message": "Arquivo não é um XML válido (sem declaração XML)"}
        
        if '<NFe' not in xml_content and '<nfeProc' not in xml_content:
            return {"success": False, "message": "Arquivo não parece ser uma NFe válida"}
        
        # Check file size
        if len(xml_content) > 5 * 1024 * 1024:  # 5MB limit
            return {"success": False, "message": "Arquivo muito grande (limite 5MB)"}
        
        # Prepare headers
        headers = {
            'X-API-KEY': token
        }
        
        # Prepare multipart form data
        files = {
            'xmlFile': (file_path.name, xml_content, 'application/xml')
        }
        
        # Make API request
        url = "https://api.validanfe.com/GuardaNFe/EnviarXml"
        
        print(f"   Enviando para: {url}")
        print(f"   Arquivo: {file_path.name}")
        print(f"   Tamanho: {len(xml_content)} chars")
        
        response = requests.post(url, files=files, headers=headers, timeout=30)
        
        print(f"   Status: {response.status_code}")
        print(f"   Resposta: {response.text[:200] if response.text else 'Vazio'}")
        
        # Handle response exactly like main.py
        if response.status_code == 200:
            try:
                result = response.json()
                return {
                    "success": True, 
                    "message": "Enviado ✅",
                    "data": result
                }
            except Exception:
                return {"success": True, "message": "Enviado com sucesso [OK] (resposta não-JSON)"}
        elif response.status_code == 401:
            return {"success": False, "message": "Token inválido/expirado ✗"}
        elif response.status_code == 400:
            try:
                error_text = response.text
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
            try:
                error_text = response.text[:100]
                return {"success": False, "message": f"HTTP {response.status_code}: {error_text}..."}
            except:
                return {"success": False, "message": f"Erro HTTP {response.status_code}"}
                
    except requests.exceptions.Timeout:
        return {"success": False, "message": "Timeout na API ⏰"}
    except requests.exceptions.ConnectionError as e:
        error_msg = str(e)
        if "Name or service not known" in error_msg:
            return {"success": False, "message": "DNS não resolveu. Verifique a URL da API 🌐"}
        elif "Connection refused" in error_msg:
            return {"success": False, "message": "Conexão recusada pelo servidor 🔌"}
        else:
            return {"success": False, "message": f"Erro de conexão: {str(e)[:50]}... 🔌"}
    except requests.exceptions.RequestException as e:
        return {"success": False, "message": f"Erro HTTP: {str(e)[:50]}..."}
    except Exception as e:
        error_msg = str(e)
        print(f"❌ ERRO INESPERADO no send_nfe: {error_msg}")
        import traceback
        print("📋 Traceback completo:")
        traceback.print_exc()
        return {"success": False, "message": f"Erro inesperado: {error_msg[:100]}..."}

def test_validanfe_api_service(xml_file, token):
    """Testar ValidaNFeAPIService melhorado"""
    print("Executando ValidaNFeAPIService...")
    
    try:
        from infrastructure.external_services.validanfe_api_service import ValidaNFeAPIService
        from domain.entities.nfe_document import NFEDocument
        from domain.value_objects.api_token import APIToken
        
        # Criar objetos
        document = NFEDocument(xml_file)
        api_token = APIToken.from_string(token)
        
        if not api_token:
            class MockResult:
                success = False
                message = "Token inválido"
                status_code = None
                response_time_ms = 0
            return MockResult()
        
        # Criar serviço e testar
        api_service = ValidaNFeAPIService()
        result = api_service.validate_nfe(document, api_token)
        
        return result
        
    except ImportError as e:
        print(f"   Erro de import: {e}")
        class MockResult:
            success = False
            message = f"Erro de import: {e}"
            status_code = None
            response_time_ms = 0
        return MockResult()

if __name__ == "__main__":
    test_both_api_implementations()