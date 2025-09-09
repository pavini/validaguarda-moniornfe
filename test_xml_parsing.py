#!/usr/bin/env python3
"""
Testar parsing de XML para identificar problemas específicos
"""
from pathlib import Path
from lxml import etree

def test_xml_parsing():
    """Testar parsing do XML problemático"""
    
    xml_file = Path("xml-problematico.xml")
    
    if not xml_file.exists():
        print("❌ Arquivo xml-problematico.xml não encontrado")
        return
    
    print("=== TESTE DE PARSING XML ===")
    
    # Método 1: Leitura direta
    try:
        xml_content = xml_file.read_text(encoding='utf-8')
        print(f"✅ Leitura UTF-8: OK ({len(xml_content)} chars)")
    except Exception as e:
        print(f"❌ Erro na leitura UTF-8: {e}")
        return
    
    # Método 2: Parse com lxml (como usado no código)
    print(f"\n=== TESTE DE PARSING COM LXML ===")
    
    # Reproduzir exatamente o método do XMLSchemaService
    encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
    
    for encoding in encodings:
        print(f"\nTestando encoding: {encoding}")
        try:
            # Método do código original
            with open(xml_file, 'r', encoding=encoding) as f:
                xml_content_file = f.read()
            
            print(f"  ✅ Arquivo lido com {encoding}")
            print(f"  Tamanho: {len(xml_content_file)} chars")
            
            # Re-encode em UTF-8 (como no código original)
            xml_bytes = xml_content_file.encode('utf-8')
            print(f"  ✅ Re-encoding para UTF-8: {len(xml_bytes)} bytes")
            
            # Parse XML
            xml_doc = etree.fromstring(xml_bytes)
            print(f"  ✅ Parse XML: Sucesso")
            print(f"  Tag raiz: {xml_doc.tag}")
            
            # Se chegou até aqui, o parsing funcionou
            break
            
        except UnicodeDecodeError:
            print(f"  ❌ UnicodeDecodeError com {encoding}")
            continue
        except etree.XMLSyntaxError as e:
            print(f"  ❌ XMLSyntaxError: {e}")
            print(f"      Linha: {e.lineno if hasattr(e, 'lineno') else 'N/A'}")
            return
        except Exception as e:
            print(f"  ❌ Erro inesperado: {e}")
            return
    
    # Métodos alternativos de parsing
    print(f"\n=== MÉTODOS ALTERNATIVOS ===")
    
    # Método 1: Parse direto sem re-encoding
    try:
        xml_doc_direct = etree.fromstring(xml_content)
        print("✅ Parse direto (sem re-encoding): Sucesso")
    except Exception as e:
        print(f"❌ Parse direto falhou: {e}")
    
    # Método 2: Parse como bytes
    try:
        xml_bytes_direct = xml_content.encode('utf-8')
        xml_doc_bytes = etree.fromstring(xml_bytes_direct)
        print("✅ Parse como bytes UTF-8: Sucesso")
    except Exception as e:
        print(f"❌ Parse como bytes falhou: {e}")
    
    # Método 3: Parse com parser específico
    try:
        parser = etree.XMLParser(encoding='utf-8', strip_cdata=False)
        xml_doc_parser = etree.fromstring(xml_content.encode('utf-8'), parser)
        print("✅ Parse com XMLParser: Sucesso")
    except Exception as e:
        print(f"❌ Parse com XMLParser falhou: {e}")
    
    # Teste específico para XML em linha única
    print(f"\n=== TESTE XML EM LINHA ÚNICA ===")
    
    lines = xml_content.split('\n')
    if len(lines) == 1:
        print("⚠️  XML está em linha única - testando formatação...")
        
        # Tentar formatar o XML
        try:
            xml_doc_formatted = etree.fromstring(xml_content)
            formatted_xml = etree.tostring(xml_doc_formatted, 
                                         pretty_print=True, 
                                         encoding='unicode')
            
            print(f"✅ Formatação bem-sucedida")
            print(f"Linhas após formatação: {len(formatted_xml.split(chr(10)))}")
            
            # Testar se a versão formatada funciona melhor
            xml_doc_test = etree.fromstring(formatted_xml)
            print(f"✅ Parse da versão formatada: Sucesso")
            
        except Exception as e:
            print(f"❌ Erro na formatação: {e}")
    else:
        print(f"✅ XML já formatado em {len(lines)} linhas")
    
    # Verificar namespaces (pode causar problemas)
    print(f"\n=== ANÁLISE DE NAMESPACES ===")
    
    if 'xmlns=' in xml_content:
        namespaces = []
        import re
        matches = re.findall(r'xmlns(?::(\w+))?="([^"]+)"', xml_content)
        for prefix, uri in matches:
            ns_name = prefix if prefix else "default"
            namespaces.append(f"{ns_name}: {uri}")
            print(f"  {ns_name}: {uri}")
        
        if namespaces:
            print("⚠️  XML usa namespaces - pode necessitar configuração específica")
    else:
        print("✅ XML sem namespaces")
    
    print(f"\n=== POSSÍVEIS SOLUÇÕES ===")
    print("1. Se o problema é XML em linha única:")
    print("   - Formatar o XML antes do parsing")
    print("   - Usar parser mais tolerante")
    print()
    print("2. Se o problema são namespaces:")
    print("   - Configurar namespaces no schema")
    print("   - Usar validação namespace-aware")
    print()
    print("3. Se o problema é encoding:")
    print("   - Evitar re-encoding desnecessário")
    print("   - Usar leitura binária + decode específico")

if __name__ == "__main__":
    test_xml_parsing()