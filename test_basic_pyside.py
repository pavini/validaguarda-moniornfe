#!/usr/bin/env python3
"""
Teste básico para verificar se PySide6 funciona e se conseguimos acessar as configurações
"""
import os
import sys

try:
    from PySide6.QtCore import QSettings, QCoreApplication
    
    # Criar aplicação mínima
    app = QCoreApplication([])
    
    # Tentar acessar configurações
    settings = QSettings("ValidateCh", "MonitorNFe")
    
    print("=== CONFIGURAÇÕES ENCONTRADAS ===")
    print(f"Pasta de monitoramento: {settings.value('monitor_folder', 'NÃO CONFIGURADO')}")
    print(f"Pasta de saída: {settings.value('output_folder', 'NÃO CONFIGURADO')}")
    print(f"Token: {settings.value('token', 'NÃO CONFIGURADO')}")
    print(f"Auto organizar: {settings.value('auto_organize', 'NÃO CONFIGURADO')}")
    
    # Verificar se tem token configurado
    token = settings.value('token', None)
    if token:
        print(f"\n✅ Token encontrado (primeiros 20 chars): {token[:20]}...")
        
        # Se tem token, podemos testar a API
        import sys
        sys.path.append('./monitor_nfe')
        
        try:
            # Tentar importar e testar
            from pathlib import Path
            import requests
            import time
            
            xml_file = Path("xml-teste.xml")
            if xml_file.exists():
                print(f"\n=== TESTANDO API COM XML ===")
                print(f"Arquivo: {xml_file}")
                print(f"Tamanho: {xml_file.stat().st_size} bytes")
                
                # Ler XML
                xml_content = xml_file.read_text(encoding='utf-8')
                
                # Configurar API
                url = "https://api.validanfe.com/GuardaNFe/EnviarXml"
                headers = {'X-API-KEY': token}
                files = {'xmlFile': ('xml-teste.xml', xml_content, 'application/xml')}
                
                print(f"Enviando para: {url}")
                
                start_time = time.time()
                try:
                    response = requests.post(url, files=files, headers=headers, timeout=30)
                    end_time = time.time()
                    
                    print(f"\n=== RESULTADO ===")
                    print(f"Status: {response.status_code}")
                    print(f"Tempo: {(end_time - start_time) * 1000:.2f}ms")
                    print(f"Headers: {dict(response.headers)}")
                    
                    if response.text:
                        print(f"Resposta (primeiros 300 chars):")
                        print(response.text[:300])
                        
                        if response.headers.get('content-type', '').startswith('application/json'):
                            try:
                                import json
                                json_data = response.json()
                                print(f"\nJSON:")
                                print(json.dumps(json_data, indent=2, ensure_ascii=False))
                            except:
                                pass
                    
                    if response.status_code == 200:
                        print("\n✅ SUCESSO!")
                    else:
                        print(f"\n❌ ERRO HTTP {response.status_code}")
                        
                except Exception as e:
                    print(f"\n❌ ERRO na requisição: {e}")
            else:
                print(f"\n❌ Arquivo {xml_file} não encontrado")
                
        except ImportError as e:
            print(f"\n⚠️  Erro ao importar módulos: {e}")
            
    else:
        print("\n❌ Token não configurado")
        print("Configure o token primeiro usando o aplicativo principal.")
    
except ImportError as e:
    print(f"❌ Erro ao importar PySide6: {e}")
    print("Instale com: pip install PySide6")
except Exception as e:
    print(f"❌ Erro: {e}")