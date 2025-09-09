#!/usr/bin/env python3
"""
Teste do ValidaNFeAPIService melhorado com logs detalhados
"""
import sys
from pathlib import Path

# Adicionar caminho para import
sys.path.append('./monitor_nfe')

def test_improved_service():
    """Testar o serviço melhorado"""
    try:
        # Imports
        from infrastructure.external_services.validanfe_api_service import ValidaNFeAPIService
        from domain.entities.nfe_document import NFEDocument
        from domain.value_objects.api_token import APIToken
        
        # Configurar
        xml_file = Path("xml-teste.xml")
        
        if not xml_file.exists():
            print("❌ Arquivo xml-teste.xml não encontrado")
            return
        
        # Pedir token
        if len(sys.argv) > 1:
            token_str = sys.argv[1]
        else:
            token_str = input("Digite o token da API ValidaNFe (ou ENTER para usar token de teste): ").strip()
            if not token_str:
                token_str = "TOKEN_DE_TESTE_PARA_DEBUG"
        
        print(f"=== TESTE DO VALIDANFE API SERVICE MELHORADO ===")
        print(f"Token: {token_str[:20]}...")
        
        # Criar objetos
        document = NFEDocument(xml_file)
        token = APIToken.from_string(token_str)
        
        if not token:
            print("❌ Token inválido")
            return
        
        # Criar serviço
        api_service = ValidaNFeAPIService()
        
        print(f"\n🚀 Enviando NFe...")
        
        # Enviar
        result = api_service.validate_nfe(document, token)
        
        print(f"\n=== RESULTADO ===")
        print(f"Sucesso: {result.success}")
        print(f"Mensagem: {result.message}")
        print(f"Status Code: {result.status_code}")
        print(f"Tempo de resposta: {result.response_time_ms:.2f}ms")
        
        if result.data:
            print(f"Dados: {result.data}")
        
        # Verificar se foi erro específico
        if not result.success:
            if result.status_code == 401:
                print("\n🔑 PROBLEMA: Token inválido ou expirado")
                print("   Solução: Verifique se o token está correto e válido")
            elif result.status_code == 409:
                print("\n📄 PROBLEMA: NFe já foi enviada")
                print("   Isso na verdade é normal se a NFe já foi processada antes")
            elif result.status_code == 400:
                print("\n📋 PROBLEMA: Dados inválidos")
                print("   Verifique se o XML está no formato correto")
            else:
                print(f"\n❓ PROBLEMA: HTTP {result.status_code}")
                print("   Verifique logs acima para mais detalhes")
        else:
            print("\n✅ SUCESSO!")
            
    except ImportError as e:
        print(f"❌ Erro de import: {e}")
        print("Certifique-se que os módulos estão disponíveis")
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_improved_service()