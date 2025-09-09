#!/bin/bash

# Script para testar envio do XML para a API ValidaNFe usando curl

XML_FILE="xml-teste.xml"
API_URL="https://api.validanfe.com/GuardaNFe/EnviarXml"

if [ ! -f "$XML_FILE" ]; then
    echo "ERRO: Arquivo $XML_FILE não encontrado"
    exit 1
fi

if [ -z "$1" ]; then
    echo "Uso: $0 <TOKEN_API>"
    echo "Exemplo: $0 seu_token_aqui"
    exit 1
fi

TOKEN="$1"

echo "=== TESTE DE ENVIO XML PARA API VALIDANFE ==="
echo "Arquivo: $XML_FILE"
echo "URL: $API_URL"
echo "Token: ${TOKEN:0:20}..."
echo "Tamanho do arquivo: $(wc -c < "$XML_FILE") bytes"
echo

echo "Enviando..."

# Fazer a requisição
curl -X POST \
  -H "X-API-KEY: $TOKEN" \
  -F "xmlFile=@$XML_FILE" \
  -w "\n\nStatus Code: %{http_code}\nTempo total: %{time_total}s\nTempo de resposta: %{time_starttransfer}s\n" \
  -v \
  "$API_URL"

echo
echo "=== FIM DO TESTE ==="