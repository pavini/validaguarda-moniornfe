@echo off
title Monitor NFe - Desinstalador
echo 🗑️  Desinstalando Monitor NFe...
echo.

set INSTALL_DIR=%USERPROFILE%\Monitor_NFe
set START_MENU=%APPDATA%\Microsoft\Windows\Start Menu\Programs

if exist "%INSTALL_DIR%" (
    echo Removendo arquivos...
    rmdir /S /Q "%INSTALL_DIR%"
    echo ✅ Arquivos removidos
) else (
    echo ⚠️  Diretorio nao encontrado
)

if exist "%START_MENU%\Monitor NFe.lnk" (
    echo Removendo atalho...
    del "%START_MENU%\Monitor NFe.lnk"
    echo ✅ Atalho removido
)

echo.
echo ✅ Desinstalacao concluida!
echo.
pause
