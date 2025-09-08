@echo off
title Monitor NFe - Instalador Windows
echo 🚀 Monitor NFe - ValidaTech Solutions
echo =====================================
echo.
echo Instalando Monitor NFe...
echo.

set INSTALL_DIR=%USERPROFILE%\Monitor_NFe
set START_MENU=%APPDATA%\Microsoft\Windows\Start Menu\Programs

echo Criando diretorio de instalacao...
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

echo Copiando executavel...
copy "Monitor NFe.exe" "%INSTALL_DIR%\" >nul

echo Criando atalho no menu iniciar...
if not exist "%START_MENU%" mkdir "%START_MENU%"

powershell -Command "& {$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%START_MENU%\Monitor NFe.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\Monitor NFe.exe'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.IconLocation = '%INSTALL_DIR%\Monitor NFe.exe'; $Shortcut.Save()}"

echo.
echo ✅ Instalacao concluida!
echo 📍 Instalado em: %INSTALL_DIR%
echo 🔗 Atalho criado no Menu Iniciar
echo.
echo Para executar: Procure "Monitor NFe" no Menu Iniciar
echo.
pause
