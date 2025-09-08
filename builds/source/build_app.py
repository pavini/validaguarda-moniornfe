#!/usr/bin/env python3
"""
Script para criar executável da aplicação Monitor NFe
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path

def create_executable():
    """Cria executável usando PyInstaller"""
    print("🚀 Criando executável do Monitor NFe...")
    
    # Verificar se PyInstaller está instalado
    try:
        import PyInstaller
    except ImportError:
        print("❌ PyInstaller não encontrado. Instalando...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Diretório atual
    current_dir = Path(__file__).parent
    main_script = current_dir / "main.py"
    
    if not main_script.exists():
        print("❌ main.py não encontrado!")
        return False
    
    # Comando PyInstaller para macOS
    cmd = [
        "pyinstaller",
        "--onedir",  # Uma pasta com dependências
        "--windowed",  # App sem console
        "--name=Monitor NFe",
        "--icon=logo-validatech.png" if (current_dir / "logo-validatech.png").exists() else "",
        # Incluir arquivos necessários
        "--add-data=schemas:schemas",
        "--add-data=logo-validatech.png:." if (current_dir / "logo-validatech.png").exists() else "",
        "--add-data=logo-validatech.svg:." if (current_dir / "logo-validatech.svg").exists() else "",
        # Limpar builds anteriores
        "--clean",
        str(main_script)
    ]
    
    # Remover argumentos vazios
    cmd = [arg for arg in cmd if arg]
    
    print(f"📦 Executando: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, cwd=current_dir, check=True, capture_output=True, text=True)
        print("✅ Build concluído com sucesso!")
        
        # Localizar o executável criado
        dist_path = current_dir / "dist" / "Monitor NFe"
        if dist_path.exists():
            print(f"🎯 Aplicação criada em: {dist_path}")
            
            # No macOS, mostrar instruções específicas
            if sys.platform == "darwin":
                app_path = dist_path / "Monitor NFe.app"
                if app_path.exists():
                    print(f"🍎 Aplicação macOS: {app_path}")
                    print("\n📋 Para usar:")
                    print(f"1. Abra o Finder e navegue até: {dist_path}")
                    print("2. Clique duplo em 'Monitor NFe.app'")
                    print("3. Se aparecer aviso de segurança, vá em 'Preferências do Sistema' > 'Segurança' e permita")
                else:
                    print(f"📁 Pasta da aplicação: {dist_path}")
                    print("Execute o arquivo 'Monitor NFe' dentro da pasta")
            
            return True
        else:
            print("❌ Pasta dist não encontrada após build")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro no build: {e}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False

def create_launcher_script():
    """Cria script de lançamento simples"""
    current_dir = Path(__file__).parent
    launcher_path = current_dir / "run_monitor.py"
    
    launcher_content = f'''#!/usr/bin/env python3
"""
Launcher simples para Monitor NFe
"""
import sys
import os
from pathlib import Path

# Adicionar diretório atual ao path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Executar aplicação
try:
    from main import main
    main()
except Exception as e:
    print(f"Erro ao executar aplicação: {{e}}")
    input("Pressione Enter para sair...")
'''
    
    with open(launcher_path, 'w', encoding='utf-8') as f:
        f.write(launcher_content)
    
    # Tornar executável no Unix
    if sys.platform in ['darwin', 'linux']:
        os.chmod(launcher_path, 0o755)
    
    print(f"📝 Launcher criado: {launcher_path}")
    return launcher_path

def main():
    print("🔧 Monitor NFe - Gerador de Executável")
    print("=" * 50)
    
    choice = input("""
Escolha uma opção:
1. Criar executável completo (.app no macOS) [Recomendado]
2. Criar apenas launcher simples
3. Sair

Digite sua escolha (1-3): """).strip()
    
    if choice == "1":
        success = create_executable()
        if success:
            print("\n🎉 Executável criado com sucesso!")
        else:
            print("\n❌ Falha ao criar executável")
            # Fallback para launcher
            print("\n🔄 Criando launcher como alternativa...")
            create_launcher_script()
    
    elif choice == "2":
        launcher = create_launcher_script()
        print(f"\n✅ Launcher criado: {launcher}")
        print("Para usar, execute: python3 run_monitor.py")
    
    elif choice == "3":
        print("👋 Saindo...")
        return
    
    else:
        print("❌ Opção inválida!")

if __name__ == "__main__":
    main()