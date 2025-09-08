@echo off
title Monitor NFe - Build Windows (Sem Problemas)

echo 🚀 Monitor NFe - Build Windows Simplificado
echo ===========================================
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python não encontrado!
    echo Execute prepare_windows_fixed.bat primeiro
    pause
    exit /b 1
)

REM Verificar se dependências estão instaladas
echo 🔍 Verificando dependências...
python -c "import PyInstaller" 2>nul || (
    echo ❌ PyInstaller não instalado!
    echo Execute prepare_windows_fixed.bat primeiro
    pause
    exit /b 1
)

python -c "import PySide6" 2>nul || (
    echo ❌ PySide6 não instalado!
    echo Execute prepare_windows_fixed.bat primeiro
    pause
    exit /b 1
)

echo ✅ Dependências OK

REM Ir para pasta do projeto
if not exist "monitor_nfe" (
    echo ❌ Pasta monitor_nfe não encontrada!
    echo Execute este script na raiz do projeto
    pause
    exit /b 1
)

cd monitor_nfe

echo 🧹 Limpando builds anteriores...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "*.spec" del /q "*.spec"

echo 🔧 Criando spec file otimizado...

REM Criar spec mais simples, sem dependências problemáticas
echo # -*- mode: python ; coding: utf-8 -*- > monitor_nfe_simple.spec
echo. >> monitor_nfe_simple.spec
echo a = Analysis( >> monitor_nfe_simple.spec
echo     ['main_refactored.py'], >> monitor_nfe_simple.spec
echo     pathex=[], >> monitor_nfe_simple.spec
echo     binaries=[], >> monitor_nfe_simple.spec
echo     datas=[ >> monitor_nfe_simple.spec
echo         ('schemas', 'schemas'^) if os.path.exists('schemas'^) else None, >> monitor_nfe_simple.spec
echo     ], >> monitor_nfe_simple.spec
echo     hiddenimports=[ >> monitor_nfe_simple.spec
echo         'PySide6.QtCore', >> monitor_nfe_simple.spec
echo         'PySide6.QtWidgets', >> monitor_nfe_simple.spec
echo         'PySide6.QtGui', >> monitor_nfe_simple.spec
echo         'shiboken6', >> monitor_nfe_simple.spec
echo         'watchdog.observers', >> monitor_nfe_simple.spec
echo         'watchdog.events', >> monitor_nfe_simple.spec
echo         'lxml.etree', >> monitor_nfe_simple.spec
echo         'requests', >> monitor_nfe_simple.spec
echo     ], >> monitor_nfe_simple.spec
echo     hookspath=[], >> monitor_nfe_simple.spec
echo     runtime_hooks=[], >> monitor_nfe_simple.spec
echo     excludes=['py7zr', 'matplotlib', 'numpy'], >> monitor_nfe_simple.spec
echo     win_no_prefer_redirects=False, >> monitor_nfe_simple.spec
echo     win_private_assemblies=False, >> monitor_nfe_simple.spec
echo     cipher=None, >> monitor_nfe_simple.spec
echo     noarchive=False, >> monitor_nfe_simple.spec
echo ^) >> monitor_nfe_simple.spec
echo. >> monitor_nfe_simple.spec
echo # Remove None entries >> monitor_nfe_simple.spec
echo a.datas = [x for x in a.datas if x is not None] >> monitor_nfe_simple.spec
echo. >> monitor_nfe_simple.spec
echo pyz = PYZ(a.pure, a.zipped_data, cipher=None^) >> monitor_nfe_simple.spec
echo. >> monitor_nfe_simple.spec
echo exe = EXE( >> monitor_nfe_simple.spec
echo     pyz, >> monitor_nfe_simple.spec
echo     a.scripts, >> monitor_nfe_simple.spec
echo     a.binaries, >> monitor_nfe_simple.spec
echo     a.zipfiles, >> monitor_nfe_simple.spec
echo     a.datas, >> monitor_nfe_simple.spec
echo     [], >> monitor_nfe_simple.spec
echo     name='Monitor NFe', >> monitor_nfe_simple.spec
echo     debug=False, >> monitor_nfe_simple.spec
echo     bootloader_ignore_signals=False, >> monitor_nfe_simple.spec
echo     strip=False, >> monitor_nfe_simple.spec
echo     upx=False, >> monitor_nfe_simple.spec
echo     runtime_tmpdir=None, >> monitor_nfe_simple.spec
echo     console=False, >> monitor_nfe_simple.spec
echo     disable_windowed_traceback=False, >> monitor_nfe_simple.spec
echo     target_arch=None, >> monitor_nfe_simple.spec
echo     codesign_identity=None, >> monitor_nfe_simple.spec
echo     entitlements_file=None, >> monitor_nfe_simple.spec
echo ^) >> monitor_nfe_simple.spec

