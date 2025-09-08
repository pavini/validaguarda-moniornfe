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

REM Criar patch avançado para corrigir threading no Windows
echo import os > windows_patch.py
echo import sys >> windows_patch.py
echo import multiprocessing >> windows_patch.py
echo import threading >> windows_patch.py
echo from concurrent.futures import ThreadPoolExecutor >> windows_patch.py
echo. >> windows_patch.py
echo # Monkey patch para corrigir ThreadHandle no Windows >> windows_patch.py
echo if sys.platform.startswith('win'^): >> windows_patch.py
echo     # Fix multiprocessing >> windows_patch.py
echo     try: >> windows_patch.py
echo         multiprocessing.set_start_method('spawn', force=True'^) >> windows_patch.py
echo     except RuntimeError: >> windows_patch.py
echo         pass >> windows_patch.py
echo     # Override problemático ThreadPoolExecutor >> windows_patch.py
echo     original_submit = ThreadPoolExecutor.submit >> windows_patch.py
echo     def patched_submit(self, fn, *args, **kwargs'^): >> windows_patch.py
echo         try: >> windows_patch.py
echo             return original_submit(self, fn, *args, **kwargs'^) >> windows_patch.py
echo         except Exception as e: >> windows_patch.py
echo             if "'handle' must be a _ThreadHandle" in str(e'^): >> windows_patch.py
echo                 # Fallback: execução síncrona >> windows_patch.py
echo                 import concurrent.futures >> windows_patch.py
echo                 future = concurrent.futures.Future('^) >> windows_patch.py
echo                 try: >> windows_patch.py
echo                     result = fn(*args, **kwargs'^) >> windows_patch.py
echo                     future.set_result(result'^) >> windows_patch.py
echo                 except Exception as ex: >> windows_patch.py
echo                     future.set_exception(ex'^) >> windows_patch.py
echo                 return future >> windows_patch.py
echo             else: >> windows_patch.py
echo                 raise >> windows_patch.py
echo     ThreadPoolExecutor.submit = patched_submit >> windows_patch.py
echo. >> windows_patch.py
echo # Executar aplicação com patches aplicados >> windows_patch.py
echo exec(open('main_refactored.py', encoding='utf-8'^).read('^)^) >> windows_patch.py

echo 🎯 Executando main_refactored.py com patch avançado Windows...
python windows_patch.py

REM Limpar patch temporário
del windows_patch.py 2>nul

cd ..
echo.
echo 👋 Aplicação finalizada
pause