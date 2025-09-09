# Guia de Debug para Problemas de Envio NFe

## Problema Identificado
Um dos arquivos XML está dando erro no envio via aplicativo, mas funciona no teste manual.

## Análise Realizada

### 1. Arquivo XML (`xml-teste.xml`)
✅ **VÁLIDO** - O arquivo está perfeito:
- 16.327 bytes
- Encoding UTF-8 correto
- Estrutura NFe válida (nfeProc)
- Chave NFe válida: `42250958318268000156550010000002091945393552`
- Contém assinatura digital
- Contém protocolo de autorização

### 2. Implementações Comparadas
Existem duas implementações de envio:

**A) `ValidaNFeAPIService`** (Clean Architecture):
- Localização: `monitor_nfe/infrastructure/external_services/validanfe_api_service.py`
- Mais robusta, mas TINHA logs insuficientes
- ✅ **CORRIGIDA** com logs detalhados

**B) `main.py`** (Implementação direta):
- Localização: `monitor_nfe/main.py:771`
- Com logs detalhados desde o início
- Funciona no teste manual

### 3. Diferenças Principais
- **Logs**: ValidaNFeAPIService não tinha logs (agora corrigidos)
- **Tratamento de erro 409**: NFe já enviada deve ser tratada como sucesso
- **Headers de resposta**: Agora são logados para debug

## Melhorias Implementadas

### 1. Logs Detalhados Adicionados
```python
print(f"[ValidaNFeAPIService] API Request: {url}")
print(f"[ValidaNFeAPIService] Headers: {{'X-API-KEY': '[TOKEN]'}}")
print(f"[ValidaNFeAPIService] XML content length: {len(xml_content)} chars")
print(f"[ValidaNFeAPIService] API Response: {response.status_code}")
print(f"[ValidaNFeAPIService] Response headers: {dict(response.headers)}")
```

### 2. Melhor Tratamento de Status Codes
- **409 Conflict**: NFe já existe → Tratado como SUCESSO
- **401 Unauthorized**: Token inválido/expirado
- **400 Bad Request**: Dados inválidos
- **429 Too Many Requests**: Rate limiting
- **500 Internal Server Error**: Erro do servidor

### 3. Scripts de Teste Criados

#### `test_improved_service.py`
Testa o ValidaNFeAPIService melhorado:
```bash
python3 test_improved_service.py SEU_TOKEN_AQUI
```

#### `test_full_simulation.py`
Simula exatamente como o main.py funciona:
```bash
python3 test_full_simulation.py SEU_TOKEN_AQUI
```

#### `debug_xml_encoding.py`
Analisa problemas de encoding:
```bash
python3 debug_xml_encoding.py
```

#### `test_api_curl.sh`
Teste manual com curl:
```bash
./test_api_curl.sh SEU_TOKEN_AQUI
```

## Como Usar o Debug

### 1. Testar com Token Real
```bash
# Usar o ValidaNFeAPIService melhorado
python3 test_improved_service.py SEU_TOKEN_DA_VALIDANFE

# Ou simular o main.py
python3 test_full_simulation.py SEU_TOKEN_DA_VALIDANFE
```

### 2. Interpretar os Logs
Com logs detalhados, você verá:
- Exatamente que URL está sendo chamada
- Tamanho e preview do XML sendo enviado
- Status code e headers da resposta
- Conteúdo da resposta (primeiros 300 chars)

### 3. Casos Mais Prováveis

#### NFe Já Enviada (HTTP 409)
```
[ValidaNFeAPIService] API Response: 409
Resultado: success=True, message="NFe já foi enviada anteriormente"
```
**Solução**: Isso é NORMAL, não é erro.

#### Token Inválido (HTTP 401)
```
[ValidaNFeAPIService] API Response: 401
Resultado: success=False, message="Token inválido/expirado"
```
**Solução**: Verificar/atualizar token no aplicativo.

#### Dados Inválidos (HTTP 400)
```
[ValidaNFeAPIService] API Response: 400
Response text: [detalhes do erro da API]
```
**Solução**: Verificar mensagem específica da API.

### 4. Comparar Implementações
Se ainda houver diferenças, compare os logs de:
- `ValidaNFeAPIService` (arquivo melhorado)
- `main.py` (que funciona manual)

Procure por diferenças em:
- Headers enviados
- Formato do multipart/form-data
- Encoding do XML
- Nome do arquivo

## Próximos Passos

1. **Teste com token real** usando os scripts criados
2. **Compare os logs** detalhados
3. **Se o problema persistir**, verifique se:
   - O ambiente da API é o mesmo (produção vs sandbox)
   - Não há rate limiting
   - O token tem as permissões corretas

## Arquivos Modificados
- ✅ `monitor_nfe/infrastructure/external_services/validanfe_api_service.py` - Adicionados logs detalhados e melhor tratamento de erros

## Arquivos Criados para Debug
- `test_improved_service.py` - Teste do serviço melhorado
- `test_full_simulation.py` - Simulação do main.py
- `debug_xml_encoding.py` - Análise de encoding
- `test_api_curl.sh` - Teste com curl
- `compare_implementations.py` - Análise comparativa
- `DEBUG_GUIDE.md` - Este guia