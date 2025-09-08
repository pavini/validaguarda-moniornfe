@echo off
echo 🔧 Instalando dependências do Monitor NFe...
echo.

:: Verifica se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python não encontrado! Por favor, instale o Python 3.8+ antes de continuar.
    echo 📥 Download: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python encontrado:
python --version

:: Atualiza pip
echo.
echo 📦 Atualizando pip...
python -m pip install --upgrade pip

:: Instala as dependências
echo.
echo 📦 Instalando dependências do requirements.txt...
python -m pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ❌ Erro ao instalar dependências!
    echo 💡 Tente executar como Administrador
    pause
    exit /b 1
)

echo.
echo ✅ Todas as dependências foram instaladas com sucesso!
echo 🚀 Agora você pode executar o Monitor NFe usando run_app.bat
echo.
pause