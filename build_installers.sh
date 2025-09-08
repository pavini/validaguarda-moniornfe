#!/bin/bash

# Monitor NFe - Build Script para Instaladores Multiplataforma
# Gera executáveis para Windows, macOS e Linux

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Variáveis de configuração
APP_NAME="Monitor NFe"
APP_VERSION="1.0.0"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="$SCRIPT_DIR/builds"
SOURCE_DIR="$SCRIPT_DIR/monitor_nfe"

echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                                                              ║${NC}"
echo -e "${CYAN}║          🚀 Monitor NFe - Build Installers v$APP_VERSION          ║${NC}"
echo -e "${CYAN}║                   ValidaTech Solutions                       ║${NC}"
echo -e "${CYAN}║                                                              ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Função para detectar plataforma
detect_platform() {
    case "$(uname -s)" in
        Darwin*)    echo "macos" ;;
        Linux*)     echo "linux" ;;
        CYGWIN*|MINGW*|MSYS*) echo "windows" ;;
        *)          echo "unknown" ;;
    esac
}

# Função para verificar dependências
check_dependencies() {
    echo -e "${YELLOW}🔍 Verificando dependências...${NC}"
    
    # Python
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python 3 não encontrado!${NC}"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo -e "${GREEN}✅ Python $PYTHON_VERSION encontrado${NC}"
    
    # Verificar se está no diretório correto
    if [ ! -d "$SOURCE_DIR" ]; then
        echo -e "${RED}❌ Diretório monitor_nfe não encontrado!${NC}"
        echo -e "${RED}   Execute este script na raiz do projeto${NC}"
        exit 1
    fi
    
    if [ ! -f "$SOURCE_DIR/main.py" ]; then
        echo -e "${RED}❌ main.py não encontrado em monitor_nfe/!${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Estrutura do projeto verificada${NC}"
}

# Função para instalar dependências Python
install_python_deps() {
    echo -e "${YELLOW}📦 Instalando dependências Python...${NC}"
    
    cd "$SOURCE_DIR"
    
    # Upgrade pip
    python3 -m pip install --upgrade pip
    
    # Instalar dependências
    if [ -f "requirements.txt" ]; then
        python3 -m pip install -r requirements.txt
        echo -e "${GREEN}✅ Dependências instaladas${NC}"
    else
        echo -e "${YELLOW}⚠️  requirements.txt não encontrado, instalando dependências básicas...${NC}"
        python3 -m pip install PyInstaller PySide6 watchdog lxml requests rarfile py7zr
    fi
    
    cd "$SCRIPT_DIR"
}

# Função para criar estrutura de build
setup_build_environment() {
    echo -e "${YELLOW}🏗️  Configurando ambiente de build...${NC}"
    
    # Limpar builds anteriores
    if [ -d "$BUILD_DIR" ]; then
        echo -e "${YELLOW}🧹 Limpando builds anteriores...${NC}"
        rm -rf "$BUILD_DIR"
    fi
    
    mkdir -p "$BUILD_DIR"/{windows,macos,linux}
    
    # Copiar arquivos source
    cp -r "$SOURCE_DIR" "$BUILD_DIR/source"
    
    echo -e "${GREEN}✅ Ambiente preparado${NC}"
}

# Função para build Windows
build_windows() {
    echo -e "${BLUE}🪟 Construindo executável Windows...${NC}"
    
    cd "$BUILD_DIR/source"
    
    # Spec file para Windows
    cat > windows.spec << EOF
# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['main_refactored.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('schemas', 'schemas'),
        ('logo-validatech.png', '.'),
        ('logo-validatech.svg', '.'),
    ],
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtWidgets',
        'PySide6.QtGui',
        'watchdog.observers',
        'watchdog.events',
        'lxml.etree',
        'rarfile',
        'py7zr',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Monitor NFe.exe',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    onefile=True,
    icon='logo-validatech.png' if os.path.exists('logo-validatech.png') else None,
)
EOF
    
    # Build
    python3 -m PyInstaller windows.spec --clean --distpath="../windows" --workpath="../temp"
    
    if [ -f "../windows/Monitor NFe.exe" ]; then
        echo -e "${GREEN}✅ Build Windows concluído${NC}"
        
        # Criar installer batch
        cat > "../windows/install.bat" << 'EOF'
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
EOF
        
        # Criar desinstalador
        cat > "../windows/uninstall.bat" << 'EOF'
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
EOF
        
        # README Windows
        cat > "../windows/README.txt" << 'EOF'
