@echo off
title Monitor NFe - Preparar Windows (Versao Corrigida)

echo 🔧 Monitor NFe - Preparação Windows (Versão Corrigida)
echo ====================================================
echo.

REM Verificar se está executando como administrador
net session >nul 2>&1
if errorlevel 1 (
    echo ⚠️  IMPORTANTE: Execute como Administrador!
    echo    Clique com botão direito no arquivo e selecione "Executar como administrador"
    echo.
    echo Pressione qualquer tecla para continuar mesmo assim...
    pause >nul
)

echo 🔍 Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python não encontrado!
    echo.
    echo 📥 Baixe e instale Python 3.11 de:
    echo    https://www.python.org/downloads/windows/
    echo.
    echo ⚠️  IMPORTANTE: 
    echo    - Marque "Add Python to PATH" 
    echo    - Use Python 3.11 (mais estável para builds)
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python %PYTHON_VERSION% encontrado

echo.
echo 🛠️  Instalando Visual C++ Build Tools...
echo.
echo ⚠️  PASSO CRÍTICO: Instale o VC++ Redistributable primeiro!

if exist "vc_redist.x64.exe" (
    echo 📦 Instalando VC++ Redistributable...
    vc_redist.x64.exe /quiet /norestart
    timeout /t 5 >nul
    echo ✅ VC++ Redistributable instalado
) else (
    echo ❌ VC++ Redistributable não encontrado!
    echo.
    echo 📥 Baixe manualmente:
    echo    https://aka.ms/vs/17/release/vc_redist.x64.exe
    echo.
    echo Salve na mesma pasta deste script e execute novamente.
    pause
    exit /b 1
)

echo.
echo 📚 Instalando Build Tools adicionais...
python -m pip install --upgrade pip setuptools wheel

echo.
echo 🧹 Limpando instalações anteriores...
python -m pip uninstall -y lxml pyinstaller pyside6 py7zr rarfile

echo.
echo 🎯 Instalando dependências PRÉ-COMPILADAS (sem compilação)...

REM Usar wheels pré-compilados para evitar compilação
echo 📦 Instalando PyInstaller...
python -m pip install pyinstaller==5.13.2

echo 📦 Instalando PySide6...
python -m pip install PySide6==6.6.0

echo 📦 Instalando lxml (wheel pré-compilado)...
python -m pip install --only-binary=all lxml==4.9.3

echo 📦 Instalando watchdog...
python -m pip install watchdog==3.0.0

echo 📦 Instalando requests...
python -m pip install requests==2.31.0

echo 📦 Instalando rarfile (Python puro)...
python -m pip install rarfile==4.0

echo 📦 Pulando py7zr (causa problemas de compilação)...
echo    ⚠️  Arquivos .7z não serão suportados nesta versão

echo.
echo 🔍 Verificando instalações...
python -c "import PySide6; print('✅ PySide6 OK')" 2>nul || echo "❌ PySide6 falhou"
python -c "import PyInstaller; print('✅ PyInstaller OK')" 2>nul || echo "❌ PyInstaller falhou"
python -c "import lxml; print('✅ lxml OK')" 2>nul || echo "❌ lxml falhou"
python -c "import watchdog; print('✅ watchdog OK')" 2>nul || echo "❌ watchdog falhou"
python -c "import requests; print('✅ requests OK')" 2>nul || echo "❌ requests falhou"
python -c "import rarfile; print('✅ rarfile OK')" 2>nul || echo "❌ rarfile falhou"

echo.
echo ✅ Preparação concluída!
echo.
echo 📋 Dependências instaladas:
echo    - PyInstaller 5.13.2
echo    - PySide6 6.6.0  
echo    - lxml 4.9.3
echo    - watchdog 3.0.0
echo    - requests 2.31.0
echo    - rarfile 4.0
echo.
echo ⚠️  NOTA: Suporte a arquivos .7z foi removido para evitar problemas de compilação
echo.
echo 🚀 Próximo passo: Execute build_windows_simple_fixed.bat
echo.
pause