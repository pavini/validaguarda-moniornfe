@echo off
setlocal enabledelayedexpansion

REM Monitor NFe - Build Script para Windows
REM Gera executável Windows (.exe)

title Monitor NFe - Build Installers v1.0.0

echo.
echo ═══════════════════════════════════════════════════════════════
echo                                                               
echo           🚀 Monitor NFe - Build Windows v1.0.0            
echo                    ValidaTech Solutions                      
echo                                                               
echo ═══════════════════════════════════════════════════════════════
echo.

REM Variáveis de configuração
set APP_NAME=Monitor NFe
set APP_VERSION=1.0.0
set SCRIPT_DIR=%~dp0
set BUILD_DIR=%SCRIPT_DIR%builds_windows
set SOURCE_DIR=%SCRIPT_DIR%monitor_nfe

echo 🔍 Verificando dependências...

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python não encontrado no PATH!
    echo Por favor, instale Python 3.8+ de https://python.org/downloads/
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python %PYTHON_VERSION% encontrado

REM Verificar se versão é 3.8+
python -c "import sys; exit(0 if sys.version_info >= (3,8) else 1)" >nul 2>&1
if errorlevel 1 (
    echo ❌ Python 3.8+ é necessário
    echo Versão atual: %PYTHON_VERSION%
    pause
    exit /b 1
)

REM Verificar estrutura do projeto
if not exist "%SOURCE_DIR%" (
    echo ❌ Diretório monitor_nfe não encontrado!
    echo Execute este script na raiz do projeto
    pause
    exit /b 1
)

if not exist "%SOURCE_DIR%\main_refactored.py" (
    echo ❌ main_refactored.py não encontrado em monitor_nfe\!
    pause
    exit /b 1
)

echo ✅ Estrutura do projeto verificada

echo.
echo 📦 Instalando dependências Python...

REM Atualizar pip
python -m pip install --upgrade pip >nul 2>&1

REM Instalar dependências
cd /d "%SOURCE_DIR%"
if exist "requirements.txt" (
    python -m pip install -r requirements.txt >nul 2>&1
    echo ✅ Dependências instaladas
) else (
    echo ⚠️  requirements.txt não encontrado, instalando dependências básicas...
    python -m pip install PyInstaller PySide6 watchdog lxml requests rarfile py7zr >nul 2>&1
)

cd /d "%SCRIPT_DIR%"

echo.
echo 🏗️  Configurando ambiente de build...

REM Limpar builds anteriores
if exist "%BUILD_DIR%" (
    echo 🧹 Limpando builds anteriores...
    rmdir /s /q "%BUILD_DIR%"
)

mkdir "%BUILD_DIR%"

REM Copiar arquivos source
xcopy /E /Y "%SOURCE_DIR%" "%BUILD_DIR%\source\" >nul

echo ✅ Ambiente preparado

echo.
echo 🪟 Construindo executável Windows...

cd /d "%BUILD_DIR%\source"

