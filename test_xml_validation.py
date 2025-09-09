#!/usr/bin/env python3
import sys
import os
from pathlib import Path
import requests
import time

# Configuração básica
project_root = Path(__file__).parent

def test_xml_validation():
    """Teste de validação do arquivo xml-teste.xml"""
    
    # Configurar caminhos
    xml_file = project_root / "xml-teste.xml"
    
    if not xml_file.exists():
        print(f"ERRO: Arquivo não encontrado: {xml_file}")
        return
    
    print(f"Testando arquivo: {xml_file}")
    print(f"Tamanho do arquivo: {xml_file.stat().st_size} bytes")
    
    # Pedir token
    token = input("Digite o token da API ValidaNFe: ").strip()
    if not token:
        print("ERRO: Token não fornecido")
        return
    
    print(f"Token: {token[:20]}...")
    
    try:
        # Ler XML
        xml_content = xml_file.read_text(encoding='utf-8')
        print(f"XML lido com sucesso ({len(xml_content)} caracteres)")
        
        # Configurar API
        base_url = "https://api.validanfe.com"
        endpoint = "/GuardaNFe/EnviarXml"
        url = f"{base_url}{endpoint}"
        
        print(f"Enviando para: {url}")
        
        # Preparar requisição
        headers = {'X-API-KEY': token}
        files = {
            'xmlFile': ('xml-teste.xml', xml_content, 'application/xml')
        }
        
        # Enviar
        start_time = time.time()
        response = requests.post(url, files=files, headers=headers, timeout=30)
        end_time = time.time()
        
        response_time_ms = (end_time - start_time) * 1000
        
        print(f"\n=== RESULTADO ===")
        print(f"Status Code: {response.status_code}")
        print(f"Tempo de resposta: {response_time_ms:.2f}ms")
        print(f"Headers de resposta: {dict(response.headers)}")
        
        if response.text:
            print(f"Corpo da resposta (primeiros 500 chars):")
            print(response.text[:500])
            
            if response.headers.get('content-type', '').startswith('application/json'):
                try:
                    json_data = response.json()
                    print(f"\nJSON da resposta:")
                    import json
                    print(json.dumps(json_data, indent=2, ensure_ascii=False))
                except:
                    pass
        
        if response.status_code == 200:
            print("\n✅ SUCESSO: NFe enviada com sucesso!")
        else:
            print(f"\n❌ ERRO: HTTP {response.status_code}")
        
    except requests.exceptions.Timeout:
        print("❌ ERRO: Timeout na conexão")
    except requests.exceptions.ConnectionError:
        print("❌ ERRO: Erro de conexão")
    except Exception as e:
        print(f"❌ ERRO INESPERADO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_xml_validation()