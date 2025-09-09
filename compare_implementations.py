#!/usr/bin/env python3
"""
Script para comparar as duas implementações de envio para API
"""
from pathlib import Path

def analyze_differences():
    """Analisar diferenças entre as implementações"""
    
    print("=== ANÁLISE COMPARATIVA DAS IMPLEMENTAÇÕES ===")
    
    xml_file = Path("xml-teste.xml")
    
    if not xml_file.exists():
        print("❌ Arquivo xml-teste.xml não encontrado")
        return
    
    # Ler o XML
    xml_content = xml_file.read_text(encoding='utf-8')
    print(f"✅ XML lido: {len(xml_content)} caracteres")
    
    print("\n=== DIFERENÇAS IDENTIFICADAS ===")
    
    print("1. MÉTODO DE LEITURA:")
    print("   ValidaNFeAPIService: Tenta múltiplos encodings [utf-8, latin-1, iso-8859-1, cp1252]")
    print("   main.py: Tenta utf-8 primeiro, depois latin-1")
    
    print("\n2. NOME DO ARQUIVO NA REQUISIÇÃO:")
    print("   ValidaNFeAPIService: usa document.filename")
    print("   main.py: usa file_path.name")
    
    # Comparar nomes
    print(f"   file_path.name seria: {xml_file.name}")
    print("   (document.filename provavelmente seria igual)")
    
    print("\n3. VALIDAÇÕES:")
    print("   ValidaNFeAPIService: _validate_xml_content() mais robusto")
    print("   main.py: validações inline mais simples")
    
    print("\n4. ESTRUTURA DA RESPOSTA:")
    print("   ValidaNFeAPIService: Retorna APIResponse com campos específicos")
    print("   main.py: Retorna dict simples")
    
    print("\n5. TRATAMENTO DE ERROS:")
    print("   ValidaNFeAPIService: Mais granular com diferentes tipos de exceção")
    print("   main.py: Tratamento mais direto")
    
    print("\n6. LOGS/DEBUG:")
    print("   ValidaNFeAPIService: Sem logs por padrão")
    print("   main.py: Logs detalhados com print statements")
    
    # Verificar se há algum problema específico no XML
    print("\n=== ANÁLISE DO XML ESPECÍFICO ===")
    
    # Extrair chave NFe
    import re
    
    # Tentar extrair com regex do main.py
    nfe_key = None
    match = re.search(r'<chNFe>([^<]+)</chNFe>', xml_content)
    if match:
        nfe_key = match.group(1)
        print(f"✅ Chave NFe encontrada via <chNFe>: {nfe_key}")
    else:
        match = re.search(r'Id="NFe(\d{44})"', xml_content)
        if match:
            nfe_key = match.group(1)
            print(f"✅ Chave NFe encontrada via Id: {nfe_key}")
        else:
            match = re.search(r'<infNFe[^>]*Id="NFe(\d{44})"', xml_content)
            if match:
                nfe_key = match.group(1)
                print(f"✅ Chave NFe encontrada via infNFe Id: {nfe_key}")
            else:
                print("❌ Chave NFe não encontrada")
    
    # Verificar se a chave é válida (44 dígitos)
    if nfe_key and len(nfe_key) == 44 and nfe_key.isdigit():
        print(f"✅ Chave NFe válida: {nfe_key}")
    elif nfe_key:
        print(f"⚠️  Chave NFe tem formato suspeito: {nfe_key} (tamanho: {len(nfe_key)})")
    
    # Verificar estrutura XML
    if '<nfeProc' in xml_content:
        print("✅ XML é nfeProc (NFe processada)")
    elif '<NFe' in xml_content:
        print("✅ XML é NFe simples")
    else:
        print("❌ XML não parece ser NFe válida")
    
    # Verificar assinatura
    if '<Signature' in xml_content:
        print("✅ XML contém assinatura digital")
    else:
        print("⚠️  XML não contém assinatura digital")
    
    # Verificar protocolo
    if '<protNFe' in xml_content:
        print("✅ XML contém protocolo de autorização")
    else:
        print("⚠️  XML não contém protocolo")
    
    print("\n=== POSSÍVEIS CAUSAS DO PROBLEMA ===")
    
    print("1. TOKEN: Pode estar inválido ou expirado")
    print("2. PERMISSÕES: Token pode não ter permissão para enviar este tipo de NFe")
    print("3. NFE JÁ ENVIADA: A NFe pode já ter sido processada anteriormente")
    print("4. FORMATO DO XML: Algum detalhe específico do XML pode estar causando rejeição")
    print("5. ENCODING: Problemas sutis de encoding não detectados")
    print("6. TIMING: Rate limiting da API")
    print("7. AMBIENTE: API pode estar em modo de teste vs produção")
    
    print("\n=== RECOMENDAÇÕES ===")
    print("1. Testar com um token válido para ver a resposta real da API")
    print("2. Comparar logs detalhados do aplicativo quando falha vs quando funciona manualmente")
    print("3. Verificar se há diferenças na configuração da API (sandbox vs produção)")
    print("4. Testar com XMLs diferentes para ver se o problema é específico deste arquivo")

if __name__ == "__main__":
    analyze_differences()