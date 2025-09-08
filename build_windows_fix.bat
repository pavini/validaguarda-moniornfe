@echo off
title Monitor NFe - Build Windows (Fixed)

echo 🚀 Monitor NFe - Build Windows (Versao Corrigida)
echo ==================================================
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python não encontrado!
    pause
    exit /b 1
)

echo ✅ Python encontrado

REM Ir para pasta do projeto
if not exist "monitor_nfe" (
    echo ❌ Pasta monitor_nfe não encontrada!
    pause
    exit /b 1
)

cd monitor_nfe

echo 🧹 Limpando cache e builds anteriores...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "__pycache__" rmdir /s /q "__pycache__"
if exist "*.spec" del /q "*.spec"

echo 📦 Atualizando PyInstaller...
python -m pip install --upgrade pip >nul 2>&1
python -m pip install --upgrade pyinstaller >nul 2>&1

echo 🔧 Criando spec file customizado...

REM Criar spec file com configurações específicas para evitar o erro
echo # -*- mode: python ; coding: utf-8 -*- > monitor_nfe_fixed.spec
echo import sys >> monitor_nfe_fixed.spec
echo import os >> monitor_nfe_fixed.spec
echo from PyInstaller.utils.hooks import collect_all >> monitor_nfe_fixed.spec
echo. >> monitor_nfe_fixed.spec
echo # Collect all PySide6 data >> monitor_nfe_fixed.spec
echo pyside6_datas, pyside6_binaries, pyside6_hiddenimports = collect_all('PySide6') >> monitor_nfe_fixed.spec
echo. >> monitor_nfe_fixed.spec
echo a = Analysis( >> monitor_nfe_fixed.spec
echo     ['main_refactored.py'], >> monitor_nfe_fixed.spec
echo     pathex=[], >> monitor_nfe_fixed.spec
echo     binaries=pyside6_binaries, >> monitor_nfe_fixed.spec
echo     datas=pyside6_datas + [ >> monitor_nfe_fixed.spec
echo         ('schemas', 'schemas'^) if os.path.exists('schemas'^) else None, >> monitor_nfe_fixed.spec
echo         ('logo-validatech.png', '.'^) if os.path.exists('logo-validatech.png'^) else None, >> monitor_nfe_fixed.spec
echo     ], >> monitor_nfe_fixed.spec
echo     hiddenimports=pyside6_hiddenimports + [ >> monitor_nfe_fixed.spec
echo         'shiboken6', >> monitor_nfe_fixed.spec
echo         'PySide6.QtCore', >> monitor_nfe_fixed.spec
echo         'PySide6.QtWidgets', >> monitor_nfe_fixed.spec
echo         'PySide6.QtGui', >> monitor_nfe_fixed.spec
echo         'watchdog.observers', >> monitor_nfe_fixed.spec
echo         'watchdog.events', >> monitor_nfe_fixed.spec
echo         'lxml.etree', >> monitor_nfe_fixed.spec
echo         'requests', >> monitor_nfe_fixed.spec
echo         'rarfile', >> monitor_nfe_fixed.spec
echo         'py7zr', >> monitor_nfe_fixed.spec
echo     ], >> monitor_nfe_fixed.spec
echo     hookspath=[], >> monitor_nfe_fixed.spec
echo     hooksconfig={}, >> monitor_nfe_fixed.spec
echo     runtime_hooks=[], >> monitor_nfe_fixed.spec
echo     excludes=[], >> monitor_nfe_fixed.spec
echo     win_no_prefer_redirects=False, >> monitor_nfe_fixed.spec
echo     win_private_assemblies=False, >> monitor_nfe_fixed.spec
echo     cipher=None, >> monitor_nfe_fixed.spec
echo     noarchive=False, >> monitor_nfe_fixed.spec
echo ^) >> monitor_nfe_fixed.spec
echo. >> monitor_nfe_fixed.spec
echo # Filter out None values from datas >> monitor_nfe_fixed.spec
echo a.datas = [x for x in a.datas if x is not None] >> monitor_nfe_fixed.spec
echo. >> monitor_nfe_fixed.spec
echo pyz = PYZ(a.pure, a.zipped_data, cipher=None^) >> monitor_nfe_fixed.spec
echo. >> monitor_nfe_fixed.spec
echo exe = EXE( >> monitor_nfe_fixed.spec
echo     pyz, >> monitor_nfe_fixed.spec
echo     a.scripts, >> monitor_nfe_fixed.spec
echo     a.binaries, >> monitor_nfe_fixed.spec
echo     a.zipfiles, >> monitor_nfe_fixed.spec
echo     a.datas, >> monitor_nfe_fixed.spec
echo     [], >> monitor_nfe_fixed.spec
echo     name='Monitor NFe', >> monitor_nfe_fixed.spec
echo     debug=False, >> monitor_nfe_fixed.spec
echo     bootloader_ignore_signals=False, >> monitor_nfe_fixed.spec
echo     strip=False, >> monitor_nfe_fixed.spec
echo     upx=False, >> monitor_nfe_fixed.spec
echo     upx_exclude=[], >> monitor_nfe_fixed.spec
echo     runtime_tmpdir=None, >> monitor_nfe_fixed.spec
echo     console=False, >> monitor_nfe_fixed.spec
echo     disable_windowed_traceback=False, >> monitor_nfe_fixed.spec
echo     argv_emulation=False, >> monitor_nfe_fixed.spec
echo     target_arch=None, >> monitor_nfe_fixed.spec
echo     codesign_identity=None, >> monitor_nfe_fixed.spec
echo     entitlements_file=None, >> monitor_nfe_fixed.spec
echo ^) >> monitor_nfe_fixed.spec