Monitor NFe - ValidaTech Solutions
=================================

INSTALAÇÃO:
1. Execute install.bat como Administrador
2. Procure "Monitor NFe" no Menu Iniciar

USO:
- Configure as pastas de monitoramento
- Insira seu token ValidaTech
- Inicie o monitoramento automático

SUPORTE:
https://validatech.com.br

DESINSTALAÇÃO:
Execute uninstall.bat
EOF
        
    else
        echo -e "${RED}❌ Falha no build Windows${NC}"
        return 1
    fi
    
    cd "$SCRIPT_DIR"
}

# Função para build macOS
build_macos() {
    echo -e "${BLUE}🍎 Construindo aplicação macOS...${NC}"
    
    cd "$BUILD_DIR/source"
    
    # Spec file para macOS
    cat > macos.spec << 'EOF'
# -*- mode: python ; coding: utf-8 -*-
import sys
from pathlib import Path

a = Analysis(
    ['main_refactored.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('schemas', 'schemas'),
        ('logo-validatech.png', '.'),
        ('logo-validatech.svg', '.'),
    ],
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtWidgets', 
        'PySide6.QtGui',
        'PySide6.QtSvg',
        'PySide6.QtOpenGL',
        'shiboken6',
        'watchdog.observers',
        'watchdog.events',
        'lxml.etree',
        'rarfile',
        'py7zr',
        'requests',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Monitor NFe',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='logo-validatech.png' if Path('logo-validatech.png').exists() else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Monitor NFe',
)

app = BUNDLE(
    coll,
    name='Monitor NFe.app',
    icon='logo-validatech.png' if Path('logo-validatech.png').exists() else None,
    bundle_identifier='com.validatech.monitornfe',
    version='1.0.0',
    info_plist={
        'NSPrincipalClass': 'NSApplication',
        'NSAppleScriptEnabled': False,
        'CFBundleName': 'Monitor NFe',
        'CFBundleDisplayName': 'Monitor NFe', 
        'CFBundleGetInfoString': 'Monitor NFe - ValidaTech',
        'CFBundleIdentifier': 'com.validatech.monitornfe',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleInfoDictionaryVersion': '6.0',
        'CFBundleExecutable': 'Monitor NFe',
        'CFBundlePackageType': 'APPL',
        'NSHighResolutionCapable': True,
        'NSRequiresAquaSystemAppearance': False,
        'LSApplicationCategoryType': 'public.app-category.business',
        'LSMinimumSystemVersion': '10.14.0',
        'NSHumanReadableCopyright': 'Copyright © 2024 ValidaTech. All rights reserved.',
        'CFBundleDocumentTypes': [
            {
                'CFBundleTypeName': 'XML Files',
                'CFBundleTypeExtensions': ['xml'],
                'CFBundleTypeRole': 'Editor',
            }
        ],
    },
)
EOF
    
    # Build
    echo -e "${YELLOW}📦 Executando PyInstaller...${NC}"
    python3 -m PyInstaller macos.spec --clean --distpath="../macos" --workpath="../temp"
    
    if [ -d "../macos/Monitor NFe.app" ]; then
        echo -e "${YELLOW}🔧 Aplicando correções específicas do macOS...${NC}"
        
        # Criar arquivo de entitlements
        cat > "../macos/entitlements.plist" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>com.apple.security.cs.allow-jit</key>
    <true/>
    <key>com.apple.security.cs.allow-unsigned-executable-memory</key>
    <true/>
    <key>com.apple.security.cs.disable-library-validation</key>
    <true/>
    <key>com.apple.security.network.client</key>
    <true/>
    <key>com.apple.security.network.server</key>
    <false/>
    <key>com.apple.security.files.user-selected.read-write</key>
    <true/>
</dict>
</plist>
EOF
        
        # Definir permissões corretas
        chmod -R 755 "../macos/Monitor NFe.app"
        
        # Verificar se o executável principal existe
        if [ -f "../macos/Monitor NFe.app/Contents/MacOS/Monitor NFe" ]; then
            chmod +x "../macos/Monitor NFe.app/Contents/MacOS/Monitor NFe"
            echo -e "${GREEN}✅ Executável principal encontrado e configurado${NC}"
        else
            echo -e "${RED}❌ Executável principal não encontrado!${NC}"
            find "../macos/Monitor NFe.app" -name "*Monitor*" -type f
        fi
        
        # Remover quarentena e aplicar assinatura ad-hoc
        echo -e "${YELLOW}🔐 Configurando assinatura e segurança...${NC}"
        xattr -r -d com.apple.quarantine "../macos/Monitor NFe.app" 2>/dev/null || true
        
        # Assinatura ad-hoc com entitlements
        codesign --force --deep --sign - --entitlements "../macos/entitlements.plist" "../macos/Monitor NFe.app" 2>/dev/null || {
            echo -e "${YELLOW}⚠️  Assinatura com entitlements falhou, tentando assinatura simples...${NC}"
            codesign --force --deep --sign - "../macos/Monitor NFe.app" 2>/dev/null || {
                echo -e "${YELLOW}⚠️  Assinatura falhou, continuando...${NC}"
            }
        }
        
        echo -e "${YELLOW}🧪 Verificando aplicação...${NC}"
        if spctl -a -v "../macos/Monitor NFe.app" 2>/dev/null; then
            echo -e "${GREEN}✅ App passou na verificação de segurança${NC}"
        else
            echo -e "${YELLOW}⚠️  App não passou na verificação automática, mas deve funcionar${NC}"
        fi
        echo -e "${GREEN}✅ Build macOS concluído${NC}"
        
        # Criar installer script
        cat > "../macos/install.sh" << 'EOF'
#!/bin/bash

echo "🚀 Monitor NFe - Instalador macOS"
echo "================================="
echo ""

INSTALL_DIR="/Applications"
APP_NAME="Monitor NFe.app"

if [ -d "$APP_NAME" ]; then
    echo "📦 Instalando $APP_NAME..."
    
    # Remover versão antiga se existir
    if [ -d "$INSTALL_DIR/$APP_NAME" ]; then
        echo "🗑️  Removendo versão anterior..."
        rm -rf "$INSTALL_DIR/$APP_NAME"
    fi
    
    # Copiar nova versão
    cp -R "$APP_NAME" "$INSTALL_DIR/"
    
    # Definir permissões e remover quarentena
    chmod -R 755 "$INSTALL_DIR/$APP_NAME"
    xattr -r -d com.apple.quarantine "$INSTALL_DIR/$APP_NAME" 2>/dev/null || true
    
    echo "✅ Instalação concluída!"
    echo "📍 Instalado em: $INSTALL_DIR/$APP_NAME"
    echo ""
    echo "🔐 IMPORTANTE - Primeira execução:"
    echo "1. Abra 'Aplicações' no Finder"
    echo "2. Clique com BOTÃO DIREITO em 'Monitor NFe'"
    echo "3. Selecione 'Abrir' (não clique duplo!)"
    echo "4. Confirme 'Abrir' na janela de segurança"
    echo ""
    echo "Após a primeira execução, você pode abrir normalmente."
    echo ""
    echo "Se ainda não funcionar:"
    echo "• Vá em Preferências do Sistema > Segurança e Privacidade"  
    echo "• Clique em 'Abrir mesmo assim' ao lado de Monitor NFe"
    echo ""
else
    echo "❌ Arquivo $APP_NAME não encontrado!"
    exit 1
fi
EOF
        chmod +x "../macos/install.sh"
        
        # Criar desinstalador
        cat > "../macos/uninstall.sh" << 'EOF'
#!/bin/bash

echo "🗑️  Monitor NFe - Desinstalador macOS"
echo "===================================="
echo ""

INSTALL_DIR="/Applications"
APP_NAME="Monitor NFe.app"

if [ -d "$INSTALL_DIR/$APP_NAME" ]; then
    echo "Removendo $APP_NAME..."
    rm -rf "$INSTALL_DIR/$APP_NAME"
    echo "✅ Desinstalação concluída!"
else
    echo "⚠️  Monitor NFe não encontrado em Aplicações"
fi
EOF
        chmod +x "../macos/uninstall.sh"
        
        # README macOS
        cat > "../macos/README.md" << 'EOF'
# Monitor NFe - macOS

## Instalação
1. Execute: `./install.sh`
2. Procure "Monitor NFe" no Launchpad

## Uso
- Configure as pastas de monitoramento
- Insira seu token ValidaTech  
- Inicie o monitoramento automático

## Suporte
https://validatech.com.br

## Desinstalação
Execute: `./uninstall.sh`
EOF
        
    else
        echo -e "${RED}❌ Falha no build macOS${NC}"
        return 1
    fi
    
    cd "$SCRIPT_DIR"
}

