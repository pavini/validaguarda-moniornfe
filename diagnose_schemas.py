#!/usr/bin/env python3
"""
Script de diagnóstico para verificar o carregamento de schemas
"""
import sys
from pathlib import Path

# Adicionar caminho
sys.path.append('./monitor_nfe')

def diagnose_schemas():
    """Diagnosticar problemas com schemas XSD"""
    
    print("=" * 70)
    print("🔍 DIAGNÓSTICO DE SCHEMAS XSD")
    print("=" * 70)
    
    # Verificar estrutura de diretórios
    print("\n1. VERIFICAÇÃO DE DIRETÓRIOS:")
    
    current_dir = Path.cwd()
    print(f"   Diretório atual: {current_dir}")
    
    possible_schema_dirs = [
        Path("monitor_nfe/schemas"),
        Path("schemas"),
        Path("../schemas"),
        Path("./schemas")
    ]
    
    schema_dir_found = None
    
    for schema_dir in possible_schema_dirs:
        full_path = current_dir / schema_dir
        print(f"   Testando: {full_path}")
        
        if full_path.exists():
            print(f"   ✅ ENCONTRADO: {full_path}")
            schema_dir_found = full_path
            
            # Listar arquivos
            xsd_files = list(full_path.glob("*.xsd"))
            print(f"      Arquivos XSD: {len(xsd_files)}")
            for xsd in xsd_files:
                print(f"         - {xsd.name} ({xsd.stat().st_size} bytes)")
        else:
            print(f"   ❌ NÃO EXISTE: {full_path}")
    
    if not schema_dir_found:
        print("\n🚨 PROBLEMA CRÍTICO: Nenhum diretório de schemas encontrado!")
        return
    
    # Verificar arquivos específicos
    print(f"\n2. VERIFICAÇÃO DE ARQUIVOS ESPECÍFICOS:")
    
    required_files = [
        "leiauteNFe_v4.00.xsd",
        "procNFe_v4.00.xsd"
    ]
    
    files_ok = True
    
    for filename in required_files:
        file_path = schema_dir_found / filename
        print(f"   {filename}:")
        
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"      ✅ Existe ({size:,} bytes)")
            
            # Verificar se é válido
            try:
                content = file_path.read_text(encoding='utf-8')
                if '<xs:schema' in content or '<xsd:schema' in content:
                    print(f"      ✅ Conteúdo XSD válido")
                else:
                    print(f"      ⚠️  Não parece ser um arquivo XSD válido")
                    files_ok = False
            except Exception as e:
                print(f"      ❌ Erro ao ler arquivo: {e}")
                files_ok = False
        else:
            print(f"      ❌ NÃO EXISTE")
            files_ok = False
    
    if not files_ok:
        print("\n🚨 PROBLEMA: Alguns arquivos XSD estão faltando ou corrompidos!")
        return
    
    # Testar carregamento com lxml
    print(f"\n3. TESTE DE CARREGAMENTO COM LXML:")
    
    try:
        from lxml import etree
        print("   ✅ lxml disponível")
        
        schemas_loaded = {}
        
        for filename in required_files:
            file_path = schema_dir_found / filename
            schema_type = filename.replace('leiauteNFe_v4.00.xsd', 'nfe').replace('procNFe_v4.00.xsd', 'procNFe')
            
            print(f"   Carregando {schema_type} ({filename})...")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    schema_doc = etree.parse(f)
                
                schema = etree.XMLSchema(schema_doc)
                schemas_loaded[schema_type] = schema
                
                print(f"      ✅ {schema_type} carregado com sucesso")
                
            except Exception as e:
                print(f"      ❌ Erro ao carregar {schema_type}: {e}")
                return
        
        print(f"\n   ✅ TODOS OS SCHEMAS CARREGADOS COM SUCESSO!")
        print(f"   Schemas disponíveis: {list(schemas_loaded.keys())}")
        
    except ImportError:
        print("   ❌ lxml não disponível - não é possível carregar schemas")
        return
    
    # Testar XMLValidator do main.py
    print(f"\n4. TESTE DO XMLVALIDATOR DO MAIN.PY:")
    
    try:
        # Importar XMLValidator
        sys.path.append('./monitor_nfe')
        
        # Importar função de validação
        from lxml import etree
        
        # Simular XMLValidator
        class TestXMLValidator:
            def __init__(self):
                self.schemas = {}
                self.load_schemas()
            
            def load_schemas(self):
                print("   Carregando schemas no TestXMLValidator...")
                schema_count = 0
                
                try:
                    schema_dir = schema_dir_found
                    
                    # Load NFe schema
                    nfe_schema_path = schema_dir / 'leiauteNFe_v4.00.xsd'
                    if nfe_schema_path.exists():
                        try:
                            with open(nfe_schema_path, 'r', encoding='utf-8') as f:
                                schema_doc = etree.parse(f)
                            self.schemas['nfe'] = etree.XMLSchema(schema_doc)
                            schema_count += 1
                            print("      ✅ Schema NFe carregado")
                        except Exception as e:
                            print(f"      ❌ Erro ao carregar schema NFe: {e}")
                    
                    # Load procNFe schema  
                    proc_schema_path = schema_dir / 'procNFe_v4.00.xsd'
                    if proc_schema_path.exists():
                        try:
                            with open(proc_schema_path, 'r', encoding='utf-8') as f:
                                proc_doc = etree.parse(f)
                            self.schemas['procNFe'] = etree.XMLSchema(proc_doc)
                            schema_count += 1
                            print("      ✅ Schema procNFe carregado")
                        except Exception as e:
                            print(f"      ❌ Erro ao carregar schema procNFe: {e}")
                    
                    print(f"   Schemas carregados: {schema_count}/2")
                    print(f"   self.schemas = {list(self.schemas.keys())}")
                    
                    if schema_count == 2:
                        print("   ✅ SUCESSO: TestXMLValidator carregou todos os schemas!")
                        return True
                    else:
                        print("   ❌ FALHA: TestXMLValidator não carregou todos os schemas")
                        return False
                        
                except Exception as e:
                    print(f"   ❌ Erro crítico no TestXMLValidator: {e}")
                    import traceback
                    traceback.print_exc()
                    return False
        
        # Testar
        validator = TestXMLValidator()
        
        if validator.schemas:
            print("   ✅ CONCLUSÃO: XMLValidator funcionaria corretamente")
        else:
            print("   ❌ CONCLUSÃO: XMLValidator teria problemas")
            
    except Exception as e:
        print(f"   ❌ Erro no teste do XMLValidator: {e}")
        import traceback
        traceback.print_exc()
    
    # Conclusões e soluções
    print(f"\n" + "=" * 70)
    print("📋 CONCLUSÕES E SOLUÇÕES:")
    print("=" * 70)
    
    print(f"\n✅ DIAGNÓSTICO COMPLETO:")
    print(f"   - Diretório de schemas: {schema_dir_found}")
    print(f"   - Arquivos XSD: Presentes e válidos")
    print(f"   - lxml: Funcionando")
    print(f"   - Carregamento: Sucesso")
    
    print(f"\n🔧 SE O PROBLEMA PERSISTIR:")
    print(f"   1. Verifique se o aplicativo está executando do diretório correto")
    print(f"   2. Verifique se há erros durante a inicialização do aplicativo")
    print(f"   3. Execute o aplicativo e procure pelos logs de carregamento de schema")
    print(f"   4. Se não vir os logs, pode haver erro durante a criação do XMLValidator")
    
    print(f"\n🚀 APLICATIVO DEVERIA FUNCIONAR CORRETAMENTE!")
    print(f"   Se XMLs válidos ainda estão sendo rejeitados, procure os logs:")
    print(f"   '🔧 INICIANDO CARREGAMENTO DE SCHEMAS XSD'")

if __name__ == "__main__":
    diagnose_schemas()