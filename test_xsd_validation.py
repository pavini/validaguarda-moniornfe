#!/usr/bin/env python3
"""
Teste específico de validação XSD
"""
import sys
from pathlib import Path

# Adicionar caminho
sys.path.append('./monitor_nfe')

def test_xsd_validation():
    """Testar validação XSD do arquivo problemático"""
    
    try:
        from infrastructure.external_services.xml_schema_service import XMLSchemaService
        from domain.entities.nfe_document import NFEDocument
        
        xml_file = Path("xml-problematico.xml")
        
        if not xml_file.exists():
            print("❌ Arquivo xml-problematico.xml não encontrado")
            return
        
        print("=== TESTE DE VALIDAÇÃO XSD ===")
        
        # Criar serviço XSD
        schema_service = XMLSchemaService()
        
        # Tentar carregar schemas
        print("🔧 Carregando schemas...")
        schemas_loaded = schema_service.load_schemas()
        
        if not schemas_loaded:
            print("❌ Falha ao carregar schemas - verifique se existem arquivos XSD")
            print("   Esperado em: schemas/leiauteNFe_v4.00.xsd e schemas/procNFe_v4.00.xsd")
            
            # Verificar se pasta existe
            schemas_folder = Path("monitor_nfe/schemas")
            if schemas_folder.exists():
                xsd_files = list(schemas_folder.glob("*.xsd"))
                print(f"   Arquivos XSD encontrados: {[f.name for f in xsd_files]}")
            else:
                schemas_folder2 = Path("schemas")
                if schemas_folder2.exists():
                    xsd_files = list(schemas_folder2.glob("*.xsd"))
                    print(f"   Arquivos XSD em ./schemas/: {[f.name for f in xsd_files]}")
                else:
                    print("   ❌ Pasta de schemas não encontrada")
            
            return
        
        print("✅ Schemas carregados com sucesso")
        
        # Criar documento
        document = NFEDocument(xml_file)
        
        # Validar
        print(f"\n🔍 Validando {xml_file.name}...")
        result = schema_service.validate_against_schema(document)
        
        print(f"\n=== RESULTADO DA VALIDAÇÃO XSD ===")
        print(f"Status: {result.status}")
        print(f"Schema válido: {result.schema_valid}")
        print(f"Número de erros: {result.error_count}")
        
        if result.has_errors:
            print(f"\n❌ ERROS ENCONTRADOS:")
            for i, error in enumerate(result.errors, 1):
                print(f"{i:2d}. Tipo: {error.type}")
                print(f"    Descrição: {error.description}")
                if error.details:
                    print(f"    Detalhes: {error.details}")
                if error.line:
                    print(f"    Linha: {error.line}")
                print()
        else:
            print("✅ Nenhum erro de validação XSD encontrado")
    
    except ImportError as e:
        print(f"❌ Erro de import: {e}")
        print("Verifique se os módulos estão disponíveis")
        
        # Teste manual sem dependências
        print("\n=== TESTE MANUAL SEM DEPENDÊNCIAS ===")
        test_manual_lxml()
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

def test_manual_lxml():
    """Teste manual usando lxml diretamente"""
    try:
        from lxml import etree
        
        xml_file = Path("xml-problematico.xml")
        
        print(f"Testando parsing manual com lxml...")
        
        # Método 1: Leitura binária
        try:
            with open(xml_file, 'rb') as f:
                xml_bytes = f.read()
            
            doc = etree.fromstring(xml_bytes)
            print(f"✅ Parse binário: sucesso")
            print(f"   Tag raiz: {doc.tag}")
            print(f"   Elementos filhos: {len(doc)}")
            
        except Exception as e:
            print(f"❌ Parse binário falhou: {e}")
        
        # Método 2: Leitura de texto
        try:
            xml_content = xml_file.read_text(encoding='utf-8')
            xml_bytes = xml_content.encode('utf-8')
            
            doc = etree.fromstring(xml_bytes)
            print(f"✅ Parse de texto: sucesso")
            
        except Exception as e:
            print(f"❌ Parse de texto falhou: {e}")
        
    except ImportError:
        print("❌ lxml não disponível")

def check_schema_files():
    """Verificar se arquivos de schema existem"""
    print("\n=== VERIFICAÇÃO DE ARQUIVOS XSD ===")
    
    possible_paths = [
        Path("monitor_nfe/schemas"),
        Path("schemas"),
        Path("../schemas"),
        Path("monitor_nfe/../schemas")
    ]
    
    for schema_path in possible_paths:
        if schema_path.exists():
            print(f"✅ Pasta encontrada: {schema_path}")
            xsd_files = list(schema_path.glob("*.xsd"))
            
            if xsd_files:
                print(f"   Arquivos XSD: {[f.name for f in xsd_files]}")
                
                # Verificar arquivos específicos
                expected = ["leiauteNFe_v4.00.xsd", "procNFe_v4.00.xsd"]
                for expected_file in expected:
                    if (schema_path / expected_file).exists():
                        print(f"   ✅ {expected_file}")
                    else:
                        print(f"   ❌ {expected_file} não encontrado")
            else:
                print(f"   ⚠️  Nenhum arquivo XSD encontrado")
        else:
            print(f"❌ Pasta não existe: {schema_path}")

if __name__ == "__main__":
    check_schema_files()
    test_xsd_validation()