# Função para build Linux
build_linux() {
    echo -e "${BLUE}🐧 Construindo executável Linux...${NC}"
    
    cd "$BUILD_DIR/source"
    
    # Spec file para Linux
    cat > linux.spec << EOF
# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['main_refactored.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('schemas', 'schemas'),
        ('logo-validatech.png', '.'),
        ('logo-validatech.svg', '.'),
    ],
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtWidgets',
        'PySide6.QtGui',
        'watchdog.observers',
        'watchdog.events',
        'lxml.etree',
        'rarfile',
        'py7zr',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='monitor-nfe',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='monitor-nfe',
)
EOF
    
    # Build
    python3 -m PyInstaller linux.spec --clean --distpath="../linux" --workpath="../temp"
    
    if [ -d "../linux/monitor-nfe" ]; then
        echo -e "${GREEN}✅ Build Linux concluído${NC}"
        
        # Criar script de execução
        cat > "../linux/monitor-nfe.sh" << 'EOF'
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/monitor-nfe"
./monitor-nfe "$@"
EOF
        chmod +x "../linux/monitor-nfe.sh"
        
        # Criar installer
        cat > "../linux/install.sh" << 'EOF'
#!/bin/bash

echo "🚀 Monitor NFe - Instalador Linux"
echo "================================="
echo ""

