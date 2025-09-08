@echo off
title Monitor NFe - Build Simples Windows

echo 🚀 Monitor NFe - Build Windows Simples
echo ======================================
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python não encontrado!
    pause
    exit /b 1
)

REM Ir para pasta do projeto
cd monitor_nfe

REM Instalar PyInstaller se necessário
echo 📦 Instalando PyInstaller...
python -m pip install pyinstaller >nul 2>&1

REM Build simples
echo 🔨 Construindo executável...
python -m PyInstaller --onefile --windowed --name "Monitor NFe" main_refactored.py

if exist "dist\Monitor NFe.exe" (
    echo ✅ Build concluído!
    echo 📍 Executável: dist\Monitor NFe.exe
    
    REM Criar pasta de distribuição
    if not exist "..\dist_windows" mkdir "..\dist_windows"
    copy "dist\Monitor NFe.exe" "..\dist_windows\" >nul
    
    echo.
    echo 📁 Arquivo copiado para: ..\dist_windows\Monitor NFe.exe
    echo 🎉 Pronto para distribuição!
    
) else (
    echo ❌ Erro no build
)

echo.
pause