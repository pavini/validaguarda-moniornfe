#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Monitor NFe - Iniciando...${NC}"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if Python 3 is installed
if command_exists python3; then
    PYTHON_CMD="python3"
elif command_exists python; then
    # Check if python is actually Python 3
    if python -c "import sys; exit(0 if sys.version_info[0] == 3 else 1)" 2>/dev/null; then
        PYTHON_CMD="python"
    else
        echo -e "${RED}Python 3 não foi encontrado.${NC}"
        echo "Por favor, instale Python 3.8 ou superior."
        exit 1
    fi
else
    echo -e "${RED}Python não foi encontrado no PATH.${NC}"
    echo "Por favor, instale Python 3.8 ou superior."
    exit 1
fi

# Get Python version
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
echo -e "${GREEN}Python $PYTHON_VERSION encontrado.${NC}"

# Check if Python version is 3.8+
if ! $PYTHON_CMD -c "import sys; exit(0 if sys.version_info >= (3,8) else 1)" 2>/dev/null; then
    echo -e "${RED}Python 3.8 ou superior é necessário.${NC}"
    echo "Versão atual: $PYTHON_VERSION"
    exit 1
fi

# Check if pip is available
if ! $PYTHON_CMD -m pip --version >/dev/null 2>&1; then
    echo -e "${RED}pip não encontrado.${NC}"
    echo "Por favor, instale pip para Python 3."
    exit 1
fi

# Navigate to app directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$SCRIPT_DIR/monitor_nfe"

if [ ! -d "$APP_DIR" ]; then
    echo -e "${RED}Diretório monitor_nfe não encontrado.${NC}"
    exit 1
fi

cd "$APP_DIR"

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}Arquivo requirements.txt não encontrado.${NC}"
    exit 1
fi

echo -e "${YELLOW}Instalando dependências...${NC}"

# Update pip
$PYTHON_CMD -m pip install --upgrade pip >/dev/null 2>&1

# Install dependencies
if $PYTHON_CMD -m pip install -r requirements.txt >/dev/null 2>&1; then
    echo -e "${GREEN}Dependências instaladas com sucesso.${NC}"
else
    echo -e "${YELLOW}Tentando instalar com --user flag...${NC}"
    if $PYTHON_CMD -m pip install --user -r requirements.txt >/dev/null 2>&1; then
        echo -e "${GREEN}Dependências instaladas com sucesso.${NC}"
    else
        echo -e "${RED}Falha ao instalar dependências.${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}Iniciando Monitor NFe...${NC}"

# Start the application
$PYTHON_CMD main_refactored.py

# Check exit code
if [ $? -ne 0 ]; then
    echo -e "${RED}A aplicação encerrou com erro.${NC}"
    read -p "Pressione Enter para continuar..."
    exit 1
fi