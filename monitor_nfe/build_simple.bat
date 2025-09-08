@echo off
title Build Simples - Monitor NFe

echo 🔨 Build Simples do Monitor NFe
echo ================================
echo.

:: Verifica Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python não encontrado!
    pause
    exit /b 1
)

:: Instala PyInstaller se necessário
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo 📦 Instalando PyInstaller...
    pip install pyinstaller
)

:: Limpa build anterior
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

echo 🏗️  Compilando...
python -m PyInstaller Monitor_NFe_Windows.spec

if errorlevel 1 (
    echo ❌ Erro no build!
    pause
    exit /b 1
)

echo.
echo ✅ Build concluído!
echo 📁 Executável em: dist\Monitor NFe\Monitor NFe.exe
echo.

:: Testa o executável
set /p test="Deseja testar o executável? (S/N): "
if /i "%test%"=="S" (
    echo 🚀 Executando teste...
    start "" "dist\Monitor NFe\Monitor NFe.exe"
)

echo.
echo 💡 Para distribuir, comprima a pasta: dist\Monitor NFe\
pause