REM Criar spec file para Windows
echo # -*- mode: python ; coding: utf-8 -*- > windows.spec
echo. >> windows.spec
echo a = Analysis( >> windows.spec
echo     ['main_refactored.py'], >> windows.spec
echo     pathex=[], >> windows.spec
echo     binaries=[], >> windows.spec
echo     datas=[ >> windows.spec
echo         ('schemas', 'schemas'^), >> windows.spec
echo         ('logo-validatech.png', '.'^), >> windows.spec
echo         ('logo-validatech.svg', '.'^), >> windows.spec
echo     ], >> windows.spec
echo     hiddenimports=[ >> windows.spec
echo         'PySide6.QtCore', >> windows.spec
echo         'PySide6.QtWidgets', >> windows.spec
echo         'PySide6.QtGui', >> windows.spec
echo         'PySide6.QtSvg', >> windows.spec
echo         'PySide6.QtOpenGL', >> windows.spec
echo         'shiboken6', >> windows.spec
echo         'watchdog.observers', >> windows.spec
echo         'watchdog.events', >> windows.spec
echo         'lxml.etree', >> windows.spec
echo         'rarfile', >> windows.spec
echo         'py7zr', >> windows.spec
echo         'requests', >> windows.spec
echo     ], >> windows.spec
echo     hookspath=[], >> windows.spec
echo     hooksconfig={}, >> windows.spec
echo     runtime_hooks=[], >> windows.spec
echo     excludes=['tkinter', 'matplotlib'], >> windows.spec
echo     win_no_prefer_redirects=False, >> windows.spec
echo     win_private_assemblies=False, >> windows.spec
echo     cipher=None, >> windows.spec
echo     noarchive=False, >> windows.spec
echo ^) >> windows.spec
echo. >> windows.spec
echo pyz = PYZ(a.pure, a.zipped_data, cipher=None^) >> windows.spec
echo. >> windows.spec
echo exe = EXE( >> windows.spec
echo     pyz, >> windows.spec
echo     a.scripts, >> windows.spec
echo     a.binaries, >> windows.spec
echo     a.zipfiles, >> windows.spec
echo     a.datas, >> windows.spec
echo     [], >> windows.spec
echo     name='Monitor NFe.exe', >> windows.spec
echo     debug=False, >> windows.spec
echo     bootloader_ignore_signals=False, >> windows.spec
echo     strip=False, >> windows.spec
echo     upx=True, >> windows.spec
echo     upx_exclude=[], >> windows.spec
echo     runtime_tmpdir=None, >> windows.spec
echo     console=False, >> windows.spec
echo     disable_windowed_traceback=False, >> windows.spec
echo     target_arch=None, >> windows.spec
echo     codesign_identity=None, >> windows.spec
echo     entitlements_file=None, >> windows.spec
echo     icon='logo-validatech.png' if os.path.exists('logo-validatech.png'^) else None, >> windows.spec
echo ^) >> windows.spec

echo 📦 Executando PyInstaller...
python -m PyInstaller windows.spec --clean --distpath="../windows" --workpath="../temp"

cd /d "%SCRIPT_DIR%"

