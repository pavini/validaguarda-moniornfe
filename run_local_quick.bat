@echo off
title Monitor NFe - Execução Rápida

REM Versão ultra-simples sem verificações
echo 🚀 Iniciando Monitor NFe...

cd monitor_nfe
python main_refactored.py
cd ..

pause