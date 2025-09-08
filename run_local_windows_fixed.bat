@echo off
title Monitor NFe - Executar Local (Windows Corrigido)

echo 🚀 Monitor NFe - Execução Local Windows (Versão Corrigida)
echo =========================================================
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python não encontrado no PATH!
    echo.
    echo 📥 Instale Python de: https://python.org/downloads/
    echo ⚠️  Marque "Add Python to PATH" na instalação
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python %PYTHON_VERSION% encontrado

REM Verificar se está na pasta correta
if not exist "monitor_nfe" (
    echo ❌ Pasta monitor_nfe não encontrada!
    echo.
    echo 📁 Execute este arquivo na pasta raiz do projeto
    echo    (onde está a pasta monitor_nfe)
    pause
    exit /b 1
)

REM Verificar arquivo principal
if not exist "monitor_nfe\main_refactored.py" (
    echo ❌ Arquivo main_refactored.py não encontrado!
    echo.
    echo 📄 Verifique se o arquivo existe em monitor_nfe\main_refactored.py
    pause
    exit /b 1
)

echo ✅ Estrutura do projeto OK

REM Ir para pasta da aplicação
cd monitor_nfe

echo.
echo 📦 Verificando e instalando dependências Windows...

REM Instalar dependências com versões específicas para Windows
echo ⚙️  Instalando PySide6...
python -m pip install PySide6>=6.5.0 --no-warn-script-location >nul 2>&1

echo ⚙️  Instalando watchdog...
python -m pip install watchdog>=3.0.0 --no-warn-script-location >nul 2>&1

echo ⚙️  Instalando lxml...
python -m pip install --only-binary=all lxml>=4.9.0 --no-warn-script-location >nul 2>&1 || (
    echo ⚠️  Fallback: tentando instalar lxml sem restrições...
    python -m pip install lxml --no-warn-script-location >nul 2>&1
)

echo ⚙️  Instalando requests...
python -m pip install requests>=2.25.0 --no-warn-script-location >nul 2>&1

echo ⚙️  Instalando rarfile...
python -m pip install rarfile>=4.0 --no-warn-script-location >nul 2>&1

echo ✅ Dependências instaladas

echo.
echo 🔧 Definindo variáveis de ambiente Windows...

REM Definir variáveis para melhor compatibilidade Windows
set QT_QPA_PLATFORM_PLUGIN_PATH=
set QT_PLUGIN_PATH=
set PYTHONIOENCODING=utf-8
set PYTHONUNBUFFERED=1

echo ✅ Ambiente configurado

echo.
echo 🎯 Iniciando Monitor NFe (versão Windows otimizada)...
echo.
echo 💡 INSTRUÇÕES:
echo    - A interface gráfica abrirá em alguns segundos
echo    - Se aparecer aviso de firewall, permita acesso
echo    - Para parar, feche a janela da aplicação (X vermelho)
echo    - OU pressione Ctrl+C neste terminal
echo.
echo 🚨 Se der erro de 'handle' ou 'ThreadHandle':
echo    - Feche a aplicação
echo    - Execute este script novamente
echo    - Problema é temporário do Windows
echo.
echo ⏳ Aguarde...
echo.

REM Executar com configurações específicas para Windows
python -u main_refactored.py

REM Capturar código de saída
set EXIT_CODE=%ERRORLEVEL%

REM Voltar para pasta raiz
cd ..

echo.
if %EXIT_CODE% EQU 0 (
    echo ✅ Monitor NFe finalizado normalmente
) else (
    echo ⚠️  Monitor NFe finalizado com código: %EXIT_CODE%
    echo.
    echo 🔍 Possíveis causas:
    echo    - Erro de threading (problema temporário)
    echo    - Arquivo em uso por outro programa
    echo    - Permissões insuficientes
    echo    - Antivírus interferindo
    echo.
    echo 💡 Soluções:
    echo    1. Execute novamente (problemas temporários)
    echo    2. Execute como Administrador
    echo    3. Feche outros programas que usam XMLs
    echo    4. Adicione exceção no antivírus
)

echo.
pause