echo 🔨 Construindo executável (pode demorar alguns minutos)...
python -m PyInstaller monitor_nfe_fixed.spec --clean --noconfirm

if exist "dist\Monitor NFe.exe" (
    echo.
    echo ✅ Build concluído com sucesso!
    echo 📁 Executável criado: dist\Monitor NFe.exe
    
    REM Verificar tamanho
    for %%A in ("dist\Monitor NFe.exe") do set size=%%~zA
    set /a sizeMB=!size!/1048576
    echo 📊 Tamanho: !sizeMB! MB
    
    REM Criar pasta de distribuição
    if not exist "..\dist_windows_fixed" mkdir "..\dist_windows_fixed"
    copy "dist\Monitor NFe.exe" "..\dist_windows_fixed\" >nul
    
    REM Criar launcher alternativo
    echo @echo off > "..\dist_windows_fixed\Executar Monitor NFe.bat"
    echo title Monitor NFe >> "..\dist_windows_fixed\Executar Monitor NFe.bat"
    echo echo Iniciando Monitor NFe... >> "..\dist_windows_fixed\Executar Monitor NFe.bat"
    echo start "" "Monitor NFe.exe" >> "..\dist_windows_fixed\Executar Monitor NFe.bat"
    
    REM Criar README
    echo Monitor NFe - ValidaTech Solutions > "..\dist_windows_fixed\LEIA-ME.txt"
    echo ================================= >> "..\dist_windows_fixed\LEIA-ME.txt"
    echo. >> "..\dist_windows_fixed\LEIA-ME.txt"
    echo COMO EXECUTAR: >> "..\dist_windows_fixed\LEIA-ME.txt"
    echo 1. Clique duplo em "Monitor NFe.exe" >> "..\dist_windows_fixed\LEIA-ME.txt"
    echo 2. OU use "Executar Monitor NFe.bat" >> "..\dist_windows_fixed\LEIA-ME.txt"
    echo. >> "..\dist_windows_fixed\LEIA-ME.txt"
    echo Se aparecer erro de DLL: >> "..\dist_windows_fixed\LEIA-ME.txt"
    echo - Instale Visual C++ Redistributable >> "..\dist_windows_fixed\LEIA-ME.txt"
    echo - Baixe de: https://aka.ms/vs/17/release/vc_redist.x64.exe >> "..\dist_windows_fixed\LEIA-ME.txt"
    echo. >> "..\dist_windows_fixed\LEIA-ME.txt"
    echo SUPORTE: https://validatech.com.br >> "..\dist_windows_fixed\LEIA-ME.txt"
    
    echo.
    echo 📁 Arquivos copiados para: ..\dist_windows_fixed\
    echo 🎉 Pronto para distribuição!
    echo.
    echo ⚠️  Se der erro de DLL, instale:
    echo    Visual C++ Redistributable 2015-2022
    echo    https://aka.ms/vs/17/release/vc_redist.x64.exe
    
) else (
    echo.
    echo ❌ Erro no build!
    echo.
    echo 🔍 Possíveis soluções:
    echo 1. Instale Visual C++ Redistributable
    echo 2. Atualize Python para versão mais recente
    echo 3. Use ambiente virtual limpo
    echo 4. Verifique se antivírus não está bloqueando
    echo.
    echo 📋 Log de erro acima pode ter mais detalhes
)

cd ..
echo.
pause