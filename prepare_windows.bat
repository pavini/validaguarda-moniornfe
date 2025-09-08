@echo off
title Monitor NFe - Preparar Ambiente Windows

echo 🔧 Monitor NFe - Preparação do Ambiente Windows
echo ================================================
echo.

REM Verificar se está executando como administrador
net session >nul 2>&1
if errorlevel 1 (
    echo ⚠️  RECOMENDADO: Execute como Administrador para melhor compatibilidade
    echo    Clique com botão direito no arquivo e selecione "Executar como administrador"
    echo.
    timeout /t 3 >nul
)

echo 🔍 Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python não encontrado!
    echo.
    echo 📥 Baixe e instale Python 3.8+ de:
    echo    https://www.python.org/downloads/
    echo.
    echo ⚠️  IMPORTANTE: Marque "Add Python to PATH" durante instalação
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python %PYTHON_VERSION% encontrado

echo.
echo 📦 Atualizando pip...
python -m pip install --upgrade pip

echo.
echo 🧹 Limpando cache do pip...
python -m pip cache purge

echo.
echo 📚 Instalando dependências base...
python -m pip install --upgrade setuptools wheel

echo.
echo 🔧 Instalando PyInstaller (versão específica)...
python -m pip uninstall -y pyinstaller
python -m pip install pyinstaller==5.13.2

echo.
echo 🎨 Instalando PySide6 (versão específica)...
python -m pip uninstall -y PySide6
python -m pip install PySide6==6.6.0

echo.
echo 📋 Instalando demais dependências...
python -m pip install watchdog==3.0.0
python -m pip install lxml==4.9.3
python -m pip install requests==2.31.0
python -m pip install rarfile==4.0
python -m pip install py7zr==0.20.6

echo.
echo 🔍 Verificando instalação...
python -c "import PySide6; print(f'✅ PySide6 {PySide6.__version__} OK')"
python -c "import PyInstaller; print(f'✅ PyInstaller {PyInstaller.__version__} OK')"

echo.
echo 📥 Baixando Visual C++ Redistributable (se necessário)...
where curl >nul 2>&1
if not errorlevel 1 (
    if not exist "vc_redist.x64.exe" (
        echo Baixando VC++ Redistributable...
        curl -L "https://aka.ms/vs/17/release/vc_redist.x64.exe" -o "vc_redist.x64.exe"
        if exist "vc_redist.x64.exe" (
            echo ✅ VC++ Redistributable baixado
            echo ❓ Deseja instalar agora? (s/N)
            set /p install_vc=
            if /i "!install_vc!"=="s" (
                echo Instalando VC++ Redistributable...
                vc_redist.x64.exe /quiet /norestart
                echo ✅ VC++ Redistributable instalado
            )
        )
    ) else (
        echo ✅ VC++ Redistributable já existe
    )
) else (
    echo ⚠️  curl não encontrado. Baixe manualmente:
    echo    https://aka.ms/vs/17/release/vc_redist.x64.exe
)

echo.
echo ✅ Ambiente preparado!
echo.
echo 📋 Próximos passos:
echo 1. Execute: build_windows_fix.bat
echo 2. Se der erro, reinicie o prompt e tente novamente
echo 3. Se persistir, execute vc_redist.x64.exe manualmente
echo.
pause