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
if not exist "monitor_nfe\main_refactored.py" (
    echo ❌ Arquivo main_refactored.py não encontrado!
    echo 📁 Execute na pasta raiz do projeto
    pause
    exit /b 1
)

echo ✅ Verificações OK

REM Configurar ambiente Windows (correção threading avançada)
set PYTHONIOENCODING=utf-8
set PYTHONUNBUFFERED=1
set QT_QPA_PLATFORM_PLUGIN_PATH=
set QT_PLUGIN_PATH=
set PYTHONUTF8=1

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

REM Criar wrapper para corrigir threading no Windows
echo import os > windows_wrapper.py
echo import sys >> windows_wrapper.py
echo import multiprocessing >> windows_wrapper.py
echo if __name__ == '__main__': >> windows_wrapper.py
echo     # Fix para Windows threading >> windows_wrapper.py
echo     if sys.platform.startswith('win'): >> windows_wrapper.py
echo         try: >> windows_wrapper.py
echo             multiprocessing.set_start_method('spawn', force=True) >> windows_wrapper.py
echo         except RuntimeError: >> windows_wrapper.py
echo             pass >> windows_wrapper.py
echo     # Executar aplicação >> windows_wrapper.py
echo     exec(open('main_refactored.py', encoding='utf-8').read()) >> windows_wrapper.py

echo 🎯 Executando main_refactored.py com correções Windows...
python windows_wrapper.py

REM Limpar wrapper temporário
del windows_wrapper.py 2>nul

cd ..
echo.
echo 👋 Aplicação finalizada
pause