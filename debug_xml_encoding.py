#!/usr/bin/env python3
"""
Script para debugar problemas de encoding no XML
"""
from pathlib import Path
import requests
import time

def test_encodings():
    """Testar diferentes encodings no arquivo XML"""
    xml_file = Path("xml-teste.xml")
    
    if not xml_file.exists():
        print(f"ERRO: Arquivo {xml_file} não encontrado")
        return
    
    print(f"=== TESTE DE ENCODINGS ===")
    print(f"Arquivo: {xml_file}")
    print(f"Tamanho: {xml_file.stat().st_size} bytes")
    
    encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
    
    for encoding in encodings:
        try:
            content = xml_file.read_text(encoding=encoding)
            print(f"\n✅ {encoding}: OK ({len(content)} caracteres)")
            print(f"   Primeiros 100 chars: {content[:100].encode('unicode_escape').decode()}")
            
            # Testar se o XML é válido segundo os critérios do código
            if not content or len(content.strip()) < 10:
                print(f"   ❌ XML muito pequeno")
                continue
                
            xml_stripped = content.strip()
            if not xml_stripped.startswith('<?xml'):
                print(f"   ❌ Não começa com <?xml")
                continue
                
            if '<NFe' not in content and '<nfeProc' not in content:
                print(f"   ❌ Não contém <NFe ou <nfeProc")
                continue
                
            print(f"   ✅ XML passou nas validações básicas")
            
            # Testar se há caracteres especiais problemáticos
            try:
                content.encode('utf-8')
                print(f"   ✅ Encoding para UTF-8: OK")
            except Exception as e:
                print(f"   ❌ Encoding para UTF-8: {e}")
            
        except UnicodeDecodeError as e:
            print(f"\n❌ {encoding}: UnicodeDecodeError - {e}")
        except Exception as e:
            print(f"\n❌ {encoding}: Erro - {e}")
    
    # Testar leitura binária
    print(f"\n=== ANÁLISE BINÁRIA ===")
    try:
        binary_content = xml_file.read_bytes()
        print(f"Tamanho binário: {len(binary_content)} bytes")
        print(f"Primeiros 50 bytes: {binary_content[:50]}")
        
        # Verificar BOM
        if binary_content.startswith(b'\xef\xbb\xbf'):
            print("⚠️  Arquivo tem BOM UTF-8")
        elif binary_content.startswith(b'\xff\xfe'):
            print("⚠️  Arquivo tem BOM UTF-16 LE")
        elif binary_content.startswith(b'\xfe\xff'):
            print("⚠️  Arquivo tem BOM UTF-16 BE")
        else:
            print("✅ Arquivo sem BOM")
            
        # Verificar caracteres não-ASCII
        non_ascii_count = sum(1 for b in binary_content if b > 127)
        print(f"Caracteres não-ASCII: {non_ascii_count} ({non_ascii_count/len(binary_content)*100:.2f}%)")
        
        if non_ascii_count > 0:
            print("⚠️  Arquivo contém caracteres não-ASCII que podem causar problemas")
            
    except Exception as e:
        print(f"❌ Erro na análise binária: {e}")

def compare_with_manual_test():
    """Comparar com um teste manual usando requests"""
    print(f"\n=== COMPARAÇÃO COM TESTE MANUAL ===")
    
    xml_file = Path("xml-teste.xml")
    if not xml_file.exists():
        print("❌ Arquivo não encontrado")
        return
    
    # Simular como o código original lê o arquivo
    encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
    xml_content = None
    
    for encoding in encodings:
        try:
            xml_content = xml_file.read_text(encoding=encoding)
            print(f"✅ Leu com encoding: {encoding}")
            break
        except UnicodeDecodeError:
            continue
        except Exception:
            break
    
    if not xml_content:
        print("❌ Não conseguiu ler o arquivo com nenhum encoding")
        return
    
    print(f"Conteúdo lido: {len(xml_content)} caracteres")
    
    # Token de teste (substitua por um real se quiser testar)
    # Para fins de debug, vamos apenas preparar a requisição
    token_test = "TOKEN_DE_TESTE"
    
    url = "https://api.validanfe.com/GuardaNFe/EnviarXml"
    headers = {'X-API-KEY': token_test}
    files = {'xmlFile': ('xml-teste.xml', xml_content, 'application/xml')}
    
    print(f"\n=== PREPARAÇÃO DA REQUISIÇÃO ===")
    print(f"URL: {url}")
    print(f"Headers: {headers}")
    print(f"Arquivo preparado: {files['xmlFile'][0]} ({len(files['xmlFile'][1])} chars)")
    print(f"Content-Type: {files['xmlFile'][2]}")
    
    # Verificar se o conteúdo seria enviado corretamente
    print(f"\n=== VERIFICAÇÃO DO CONTEÚDO ===")
    if xml_content.strip().startswith('<?xml'):
        print("✅ Começa com declaração XML")
    else:
        print("❌ Não começa com declaração XML")
        
    if '<nfeProc' in xml_content:
        print("✅ Contém tag nfeProc")
    elif '<NFe' in xml_content:
        print("✅ Contém tag NFe")
    else:
        print("❌ Não contém tags NFe esperadas")
    
    # Verificar tamanho
    content_bytes = xml_content.encode('utf-8')
    size_mb = len(content_bytes) / (1024 * 1024)
    print(f"Tamanho em UTF-8: {len(content_bytes)} bytes ({size_mb:.2f} MB)")
    
    if size_mb > 5:
        print("❌ Arquivo maior que 5MB (limite da API)")
    else:
        print("✅ Arquivo dentro do limite de tamanho")

if __name__ == "__main__":
    test_encodings()
    compare_with_manual_test()