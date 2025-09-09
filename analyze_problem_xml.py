#!/usr/bin/env python3
"""
Analisar por que XMLs válidos estão sendo rejeitados
"""
from pathlib import Path
import re

def analyze_xml_validation():
    """Analisar validação do XML problemático"""
    
    xml_file = Path("xml-problematico.xml")
    
    if not xml_file.exists():
        print("❌ Arquivo xml-problematico.xml não encontrado")
        return
    
    print("=== ANÁLISE DO XML QUE ESTÁ SENDO REJEITADO ===")
    
    # Ler XML
    xml_content = xml_file.read_text(encoding='utf-8')
    
    print(f"Tamanho: {len(xml_content)} caracteres")
    print(f"Tamanho em bytes: {len(xml_content.encode('utf-8'))} bytes")
    
    # === TESTE DAS VALIDAÇÕES DO CÓDIGO ===
    print(f"\n=== TESTANDO VALIDAÇÕES DO CÓDIGO ===")
    
    # 1. Teste de tamanho mínimo
    if not xml_content or len(xml_content.strip()) < 10:
        print("❌ FALHOU: XML vazio ou muito pequeno")
        return
    else:
        print("✅ PASSOU: Tamanho mínimo OK")
    
    # 2. Teste de início com <?xml
    xml_stripped = xml_content.strip()
    if not xml_stripped.startswith('<?xml'):
        print("❌ FALHOU: Não começa com <?xml")
        print(f"   Começa com: {xml_stripped[:50]}...")
        return
    else:
        print("✅ PASSOU: Começa com <?xml")
    
    # 3. Teste de conteúdo NFe
    if '<NFe' not in xml_content and '<nfeProc' not in xml_content:
        print("❌ FALHOU: Não contém <NFe ou <nfeProc")
        return
    else:
        has_nfe = '<NFe' in xml_content
        has_nfeproc = '<nfeProc' in xml_content
        print(f"✅ PASSOU: Contém NFe tags (NFe: {has_nfe}, nfeProc: {has_nfeproc})")
    
    # 4. Teste de limite de tamanho (5MB)
    size_mb = len(xml_content.encode('utf-8')) / (1024 * 1024)
    if size_mb > 5:
        print(f"❌ FALHOU: Arquivo muito grande ({size_mb:.2f}MB > 5MB)")
        return
    else:
        print(f"✅ PASSOU: Tamanho OK ({size_mb:.3f}MB < 5MB)")
    
    print(f"\n=== ANÁLISE DETALHADA DO CONTEÚDO ===")
    
    # Extrair chave NFe
    nfe_key = None
    
    # Método 1: <chNFe>
    match = re.search(r'<chNFe>([^<]+)</chNFe>', xml_content)
    if match:
        nfe_key = match.group(1)
        print(f"✅ Chave NFe via <chNFe>: {nfe_key}")
    else:
        print("⚠️  Não encontrou chave via <chNFe>")
    
    # Método 2: Id="NFe..."
    match = re.search(r'Id="NFe(\d{44})"', xml_content)
    if match:
        nfe_key_id = match.group(1)
        print(f"✅ Chave NFe via Id: {nfe_key_id}")
        if not nfe_key:
            nfe_key = nfe_key_id
    else:
        print("⚠️  Não encontrou chave via Id=\"NFe...\"")
    
    # Método 3: infNFe Id
    match = re.search(r'<infNFe[^>]*Id="NFe(\d{44})"', xml_content)
    if match:
        nfe_key_infnfe = match.group(1)
        print(f"✅ Chave NFe via infNFe Id: {nfe_key_infnfe}")
        if not nfe_key:
            nfe_key = nfe_key_infnfe
    else:
        print("⚠️  Não encontrou chave via infNFe Id")
    
    if nfe_key:
        if len(nfe_key) == 44 and nfe_key.isdigit():
            print(f"✅ Chave NFe VÁLIDA: {nfe_key}")
        else:
            print(f"❌ Chave NFe INVÁLIDA: {nfe_key} (tamanho: {len(nfe_key)})")
    else:
        print("❌ PROBLEMA: Nenhuma chave NFe encontrada!")
    
    # Verificar estrutura específica
    print(f"\n=== ESTRUTURA DO XML ===")
    
    if '<nfeProc' in xml_content:
        print("✅ Tipo: nfeProc (NFe processada)")
    elif '<NFe' in xml_content:
        print("✅ Tipo: NFe simples")
    else:
        print("❌ Tipo: Desconhecido")
    
    if '<Signature' in xml_content:
        print("✅ Contém assinatura digital")
    else:
        print("⚠️  Não contém assinatura digital")
    
    if '<protNFe' in xml_content:
        print("✅ Contém protocolo de autorização")
    else:
        print("⚠️  Não contém protocolo")
    
    # Verificar status
    match = re.search(r'<cStat>(\d+)</cStat>', xml_content)
    if match:
        cstat = match.group(1)
        print(f"✅ Status: {cstat}")
        if cstat == "100":
            print("✅ Status 100: Autorizada")
        else:
            print(f"⚠️  Status {cstat}: Verificar se é válido")
    else:
        print("⚠️  Status não encontrado")
    
    # Verificar possíveis problemas de caracteres especiais
    print(f"\n=== ANÁLISE DE CARACTERES ===")
    
    try:
        xml_content.encode('utf-8')
        print("✅ Encoding UTF-8: OK")
    except UnicodeEncodeError as e:
        print(f"❌ Problema de encoding UTF-8: {e}")
    
    # Verificar caracteres de controle
    control_chars = [c for c in xml_content if ord(c) < 32 and c not in '\r\n\t']
    if control_chars:
        print(f"⚠️  Caracteres de controle encontrados: {len(control_chars)}")
        print(f"   Primeiros 5: {[ord(c) for c in control_chars[:5]]}")
    else:
        print("✅ Sem caracteres de controle problemáticos")
    
    # Verificar BOM
    if xml_content.startswith('\ufeff'):
        print("⚠️  Contém BOM (Byte Order Mark)")
    else:
        print("✅ Sem BOM")
    
    print(f"\n=== POSSÍVEIS PROBLEMAS ===")
    
    # Verificar se o XML está em uma linha só (pode causar problemas)
    lines = xml_content.split('\n')
    if len(lines) == 1:
        print("⚠️  XML em linha única - pode causar problemas de parsing")
    else:
        print(f"✅ XML formatado em {len(lines)} linhas")
    
    # Verificar se há espaços extras no início/fim
    if xml_content != xml_content.strip():
        print("⚠️  XML tem espaços/quebras extras no início/fim")
    else:
        print("✅ XML sem espaços extras")
    
    # Teste final: simular exatamente a função _validate_xml_content
    print(f"\n=== TESTE DA FUNÇÃO _validate_xml_content ===")
    
    def test_validate_xml_content(xml_content):
        """Replica exata da função _validate_xml_content"""
        if not xml_content or len(xml_content.strip()) < 10:
            return "Arquivo XML vazio ou muito pequeno"
        
        xml_stripped = xml_content.strip()
        if not xml_stripped.startswith('<?xml'):
            return "Arquivo não é um XML válido (sem declaração XML)"
        
        if '<NFe' not in xml_content and '<nfeProc' not in xml_content:
            return "Arquivo não parece ser uma NFe válida"
        
        return None
    
    validation_error = test_validate_xml_content(xml_content)
    if validation_error:
        print(f"❌ FUNÇÃO _validate_xml_content FALHOU: {validation_error}")
    else:
        print("✅ FUNÇÃO _validate_xml_content PASSOU")
    
    print(f"\n=== CONCLUSÃO ===")
    print("Se todas as validações passaram mas o aplicativo ainda rejeita,")
    print("o problema pode estar em:")
    print("1. Validação XSD (schema)")
    print("2. Processamento posterior na API")
    print("3. Problemas de encoding não detectados")
    print("4. Validações adicionais não testadas aqui")

if __name__ == "__main__":
    analyze_xml_validation()