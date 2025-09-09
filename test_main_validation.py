#!/usr/bin/env python3
"""
Testar validação exatamente como feito no main.py
"""
from pathlib import Path
from lxml import etree

def test_main_validation():
    """Reproduzir exatamente a lógica de validação do main.py"""
    
    xml_file = Path("xml-problematico.xml")
    
    if not xml_file.exists():
        print("❌ Arquivo xml-problematico.xml não encontrado")
        return
    
    print("=== TESTE DA LÓGICA DE VALIDAÇÃO DO MAIN.PY ===")
    
    # Simular validate_structure
    structure_status = simulate_validate_structure(str(xml_file))
    print(f"Structure Status: '{structure_status}'")
    
    # Simular validate_signature
    signature_status = simulate_validate_signature(str(xml_file))
    print(f"Signature Status: '{signature_status}'")
    
    # Simular _is_file_valid
    structure_ok = "✅" in structure_status
    signature_ok = "✅" in signature_status
    is_valid = structure_ok and signature_ok
    
    print(f"\n=== RESULTADO FINAL ===")
    print(f"🔍 Validando arquivo:")
    print(f"   Estrutura: '{structure_status}' -> {structure_ok}")
    print(f"   Assinatura: '{signature_status}' -> {signature_ok}")
    print(f"   Resultado final: {is_valid}")
    print("-" * 50)
    
    if is_valid:
        print("✅ ARQUIVO CONSIDERADO VÁLIDO")
    else:
        print("❌ ARQUIVO CONSIDERADO INVÁLIDO")
        print("⚠️  Arquivo não será enviado para API")

def simulate_validate_structure(xml_path):
    """Simular a função validate_structure do main.py"""
    try:
        print(f"🔍 Validando estrutura XML: {xml_path}")
        
        # Note: O main.py usa schemas carregados, mas não temos acesso aqui
        # Vamos simular o que aconteceria se os schemas não estivessem carregados
        
        # Simular detecção de tipo
        xml_type = detect_xml_type(xml_path)
        print(f"   Tipo detectado: {xml_type}")
        
        if xml_type == 'unknown':
            print("❌ Tipo XML não reconhecido - não é possível validar")
            return f"Schema não encontrado para tipo: {xml_type}"
        
        # Para o teste, vamos assumir que os schemas não estão carregados
        # (isso pode ser a causa do problema)
        schemas = {}  # Simular schemas vazios
        
        if not schemas:
            print("❌ Nenhum schema carregado!")
            return "Schemas não encontrados"
        
        # Se chegasse até aqui (com schemas carregados), faria validação XSD
        # Mas como os schemas estão vazios, retorna erro
        
    except Exception as e:
        return f"Erro na validação: {str(e)[:50]}..."

def simulate_validate_signature(xml_path):
    """Simular a função validate_signature do main.py"""
    try:
        # Check if file exists and is readable
        if not Path(xml_path).exists():
            return "Arquivo não encontrado ✗"
        
        # Try parsing with better error handling  
        try:
            xml_doc = etree.parse(xml_path)
        except etree.XMLSyntaxError as e:
            return f"XML mal formado ✗: {str(e)[:30]}..."
        except Exception as e:
            return f"Erro ao ler arquivo ✗: {str(e)[:30]}..."
        
        # Check if signature element exists
        signature_elements = xml_doc.xpath("//ds:Signature", 
                                         namespaces={'ds': 'http://www.w3.org/2000/09/xmldsig#'})
        
        if not signature_elements:
            return "Nenhuma assinatura encontrada ✗"
        else:
            return "Assinatura presente ✅"
                
    except Exception as e:
        return f"Erro na verificação ✗: {str(e)[:40]}..."

def detect_xml_type(xml_path):
    """Simular detecção de tipo XML"""
    try:
        content = Path(xml_path).read_text(encoding='utf-8')
        
        if '<nfeProc' in content:
            return 'procNFe'
        elif '<NFe' in content:
            return 'nfe'
        else:
            return 'unknown'
    except:
        return 'unknown'

def test_real_schema_loading():
    """Testar carregamento real de schemas"""
    print(f"\n=== TESTE DE CARREGAMENTO DE SCHEMAS ===")
    
    schema_paths = [
        Path("monitor_nfe/schemas/leiauteNFe_v4.00.xsd"),
        Path("monitor_nfe/schemas/procNFe_v4.00.xsd")
    ]
    
    schemas = {}
    
    for schema_path in schema_paths:
        if schema_path.exists():
            try:
                with open(schema_path, 'r', encoding='utf-8') as f:
                    schema_doc = etree.parse(f)
                schema = etree.XMLSchema(schema_doc)
                
                schema_type = 'procNFe' if 'procNFe' in schema_path.name else 'nfe'
                schemas[schema_type] = schema
                
                print(f"✅ Schema {schema_type} carregado: {schema_path.name}")
            except Exception as e:
                print(f"❌ Erro ao carregar {schema_path.name}: {e}")
        else:
            print(f"❌ Schema não encontrado: {schema_path}")
    
    print(f"Schemas carregados: {list(schemas.keys())}")
    
    # Se temos schemas, testar validação real
    if schemas:
        xml_file = Path("xml-problematico.xml")
        xml_type = detect_xml_type(str(xml_file))
        
        if xml_type in schemas:
            print(f"\n🔍 Testando validação real com schema {xml_type}...")
            
            try:
                # Parse XML
                with open(xml_file, 'rb') as f:
                    xml_bytes = f.read()
                xml_doc = etree.fromstring(xml_bytes)
                
                # Validate
                schema = schemas[xml_type]
                if schema.validate(xml_doc):
                    print(f"✅ Validação XSD bem-sucedida!")
                    return f"XML ✅ ({xml_type})"
                else:
                    errors = [str(error) for error in schema.error_log]
                    print(f"❌ Validação XSD falhou - {len(errors)} erro(s)")
                    for i, error in enumerate(errors[:3]):
                        print(f"   Erro {i+1}: {error}")
                    return f"XML ✗ ({xml_type}): {'; '.join(errors[:1])}"
                    
            except Exception as e:
                print(f"❌ Erro no parsing/validação: {e}")
                return f"Erro de parsing XML ✗: {str(e)[:100]}..."
    
    return "Schemas não carregados"

if __name__ == "__main__":
    test_main_validation()
    
    # Testar com schemas reais
    structure_status_real = test_real_schema_loading()
    if structure_status_real != "Schemas não carregados":
        print(f"\n=== RESULTADO COM SCHEMAS REAIS ===")
        print(f"Structure Status Real: '{structure_status_real}'")
        
        signature_status = simulate_validate_signature("xml-problematico.xml")
        
        structure_ok = "✅" in structure_status_real
        signature_ok = "✅" in signature_status
        is_valid_real = structure_ok and signature_ok
        
        print(f"Validação final com schemas reais: {is_valid_real}")
        if is_valid_real:
            print("✅ COM SCHEMAS REAIS: ARQUIVO SERIA CONSIDERADO VÁLIDO")
        else:
            print("❌ COM SCHEMAS REAIS: ARQUIVO AINDA SERIA INVÁLIDO")