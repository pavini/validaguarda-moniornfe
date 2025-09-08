@echo off
title Monitor NFe - Executar Local

echo 🚀 Monitor NFe - ValidaTech Solutions
echo =====================================
echo.

REM Verificar Python
python --version >nul 2>&1 || (
    echo ❌ Python não encontrado!
    echo 📥 Instale de: https://python.org/downloads/
    echo ⚠️  Marque "Add Python to PATH"
    pause
    exit /b 1
)

REM Verificar estrutura
if not exist "monitor_nfe\main.py" (
    if not exist "monitor_nfe\main_refactored.py" (
        echo ❌ Nenhum arquivo main encontrado!
        echo 📁 Execute na pasta raiz do projeto
        pause
        exit /b 1
    )
)

echo ✅ Verificações OK

REM Configurar ambiente Windows (correção threading)
set PYTHONIOENCODING=utf-8
set PYTHONUNBUFFERED=1
set QT_QPA_PLATFORM_PLUGIN_PATH=
set QT_PLUGIN_PATH=

REM Ir para pasta da aplicação
cd monitor_nfe

echo 📦 Verificando dependências...
python -c "import PySide6" 2>nul || python -m pip install PySide6 --quiet
python -c "import watchdog" 2>nul || python -m pip install watchdog --quiet
python -c "import lxml" 2>nul || python -m pip install --only-binary=all lxml --quiet
python -c "import requests" 2>nul || python -m pip install requests --quiet

echo ✅ Dependências OK
echo.
echo 🎯 Iniciando Monitor NFe...
echo 💡 Feche a janela da aplicação ou pressione Ctrl+C para parar
echo.
echo ⚠️  Se der erro de 'ThreadHandle', feche e execute novamente
echo.

REM Tentar main.py primeiro (menos problemas de threading), depois main_refactored.py
if exist "main.py" (
    echo 🎯 Usando main.py (versão estável)
    python main.py
) else (
    echo 🎯 Usando main_refactored.py 
    python main_refactored.py
)

cd ..
echo.
echo 👋 Aplicação finalizada
pause