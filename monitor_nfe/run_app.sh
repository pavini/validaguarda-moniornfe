#!/bin/bash

echo "🚀 Iniciando Monitor NFe..."
echo "📂 Diretório atual: $(pwd)"
echo "🐍 Versão Python: $(python3 --version)"

# Muda para o diretório correto
cd "$(dirname "$0")"

echo "📍 Executando em: $(pwd)"

# Verifica se o arquivo principal existe
if [ -f "main.py" ]; then
    echo "✅ main.py encontrado"
    echo "🔄 Executando aplicação..."
    python3 main.py
else
    echo "❌ main.py não encontrado no diretório atual"
    echo "📁 Arquivos disponíveis:"
    ls -la *.py
fi