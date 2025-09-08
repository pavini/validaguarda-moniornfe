@echo off
title Monitor NFe - Diagnóstico Windows

echo 🔍 Monitor NFe - Diagnóstico Windows
echo ====================================
echo.

echo 📊 Informações do Sistema:
echo OS: %OS%
echo Arquitetura: %PROCESSOR_ARCHITECTURE%
echo Python: 
python --version 2>&1
echo.

echo 📁 Verificando estrutura do projeto:
if exist "monitor_nfe" (
    echo ✅ Pasta monitor_nfe encontrada
) else (
    echo ❌ Pasta monitor_nfe NÃO encontrada
)

if exist "monitor_nfe\main_refactored.py" (
    echo ✅ main_refactored.py encontrado
) else (
    echo ❌ main_refactored.py NÃO encontrado
)

echo.
echo 📦 Verificando dependências Python:
python -c "import sys; print(f'Python Path: {sys.executable}')"
echo.

echo Testando PySide6...
python -c "import PySide6; print('✅ PySide6 OK')" 2>&1 || echo "❌ PySide6 ERRO"

echo Testando watchdog...
python -c "import watchdog; print('✅ watchdog OK')" 2>&1 || echo "❌ watchdog ERRO"

echo Testando lxml...
python -c "import lxml; print('✅ lxml OK')" 2>&1 || echo "❌ lxml ERRO"

echo Testando requests...
python -c "import requests; print('✅ requests OK')" 2>&1 || echo "❌ requests ERRO"

echo.
echo 🔧 Testando importações específicas do projeto:
cd monitor_nfe

echo Testando config.dependency_container...
python -c "from config.dependency_container import DependencyContainer; print('✅ DependencyContainer OK')" 2>&1 || echo "❌ DependencyContainer ERRO"

echo Testando presentation.ui.config_dialog...
python -c "from presentation.ui.config_dialog import ConfigDialog; print('✅ ConfigDialog OK')" 2>&1 || echo "❌ ConfigDialog ERRO"

echo Testando presentation.viewmodels.main_view_model...
python -c "from presentation.viewmodels.main_view_model import MainViewModel; print('✅ MainViewModel OK')" 2>&1 || echo "❌ MainViewModel ERRO"

echo.
echo 🧪 Teste de Threading (possível causa do erro):
python -c "import threading; import multiprocessing; print(f'Threading OK - Active: {threading.active_count()}'); print(f'Multiprocessing OK - CPU count: {multiprocessing.cpu_count()}')" 2>&1

echo.
echo 🖼️  Teste básico de PySide6/Qt:
python -c "
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QThread

print('Testando QApplication...')
app = QApplication(sys.argv)
print('✅ QApplication criado')

print('Testando QThread...')
thread = QThread()
print('✅ QThread criado')

print('✅ Testes Qt básicos OK')
app.quit()
" 2>&1 || echo "❌ ERRO nos testes Qt"

cd ..

echo.
echo 📋 Resultados do diagnóstico salvos.
echo.
echo 💡 Se todos os testes passaram, o problema pode ser:
echo    1. Conflito de antivírus
echo    2. Arquivos corrompidos temporariamente  
echo    3. Permissões do Windows
echo    4. Múltiplas instâncias rodando
echo.
pause