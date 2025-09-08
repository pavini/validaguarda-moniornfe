@echo off
title Monitor NFe - ValidaGuarda

echo 🚀 Iniciando Monitor de Validação NFe...
echo 📂 Diretório: %cd%
echo.

:: Verifica se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python não encontrado!
    echo.
    echo 💡 Para instalar as dependências, execute: install_requirements.bat
    echo 📥 Download Python: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

:: Verifica se o arquivo principal existe
if not exist "main.py" (
    echo ❌ Arquivo main.py não encontrado!
    echo 📂 Certifique-se de estar na pasta correta do projeto.
    echo.
    dir *.py
    echo.
    pause
    exit /b 1
)

:: Verifica se as dependências estão instaladas (testa PySide6)
python -c "import PySide6" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Dependências não instaladas!
    echo.
    echo 💡 Execute install_requirements.bat primeiro para instalar as dependências.
    echo.
    set /p choice="Deseja instalar as dependências agora? (S/N): "
    if /i "%choice%"=="S" (
        call install_requirements.bat
        if errorlevel 1 (
            echo ❌ Falha na instalação. Saindo...
            pause
            exit /b 1
        )
    ) else (
        echo Saindo...
        pause
        exit /b 1
    )
)

echo ✅ Dependências verificadas
echo 🏃 Executando Monitor NFe...
echo.
echo 💡 Pressione Ctrl+C para parar a aplicação
echo ================================================
echo.

:: Executa o aplicativo
python main.py

:: Se chegou aqui, o aplicativo foi fechado
echo.
echo ================================================
echo 📊 Monitor NFe finalizado
echo.
pause