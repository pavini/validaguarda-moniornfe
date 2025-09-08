@echo off
setlocal

REM Hide console window when app starts
if not "%1"=="hide" (
    start /min cmd /c "%0" hide
    exit /b
)

REM Set window title
title Monitor NFe - Starting...

echo Verificando Python...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python nao foi encontrado no PATH.
    echo Por favor, instale o Python 3.8 ou superior.
    echo Download: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Python %PYTHON_VERSION% encontrado.

REM Check if version is 3.8+
python -c "import sys; exit(0 if sys.version_info >= (3,8) else 1)" >nul 2>&1
if errorlevel 1 (
    echo Python 3.8 ou superior e necessario.
    echo Versao atual: %PYTHON_VERSION%
    pause
    exit /b 1
)

REM Navigate to app directory
cd /d "%~dp0monitor_nfe"

REM Check if requirements.txt exists
if not exist "requirements.txt" (
    echo Arquivo requirements.txt nao encontrado.
    pause
    exit /b 1
)

echo Instalando dependencias...

REM Install dependencies
python -m pip install --upgrade pip >nul 2>&1
python -m pip install -r requirements.txt

if errorlevel 1 (
    echo Erro ao instalar dependencias.
    echo Tentando com --user flag...
    python -m pip install --user -r requirements.txt
    if errorlevel 1 (
        echo Falha ao instalar dependencias.
        pause
        exit /b 1
    )
)

echo Dependencias instaladas com sucesso.
echo Iniciando Monitor NFe...

REM Start the application
python main_refactored.py

REM If app exits with error, show message
if errorlevel 1 (
    echo.
    echo A aplicacao encerrou com erro.
    pause
)

endlocal