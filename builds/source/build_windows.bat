@echo off
title Build Monitor NFe para Windows

echo ========================================
echo 🏗️  BUILD MONITOR NFE PARA WINDOWS
echo ========================================
echo.

:: Verifica se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python não encontrado!
    echo 📥 Instale Python 3.8+ de: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python encontrado:
python --version
echo.

:: Verifica se PyInstaller está instalado
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo 📦 Instalando PyInstaller...
    python -m pip install pyinstaller
    if errorlevel 1 (
        echo ❌ Falha ao instalar PyInstaller
        pause
        exit /b 1
    )
)

:: Limpa builds anteriores
echo 🧹 Limpando builds anteriores...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
if exist "*.spec" del "*.spec"

:: Cria diretório de assets se não existir
if not exist "assets" mkdir assets

:: Copia arquivos necessários
echo 📋 Preparando arquivos...
if exist "logo-validatech.png" copy "logo-validatech.png" "assets\" >nul
if exist "logo-validatech.svg" copy "logo-validatech.svg" "assets\" >nul

:: Build do executável
echo.
echo 🔨 Compilando aplicação...
echo ⏱️  Este processo pode demorar alguns minutos...
echo.

python -m PyInstaller ^
    --onedir ^
    --windowed ^
    --name "Monitor NFe" ^
    --add-data "requirements.txt;." ^
    --add-data "assets;assets" ^
    --add-data "schemas;schemas" ^
    --icon="assets/logo-validatech.png" ^
    --distpath="dist" ^
    --workpath="build" ^
    --specpath="." ^
    main.py

if errorlevel 1 (
    echo.
    echo ❌ Erro durante o build!
    echo 💡 Verifique se todas as dependências estão instaladas
    echo    Execute: pip install -r requirements.txt
    pause
    exit /b 1
)

:: Cria estrutura de distribuição
echo.
echo 📦 Criando pacote de distribuição...

if not exist "dist\Monitor NFe Package" mkdir "dist\Monitor NFe Package"

:: Copia arquivos do executável
xcopy "dist\Monitor NFe" "dist\Monitor NFe Package\Monitor NFe" /s /e /i /q

:: Cria arquivos adicionais
echo.
echo 📄 Criando arquivos de distribuição...

:: README para usuário final
echo # Monitor de Validação NFe - ValidaGuarda > "dist\Monitor NFe Package\LEIA-ME.txt"
echo. >> "dist\Monitor NFe Package\LEIA-ME.txt"
echo ## Como usar: >> "dist\Monitor NFe Package\LEIA-ME.txt"
echo. >> "dist\Monitor NFe Package\LEIA-ME.txt"
echo 1. Execute "Monitor NFe.exe" >> "dist\Monitor NFe Package\LEIA-ME.txt"
echo 2. Configure as pastas de monitoramento e saída >> "dist\Monitor NFe Package\LEIA-ME.txt"
echo 3. Insira o token da API ValidaNFe >> "dist\Monitor NFe Package\LEIA-ME.txt"
echo 4. Clique em "Iniciar Monitoramento" >> "dist\Monitor NFe Package\LEIA-ME.txt"
echo. >> "dist\Monitor NFe Package\LEIA-ME.txt"
echo ## Requisitos: >> "dist\Monitor NFe Package\LEIA-ME.txt"
echo - Windows 10 ou superior >> "dist\Monitor NFe Package\LEIA-ME.txt"
echo - Conexão com internet para envio à API >> "dist\Monitor NFe Package\LEIA-ME.txt"
echo. >> "dist\Monitor NFe Package\LEIA-ME.txt"
echo ## Suporte: >> "dist\Monitor NFe Package\LEIA-ME.txt"
echo Este software foi desenvolvido para validar e processar >> "dist\Monitor NFe Package\LEIA-ME.txt"
echo arquivos XML de Nota Fiscal Eletrônica (NFe) brasileiras. >> "dist\Monitor NFe Package\LEIA-ME.txt"

:: Arquivo batch para executar
echo @echo off > "dist\Monitor NFe Package\Executar Monitor NFe.bat"
echo title Monitor NFe - ValidaGuarda >> "dist\Monitor NFe Package\Executar Monitor NFe.bat"
echo cd /d "%%~dp0" >> "dist\Monitor NFe Package\Executar Monitor NFe.bat"
echo start "" "Monitor NFe\Monitor NFe.exe" >> "dist\Monitor NFe Package\Executar Monitor NFe.bat"

:: Versão com console para debug
echo @echo off > "dist\Monitor NFe Package\Executar com Console (Debug).bat"
echo title Monitor NFe - Console Debug >> "dist\Monitor NFe Package\Executar com Console (Debug).bat"
echo cd /d "%%~dp0" >> "dist\Monitor NFe Package\Executar com Console (Debug).bat"
echo "Monitor NFe\Monitor NFe.exe" >> "dist\Monitor NFe Package\Executar com Console (Debug).bat"
echo pause >> "dist\Monitor NFe Package\Executar com Console (Debug).bat"

echo.
echo ✅ Build concluído com sucesso!
echo.
echo 📁 Arquivos gerados:
echo    📂 dist\Monitor NFe Package\
echo       📄 Executar Monitor NFe.bat
echo       📄 Executar com Console (Debug).bat
echo       📄 LEIA-ME.txt
echo       📂 Monitor NFe\
echo          📄 Monitor NFe.exe
echo          📄 [dependências...]
echo.
echo 🚀 Para distribuir:
echo    1. Comprima a pasta "Monitor NFe Package"
echo    2. Envie o arquivo ZIP para os usuários
echo    3. Usuários devem descompactar e executar o .bat
echo.

:: Abre a pasta de distribuição
start explorer "dist\Monitor NFe Package"

echo 💡 Pressione qualquer tecla para finalizar...
pause >nul