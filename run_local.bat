@echo off
title Monitor NFe - Executar Local

echo 🚀 Monitor NFe - Execução Local
echo ================================
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python não encontrado no PATH!
    echo.
    echo 📥 Instale Python de: https://python.org/downloads/
    echo ⚠️  Marque "Add Python to PATH" na instalação
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python %PYTHON_VERSION% encontrado

REM Verificar se está na pasta correta
if not exist "monitor_nfe" (
    echo ❌ Pasta monitor_nfe não encontrada!
    echo.
    echo 📁 Execute este arquivo na pasta raiz do projeto
    echo    (onde está a pasta monitor_nfe)
    pause
    exit /b 1
)

REM Verificar arquivo principal
if not exist "monitor_nfe\main_refactored.py" (
    echo ❌ Arquivo main_refactored.py não encontrado!
    echo.
    echo 📄 Verifique se o arquivo existe em monitor_nfe\main_refactored.py
    pause
    exit /b 1
)

echo ✅ Estrutura do projeto OK

REM Ir para pasta da aplicação
cd monitor_nfe

echo.
echo 📦 Verificando dependências básicas...

REM Verificar dependências essenciais
python -c "import PySide6" 2>nul || (
    echo ⚠️  PySide6 não encontrado, instalando...
    python -m pip install PySide6
)

python -c "import watchdog" 2>nul || (
    echo ⚠️  watchdog não encontrado, instalando...
    python -m pip install watchdog
)

python -c "import lxml" 2>nul || (
    echo ⚠️  lxml não encontrado, instalando...
    python -m pip install --only-binary=all lxml || python -m pip install lxml
)

python -c "import requests" 2>nul || (
    echo ⚠️  requests não encontrado, instalando...
    python -m pip install requests
)

echo ✅ Dependências verificadas

echo.
echo 🎯 Iniciando Monitor NFe...
echo    💡 A interface gráfica abrirá em alguns segundos
echo    ❌ Para encerrar, feche a janela da aplicação ou pressione Ctrl+C aqui
echo.

REM Executar aplicação
python main_refactored.py

REM Voltar para pasta raiz
cd ..

echo.
echo 👋 Monitor NFe finalizado
echo.
pause