INSTALL_DIR="$HOME/.local/share/monitor-nfe"
BIN_DIR="$HOME/.local/bin"
DESKTOP_DIR="$HOME/.local/share/applications"

# Criar diretórios
mkdir -p "$INSTALL_DIR" "$BIN_DIR" "$DESKTOP_DIR"

# Copiar arquivos
echo "📦 Copiando arquivos..."
cp -R monitor-nfe/* "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/monitor-nfe"

# Criar script executável
cat > "$BIN_DIR/monitor-nfe" << EOL
#!/bin/bash
cd "$INSTALL_DIR"
./monitor-nfe "\$@"
EOL
chmod +x "$BIN_DIR/monitor-nfe"

# Criar entrada no menu
cat > "$DESKTOP_DIR/monitor-nfe.desktop" << EOL
[Desktop Entry]
Name=Monitor NFe
Comment=Monitor de validação de arquivos NFe para ValidaGuarda
Exec=$BIN_DIR/monitor-nfe
Icon=$INSTALL_DIR/logo-validatech.png
Terminal=false
Type=Application
Categories=Office;Development;
EOL

echo "✅ Instalação concluída!"
echo "📍 Instalado em: $INSTALL_DIR"
echo "🔗 Comando: monitor-nfe"
echo ""
echo "Para executar: Digite 'monitor-nfe' no terminal"
echo "             Ou procure 'Monitor NFe' no menu de aplicações"
EOF
        chmod +x "../linux/install.sh"
        
        # Criar desinstalador
        cat > "../linux/uninstall.sh" << 'EOF'
#!/bin/bash

echo "🗑️  Monitor NFe - Desinstalador Linux"
echo "===================================="
echo ""

INSTALL_DIR="$HOME/.local/share/monitor-nfe"
BIN_DIR="$HOME/.local/bin"
DESKTOP_DIR="$HOME/.local/share/applications"

# Remover arquivos
if [ -d "$INSTALL_DIR" ]; then
    rm -rf "$INSTALL_DIR"
    echo "✅ Arquivos removidos"
fi

if [ -f "$BIN_DIR/monitor-nfe" ]; then
    rm "$BIN_DIR/monitor-nfe"
    echo "✅ Comando removido"
fi

if [ -f "$DESKTOP_DIR/monitor-nfe.desktop" ]; then
    rm "$DESKTOP_DIR/monitor-nfe.desktop"
    echo "✅ Entrada do menu removida"
fi

echo ""
echo "✅ Desinstalação concluída!"
EOF
        chmod +x "../linux/uninstall.sh"
        
        # README Linux
        cat > "../linux/README.md" << 'EOF'
# Monitor NFe - Linux

## Instalação
1. Execute: `./install.sh`
2. Digite `monitor-nfe` no terminal ou procure no menu

## Uso  
- Configure as pastas de monitoramento
- Insira seu token ValidaTech
- Inicie o monitoramento automático

## Suporte
https://validatech.com.br

## Desinstalação
Execute: `./uninstall.sh`
EOF
        
    else
        echo -e "${RED}❌ Falha no build Linux${NC}"
        return 1
    fi
    
    cd "$SCRIPT_DIR"
}

# Função para criar pacotes finais
create_packages() {
    echo -e "${YELLOW}📦 Criando pacotes finais...${NC}"
    
    cd "$BUILD_DIR"
    
    # Criar README geral
    cat > README.md << 'EOF'
# Monitor NFe - ValidaTech Solutions

Instaladores multiplataforma para o Monitor NFe - Sistema de validação e envio automático de NFes para ValidaGuarda.

## 📁 Conteúdo

- **windows/**: Executável e instalador para Windows
- **macos/**: Aplicação .app e instalador para macOS  
- **linux/**: Executável e instalador para Linux

## 🚀 Instalação Rápida

### Windows
1. Acesse a pasta `windows/`
2. Execute `install.bat` como Administrador

### macOS
1. Acesse a pasta `macos/`
2. Execute `./install.sh`

### Linux
1. Acesse a pasta `linux/`
2. Execute `./install.sh`

## 📞 Suporte

**ValidaTech**: https://validatech.com.br

## 📋 Requisitos

- Windows 7+ / macOS 10.14+ / Linux (Ubuntu 18.04+)
- Conexão com internet para envio de NFes
- Token de acesso ValidaTech

---

*Monitor NFe v1.0.0 - ValidaTech Solutions*
EOF
    
    # Criar arquivo de versão
    echo "$APP_VERSION" > VERSION
    
    # Criar arquivos compactados por plataforma
    echo -e "${YELLOW}🗜️  Compactando instaladores...${NC}"
    
    if [ -d "windows" ]; then
        tar -czf "Monitor_NFe_Windows_v${APP_VERSION}.tar.gz" windows/ README.md VERSION
        echo -e "${GREEN}✅ Pacote Windows criado: Monitor_NFe_Windows_v${APP_VERSION}.tar.gz${NC}"
    fi
    
    if [ -d "macos" ]; then
        tar -czf "Monitor_NFe_macOS_v${APP_VERSION}.tar.gz" macos/ README.md VERSION
        echo -e "${GREEN}✅ Pacote macOS criado: Monitor_NFe_macOS_v${APP_VERSION}.tar.gz${NC}"
    fi
    
    if [ -d "linux" ]; then
        tar -czf "Monitor_NFe_Linux_v${APP_VERSION}.tar.gz" linux/ README.md VERSION
        echo -e "${GREEN}✅ Pacote Linux criado: Monitor_NFe_Linux_v${APP_VERSION}.tar.gz${NC}"
    fi
    
    cd "$SCRIPT_DIR"
}

# Função principal de menu
main_menu() {
    echo -e "${PURPLE}Selecione as plataformas para build:${NC}"
    echo ""
    echo "1) 🪟  Apenas Windows"
    echo "2) 🍎  Apenas macOS" 
    echo "3) 🐧  Apenas Linux"
    echo "4) 🌐  Todas as plataformas"
    echo "5) ❌  Sair"
    echo ""
    read -p "Digite sua escolha (1-5): " choice
    
    case $choice in
        1)
            echo -e "${BLUE}Construindo apenas para Windows...${NC}"
            build_windows
            ;;
        2)
            echo -e "${BLUE}Construindo apenas para macOS...${NC}"
            build_macos
            ;;
        3)
            echo -e "${BLUE}Construindo apenas para Linux...${NC}"
            build_linux
            ;;
        4)
            echo -e "${BLUE}Construindo para todas as plataformas...${NC}"
            build_windows
            build_macos  
            build_linux
            ;;
        5)
            echo -e "${YELLOW}👋 Saindo...${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Opção inválida!${NC}"
            exit 1
            ;;
    esac
}

# Script principal
main() {
    # Verificações iniciais
    check_dependencies
    install_python_deps
    setup_build_environment
    
    # Menu de seleção
    main_menu
    
    # Criar pacotes finais
    create_packages
    
    # Resumo final
    echo ""
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║                                                              ║${NC}"
    echo -e "${CYAN}║                    🎉 BUILD CONCLUÍDO! 🎉                    ║${NC}"
    echo -e "${CYAN}║                                                              ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${GREEN}📁 Localização dos builds: $BUILD_DIR${NC}"
    echo -e "${GREEN}📦 Pacotes compactados criados${NC}"
    echo -e "${GREEN}📋 READMEs de instalação incluídos${NC}"
    echo ""
    echo -e "${YELLOW}📋 Próximos passos:${NC}"
    echo -e "${YELLOW}1. Teste os instaladores em cada plataforma${NC}"
    echo -e "${YELLOW}2. Distribua os pacotes .tar.gz para usuários${NC}"
    echo -e "${YELLOW}3. Documente no site ValidaTech${NC}"
    echo ""
    echo -e "${BLUE}🌐 ValidaTech: https://validatech.com.br${NC}"
}

# Executar script principal
main "$@"