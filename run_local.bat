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

REM Criar script temporário para fix de threading
echo import multiprocessing > temp_fix.py
echo if __name__ == '__main__': >> temp_fix.py
echo     try: >> temp_fix.py
echo         multiprocessing.set_start_method('spawn', force=True) >> temp_fix.py
echo     except: >> temp_fix.py
echo         pass >> temp_fix.py
echo     exec(open('main_refactored.py').read()) >> temp_fix.py

REM Executar com fix
python temp_fix.py

REM Limpar arquivo temporário
del temp_fix.py 2>nul

cd ..
echo.
echo 👋 Aplicação finalizada
pause