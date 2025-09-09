#!/usr/bin/env python3
"""
Script para debugar especificamente o erro da API ValidaNFe
"""
import sys
from pathlib import Path
import requests
import time

# Adicionar caminho
sys.path.append('./monitor_nfe')

def debug_api_error():
    """Debug detalhado do erro da API"""
    
    print("=" * 70)
    print("🔍 DEBUG DETALHADO DO ERRO DA API VALIDANFE")
    print("=" * 70)
    
    xml_file = Path("xml-problematico.xml")
    
    if not xml_file.exists():
        print("❌ Arquivo xml-problematico.xml não encontrado")
        return
    
    # Pedir token
    print("Para investigar o erro da API, preciso de um token válido.")
    print("Você pode:")
    print("1. Fornecer um token real para teste completo")
    print("2. Pressionar ENTER para usar um token de teste (mostrará erros esperados)")
    
    token = input("\nDigite o token da ValidaNFe API (ou ENTER para teste): ").strip()
    if not token:
        token = "TOKEN_DE_TESTE_PARA_DEBUG"
        print("⚠️  Usando token de teste - erros são esperados")
    else:
        print(f"✅ Usando token real: {token[:20]}...")
    
    print(f"\n" + "=" * 70)
    print("📋 INFORMAÇÕES DO ARQUIVO")
    print("=" * 70)
    
    # Informações básicas do arquivo
    file_size = xml_file.stat().st_size
    print(f"📁 Arquivo: {xml_file.name}")
    print(f"📏 Tamanho: {file_size:,} bytes ({file_size / 1024:.2f} KB)")
    
    # Ler conteúdo
    try:
        xml_content = xml_file.read_text(encoding='utf-8')
        print(f"✅ Leitura UTF-8: OK ({len(xml_content):,} caracteres)")
    except Exception as e:
        print(f"❌ Erro na leitura UTF-8: {e}")
        return
    
    # Verificar estrutura básica
    if '<nfeProc' in xml_content:
        print("✅ Tipo: nfeProc (NFe processada)")
    elif '<NFe' in xml_content:
        print("✅ Tipo: NFe simples")
    else:
        print("⚠️  Tipo: Não identificado")
    
    # Extrair chave NFe
    import re
    nfe_key = None
    match = re.search(r'<chNFe>([^<]+)</chNFe>', xml_content)
    if match:
        nfe_key = match.group(1)
        print(f"🔑 Chave NFe: {nfe_key}")
    else:
        match = re.search(r'Id="NFe(\d{44})"', xml_content)
        if match:
            nfe_key = match.group(1)
            print(f"🔑 Chave NFe (via Id): {nfe_key}")
    
    print(f"\n" + "=" * 70)
    print("🚀 TESTE DA API - REQUISIÇÃO DETALHADA")
    print("=" * 70)
    
    # Configuração da API
    base_url = "https://api.validanfe.com"
    endpoint = "/GuardaNFe/EnviarXml"
    url = f"{base_url}{endpoint}"
    
    print(f"🌐 URL: {url}")
    print(f"🔑 Token: {token[:20]}{'...' if len(token) > 20 else ''}")
    print(f"📦 Method: POST")
    print(f"📋 Content-Type: multipart/form-data")
    
    # Preparar headers
    headers = {
        'X-API-KEY': token,
        'User-Agent': 'Monitor-NFe/1.0 (Python)'
    }
    
    print(f"\n📤 HEADERS:")
    for key, value in headers.items():
        if key == 'X-API-KEY':
            print(f"   {key}: {value[:20]}...")
        else:
            print(f"   {key}: {value}")
    
    # Preparar arquivo
    files = {
        'xmlFile': (xml_file.name, xml_content, 'application/xml')
    }
    
    print(f"\n📎 MULTIPART FILES:")
    print(f"   Field: xmlFile")
    print(f"   Filename: {xml_file.name}")
    print(f"   Content-Type: application/xml")
    print(f"   Size: {len(xml_content):,} bytes")
    
    # Fazer a requisição
    print(f"\n" + "=" * 70)
    print("🔄 ENVIANDO REQUISIÇÃO...")
    print("=" * 70)
    
    start_time = time.time()
    
    try:
        print("⏳ Fazendo requisição POST...")
        response = requests.post(url, files=files, headers=headers, timeout=30)
        
        end_time = time.time()
        response_time = (end_time - start_time) * 1000
        
        print(f"✅ Requisição concluída em {response_time:.2f}ms")
        
    except requests.exceptions.Timeout:
        print("❌ TIMEOUT: A API não respondeu em 30 segundos")
        print("   Possíveis causas:")
        print("   - API sobrecarregada")
        print("   - Problemas de rede")
        print("   - Arquivo muito grande")
        return
        
    except requests.exceptions.ConnectionError as e:
        print(f"❌ ERRO DE CONEXÃO: {e}")
        print("   Possíveis causas:")
        print("   - URL incorreta")
        print("   - API fora do ar")
        print("   - Problemas de DNS/rede")
        return
        
    except requests.exceptions.RequestException as e:
        print(f"❌ ERRO NA REQUISIÇÃO: {e}")
        return
        
    except Exception as e:
        print(f"❌ ERRO INESPERADO: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Analisar resposta
    print(f"\n" + "=" * 70)
    print("📥 RESPOSTA DA API")
    print("=" * 70)
    
    print(f"🔢 Status Code: {response.status_code}")
    print(f"⏱️  Tempo de resposta: {response_time:.2f}ms")
    
    # Headers de resposta
    print(f"\n📥 RESPONSE HEADERS:")
    for key, value in response.headers.items():
        print(f"   {key}: {value}")
    
    # Corpo da resposta
    print(f"\n📄 RESPONSE BODY:")
    if response.text:
        print(f"   Tamanho: {len(response.text)} caracteres")
        print(f"   Conteúdo (primeiros 1000 chars):")
        print("   " + "-" * 50)
        print(response.text[:1000])
        print("   " + "-" * 50)
        
        if len(response.text) > 1000:
            print(f"   ... (+{len(response.text) - 1000} caracteres)")
    else:
        print("   (vazio)")
    
    # Tentar parsear JSON
    print(f"\n🔍 ANÁLISE DA RESPOSTA:")
    
    if response.headers.get('content-type', '').startswith('application/json'):
        try:
            json_data = response.json()
            print("✅ Resposta é JSON válido")
            import json
            print("📋 JSON formatado:")
            print(json.dumps(json_data, indent=2, ensure_ascii=False))
        except Exception as e:
            print(f"❌ Erro ao parsear JSON: {e}")
    else:
        print("⚠️  Resposta não é JSON")
    
    # Interpretar status codes comuns
    print(f"\n" + "=" * 70)
    print("🧠 INTERPRETAÇÃO DO STATUS CODE")
    print("=" * 70)
    
    if response.status_code == 200:
        print("✅ 200 OK: Requisição bem-sucedida")
        print("   A NFe foi processada com sucesso pela API")
        
    elif response.status_code == 400:
        print("❌ 400 Bad Request: Dados inválidos")
        print("   Possíveis causas:")
        print("   - XML malformado")
        print("   - Campos obrigatórios ausentes")
        print("   - Formato de dados incorreto")
        print("   - Validações de negócio da NFe falharam")
        
    elif response.status_code == 401:
        print("❌ 401 Unauthorized: Problema de autenticação")
        print("   Possíveis causas:")
        print("   - Token inválido")
        print("   - Token expirado")
        print("   - Header X-API-KEY ausente ou incorreto")
        
    elif response.status_code == 403:
        print("❌ 403 Forbidden: Sem permissão")
        print("   Possíveis causas:")
        print("   - Token válido mas sem permissões para esta operação")
        print("   - Conta sem créditos")
        print("   - Tipo de NFe não permitido para sua conta")
        
    elif response.status_code == 404:
        print("❌ 404 Not Found: Endpoint não encontrado")
        print("   Possíveis causas:")
        print("   - URL incorreta")
        print("   - Endpoint descontinuado")
        
    elif response.status_code == 409:
        print("⚠️  409 Conflict: NFe já processada")
        print("   Esta NFe já foi enviada anteriormente")
        print("   Isso é normal e pode ser considerado sucesso")
        
    elif response.status_code == 422:
        print("❌ 422 Unprocessable Entity: Dados inválidos")
        print("   XML tem estrutura correta mas conteúdo inválido")
        
    elif response.status_code == 429:
        print("⚠️  429 Too Many Requests: Rate limit")
        print("   Muitas requisições em pouco tempo")
        print("   Aguarde alguns minutos e tente novamente")
        
    elif response.status_code >= 500:
        print(f"❌ {response.status_code} Server Error: Erro do servidor")
        print("   Problema interno da API ValidaNFe")
        print("   Tente novamente mais tarde")
        
    else:
        print(f"❓ Status {response.status_code}: Não documentado")
    
    # Conclusões
    print(f"\n" + "=" * 70)
    print("🎯 CONCLUSÕES E PRÓXIMOS PASSOS")
    print("=" * 70)
    
    if response.status_code == 200:
        print("✅ SUCESSO: A API funcionou corretamente")
        print("   O problema não é na comunicação com a API")
        
    elif response.status_code == 409:
        print("✅ NFe JÁ PROCESSADA: Isso é esperado")
        print("   A NFe foi enviada com sucesso anteriormente")
        print("   O aplicativo deveria tratar isso como sucesso")
        
    elif response.status_code == 401:
        print("🔑 PROBLEMA DE TOKEN:")
        if token == "TOKEN_DE_TESTE_PARA_DEBUG":
            print("   Use um token real da ValidaNFe para teste completo")
        else:
            print("   Verifique se o token está correto e ainda válido")
            
    elif response.status_code == 400:
        print("📋 PROBLEMA NOS DADOS:")
        print("   Examine a resposta acima para detalhes específicos do erro")
        print("   Pode ser um problema específico com este XML")
        
    else:
        print("🔧 PROBLEMA NA API OU CONFIGURAÇÃO:")
        print("   Verifique os detalhes da resposta acima")
        print("   Pode ser necessário contatar o suporte da ValidaNFe")
    
    print(f"\n📞 Se precisar de suporte:")
    print("   - Documente o status code e resposta acima")
    print("   - Verifique a documentação da ValidaNFe API")
    print("   - Entre em contato com o suporte técnico da ValidaNFe")

if __name__ == "__main__":
    debug_api_error()