@echo off
title Monitor NFe - Debug Local

echo 🔍 Monitor NFe - Execução com Debug
echo ===================================
echo.

REM Verificações básicas
python --version >nul 2>&1 || (
    echo ❌ Python não encontrado!
    pause
    exit /b 1
)

if not exist "monitor_nfe\main_refactored.py" (
    echo ❌ main_refactored.py não encontrado!
    pause  
    exit /b 1
)

echo ✅ Verificações OK
echo.

cd monitor_nfe

echo 🐛 Executando com logs detalhados...
echo    📋 Todos os prints/erros serão exibidos aqui
echo    ❌ Pressione Ctrl+C para parar
echo.
echo ════════════════════════════════════════════════
echo.

REM Executar com máximo de detalhes
python -u main_refactored.py

echo.
echo ════════════════════════════════════════════════
echo 🔍 Aplicação finalizada

cd ..

echo.
echo 📊 Informações do sistema:
python --version
echo Pasta atual: %CD%
echo.

pause