if exist "%BUILD_DIR%\windows\Monitor NFe.exe" (
    echo ✅ Build Windows concluído!
    echo 📍 Executável criado: %BUILD_DIR%\windows\Monitor NFe.exe
    
    REM Verificar tamanho do arquivo
    for %%A in ("%BUILD_DIR%\windows\Monitor NFe.exe") do set filesize=%%~zA
    set /a filesizeMB=!filesize!/1048576
    echo 📊 Tamanho: !filesizeMB! MB
    
    echo.
    echo 🛠️  Criando instalador...
    
    REM Criar installer batch
    echo @echo off > "%BUILD_DIR%\windows\install.bat"
    echo title Monitor NFe - Instalador Windows >> "%BUILD_DIR%\windows\install.bat"
    echo echo 🚀 Monitor NFe - ValidaTech Solutions >> "%BUILD_DIR%\windows\install.bat"
    echo echo ===================================== >> "%BUILD_DIR%\windows\install.bat"
    echo echo. >> "%BUILD_DIR%\windows\install.bat"
    echo echo Instalando Monitor NFe... >> "%BUILD_DIR%\windows\install.bat"
    echo echo. >> "%BUILD_DIR%\windows\install.bat"
    echo. >> "%BUILD_DIR%\windows\install.bat"
    echo set INSTALL_DIR=%%USERPROFILE%%\Monitor_NFe >> "%BUILD_DIR%\windows\install.bat"
    echo set START_MENU=%%APPDATA%%\Microsoft\Windows\Start Menu\Programs >> "%BUILD_DIR%\windows\install.bat"
    echo. >> "%BUILD_DIR%\windows\install.bat"
    echo echo Criando diretorio de instalacao... >> "%BUILD_DIR%\windows\install.bat"
    echo if not exist "%%INSTALL_DIR%%" mkdir "%%INSTALL_DIR%%" >> "%BUILD_DIR%\windows\install.bat"
    echo. >> "%BUILD_DIR%\windows\install.bat"
    echo echo Copiando executavel... >> "%BUILD_DIR%\windows\install.bat"
    echo copy "Monitor NFe.exe" "%%INSTALL_DIR%%\" ^>nul >> "%BUILD_DIR%\windows\install.bat"
    echo. >> "%BUILD_DIR%\windows\install.bat"
    echo echo Criando atalho no menu iniciar... >> "%BUILD_DIR%\windows\install.bat"
    echo if not exist "%%START_MENU%%" mkdir "%%START_MENU%%" >> "%BUILD_DIR%\windows\install.bat"
    echo. >> "%BUILD_DIR%\windows\install.bat"
    echo powershell -Command "& {$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%%START_MENU%%\Monitor NFe.lnk'^); $Shortcut.TargetPath = '%%INSTALL_DIR%%\Monitor NFe.exe'; $Shortcut.WorkingDirectory = '%%INSTALL_DIR%%'; $Shortcut.IconLocation = '%%INSTALL_DIR%%\Monitor NFe.exe'; $Shortcut.Save()}" >> "%BUILD_DIR%\windows\install.bat"
    echo. >> "%BUILD_DIR%\windows\install.bat"
    echo echo. >> "%BUILD_DIR%\windows\install.bat"
    echo echo ✅ Instalacao concluida! >> "%BUILD_DIR%\windows\install.bat"
    echo echo 📍 Instalado em: %%INSTALL_DIR%% >> "%BUILD_DIR%\windows\install.bat"
    echo echo 🔗 Atalho criado no Menu Iniciar >> "%BUILD_DIR%\windows\install.bat"
    echo echo. >> "%BUILD_DIR%\windows\install.bat"
    echo echo Para executar: Procure "Monitor NFe" no Menu Iniciar >> "%BUILD_DIR%\windows\install.bat"
    echo echo. >> "%BUILD_DIR%\windows\install.bat"
    echo pause >> "%BUILD_DIR%\windows\install.bat"
    
    REM Criar desinstalador
    echo @echo off > "%BUILD_DIR%\windows\uninstall.bat"
    echo title Monitor NFe - Desinstalador >> "%BUILD_DIR%\windows\uninstall.bat"
    echo echo 🗑️  Desinstalando Monitor NFe... >> "%BUILD_DIR%\windows\uninstall.bat"
    echo echo. >> "%BUILD_DIR%\windows\uninstall.bat"
    echo. >> "%BUILD_DIR%\windows\uninstall.bat"
    echo set INSTALL_DIR=%%USERPROFILE%%\Monitor_NFe >> "%BUILD_DIR%\windows\uninstall.bat"
    echo set START_MENU=%%APPDATA%%\Microsoft\Windows\Start Menu\Programs >> "%BUILD_DIR%\windows\uninstall.bat"
    echo. >> "%BUILD_DIR%\windows\uninstall.bat"
    echo if exist "%%INSTALL_DIR%%" ^( >> "%BUILD_DIR%\windows\uninstall.bat"
    echo     echo Removendo arquivos... >> "%BUILD_DIR%\windows\uninstall.bat"
    echo     rmdir /S /Q "%%INSTALL_DIR%%" >> "%BUILD_DIR%\windows\uninstall.bat"
    echo     echo ✅ Arquivos removidos >> "%BUILD_DIR%\windows\uninstall.bat"
    echo ^) else ^( >> "%BUILD_DIR%\windows\uninstall.bat"
    echo     echo ⚠️  Diretorio nao encontrado >> "%BUILD_DIR%\windows\uninstall.bat"
    echo ^) >> "%BUILD_DIR%\windows\uninstall.bat"
    echo. >> "%BUILD_DIR%\windows\uninstall.bat"
    echo if exist "%%START_MENU%%\Monitor NFe.lnk" ^( >> "%BUILD_DIR%\windows\uninstall.bat"
    echo     echo Removendo atalho... >> "%BUILD_DIR%\windows\uninstall.bat"
    echo     del "%%START_MENU%%\Monitor NFe.lnk" >> "%BUILD_DIR%\windows\uninstall.bat"
    echo     echo ✅ Atalho removido >> "%BUILD_DIR%\windows\uninstall.bat"
    echo ^) >> "%BUILD_DIR%\windows\uninstall.bat"
    echo. >> "%BUILD_DIR%\windows\uninstall.bat"
    echo echo. >> "%BUILD_DIR%\windows\uninstall.bat"
    echo echo ✅ Desinstalacao concluida! >> "%BUILD_DIR%\windows\uninstall.bat"
    echo echo. >> "%BUILD_DIR%\windows\uninstall.bat"
    echo pause >> "%BUILD_DIR%\windows\uninstall.bat"
    
    REM Criar README
    echo Monitor NFe - ValidaTech Solutions > "%BUILD_DIR%\windows\README.txt"
    echo ================================= >> "%BUILD_DIR%\windows\README.txt"
    echo. >> "%BUILD_DIR%\windows\README.txt"
    echo INSTALAÇÃO: >> "%BUILD_DIR%\windows\README.txt"
    echo 1. Execute install.bat como Administrador >> "%BUILD_DIR%\windows\README.txt"
    echo 2. Procure "Monitor NFe" no Menu Iniciar >> "%BUILD_DIR%\windows\README.txt"
    echo. >> "%BUILD_DIR%\windows\README.txt"
    echo USO: >> "%BUILD_DIR%\windows\README.txt"
    echo - Configure as pastas de monitoramento >> "%BUILD_DIR%\windows\README.txt"
    echo - Insira seu token ValidaTech >> "%BUILD_DIR%\windows\README.txt"
    echo - Inicie o monitoramento automático >> "%BUILD_DIR%\windows\README.txt"
    echo. >> "%BUILD_DIR%\windows\README.txt"
    echo SUPORTE: >> "%BUILD_DIR%\windows\README.txt"
    echo https://validatech.com.br >> "%BUILD_DIR%\windows\README.txt"
    echo. >> "%BUILD_DIR%\windows\README.txt"
    echo DESINSTALAÇÃO: >> "%BUILD_DIR%\windows\README.txt"
    echo Execute uninstall.bat >> "%BUILD_DIR%\windows\README.txt"
    
    echo ✅ Instalador criado: %BUILD_DIR%\windows\install.bat
    echo ✅ Desinstalador criado: %BUILD_DIR%\windows\uninstall.bat
    echo ✅ README criado: %BUILD_DIR%\windows\README.txt
    
    echo.
    echo 📦 Criando pacote final...
    cd /d "%BUILD_DIR%"
    
    REM Criar arquivo compactado (se 7zip estiver disponível)
    where 7z >nul 2>&1
    if not errorlevel 1 (
        7z a -tzip "Monitor_NFe_Windows_v%APP_VERSION%.zip" windows\ >nul
        echo ✅ Pacote criado: Monitor_NFe_Windows_v%APP_VERSION%.zip
    ) else (
        echo ⚠️  7zip não encontrado. Pacote manual: copie a pasta 'windows\'
    )
    
    cd /d "%SCRIPT_DIR%"
    
    echo.
    echo ═══════════════════════════════════════════════════════════════
    echo                                                               
    echo                    🎉 BUILD CONCLUÍDO! 🎉                   
    echo                                                               
    echo ═══════════════════════════════════════════════════════════════
    echo.
    echo 📁 Localização: %BUILD_DIR%\windows\
    echo 📦 Executável: Monitor NFe.exe
    echo 🛠️  Instalador: install.bat
    echo 🗑️  Desinstalador: uninstall.bat
    echo.
    echo 📋 Próximos passos:
    echo 1. Teste o executável: Monitor NFe.exe
    echo 2. Teste o instalador: install.bat
    echo 3. Distribua para usuários finais
    echo.
    echo 🌐 ValidaTech: https://validatech.com.br
    
) else (
    echo ❌ Falha no build Windows
    echo 📋 Verifique os logs acima para mais detalhes
)

echo.
pause