echo 🔨 Construindo executável (aguarde 2-5 minutos)...
echo    ⏳ Isso pode demorar, seja paciente...
echo.

python -m PyInstaller monitor_nfe_simple.spec --clean --noconfirm

if exist "dist\Monitor NFe.exe" (
    echo.
    echo ✅ BUILD CONCLUÍDO COM SUCESSO!
    echo.
    
    REM Verificar tamanho
    for %%A in ("dist\Monitor NFe.exe") do set size=%%~zA
    set /a sizeMB=!size!/1048576
    echo 📊 Tamanho do executável: !sizeMB! MB
    
    REM Criar pasta de distribuição
    if not exist "..\dist_windows_final" mkdir "..\dist_windows_final"
    copy "dist\Monitor NFe.exe" "..\dist_windows_final\" >nul
    
    REM Criar launcher
    echo @echo off > "..\dist_windows_final\Iniciar Monitor NFe.bat"
    echo title Monitor NFe - ValidaTech >> "..\dist_windows_final\Iniciar Monitor NFe.bat"
    echo echo 🚀 Iniciando Monitor NFe... >> "..\dist_windows_final\Iniciar Monitor NFe.bat"
    echo echo    Aguarde a interface abrir... >> "..\dist_windows_final\Iniciar Monitor NFe.bat"
    echo start "" "Monitor NFe.exe" >> "..\dist_windows_final\Iniciar Monitor NFe.bat"
    echo timeout /t 2 >nul >> "..\dist_windows_final\Iniciar Monitor NFe.bat"
    
    REM Criar README final
    echo Monitor NFe - ValidaTech Solutions > "..\dist_windows_final\LEIA-ME.txt"
    echo ================================= >> "..\dist_windows_final\LEIA-ME.txt"
    echo. >> "..\dist_windows_final\LEIA-ME.txt"
    echo COMO USAR: >> "..\dist_windows_final\LEIA-ME.txt"
    echo 1. Clique duplo em "Monitor NFe.exe" >> "..\dist_windows_final\LEIA-ME.txt"
    echo 2. OU use "Iniciar Monitor NFe.bat" >> "..\dist_windows_final\LEIA-ME.txt"
    echo. >> "..\dist_windows_final\LEIA-ME.txt"
    echo CONFIGURACAO: >> "..\dist_windows_final\LEIA-ME.txt"
    echo - Configure pasta de monitoramento >> "..\dist_windows_final\LEIA-ME.txt"
    echo - Insira token ValidaTech >> "..\dist_windows_final\LEIA-ME.txt"
    echo - Inicie monitoramento automatico >> "..\dist_windows_final\LEIA-ME.txt"
    echo. >> "..\dist_windows_final\LEIA-ME.txt"
    echo SUPORTE ARQUIVOS: >> "..\dist_windows_final\LEIA-ME.txt"
    echo ✅ XML (NFe individuais) >> "..\dist_windows_final\LEIA-ME.txt"
    echo ✅ ZIP (arquivos compactados) >> "..\dist_windows_final\LEIA-ME.txt"
    echo ✅ RAR (arquivos compactados) >> "..\dist_windows_final\LEIA-ME.txt"
    echo ❌ 7Z (não suportado nesta versão) >> "..\dist_windows_final\LEIA-ME.txt"
    echo. >> "..\dist_windows_final\LEIA-ME.txt"
    echo SUPORTE: https://validatech.com.br >> "..\dist_windows_final\LEIA-ME.txt"
    
    echo 📁 Arquivos criados em: ..\dist_windows_final\
    echo    📄 Monitor NFe.exe (executável principal)
    echo    📄 Iniciar Monitor NFe.bat (launcher)
    echo    📄 LEIA-ME.txt (instruções)
    echo.
    echo 🎉 PRONTO PARA DISTRIBUIÇÃO!
    echo.
    echo 🧪 Para testar: Execute "Monitor NFe.exe"
    echo.
    
) else (
    echo.
    echo ❌ ERRO NO BUILD!
    echo.
    echo 🔍 Possíveis causas:
    echo 1. Dependências não instaladas corretamente
    echo 2. Antivírus bloqueando PyInstaller
    echo 3. Falta de espaço em disco
    echo 4. Arquivos corrompidos
    echo.
    echo 💡 Soluções:
    echo 1. Execute prepare_windows_fixed.bat novamente
    echo 2. Desative antivírus temporariamente
    echo 3. Libere espaço em disco (mín. 500MB)
    echo 4. Reinicie o computador e tente novamente
    echo.
)

cd ..
echo.
pause