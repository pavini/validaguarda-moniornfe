#!/usr/bin/env python3
import sys
import os
import platform
from pathlib import Path
from datetime import datetime
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, 
                               QHBoxLayout, QWidget, QPushButton, QLabel, 
                               QTableWidget, QTableWidgetItem, QFileDialog,
                               QLineEdit, QMessageBox, QHeaderView, QDialog,
                               QFormLayout, QGroupBox, QMenuBar, QMenu)
from PySide6.QtCore import QThread, Signal, QTimer
from PySide6.QtGui import QFont, QColor
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from lxml import etree
# from signxml import XMLVerifier  # Not needed since we simplified signature validation
import zipfile
import tempfile
import shutil
import os
import json
import requests
import base64
import locale
import threading
import queue
from concurrent.futures import ThreadPoolExecutor, as_completed
from PySide6.QtCore import QSettings

# Set Brazilian locale for date/time formatting
try:
    locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_TIME, 'pt_BR')
    except:
        pass  # Keep default if Brazilian locale not available


class ConfigManager:
    def __init__(self):
        self.settings = QSettings("ValidateCh", "MonitorNFe")
        self.config = self.load_config()
    
    def load_config(self):
        """Load configuration from settings"""
        config = {
            'monitor_folder': self.settings.value('monitor_folder', ''),
            'output_folder': self.settings.value('output_folder', ''),
            'token': self.settings.value('token', ''),
            'auto_organize': self.settings.value('auto_organize', True, type=bool),
            'log_level': self.settings.value('log_level', 'INFO'),
        }
        return config
    
    def save_config(self):
        """Save configuration to settings"""
        for key, value in self.config.items():
            self.settings.setValue(key, value)
        self.settings.sync()
    
    def get(self, key, default=None):
        """Get configuration value"""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """Set configuration value"""
        self.config[key] = value
        self.save_config()
    
    def ensure_output_folders(self):
        """Create output folder structure if it doesn't exist"""
        if not self.config['output_folder']:
            return False
        
        try:
            base_path = Path(self.config['output_folder'])
            folders = ['processed', 'errors', 'logs']
            
            for folder in folders:
                folder_path = base_path / folder
                folder_path.mkdir(parents=True, exist_ok=True)
            
            return True
        except Exception as e:
            print(f"Erro ao criar estrutura de pastas: {e}")
            return False


class ConfigDialog(QDialog):
    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.setWindowTitle("Configurações")
        self.setModal(True)
        self.resize(500, 400)
        self.setup_ui()
        self.load_current_config()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Monitoring Configuration Group
        monitor_group = QGroupBox("Monitoramento")
        monitor_layout = QFormLayout(monitor_group)
        
        # Monitor folder
        monitor_folder_layout = QHBoxLayout()
        self.monitor_folder_input = QLineEdit()
        self.monitor_folder_input.setPlaceholderText("Pasta para monitorar arquivos XML/ZIP (incluindo subpastas)...")
        monitor_browse_btn = QPushButton("Procurar")
        monitor_browse_btn.clicked.connect(self.browse_monitor_folder)
        monitor_folder_layout.addWidget(self.monitor_folder_input)
        monitor_folder_layout.addWidget(monitor_browse_btn)
        monitor_layout.addRow("Pasta de Monitoramento:", monitor_folder_layout)
        
        # Output folder
        output_folder_layout = QHBoxLayout()
        self.output_folder_input = QLineEdit()
        self.output_folder_input.setPlaceholderText("Pasta para arquivos processados, erros e logs...")
        output_browse_btn = QPushButton("Procurar")
        output_browse_btn.clicked.connect(self.browse_output_folder)
        output_folder_layout.addWidget(self.output_folder_input)
        output_folder_layout.addWidget(output_browse_btn)
        monitor_layout.addRow("Pasta de Saída:", output_folder_layout)
        
        layout.addWidget(monitor_group)
        
        # Options Group
        options_group = QGroupBox("Opções")
        options_layout = QFormLayout(options_group)
        
        from PySide6.QtWidgets import QCheckBox
        self.auto_organize_check = QCheckBox("Organizar arquivos automaticamente")
        self.auto_organize_check.setToolTip("Move arquivos processados para pastas 'processed' ou 'errors'")
        options_layout.addRow("", self.auto_organize_check)
        
        layout.addWidget(options_group)
        
        # API Configuration Group
        api_group = QGroupBox("Configuração da API")
        api_layout = QFormLayout(api_group)
        
        self.token_input = QLineEdit()
        self.token_input.setPlaceholderText("Token de acesso para API...")
        self.token_input.setEchoMode(QLineEdit.EchoMode.Password)
        api_layout.addRow("Token de Acesso:", self.token_input)
        
        # Show/Hide token button and test API
        token_buttons_layout = QHBoxLayout()
        show_token_btn = QPushButton("Mostrar/Ocultar Token")
        show_token_btn.clicked.connect(self.toggle_token_visibility)
        token_buttons_layout.addWidget(show_token_btn)
        
        test_api_btn = QPushButton("Testar API")
        test_api_btn.clicked.connect(self.test_api_connection)
        token_buttons_layout.addWidget(test_api_btn)
        
        api_layout.addRow("", token_buttons_layout)
        
        layout.addWidget(api_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Salvar")
        save_btn.clicked.connect(self.save_config)
        save_btn.setDefault(True)
        
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        
        test_folders_btn = QPushButton("Testar Pastas")
        test_folders_btn.clicked.connect(self.test_folders)
        
        button_layout.addWidget(test_folders_btn)
        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def load_current_config(self):
        """Load current configuration into form"""
        self.monitor_folder_input.setText(self.config_manager.get('monitor_folder', ''))
        self.output_folder_input.setText(self.config_manager.get('output_folder', ''))
        self.token_input.setText(self.config_manager.get('token', ''))
        self.auto_organize_check.setChecked(self.config_manager.get('auto_organize', True))
    
    def browse_monitor_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Selecionar Pasta de Monitoramento")
        if folder:
            self.monitor_folder_input.setText(folder)
    
    def browse_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Selecionar Pasta de Saída")
        if folder:
            self.output_folder_input.setText(folder)
    
    def toggle_token_visibility(self):
        if self.token_input.echoMode() == QLineEdit.EchoMode.Password:
            self.token_input.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.token_input.setEchoMode(QLineEdit.EchoMode.Password)
    
    def test_api_connection(self):
        """Test API connection with current token"""
        # Save current token temporarily for testing
        current_token = self.token_input.text().strip()
        if not current_token:
            QMessageBox.warning(self, "Token Necessário", "Por favor, insira um token antes de testar.")
            return
        
        # Update config temporarily for testing
        original_token = self.config_manager.get('token', '')
        self.config_manager.set('token', current_token)
        
        try:
            api_client = ValidaNFeAPI(self.config_manager)
            result = api_client.test_connection()
            
            if result['success']:
                QMessageBox.information(self, "Teste da API", f"✅ {result['message']}")
            else:
                QMessageBox.warning(self, "Teste da API", f"✗ {result['message']}")
                
        except Exception as e:
            QMessageBox.critical(self, "Erro no Teste", f"Erro ao testar API: {e}")
        finally:
            # Restore original token
            self.config_manager.set('token', original_token)
    
    def test_folders(self):
        """Test if folders are accessible and create structure"""
        monitor_folder = self.monitor_folder_input.text().strip()
        output_folder = self.output_folder_input.text().strip()
        
        issues = []
        
        # Check for folder overlap to prevent infinite loops
        if monitor_folder and output_folder:
            monitor_path = Path(monitor_folder).resolve()
            output_path = Path(output_folder).resolve()
            
            # Check if paths are the same or one is inside the other
            if monitor_path == output_path:
                issues.append("✗ Pasta de monitoramento não pode ser igual à pasta de saída")
            elif monitor_path in output_path.parents:
                issues.append("✗ Pasta de saída não pode estar dentro da pasta de monitoramento")
            elif output_path in monitor_path.parents:
                issues.append("✗ Pasta de monitoramento não pode estar dentro da pasta de saída")
        
        if monitor_folder:
            if not Path(monitor_folder).exists():
                issues.append(f"Pasta de monitoramento não existe: {monitor_folder}")
            elif not os.access(monitor_folder, os.R_OK):
                issues.append(f"Sem permissão de leitura na pasta: {monitor_folder}")
        else:
            issues.append("Pasta de monitoramento não especificada")
        
        if output_folder:
            try:
                output_path = Path(output_folder)
                output_path.mkdir(parents=True, exist_ok=True)
                
                # Test write permission
                test_file = output_path / 'test_write.tmp'
                test_file.write_text('test')
                test_file.unlink()
                
                # Create folder structure
                folders = ['processed', 'errors', 'logs']
                for folder in folders:
                    (output_path / folder).mkdir(exist_ok=True)
                
            except Exception as e:
                issues.append(f"Erro na pasta de saída: {e}")
        else:
            issues.append("Pasta de saída não especificada")
        
        if issues:
            QMessageBox.warning(self, "Problemas Encontrados", "\n".join(issues))
        else:
            QMessageBox.information(self, "Teste Concluído", 
                                   "✅ Todas as pastas estão configuradas corretamente!\n\n"
                                   "Estrutura criada:\n"
                                   f"📁 {output_folder}/processed/\n"
                                   f"📁 {output_folder}/errors/\n"
                                   f"📁 {output_folder}/logs/")
    
    def save_config(self):
        """Save configuration"""
        monitor_folder = self.monitor_folder_input.text().strip()
        output_folder = self.output_folder_input.text().strip()
        
        # Validate folders to prevent infinite loops
        if monitor_folder and output_folder:
            monitor_path = Path(monitor_folder).resolve()
            output_path = Path(output_folder).resolve()
            
            if monitor_path == output_path:
                QMessageBox.critical(self, "Erro", "Pasta de monitoramento não pode ser igual à pasta de saída!")
                return
            elif monitor_path in output_path.parents:
                QMessageBox.critical(self, "Erro", "Pasta de saída não pode estar dentro da pasta de monitoramento!")
                return
            elif output_path in monitor_path.parents:
                QMessageBox.critical(self, "Erro", "Pasta de monitoramento não pode estar dentro da pasta de saída!")
                return
        
        self.config_manager.set('monitor_folder', monitor_folder)
        self.config_manager.set('output_folder', output_folder)
        self.config_manager.set('token', self.token_input.text().strip())
        self.config_manager.set('auto_organize', self.auto_organize_check.isChecked())
        
        # Ensure output folder structure
        self.config_manager.ensure_output_folders()
        
        self.accept()


class NFEHandler(FileSystemEventHandler):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback
        self.recently_handled = set()
        import time
        self.time = time
        self.last_handled = {}  # Track when each file was last handled
    
    def _should_process_file(self, file_path):
        """Determine if file should be processed (avoid duplicate events)"""
        current_time = self.time.time()
        
        # Only process if we haven't handled this file in the last 2 seconds
        if file_path in self.last_handled:
            time_since_last = current_time - self.last_handled[file_path]
            if time_since_last < 2.0:  # 2 second cooldown
                return False
        
        self.last_handled[file_path] = current_time
        return True
    
    def on_created(self, event):
        if not event.is_directory:
            print(f"🔍 Arquivo detectado: {event.src_path}")
            if (event.src_path.endswith('.xml') or 
                event.src_path.endswith(('.zip', '.rar', '.7z'))):
                print(f"📄 Arquivo válido para processamento: {event.src_path}")
                if self._should_process_file(event.src_path):
                    print(f"✅ Processando arquivo: {event.src_path}")
                    self.callback(event.src_path)
                else:
                    print(f"⏸️  Arquivo ignorado (cooldown): {event.src_path}")
            else:
                print(f"🚫 Arquivo ignorado (tipo inválido): {event.src_path}")
    
    def on_modified(self, event):
        # Only process modification events for archives (they might be being written)
        if not event.is_directory:
            print(f"🔄 Arquivo modificado: {event.src_path}")
            if event.src_path.endswith(('.zip', '.rar', '.7z')):
                print(f"📦 Arquivo compactado modificado: {event.src_path}")
                if self._should_process_file(event.src_path):
                    print(f"✅ Processando arquivo modificado: {event.src_path}")
                    self.callback(event.src_path)
                else:
                    print(f"⏸️  Arquivo modificado ignorado (cooldown): {event.src_path}")


class ArchiveExtractor:
    def __init__(self):
        self.temp_dirs = []
    
    def extract_archive(self, archive_path, max_depth=3):
        """Extract archive recursively and return list of XML files found"""
        xml_files = []
        
        try:
            if max_depth <= 0:
                return xml_files
            
            # Create temporary directory
            temp_dir = tempfile.mkdtemp(prefix="nfe_extract_")
            self.temp_dirs.append(temp_dir)
            
            extracted_files = self._extract_single_archive(archive_path, temp_dir)
            
            for extracted_file in extracted_files:
                file_path = Path(extracted_file)
                
                if file_path.suffix.lower() == '.xml':
                    xml_files.append(str(file_path))
                elif file_path.suffix.lower() in ['.zip', '.rar', '.7z']:
                    # Recursive extraction
                    nested_xml_files = self.extract_archive(str(file_path), max_depth - 1)
                    xml_files.extend(nested_xml_files)
            
        except Exception as e:
            print(f"Erro ao extrair arquivo {archive_path}: {e}")
        
        return xml_files
    
    def _extract_single_archive(self, archive_path, extract_to):
        """Extract a single archive file"""
        extracted_files = []
        archive_path = Path(archive_path)
        
        try:
            if archive_path.suffix.lower() == '.zip':
                with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_to)
                    for root, dirs, files in os.walk(extract_to):
                        for file in files:
                            extracted_files.append(os.path.join(root, file))
            
            elif archive_path.suffix.lower() == '.rar':
                try:
                    import rarfile
                    with rarfile.RarFile(archive_path, 'r') as rar_ref:
                        rar_ref.extractall(extract_to)
                        for root, dirs, files in os.walk(extract_to):
                            for file in files:
                                extracted_files.append(os.path.join(root, file))
                except ImportError:
                    print("⚠️ rarfile não instalado - arquivos RAR serão ignorados")
                except Exception as e:
                    print(f"⚠️ Erro ao extrair RAR: {e}")
            
            elif archive_path.suffix.lower() == '.7z':
                try:
                    import py7zr
                    with py7zr.SevenZipFile(archive_path, mode="r") as z:
                        z.extractall(path=extract_to)
                        for root, dirs, files in os.walk(extract_to):
                            for file in files:
                                extracted_files.append(os.path.join(root, file))
                except ImportError:
                    print("⚠️ py7zr não instalado - arquivos 7Z serão ignorados")
                except Exception as e:
                    print(f"⚠️ Erro ao extrair 7Z: {e}")
        
        except Exception as e:
            print(f"Erro na extração: {e}")
        
        return extracted_files
    
    def cleanup(self):
        """Clean up temporary directories"""
        for temp_dir in self.temp_dirs:
            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                print(f"Erro ao limpar diretório temporário: {e}")
        self.temp_dirs.clear()


class XMLValidator:
    def __init__(self):
        self.schemas = {}
        self.load_schemas()
    
    def load_schemas(self):
        print("=" * 60)
        print("🔧 INICIANDO CARREGAMENTO DE SCHEMAS XSD")
        print("=" * 60)
        schema_count = 0
        
        try:
            schema_dir = Path(__file__).parent / 'schemas'
            print(f"   Diretório de schemas: {schema_dir}")
            
            if not schema_dir.exists():
                print(f"❌ Diretório de schemas não existe!")
                return
            
            # List all XSD files
            xsd_files = list(schema_dir.glob('*.xsd'))
            print(f"   Arquivos XSD encontrados: {len(xsd_files)}")
            for xsd_file in xsd_files:
                print(f"      - {xsd_file.name}")
            
            # Load NFe schema
            nfe_schema_path = schema_dir / 'leiauteNFe_v4.00.xsd'
            print(f"   Carregando schema NFe: {nfe_schema_path}")
            
            if nfe_schema_path.exists():
                try:
                    with open(nfe_schema_path, 'r', encoding='utf-8') as f:
                        schema_doc = etree.parse(f)
                    self.schemas['nfe'] = etree.XMLSchema(schema_doc)
                    schema_count += 1
                    print("   ✅ Schema NFe carregado com sucesso!")
                except Exception as e:
                    print(f"   ❌ Erro ao carregar schema NFe: {e}")
            else:
                print("   ⚠️  Arquivo leiauteNFe_v4.00.xsd não encontrado")
            
            # Load procNFe schema  
            proc_schema_path = schema_dir / 'procNFe_v4.00.xsd'
            print(f"   Carregando schema procNFe: {proc_schema_path}")
            
            if proc_schema_path.exists():
                try:
                    with open(proc_schema_path, 'r', encoding='utf-8') as f:
                        proc_doc = etree.parse(f)
                    self.schemas['procNFe'] = etree.XMLSchema(proc_doc)
                    schema_count += 1
                    print("   ✅ Schema procNFe carregado com sucesso!")
                except Exception as e:
                    print(f"   ❌ Erro ao carregar schema procNFe: {e}")
            else:
                print("   ⚠️  Arquivo procNFe_v4.00.xsd não encontrado")
            
            # Summary
            print("=" * 60)
            print(f"📊 RESUMO DO CARREGAMENTO DE SCHEMAS:")
            print(f"   Schemas carregados: {schema_count}/2")
            print(f"   Tipos disponíveis: {list(self.schemas.keys())}")
            
            if schema_count == 0:
                print("🚨 ERRO CRÍTICO: Nenhum schema foi carregado - validação não funcionará!")
                print("🚨 XMLs serão marcados como inválidos automaticamente!")
            elif schema_count < 2:
                print("⚠️  ATENÇÃO: Alguns schemas faltam - validação pode falhar para alguns tipos")
            else:
                print("✅ SUCESSO: Todos os schemas carregados com sucesso!")
                print("✅ Validação XSD está funcionando corretamente!")
            print("=" * 60)
                
        except Exception as e:
            print(f"❌ Erro crítico ao carregar schemas: {e}")
            import traceback
            traceback.print_exc()
    
    def detect_xml_type(self, xml_path):
        """Detect if XML is NFe or procNFe based on root element"""
        print(f"🔍 Detectando tipo XML para: {xml_path}")
        
        # Try different encodings
        encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
        
        for encoding in encodings:
            try:
                print(f"   Tentando encoding: {encoding}")
                
                # Try to parse with specific encoding
                with open(xml_path, 'r', encoding=encoding) as f:
                    content = f.read()
                
                # Parse XML
                tree = etree.fromstring(content.encode('utf-8'))
                
                # Get root tag without namespace
                root_tag = tree.tag.split('}')[-1] if '}' in tree.tag else tree.tag
                
                print(f"   Tag root encontrada: '{root_tag}'")
                print(f"   Tag completa: '{tree.tag}'")
                
                # Determine type
                if root_tag == 'nfeProc':
                    print(f"✅ Tipo detectado: procNFe")
                    return 'procNFe'
                elif root_tag == 'NFe':
                    print(f"✅ Tipo detectado: nfe")
                    return 'nfe'
                else:
                    print(f"⚠️  Tag root desconhecida: '{root_tag}'")
                    # Check if it contains NFe elements
                    if 'nfe' in root_tag.lower() or 'NFe' in content:
                        print(f"   Contém NFe no conteúdo, assumindo nfeProc")
                        return 'procNFe'
                    continue
                    
            except UnicodeDecodeError:
                print(f"   ❌ Encoding {encoding} falhou")
                continue
            except etree.XMLSyntaxError as e:
                print(f"   ❌ Erro XML com {encoding}: {str(e)[:100]}...")
                continue
            except Exception as e:
                print(f"   ❌ Erro geral com {encoding}: {str(e)[:100]}...")
                continue
        
        # If all encodings failed, try one more approach
        try:
            print("   🔄 Última tentativa: leitura binária...")
            with open(xml_path, 'rb') as f:
                content = f.read()
            
            # Try to detect from content
            content_str = content.decode('utf-8', errors='ignore')
            if '<nfeProc' in content_str:
                print("✅ Detectado nfeProc por conteúdo")
                return 'procNFe'
            elif '<NFe' in content_str:
                print("✅ Detectado NFe por conteúdo")
                return 'nfe'
                
        except Exception as e:
            print(f"   ❌ Última tentativa falhou: {e}")
        
        print(f"❌ Tipo XML não identificado para: {xml_path}")
        return 'unknown'
    
    def download_schema(self, schema_path):
        try:
            import urllib.request
            url = "https://raw.githubusercontent.com/TadaSoftware/PyNFe/main/pynfe/data/XSDs/NF-e/leiauteNFe_v4.00.xsd"
            print("Baixando schema NFe v4.00...")
            urllib.request.urlretrieve(url, schema_path)
            print("Schema baixado com sucesso!")
        except Exception as e:
            print(f"Erro ao baixar schema: {e}")
    
    def validate_structure(self, xml_path):
        print(f"🔍 Validando estrutura XML: {xml_path}")
        
        try:
            # IMPORTANTE: Log crítico para debug
            print(f"⚠️  DEBUG: Verificando schemas disponíveis...")
            print(f"   self.schemas = {self.schemas}")
            print(f"   Número de schemas: {len(self.schemas) if self.schemas else 0}")
            print(f"   Tipos disponíveis: {list(self.schemas.keys()) if self.schemas else 'NENHUM'}")
            
            if not self.schemas:
                print("❌ PROBLEMA CRÍTICO: Nenhum schema carregado!")
                print("❌ Tentando recarregar schemas...")
                self.load_schemas()  # Tentar recarregar
                
                if not self.schemas:
                    print("❌ FALHA: Schemas ainda não carregados após tentativa de recarga")
                    return "⚠️  Schemas não encontrados - validação desabilitada"
                else:
                    print("✅ SUCESSO: Schemas recarregados com sucesso!")
                    
            if not self.schemas:
                print("❌ Nenhum schema carregado!")
                return "⚠️  Schemas não encontrados"
            
            print(f"   Schemas disponíveis: {list(self.schemas.keys())}")
            
            # Detect XML type
            xml_type = self.detect_xml_type(xml_path)
            print(f"   Tipo detectado: {xml_type}")
            
            if xml_type == 'unknown':
                print("❌ Tipo XML não reconhecido - não é possível validar")
                return f"Schema não encontrado para tipo: {xml_type}"
            
            if xml_type not in self.schemas:
                print(f"❌ Schema para tipo '{xml_type}' não está carregado")
                print(f"   Tipos disponíveis: {list(self.schemas.keys())}")
                return f"Schema não encontrado para tipo: {xml_type}"
            
            print(f"   Usando schema para tipo: {xml_type}")
            schema = self.schemas[xml_type]
            
            # Parse XML with different encoding attempts
            xml_doc = None
            parse_error = None
            encodings = ['utf-8', 'latin-1', 'iso-8859-1']
            
            for encoding in encodings:
                try:
                    print(f"   Tentando parsing com encoding: {encoding}")
                    with open(xml_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    xml_doc = etree.fromstring(content.encode('utf-8'))
                    print(f"   ✅ Parsing com {encoding} bem-sucedido!")
                    break
                except Exception as e:
                    parse_error = e
                    print(f"   ❌ Parsing com {encoding} falhou: {str(e)[:50]}...")
                    continue
            
            if xml_doc is None:
                print(f"❌ Falha em todos os encodings")
                return f"Erro de parsing XML ✗: {str(parse_error)[:100]}..."
            
            # Validate against schema
            print(f"   Executando validação contra schema...")
            if schema.validate(xml_doc):
                print(f"✅ Validação bem-sucedida!")
                return f"XML ✅ ({xml_type})"
            else:
                errors = [str(error) for error in schema.error_log]
                print(f"❌ Validação falhou - {len(errors)} erro(s)")
                for i, error in enumerate(errors[:3]):  # Show first 3 errors
                    print(f"   Erro {i+1}: {error}")
                return f"XML ✗ ({xml_type}): {'; '.join(errors[:1])}"
                
        except Exception as e:
            print(f"❌ Erro crítico na validação: {str(e)}")
            import traceback
            traceback.print_exc()
            return f"Erro na validação ✗: {str(e)[:100]}..."
    
    def validate_signature(self, xml_path):
        """
        Simplified signature validation - just checks if signature element exists.
        Full validation is done by the API.
        """
        try:
            # Check if file exists and is readable
            if not Path(xml_path).exists():
                return "Arquivo não encontrado ✗"
            
            # Try parsing with better error handling  
            try:
                xml_doc = etree.parse(xml_path)
            except etree.XMLSyntaxError as e:
                return f"XML mal formado ✗: {str(e)[:30]}..."
            except Exception as e:
                return f"Erro ao ler arquivo ✗: {str(e)[:30]}..."
            
            # Check if signature element exists
            signature_elements = xml_doc.xpath("//ds:Signature", 
                                             namespaces={'ds': 'http://www.w3.org/2000/09/xmldsig#'})
            
            if not signature_elements:
                return "Nenhuma assinatura encontrada ✗"
            else:
                return "Assinatura presente ✅"
                    
        except Exception as e:
            return f"Erro na verificação ✗: {str(e)[:40]}..."
    
    # COMMENTED: Full signature validation - uncomment if needed
    """
    def validate_signature_full(self, xml_path):
        try:
            # Check if file exists and is readable
            if not Path(xml_path).exists():
                return "Arquivo não encontrado ✗"
            
            # Try parsing with better error handling  
            try:
                xml_doc = etree.parse(xml_path)
            except etree.XMLSyntaxError as e:
                return f"XML mal formado ✗: {str(e)[:30]}..."
            except Exception as e:
                return f"Erro ao ler arquivo ✗: {str(e)[:30]}..."
            
            # Check if signature element exists
            signature_elements = xml_doc.xpath("//ds:Signature", 
                                             namespaces={'ds': 'http://www.w3.org/2000/09/xmldsig#'})
            
            if not signature_elements:
                return "Nenhuma assinatura encontrada ✗"
            
            # For NFe, we'll do a basic validation since RSA-SHA1 is commonly used but restricted
            try:
                # Try standard verification first
                verifier = XMLVerifier()
                verified = verifier.verify(xml_doc)
                return "Assinatura válida ✅"
            except Exception as e:
                error_msg = str(e).lower()
                
                # Handle RSA-SHA1 specifically (common in Brazilian NFe)
                if "rsa_sha1" in error_msg or "forbidden" in error_msg or "sha1" in error_msg:
                    # Check if signature structure is present and well-formed
                    try:
                        cert_elements = xml_doc.xpath("//ds:X509Certificate", 
                                                    namespaces={'ds': 'http://www.w3.org/2000/09/xmldsig#'})
                        if cert_elements and len(cert_elements[0].text.strip()) > 100:
                            return "Assinatura ✅ (RSA-SHA1)"
                        else:
                            return "Assinatura malformada ✗"
                    except Exception:
                        return "Assinatura ⚠️ (não validável)"
                
                # Handle other signature errors
                elif "certificate" in error_msg:
                    return "Certificado inválido ✗"
                elif "digest" in error_msg or "hash" in error_msg:
                    return "Hash inválido ✗"
                else:
                    return f"Assinatura inválida ✗: {error_msg[:30]}..."
                    
        except Exception as e:
            return f"Erro na verificação ✗: {str(e)[:40]}..."
    """


class ValidaNFeAPI:
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.base_url = "https://api.validanfe.com"
        self.guarda_endpoint = "/GuardaNFe/EnviarXml"
        
    def send_nfe(self, xml_file_path):
        """Send NFe file to ValidaNFe API"""
        try:
            token = self.config_manager.get('token', '')
            if not token:
                return {"success": False, "message": "Token não configurado"}
            
            # Check if file exists
            file_path = Path(xml_file_path)
            if not file_path.exists():
                return {"success": False, "message": f"Arquivo não encontrado: {file_path.name}"}
            
            # Read XML file with better error handling
            try:
                xml_content = file_path.read_text(encoding='utf-8')
            except UnicodeDecodeError:
                try:
                    # Try with latin-1 encoding if utf-8 fails
                    xml_content = file_path.read_text(encoding='latin-1')
                except Exception as e:
                    return {"success": False, "message": f"Erro de encoding: {str(e)[:50]}..."}
            except Exception as e:
                return {"success": False, "message": f"Erro na leitura: {str(e)[:50]}..."}
            
            # Validate XML content
            if not xml_content or len(xml_content.strip()) < 10:
                return {"success": False, "message": "Arquivo XML vazio ou muito pequeno"}
            
            # Basic XML validation - must start with <?xml and contain <NFe or <nfeProc
            xml_stripped = xml_content.strip()
            if not xml_stripped.startswith('<?xml'):
                return {"success": False, "message": "Arquivo não é um XML válido (sem declaração XML)"}
            
            if '<NFe' not in xml_content and '<nfeProc' not in xml_content:
                return {"success": False, "message": "Arquivo não parece ser uma NFe válida"}
            
            # Extract NFe key from XML if possible
            nfe_chave = self._extract_nfe_key(xml_content)
            
            # Prepare headers (ValidaNFe uses X-API-KEY with multipart/form-data)
            headers = {
                'X-API-KEY': token
                # Don't set Content-Type - let requests set it for multipart
            }
            
            # Prepare multipart form data (like .NET example)
            files = {
                'xmlFile': (file_path.name, xml_content, 'application/xml')
            }
            
            # Make API request
            url = f"{self.base_url}{self.guarda_endpoint}"
            
            # Log API request details for debugging
            print(f"API Request: {url}")
            print(f"Headers: {{'X-API-KEY': '[TOKEN]'}}")
            print(f"Sending as multipart/form-data with xmlFile field")
            print(f"XML content length: {len(xml_content)} chars")
            print(f"XML starts with: {xml_content[:100]}...")
            print(f"NFe key: {nfe_chave[:20]}..." if nfe_chave else "NFe key: (não encontrada)")
            
            # Check file size
            if len(xml_content) > 5 * 1024 * 1024:  # 5MB limit
                return {"success": False, "message": "Arquivo muito grande (limite 5MB)"}
            
            # Try with retry logic for temporary server errors
        response = self._make_request_with_retry(url, files, headers)
            
            # Log response for debugging
            print(f"API Response: {response.status_code}")
            if response.status_code != 200:
                print(f"Response text: {response.text[:200]}...")
            
            # Handle response
            if response.status_code == 200:
                try:
                    result = response.json()
                    return {
                        "success": True, 
                        "message": "Enviado ✅",
                        "data": result
                    }
                except Exception:
                    return {"success": True, "message": "Enviado com sucesso [OK] (resposta não-JSON)"}
            elif response.status_code == 401:
                return {"success": False, "message": "Token inválido/expirado ✗"}
            elif response.status_code == 400:
                try:
                    error_text = response.text
                    return {"success": False, "message": f"Validação falhou: {error_text[:100]}..."}
                except:
                    return {"success": False, "message": "Erro 400: Dados inválidos"}
            elif response.status_code == 404:
                return {"success": False, "message": "Endpoint não encontrado (404) - Verifique a URL da API"}
            elif response.status_code == 409:
                return {"success": True, "message": "NFe já existe ⚠️"}
            elif response.status_code == 429:
                return {"success": False, "message": "API sobrecarregada - tente novamente ⏰"}
            elif response.status_code == 500:
                return {"success": False, "message": "Erro interno do servidor (500)"}
            elif response.status_code == 502:
                return {"success": False, "message": "Bad Gateway (502) - Servidor indisponível temporariamente ⏰"}
            elif response.status_code == 503:
                return {"success": False, "message": "Service Unavailable (503) - Servidor sobrecarregado temporariamente ⏰"}
            elif response.status_code == 504:
                return {"success": False, "message": "Gateway Timeout (504) - Timeout no servidor ⏰"}
            else:
                try:
                    error_text = response.text[:100]
                    return {"success": False, "message": f"HTTP {response.status_code}: {error_text}..."}
                except:
                    return {"success": False, "message": f"Erro HTTP {response.status_code}"}
                
        except requests.exceptions.Timeout:
            return {"success": False, "message": "Timeout na API ⏰"}
        except requests.exceptions.ConnectionError as e:
            error_msg = str(e)
            if "Name or service not known" in error_msg or "nodename nor servname provided" in error_msg:
                return {"success": False, "message": "DNS não resolveu. Verifique a URL da API 🌐"}
            elif "Connection refused" in error_msg:
                return {"success": False, "message": "Conexão recusada pelo servidor 🔌"}
            else:
                return {"success": False, "message": f"Erro de conexão: {str(e)[:50]}... 🔌"}
        except requests.exceptions.RequestException as e:
            return {"success": False, "message": f"Erro HTTP: {str(e)[:50]}..."}
        except Exception as e:
            error_msg = str(e)
            print(f"❌ ERRO INESPERADO no send_nfe: {error_msg}")
            import traceback
            print("📋 Traceback completo:")
            traceback.print_exc()
            return {"success": False, "message": f"Erro inesperado: {error_msg[:100]}..."}
    
    def _make_request_with_retry(self, url, files, headers, max_retries=3):
        """Make HTTP request with retry logic for temporary server errors"""
        import time
        
        for attempt in range(max_retries + 1):
            try:
                print(f"🌐 Tentativa {attempt + 1}/{max_retries + 1} - Enviando para API...")
                response = requests.post(url, files=files, headers=headers, timeout=30)
                
                # If success or permanent error, return immediately
                if response.status_code < 500 or response.status_code in [500]:
                    return response
                
                # If temporary error (502, 503, 504) and not last attempt, retry
                if response.status_code in [502, 503, 504] and attempt < max_retries:
                    wait_time = (2 ** attempt)  # Exponential backoff: 1s, 2s, 4s
                    print(f"⏰ HTTP {response.status_code} - Aguardando {wait_time}s antes de tentar novamente...")
                    print(f"   Motivo: {response.text[:100] if response.text else 'Servidor indisponível'}")
                    time.sleep(wait_time)
                    continue
                
                return response
                
            except requests.exceptions.Timeout:
                if attempt < max_retries:
                    wait_time = (2 ** attempt)
                    print(f"⏰ Timeout - Tentando novamente em {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    raise
            
            except requests.exceptions.ConnectionError as e:
                if attempt < max_retries and ("connection" in str(e).lower() or "reset" in str(e).lower()):
                    wait_time = (2 ** attempt)
                    print(f"⏰ Erro de conexão - Tentando novamente em {wait_time}s...")
                    print(f"   Motivo: {str(e)[:100]}")
                    time.sleep(wait_time)
                    continue
                else:
                    raise
        
        # Should not reach here
        return response

    def _extract_nfe_key(self, xml_content):
        """Extract NFe key from XML content"""
        try:
            # Try to extract chNFe from XML
            import re
            # Look for chNFe tag
            match = re.search(r'<chNFe>([^<]+)</chNFe>', xml_content)
            if match:
                return match.group(1)
            
            # Alternative: look for Id attribute
            match = re.search(r'Id="NFe(\d{44})"', xml_content)
            if match:
                return match.group(1)
                
            # Alternative: try to extract from infNFe Id
            match = re.search(r'<infNFe.*?Id="NFe(\d{44})"', xml_content)
            if match:
                return match.group(1)
                
            return ""
        except Exception:
            return ""
    
    def test_connection(self):
        """Test API connection and token validity"""
        try:
            token = self.config_manager.get('token', '')
            if not token:
                return {"success": False, "message": "Token não configurado"}
            
            headers = {
                'X-API-KEY': token,
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            
            # Test basic connectivity to the API base URL
            test_url = f"{self.base_url}/status"  # Try a status endpoint if available
            try:
                response = requests.get(test_url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    return {"success": True, "message": "Conexão OK ✅"}
                elif response.status_code == 401:
                    return {"success": False, "message": "Token inválido ✗"}
                elif response.status_code == 404:
                    # Endpoint not found, but connection works
                    return {"success": True, "message": "Conectado (endpoint teste não disponível) ⚠️"}
                else:
                    return {"success": False, "message": f"HTTP {response.status_code}"}
            except requests.exceptions.ConnectionError:
                return {"success": False, "message": "Erro de conexão 🔌"}
            except requests.exceptions.Timeout:
                return {"success": False, "message": "Timeout na conexão ⏰"}
                
        except Exception as e:
            error_msg = str(e)
            print(f"❌ ERRO INESPERADO no send_nfe: {error_msg}")
            import traceback
            print("📋 Traceback completo:")
            traceback.print_exc()
            return {"success": False, "message": f"Erro inesperado: {error_msg[:100]}..."}


class ParallelAPIManager:
    def __init__(self, api_client, organizer):
        self.api_client = api_client
        self.organizer = organizer
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.file_locks = {}  # Dictionary to track files being processed
        self.lock = threading.Lock()  # Lock for the file_locks dictionary
        
    def add_to_queue(self, xml_file, structure_status, signature_status, callback=None):
        """Add file to parallel processing queue"""
        xml_path = Path(xml_file)
        
        # Check if file is already being processed
        with self.lock:
            if str(xml_path) in self.file_locks:
                print(f"File already being processed: {xml_path.name}")
                return
            
            # Mark file as being processed
            self.file_locks[str(xml_path)] = True
        
        # Submit to thread pool
        future = self.executor.submit(
            self._process_file_parallel, 
            xml_file, structure_status, signature_status, callback
        )
        
        # Clean up lock when done
        future.add_done_callback(lambda f: self._cleanup_file_lock(str(xml_path)))
    
    def _process_file_parallel(self, xml_file, structure_status, signature_status, callback=None):
        """Process a single file in parallel thread"""
        try:
            xml_path = Path(xml_file)
            
            # Double-check file still exists (might have been moved by another thread)
            if not xml_path.exists():
                print(f"File no longer exists: {xml_path.name}")
                return
            
            # Determine if file should be sent to API
            is_valid = self._is_file_valid(structure_status, signature_status)
            
            # Send to API if valid and token is configured
            if is_valid and self.api_client:
                token = self.api_client.config_manager.get('token', '')
                if token:
                    try:
                        # Make sure file still exists before API call
                        if xml_path.exists():
                            api_result = self.api_client.send_nfe(str(xml_path))
                            api_status = api_result['message']
                            
                            # Log API result with full details
                            print(f"🔍 API Response for {xml_path.name}:")
                            print(f"   Success: {api_result.get('success', 'N/A')}")
                            print(f"   Message: {api_result.get('message', 'N/A')}")
                            if 'data' in api_result:
                                print(f"   Data: {api_result['data']}")
                            print("-" * 50)
                            
                            self._log_api_result(xml_path, api_result)
                        else:
                            api_status = "Arquivo não encontrado para API"
                    except Exception as e:
                        error_msg = str(e)
                        print(f"❌ ERRO CRÍTICO NA API: {error_msg}")
                        import traceback
                        print("📋 Traceback completo:")
                        traceback.print_exc()
                        api_status = f"Erro API: {error_msg[:100]}..."
                else:
                    api_status = "Token não configurado"
            elif not is_valid:
                # Log why file is invalid
                print(f"⚠️  Arquivo {xml_path.name} não foi enviado - Motivos:")
                print(f"   Estrutura XML: {structure_status}")
                print(f"   Assinatura Digital: {signature_status}")
                print("-" * 50)
                api_status = "Não enviado - Arquivo inválido"
            else:
                api_status = "API não configurada"
            
            # Organize file AFTER API processing (with another existence check)
            moved = False
            if self.organizer and self.organizer.config_manager.get('auto_organize', True):
                try:
                    if xml_path.exists():  # Final check before moving
                        moved = self.organizer.organize_file(str(xml_path), structure_status, signature_status)
                    else:
                        print(f"File disappeared before organization: {xml_path.name}")
                except Exception as e:
                    print(f"Erro ao organizar: {e}")
            
            # Call callback with results (for UI update)
            if callback:
                callback(xml_path.name, structure_status, signature_status, api_status, moved)
                
        except Exception as e:
            print(f"Erro no processamento paralelo: {e}")
    
    def _cleanup_file_lock(self, file_path):
        """Clean up file lock when processing is complete"""
        with self.lock:
            self.file_locks.pop(file_path, None)
    
    def _is_file_valid(self, structure_status, signature_status):
        """Check if file passed validation"""
        structure_ok = "✅" in structure_status
        signature_ok = "✅" in signature_status
        
        # Debug validation logic
        print(f"🔍 Validando arquivo:")
        print(f"   Estrutura: '{structure_status}' -> {structure_ok}")
        print(f"   Assinatura: '{signature_status}' -> {signature_ok}")
        print(f"   Resultado final: {structure_ok and signature_ok}")
        print("-" * 50)
        
        return structure_ok and signature_ok
    
    def _log_api_result(self, file_path, api_result):
        """Log API result to file"""
        try:
            # This should match the existing logging logic
            timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            status = "SUCCESS" if api_result.get('success', False) else "ERROR"
            
            print(f"{timestamp} | API {status} | {file_path.name}")
            print(f"  Mensagem: {api_result.get('message', 'N/A')}")
        except Exception as e:
            print(f"Erro no log da API: {e}")
    
    def shutdown(self):
        """Shutdown the thread pool gracefully"""
        try:
            print("Encerrando processamento paralelo...")
            # Cancel pending futures
            self.executor._threads.clear() if hasattr(self.executor, '_threads') else None
            # Shutdown with timeout
            self.executor.shutdown(wait=True)
            print("✅ Processamento paralelo encerrado")
        except Exception as e:
            print(f"Erro no shutdown do executor: {e}")
            # Force shutdown
            try:
                import threading
                for thread in threading.enumerate():
                    if thread != threading.current_thread() and hasattr(thread, '_target'):
                        print(f"Forçando encerramento da thread: {thread.name}")
            except:
                pass


class FileOrganizer:
    def __init__(self, config_manager):
        self.config_manager = config_manager
        
    def organize_file(self, file_path, structure_status, signature_status):
        """Organize file based on validation results"""
        try:
            file_path = Path(file_path)
            output_base = Path(self.config_manager.get('output_folder', ''))
            
            if not output_base or not output_base.exists():
                return False
            
            # Determine if file is successful or has errors
            is_success = self._is_successful(structure_status, signature_status)
            
            if is_success:
                target_folder = output_base / 'processed'
            else:
                target_folder = output_base / 'errors'
            
            # Create target folder if needed
            target_folder.mkdir(parents=True, exist_ok=True)
            
            # Get target file (will overwrite if exists)
            target_file = self._get_target_filename(target_folder, file_path.name)
            
            # Remove existing file if it exists
            if target_file.exists():
                target_file.unlink()
            
            # Move file
            shutil.move(str(file_path), str(target_file))
            
            # Log the movement
            self._log_file_movement(file_path, target_file, is_success, structure_status, signature_status)
            
            return True
            
        except Exception as e:
            print(f"Erro ao organizar arquivo {file_path}: {e}")
            return False
    
    def _is_successful(self, structure_status, signature_status):
        """Determine if validation was successful"""
        structure_ok = "válida ✅" in structure_status
        signature_ok = ("válida ✅" in signature_status or 
                       "presente ✅" in signature_status)
        
        return structure_ok and signature_ok
    
    def _get_target_filename(self, target_folder, filename):
        """Get target filename (overwrite if exists)"""
        return target_folder / filename
    
    def _log_file_movement(self, source, target, success, structure_status, signature_status):
        """Log file movement to logs folder"""
        try:
            logs_folder = Path(self.config_manager.get('output_folder', '')) / 'logs'
            logs_folder.mkdir(parents=True, exist_ok=True)
            
            log_file = logs_folder / f"file_movements_{datetime.now().strftime('%Y%m%d')}.log"
            
            with open(log_file, 'a', encoding='utf-8') as f:
                timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                status = "SUCCESS" if success else "ERROR"
                
                f.write(f"{timestamp} | {status} | {source.name} -> {target.name}\n")
                f.write(f"  Estrutura: {structure_status}\n")
                f.write(f"  Assinatura: {signature_status}\n")
                f.write(f"  Caminho: {target}\n\n")
                
        except Exception as e:
            print(f"Erro ao criar log: {e}")


class MonitorThread(QThread):
    file_processed = Signal(str, str, str, str, str)  # Added API status
    
    def __init__(self, watch_path, config_manager=None):
        super().__init__()
        self.watch_path = watch_path
        self.config_manager = config_manager
        self.observer = None
        self.validator = XMLValidator()
        self.extractor = ArchiveExtractor()
        self.organizer = FileOrganizer(config_manager) if config_manager else None
        self.api_client = ValidaNFeAPI(config_manager) if config_manager else None
        # Initialize parallel API manager
        self.parallel_api = ParallelAPIManager(self.api_client, self.organizer) if (self.api_client and self.organizer) else None
        self.running = False
        
        # Track processed files to prevent duplicates
        self.processed_files = set()
        self.processing_files = set()  # Files currently being processed
    
    def run(self):
        self.running = True
        print(f"🚀 Iniciando monitoramento da pasta: {self.watch_path}")
        
        # Process existing files first
        self.process_existing_files()
        
        # Then start monitoring for new/changed files
        self.observer = Observer()
        handler = NFEHandler(self.process_file)
        self.observer.schedule(handler, self.watch_path, recursive=True)
        self.observer.start()
        print(f"👁️  Observer iniciado - monitorando recursivamente: {self.watch_path}")
        print(f"📊 Observer ativo: {self.observer.is_alive()}")
        
        while self.running:
            self.msleep(100)
    
    def process_existing_files(self):
        """Process XML and archive files that already exist in the watch folder"""
        try:
            import glob
            import os
            
            # Find all XML files in the watch path (including subdirectories)
            xml_pattern = os.path.join(self.watch_path, "**", "*.xml")
            xml_files = glob.glob(xml_pattern, recursive=True)
            
            # Find all archive files
            archive_patterns = ["*.zip", "*.rar", "*.7z"]
            archive_files = []
            for pattern in archive_patterns:
                archive_pattern = os.path.join(self.watch_path, "**", pattern)
                archive_files.extend(glob.glob(archive_pattern, recursive=True))
            
            # Process XML files
            for xml_file in xml_files:
                if self.running:  # Check if still running
                    self.process_file(xml_file)
                    self.msleep(50)  # Small delay to avoid overwhelming the UI
            
            # Process archive files
            for archive_file in archive_files:
                if self.running:  # Check if still running
                    self.process_file(archive_file)
                    self.msleep(100)  # Longer delay for archive processing
                    
        except Exception as e:
            print(f"Erro ao processar arquivos existentes: {e}")
    
    def stop(self):
        print("🛑 Parando monitoramento...")
        self.running = False
        if self.observer:
            print(f"📊 Observer estava ativo: {self.observer.is_alive()}")
            self.observer.stop()
            self.observer.join()
            print("👁️  Observer parado e finalizado")
        # Shutdown parallel processing
        if self.parallel_api:
            self.parallel_api.shutdown()
            print("🔧 Parallel API desligado")
        # Clean up temporary files
        self.extractor.cleanup()
        print("🧹 Limpeza de arquivos temporários concluída")
        
    def clear_processed_files_cache(self):
        """Clear the cache of processed files (useful when restarting monitoring)"""
        print(f"🗑️  Limpando cache de arquivos processados ({len(self.processed_files)} arquivos)")
        self.processed_files.clear()
        self.processing_files.clear()
        print("✅ Cache limpo - arquivos podem ser reprocessados")
    
    def process_file(self, file_path):
        file_path = Path(file_path)
        file_key = str(file_path.resolve())  # Use absolute path as key
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        # Skip if file is in output folders to prevent infinite loops
        if self._is_in_output_folders(file_path):
            return
        
        # Skip if file is already processed or being processed
        if file_key in self.processed_files or file_key in self.processing_files:
            return
        
        # Mark file as being processed
        self.processing_files.add(file_key)
        
        try:
            # Check if it's an archive file
            if file_path.suffix.lower() in ['.zip', '.rar', '.7z']:
                self.process_archive_file(file_path, timestamp)
            else:
                # Process XML file
                self.process_xml_file(file_path, timestamp)
        finally:
            # Remove from processing set and mark as processed
            self.processing_files.discard(file_key)
            self.processed_files.add(file_key)
    
    def _is_in_output_folders(self, file_path):
        """Check if file is in output folders to prevent infinite loops"""
        if not self.config_manager:
            return False
        
        output_folder = self.config_manager.get('output_folder', '')
        if not output_folder:
            return False
        
        try:
            file_path_resolved = file_path.resolve()
            output_path_resolved = Path(output_folder).resolve()
            
            # Check if file is in output folder or any of its subfolders
            return output_path_resolved in file_path_resolved.parents or file_path_resolved.parent == output_path_resolved
        except Exception:
            return False
    
    def process_archive_file(self, archive_path, timestamp):
        """Process archive file and extract XML files"""
        try:
            archive_name = archive_path.name
            
            # Extract XML files from archive
            xml_files = self.extractor.extract_archive(str(archive_path))
            
            if not xml_files:
                # Move archive to errors folder if no XMLs found and auto_organize is enabled
                no_xml_message = "Nenhum XML encontrado"
                
                if self.organizer and self.organizer.config_manager.get('auto_organize', True):
                    try:
                        output_base = Path(self.organizer.config_manager.get('output_folder', ''))
                        errors_folder = output_base / 'errors'
                        errors_folder.mkdir(parents=True, exist_ok=True)
                        
                        # Get target for archive in errors folder
                        archive_target = self.organizer._get_target_filename(errors_folder, archive_path.name)
                        
                        # Remove existing file if it exists
                        if archive_target.exists():
                            archive_target.unlink()
                        
                        # Move the archive file to errors
                        shutil.move(str(archive_path), str(archive_target))
                        no_xml_message = "Nenhum XML encontrado - Arquivo movido para erros"
                        
                        # Log the archive movement
                        self.organizer._log_file_movement(
                            archive_path, 
                            archive_target, 
                            False,  # Error case - no XMLs
                            "Nenhum XML encontrado", 
                            "Arquivo vazio"
                        )
                        
                    except Exception as move_error:
                        print(f"Erro ao mover arquivo sem XML {archive_path}: {move_error}")
                        no_xml_message = "Nenhum XML encontrado - Erro ao mover arquivo"
                
                self.file_processed.emit(
                    archive_name, 
                    no_xml_message, 
                    "N/A", 
                    timestamp,
                    "N/A"
                )
                return
            
            # Process each extracted XML
            for i, xml_file in enumerate(xml_files):
                if not self.running:
                    break
                
                try:
                    xml_name = f"{archive_name}[{Path(xml_file).name}]"
                    structure_status = self.validator.validate_structure(xml_file)
                    signature_status = self.validator.validate_signature(xml_file)
                    
                    # Check if valid for API submission
                    is_valid = self._is_file_valid(structure_status, signature_status)
                    
                    # Send to API if valid and token is configured
                    if is_valid and self.api_client:
                        token = self.api_client.config_manager.get('token', '')
                        if token:
                            try:
                                # Read XML content before organizing (to avoid file movement issues)
                                xml_path = Path(xml_file)
                                if xml_path.exists():
                                    xml_content_backup = xml_path.read_text(encoding='utf-8', errors='ignore')
                                    api_result = self.api_client.send_nfe(xml_file)
                                    api_status = api_result['message']
                                    self._log_api_result(xml_path, api_result)
                                else:
                                    api_status = "Arquivo não encontrado para API"
                            except Exception as e:
                                api_status = f"Erro API: {str(e)[:30]}..."
                        else:
                            api_status = "Token não configurado"
                    elif not is_valid:
                        api_status = "Não enviado - Arquivo inválido"
                    else:
                        api_status = "API não configurada"
                    
                    # Organize extracted XML if organizer is available and auto_organize is enabled
                    moved = False
                    if self.organizer and self.organizer.config_manager.get('auto_organize', True):
                        try:
                            # Create a copy of the extracted file in output folder for organization
                            xml_path = Path(xml_file)
                            temp_xml_path = Path(self.organizer.config_manager.get('monitor_folder', '')) / xml_path.name
                            
                            # Copy to monitor folder temporarily for organization
                            shutil.copy2(str(xml_path), str(temp_xml_path))
                            
                            if self.organizer.organize_file(temp_xml_path, structure_status, signature_status):
                                moved = True
                                
                        except Exception as e:
                            print(f"Erro ao organizar XML extraído {xml_file}: {e}")
                    
                    # Emit result to UI (only once)
                    if moved:
                        moved_status = "✅ Extraído e processado" if self.organizer._is_successful(structure_status, signature_status) else "✗ Extraído com erro"
                        self.file_processed.emit(f"📄 {xml_name}", structure_status, signature_status, timestamp, api_status)
                    else:
                        self.file_processed.emit(xml_name, structure_status, signature_status, timestamp, api_status)
                    
                    # Small delay between files from same archive
                    self.msleep(100)
                    
                except Exception as e:
                    xml_name = f"{archive_name}[{Path(xml_file).name}]"
                    self.file_processed.emit(
                        xml_name, 
                        f"Erro: {str(e)[:30]}...", 
                        "N/A", 
                        timestamp,
                        "N/A"
                    )
            
            # Show summary and organize archive file if auto_organize is enabled
            summary_message = f"Extraído: {len(xml_files)} XML(s)"
            
            # Move or delete the archive file after processing if auto_organize is enabled
            if self.organizer and self.organizer.config_manager.get('auto_organize', True):
                try:
                    # Move archive to processed folder (since we extracted content)
                    output_base = Path(self.organizer.config_manager.get('output_folder', ''))
                    processed_folder = output_base / 'processed'
                    processed_folder.mkdir(parents=True, exist_ok=True)
                    
                    # Get target for archive in processed folder
                    archive_target = self.organizer._get_target_filename(processed_folder, archive_path.name)
                    
                    # Remove existing file if it exists
                    if archive_target.exists():
                        archive_target.unlink()
                    
                    # Move the archive file
                    shutil.move(str(archive_path), str(archive_target))
                    summary_message = f"Extraído: {len(xml_files)} XML(s) - Arquivo movido ✅"
                    
                    # Log the archive movement
                    self.organizer._log_file_movement(
                        archive_path, 
                        archive_target, 
                        True,  # Consider as success since we processed the content
                        f"Arquivo extraído com sucesso", 
                        "N/A"
                    )
                    
                except Exception as e:
                    print(f"Erro ao mover arquivo {archive_path}: {e}")
                    summary_message = f"Extraído: {len(xml_files)} XML(s) - Erro ao mover arquivo ⚠️"
            
            self.file_processed.emit(
                f"📦 {archive_name}", 
                summary_message, 
                "Processamento concluído", 
                timestamp,
                "N/A"
            )
            
        except Exception as e:
            # Move archive to errors folder if extraction failed and auto_organize is enabled
            error_message = f"Erro na extração: {str(e)[:40]}..."
            
            if self.organizer and self.organizer.config_manager.get('auto_organize', True):
                try:
                    output_base = Path(self.organizer.config_manager.get('output_folder', ''))
                    errors_folder = output_base / 'errors'
                    errors_folder.mkdir(parents=True, exist_ok=True)
                    
                    # Get target for archive in errors folder
                    archive_target = self.organizer._get_target_filename(errors_folder, archive_path.name)
                    
                    # Remove existing file if it exists
                    if archive_target.exists():
                        archive_target.unlink()
                    
                    # Move the archive file to errors
                    shutil.move(str(archive_path), str(archive_target))
                    error_message = f"Erro na extração - Arquivo movido para erros: {str(e)[:30]}..."
                    
                    # Log the archive movement
                    self.organizer._log_file_movement(
                        archive_path, 
                        archive_target, 
                        False,  # Error case
                        f"Erro na extração", 
                        str(e)
                    )
                    
                except Exception as move_error:
                    print(f"Erro ao mover arquivo com erro {archive_path}: {move_error}")
                    error_message = f"Erro na extração + erro ao mover: {str(e)[:20]}..."
            
            self.file_processed.emit(
                archive_path.name, 
                error_message, 
                "N/A", 
                timestamp,
                "N/A"
            )
    
    def process_xml_file(self, xml_path, timestamp):
        """Process individual XML file"""
        # Show relative path for files in subfolders
        try:
            monitor_path = Path(self.watch_path)
            relative_path = xml_path.relative_to(monitor_path)
            filename = str(relative_path) if len(relative_path.parts) > 1 else xml_path.name
        except (ValueError, AttributeError):
            filename = xml_path.name
        
        structure_status = self.validator.validate_structure(str(xml_path))
        signature_status = self.validator.validate_signature(str(xml_path))
        
        # Use parallel processing if available, otherwise fallback to sequential
        if self.parallel_api:
            # Create callback to update UI when processing is complete
            def on_processing_complete(final_filename, final_structure, final_signature, final_api_status, file_moved):
                try:
                    if file_moved:
                        moved_status = "✅ Processado" if self.organizer._is_successful(final_structure, final_signature) else "✗ Erro encontrado"
                        self.file_processed.emit(f"📄 {final_filename}", final_structure, final_signature, timestamp, final_api_status)
                    else:
                        self.file_processed.emit(final_filename, final_structure, final_signature, timestamp, final_api_status)
                except Exception as e:
                    print(f"Erro no callback da UI: {e}")
                    # Fallback emit
                    try:
                        self.file_processed.emit(final_filename, final_structure, final_signature, timestamp, "Erro no callback")
                    except:
                        pass
            
            # Submit to parallel processing queue with filename context
            def callback_wrapper(final_filename, final_structure, final_signature, final_api_status, file_moved):
                try:
                    on_processing_complete(filename, final_structure, final_signature, final_api_status, file_moved)
                except Exception as e:
                    print(f"Erro no wrapper do callback: {e}")
            
            try:
                self.parallel_api.add_to_queue(
                    str(xml_path), 
                    structure_status, 
                    signature_status, 
                    callback=callback_wrapper
                )
            except Exception as e:
                print(f"Erro ao adicionar à fila paralela: {e}")
                # Fallback to sequential processing
                self._process_sequential(xml_path, filename, structure_status, signature_status, timestamp)
        else:
            # Fallback to sequential processing (original logic)
            is_valid = self._is_file_valid(structure_status, signature_status)
            
            # Determine initial API status
            if is_valid and self.api_client:
                token = self.api_client.config_manager.get('token', '')
                if token:
                    api_status = "Preparando para envio..."
                else:
                    api_status = "Token não configurado"
            elif not is_valid:
                # Log why file is invalid
                print(f"⚠️  Arquivo {xml_path.name} não foi enviado - Motivos:")
                print(f"   Estrutura XML: {structure_status}")
                print(f"   Assinatura Digital: {signature_status}")
                print("-" * 50)
                api_status = "Não enviado - Arquivo inválido"
            else:
                api_status = "API não configurada"
            
            # Send to API if valid and token is configured
            if is_valid and self.api_client:
                token = self.api_client.config_manager.get('token', '')
                if token:
                    try:
                        # Verify file exists before API call
                        if xml_path.exists():
                            api_result = self.api_client.send_nfe(str(xml_path))
                            api_status = api_result['message']
                            
                            # Log API result with full details
                            print(f"🔍 API Response for {xml_path.name}:")
                            print(f"   Success: {api_result.get('success', 'N/A')}")
                            print(f"   Message: {api_result.get('message', 'N/A')}")
                            if 'data' in api_result:
                                print(f"   Data: {api_result['data']}")
                            print("-" * 50)
                            
                            self._log_api_result(xml_path, api_result)
                        else:
                            api_status = "Arquivo não encontrado para API"
                        
                    except Exception as e:
                        error_msg = str(e)
                        print(f"❌ ERRO CRÍTICO NA API: {error_msg}")
                        import traceback
                        print("📋 Traceback completo:")
                        traceback.print_exc()
                        api_status = f"Erro API: {error_msg[:100]}..."
            
            # Organize file if organizer is available and auto_organize is enabled
            moved = False
            if self.organizer and self.organizer.config_manager.get('auto_organize', True):
                try:
                    if self.organizer.organize_file(xml_path, structure_status, signature_status):
                        moved = True
                except Exception as e:
                    print(f"Erro ao organizar arquivo {xml_path}: {e}")
            
            # Emit result to UI (only once)
            if moved:
                moved_status = "✅ Processado" if self.organizer._is_successful(structure_status, signature_status) else "✗ Erro encontrado"
                self.file_processed.emit(f"📄 {filename}", structure_status, signature_status, timestamp, api_status)
            else:
                self.file_processed.emit(filename, structure_status, signature_status, timestamp, api_status)
    
    def _process_sequential(self, xml_path, filename, structure_status, signature_status, timestamp):
        """Sequential processing fallback"""
        is_valid = self._is_file_valid(structure_status, signature_status)
        
        # Determine initial API status
        if is_valid and self.api_client:
            token = self.api_client.config_manager.get('token', '')
            if token:
                api_status = "Preparando para envio..."
            else:
                api_status = "Token não configurado"
        elif not is_valid:
            api_status = "Não enviado - Arquivo inválido"
        else:
            api_status = "API não configurada"
        
        # Send to API if valid and token is configured
        if is_valid and self.api_client:
            token = self.api_client.config_manager.get('token', '')
            if token:
                try:
                    # Verify file exists before API call
                    if xml_path.exists():
                        api_result = self.api_client.send_nfe(str(xml_path))
                        api_status = api_result['message']
                        
                        # Log API result
                        self._log_api_result(xml_path, api_result)
                    else:
                        api_status = "Arquivo não encontrado para API"
                    
                except Exception as e:
                    api_status = f"Erro API: {str(e)[:30]}..."
        
        # Organize file if organizer is available and auto_organize is enabled
        moved = False
        if self.organizer and self.organizer.config_manager.get('auto_organize', True):
            try:
                if self.organizer.organize_file(xml_path, structure_status, signature_status):
                    moved = True
            except Exception as e:
                print(f"Erro ao organizar arquivo {xml_path}: {e}")
        
        # Emit result to UI (only once)
        if moved:
            moved_status = "✅ Processado" if self.organizer._is_successful(structure_status, signature_status) else "✗ Erro encontrado"
            self.file_processed.emit(f"📄 {filename}", structure_status, signature_status, timestamp, api_status)
        else:
            self.file_processed.emit(filename, structure_status, signature_status, timestamp, api_status)
    
    def _is_file_valid(self, structure_status, signature_status):
        """Check if file is valid for API submission"""
        structure_ok = "✅" in structure_status
        signature_ok = "✅" in signature_status
        
        # Debug validation logic
        print(f"🔍 Validando arquivo (sequential):")
        print(f"   Estrutura: '{structure_status}' -> {structure_ok}")
        print(f"   Assinatura: '{signature_status}' -> {signature_ok}")
        print(f"   Resultado final: {structure_ok and signature_ok}")
        print("-" * 50)
        
        return structure_ok and signature_ok
    
    def _log_api_result(self, file_path, api_result):
        """Log API result"""
        try:
            if self.organizer:
                logs_folder = Path(self.organizer.config_manager.get('output_folder', '')) / 'logs'
                logs_folder.mkdir(parents=True, exist_ok=True)
                
                log_file = logs_folder / f"api_results_{datetime.now().strftime('%Y%m%d')}.log"
                
                with open(log_file, 'a', encoding='utf-8') as f:
                    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    status = "SUCCESS" if api_result['success'] else "ERROR"
                    
                    f.write(f"{timestamp} | API {status} | {file_path.name}\n")
                    f.write(f"  Mensagem: {api_result['message']}\n")
                    if 'data' in api_result:
                        f.write(f"  Dados: {api_result['data']}\n")
                    f.write("\n")
                    
        except Exception as e:
            print(f"Erro ao criar log da API: {e}")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.monitor_thread = None
        self.config_manager = ConfigManager()
        
        # Statistics tracking
        self.session_start_time = datetime.now()
        self.xml_count_success = 0
        self.xml_count_error = 0
        
        # macOS specific: Timer to keep app active
        if platform.system() == "Darwin":
            self.keepalive_timer = QTimer(self)
            self.keepalive_timer.timeout.connect(self.keep_alive)
            self.keepalive_timer.start(30000)  # Every 30 seconds
        
        self.setup_ui()
        self.load_initial_config()
    
    def apply_light_theme(self):
        """Aplica tema light consistente em toda a aplicação"""
        light_style = """
        QMainWindow {
            background-color: #ffffff;
            color: #2c3e50;
        }
        
        QWidget {
            background-color: #ffffff;
            color: #2c3e50;
        }
        
        QGroupBox {
            font-weight: bold;
            border: 2px solid #bdc3c7;
            border-radius: 8px;
            margin-top: 10px;
            padding-top: 10px;
            background-color: #f8f9fa;
            color: #2c3e50;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 8px 0 8px;
            background-color: #ffffff;
            color: #34495e;
            font-size: 12px;
        }
        
        QPushButton {
            background-color: #3498db;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            font-weight: bold;
            min-height: 16px;
        }
        
        QPushButton:hover {
            background-color: #2980b9;
        }
        
        QPushButton:pressed {
            background-color: #21618c;
        }
        
        QPushButton:disabled {
            background-color: #bdc3c7;
            color: #7f8c8d;
        }
        
        QLineEdit {
            padding: 8px;
            border: 1px solid #bdc3c7;
            border-radius: 4px;
            background-color: #ffffff;
            color: #2c3e50;
            font-size: 11px;
        }
        
        QLineEdit:focus {
            border: 2px solid #3498db;
        }
        
        QTableWidget {
            background-color: #ffffff;
            alternate-background-color: #f8f9fa;
            color: #2c3e50;
            gridline-color: #ecf0f1;
            border: 1px solid #bdc3c7;
            border-radius: 4px;
        }
        
        QTableWidget::item {
            padding: 8px;
            border-bottom: 1px solid #ecf0f1;
        }
        
        QTableWidget::item:selected {
            background-color: #d5dbdb;
            color: #2c3e50;
        }
        
        QHeaderView::section {
            background-color: #ecf0f1;
            color: #2c3e50;
            padding: 8px;
            border: none;
            border-bottom: 2px solid #bdc3c7;
            font-weight: bold;
        }
        
        QLabel {
            color: #2c3e50;
        }
        
        QMenuBar {
            background-color: #ecf0f1;
            color: #2c3e50;
            border-bottom: 1px solid #bdc3c7;
        }
        
        QMenuBar::item {
            background-color: transparent;
            padding: 8px 12px;
        }
        
        QMenuBar::item:selected {
            background-color: #d5dbdb;
        }
        
        QMenu {
            background-color: #ffffff;
            color: #2c3e50;
            border: 1px solid #bdc3c7;
        }
        
        QMenu::item {
            padding: 8px 20px;
        }
        
        QMenu::item:selected {
            background-color: #d5dbdb;
        }
        
        /* Status colors específicos */
        .status-success { color: #27ae60; font-weight: bold; }
        .status-error { color: #e74c3c; font-weight: bold; }
        .status-warning { color: #f39c12; font-weight: bold; }
        .status-info { color: #3498db; font-weight: bold; }
        """
        
        self.setStyleSheet(light_style)
    
    def update_session_info(self):
        """Update session start date and time info"""
        session_date = self.session_start_time.strftime("%d/%m/%Y")
        session_time = self.session_start_time.strftime("%H:%M:%S")
        self.session_info_label.setText(f"📅 Sessão iniciada: {session_date} às {session_time}")
    
    def update_statistics(self):
        """Update the statistics counters"""
        self.stats_success_label.setText(f"[OK] Sucesso: {self.xml_count_success}")
        self.stats_error_label.setText(f"[ERRO] Erro: {self.xml_count_error}")
    
    def update_file_statistics(self, structure_status, signature_status, api_status):
        """Update statistics based on file processing results"""
        # Consider a file successful if both structure and signature are valid
        # Look for checkmark (✅) instead of "válido" text
        structure_ok = "✅" in structure_status
        signature_ok = "✅" in signature_status
        api_error = "✗" in api_status or "❌" in api_status
        
        # Only count XML files (skip archive files that show "Nenhum XML encontrado")
        if "Nenhum XML encontrado" in structure_status:
            return  # Don't count archive files without XMLs
        
        # Debug logging
        print(f"📊 Contabilizando arquivo:")
        print(f"   Estrutura OK: {structure_ok} ({structure_status})")
        print(f"   Assinatura OK: {signature_ok} ({signature_status})")
        print(f"   API Error: {api_error} ({api_status})")
        
        # Count as success if structure and signature are OK
        # API success is not required for counting as success (API might fail for other reasons)
        if structure_ok and signature_ok:
            self.xml_count_success += 1
            print(f"   ✅ Contado como sucesso (Total: {self.xml_count_success})")
        else:
            self.xml_count_error += 1
            print(f"   ❌ Contado como erro (Total: {self.xml_count_error})")
        
        self.update_statistics()
    
    def setup_ui(self):
        print("🪟 Configurando UI...")
        self.setWindowTitle("Monitor de Validação de NF-e")
        
        # Aplicar tema light consistente
        self.apply_light_theme()
        
        # Força uma geometria bem visível
        self.setGeometry(200, 200, 900, 700)
        
        # Força janela para frente no macOS
        if platform.system() == "Darwin":
            from PySide6.QtCore import Qt
            self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
            self.raise_()
            self.activateWindow()
        
        print(f"🎯 Geometria configurada: {self.geometry()}")
        
        # Set window icon if available
        icon_paths = [
            Path(__file__).parent / 'logo-validatech.png',
            Path(__file__).parent / 'icon.png'
        ]
        
        for icon_path in icon_paths:
            if icon_path.exists():
                from PySide6.QtGui import QIcon
                self.setWindowIcon(QIcon(str(icon_path)))
                break
        
        # Create menu bar
        self.create_menu_bar()
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Configuration status layout
        config_layout = QHBoxLayout()
        config_layout.addWidget(QLabel("Status:"))
        
        self.config_status_label = QLabel("Configuração não definida")
        self.config_status_label.setStyleSheet("color: #f39c12; font-weight: bold;")
        config_layout.addWidget(self.config_status_label)
        
        config_layout.addStretch()
        
        config_btn = QPushButton("⚙️ Configurações")
        config_btn.clicked.connect(self.open_config)
        config_layout.addWidget(config_btn)
        
        layout.addLayout(config_layout)
        
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("▶️ Iniciar Monitoramento")
        self.start_button.clicked.connect(self.start_monitoring)
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-weight: bold;
                padding: 12px 20px;
                border-radius: 8px;
                font-size: 14px;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
            QPushButton:pressed {
                background-color: #229954;
            }
            QPushButton:disabled {
                background-color: #6c757d;
                color: #adb5bd;
                border: 1px solid #dee2e6;
            }
        """)
        button_layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("⏹️ Parar Monitoramento")
        self.stop_button.clicked.connect(self.stop_monitoring)
        self.stop_button.setEnabled(False)
        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                font-weight: bold;
                padding: 12px 20px;
                border-radius: 8px;
                font-size: 14px;
                min-height: 20px;
            }
            QPushButton:hover:enabled {
                background-color: #c0392b;
            }
            QPushButton:pressed:enabled {
                background-color: #a93226;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """)
        button_layout.addWidget(self.stop_button)
        
        layout.addLayout(button_layout)
        
        # Statistics panel
        stats_group = QGroupBox("📊 Estatísticas da Sessão")
        stats_layout = QHBoxLayout()
        
        # Session start info
        self.session_info_label = QLabel()
        self.update_session_info()
        stats_layout.addWidget(self.session_info_label)
        
        stats_layout.addStretch()  # Add space between elements
        
        # Counters
        self.stats_success_label = QLabel("[OK] Sucesso: 0")
        self.stats_success_label.setStyleSheet("color: #27ae60; font-weight: bold;")
        stats_layout.addWidget(self.stats_success_label)
        
        self.stats_error_label = QLabel("[ERRO] Erro: 0")
        self.stats_error_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
        stats_layout.addWidget(self.stats_error_label)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        self.status_label = QLabel("Status: Aguardando...")
        layout.addWidget(self.status_label)
        
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Nome do Arquivo", 
            "Status da Estrutura", 
            "Status da Assinatura", 
            "Data/Hora",
            "Status da API"
        ])
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        
        layout.addWidget(self.table)
        
        info_label = QLabel(f"Sistema: {platform.system()} {platform.release()}")
        info_label.setFont(QFont("Arial", 8))
        layout.addWidget(info_label)
    
    def create_menu_bar(self):
        """Create application menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('Arquivo')
        
        config_action = file_menu.addAction('⚙️ Configurações')
        config_action.triggered.connect(self.open_config)
        
        file_menu.addSeparator()
        
        exit_action = file_menu.addAction('Sair')
        exit_action.triggered.connect(self.close)
        
        # Tools menu
        tools_menu = menubar.addMenu('Ferramentas')
        
        clear_table_action = tools_menu.addAction('🗑️ Limpar Tabela')
        clear_table_action.triggered.connect(self.clear_table)
        
        export_results_action = tools_menu.addAction('📊 Exportar Resultados')
        export_results_action.triggered.connect(self.export_results)
        
        # Help menu
        help_menu = menubar.addMenu('Ajuda')
        
        about_action = help_menu.addAction('Sobre')
        about_action.triggered.connect(self.show_about)
    
    def load_initial_config(self):
        """Load and display initial configuration"""
        self.update_config_status()
    
    def update_config_status(self):
        """Update configuration status display"""
        monitor_folder = self.config_manager.get('monitor_folder', '')
        output_folder = self.config_manager.get('output_folder', '')
        token = self.config_manager.get('token', '')
        
        if monitor_folder and output_folder:
            if token:
                self.config_status_label.setText("✅ Configuração completa")
                self.config_status_label.setStyleSheet("color: #27ae60; font-weight: bold;")
            else:
                self.config_status_label.setText("⚠️ Token não configurado")
                self.config_status_label.setStyleSheet("color: #f39c12; font-weight: bold;")
        else:
            self.config_status_label.setText("✗ Pastas não configuradas")
            self.config_status_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
    
    def open_config(self):
        """Open configuration dialog"""
        dialog = ConfigDialog(self.config_manager, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.update_config_status()
            QMessageBox.information(self, "Configuração", "Configurações salvas com sucesso!")
    
    def clear_table(self):
        """Clear results table"""
        reply = QMessageBox.question(
            self, 
            "Limpar Tabela",
            "Deseja realmente limpar todos os resultados?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.table.setRowCount(0)
    
    def export_results(self):
        """Export results to CSV file"""
        if self.table.rowCount() == 0:
            QMessageBox.information(self, "Exportar", "Nenhum resultado para exportar.")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Exportar Resultados",
            f"resultados_nfe_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "CSV Files (*.csv)"
        )
        
        if file_path:
            try:
                import csv
                
                with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    
                    # Write header
                    headers = [
                        self.table.horizontalHeaderItem(i).text()
                        for i in range(self.table.columnCount())
                    ]
                    writer.writerow(headers)
                    
                    # Write data
                    for row in range(self.table.rowCount()):
                        row_data = [
                            self.table.item(row, col).text() if self.table.item(row, col) else ""
                            for col in range(self.table.columnCount())
                        ]
                        writer.writerow(row_data)
                
                QMessageBox.information(self, "Exportar", f"Resultados exportados para:\n{file_path}")
                
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao exportar: {e}")
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "Sobre",
            "<h3>Monitor de Validação de NF-e</h3>"
            "<p><b>Versão:</b> 1.0</p>"
            "<p><b>Desenvolvido por:</b> ValidateCh</p>"
            "<p><b>Funcionalidades:</b></p>"
            "<ul>"
            "<li>Monitoramento de pastas</li>"
            "<li>Validação de XML/XSD</li>"
            "<li>Verificação de assinatura</li>"
            "<li>Suporte a ZIP/RAR/7Z</li>"
            "<li>Organização automática</li>"
            "</ul>"
        )
    
    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Selecionar Pasta")
        if folder:
            self.path_input.setText(folder)
    
    def start_monitoring(self):
        # Check if monitoring is already running
        if self.monitor_thread and self.monitor_thread.isRunning():
            QMessageBox.information(
                self, 
                "Monitoramento Ativo", 
                "O monitoramento já está ativo!\n\n"
                "Use o botão 'Parar Monitoramento' para interromper."
            )
            return
        
        # Check configuration
        monitor_folder = self.config_manager.get('monitor_folder', '')
        output_folder = self.config_manager.get('output_folder', '')
        
        if not monitor_folder:
            QMessageBox.warning(
                self, 
                "Configuração Necessária", 
                "Por favor, configure a pasta de monitoramento primeiro.\n"
                "Vá em Configurações para definir as pastas."
            )
            self.open_config()
            return
        
        if not Path(monitor_folder).exists():
            QMessageBox.warning(self, "Erro", f"A pasta de monitoramento não existe:\n{monitor_folder}")
            return
        
        if not output_folder:
            QMessageBox.warning(
                self, 
                "Configuração Necessária", 
                "Por favor, configure a pasta de saída primeiro.\n"
                "Vá em Configurações para definir as pastas."
            )
            self.open_config()
            return
        
        # Additional validation to prevent infinite loops
        monitor_path = Path(monitor_folder).resolve()
        output_path = Path(output_folder).resolve()
        
        if monitor_path == output_path:
            QMessageBox.critical(self, "Erro", "Pasta de monitoramento não pode ser igual à pasta de saída!")
            self.open_config()
            return
        elif monitor_path in output_path.parents:
            QMessageBox.critical(self, "Erro", "Pasta de saída não pode estar dentro da pasta de monitoramento!")
            self.open_config()
            return
        elif output_path in monitor_path.parents:
            QMessageBox.critical(self, "Erro", "Pasta de monitoramento não pode estar dentro da pasta de saída!")
            self.open_config()
            return
        
        # Ensure output folder structure exists
        if not self.config_manager.ensure_output_folders():
            QMessageBox.warning(self, "Erro", "Não foi possível criar a estrutura de pastas de saída.")
            return
        
        schema_path = Path(__file__).parent / 'schemas' / 'leiauteNFe_v4.00.xsd'
        if not schema_path.exists():
            reply = QMessageBox.question(
                self,
                "Schema não encontrado",
                "O schema NFe v4.00 não foi encontrado.\n"
                "Deseja baixá-lo automaticamente do repositório PyNFe?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return
        
        # Reset statistics for new session
        self.xml_count_success = 0
        self.xml_count_error = 0
        self.session_start_time = datetime.now()
        self.update_session_info()
        self.update_statistics()
        
        self.monitor_thread = MonitorThread(monitor_folder, self.config_manager)
        # Clear previous cache to avoid issues with old processed files
        self.monitor_thread.clear_processed_files_cache()
        self.monitor_thread.file_processed.connect(self.add_result)
        self.monitor_thread.start()
        
        # Update button states and texts
        self.start_button.setEnabled(False)
        self.start_button.setText("🔄 Monitoramento Ativo")
        self.stop_button.setEnabled(True)
        self.status_label.setText(f"Status: Monitorando '{Path(monitor_folder).name}' e subpastas 📁")
    
    def stop_monitoring(self):
        if self.monitor_thread:
            self.monitor_thread.stop()
            self.monitor_thread.wait()
        
        # Restore button states and texts
        self.start_button.setEnabled(True)
        self.start_button.setText("▶️ Iniciar Monitoramento")
        self.stop_button.setEnabled(False)
        self.status_label.setText("Status: Monitoramento parado")
    
    def add_result(self, filename, structure_status, signature_status, timestamp, api_status="N/A"):
        try:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # Add visual indicator if filename contains path info from subfolders
            display_filename = filename
            if '/' in filename or '\\' in filename:
                # This indicates a file from a subfolder
                display_filename = f"📄 {filename}"
            
            self.table.setItem(row, 0, QTableWidgetItem(display_filename))
            self.table.setItem(row, 1, QTableWidgetItem(structure_status))
            self.table.setItem(row, 2, QTableWidgetItem(signature_status))
            self.table.setItem(row, 3, QTableWidgetItem(timestamp))
            
            # Create API status item with color coding
            api_item = QTableWidgetItem(api_status)
            
            
            # Set row background color based on API status
            # Use light yellow/cream background for all API results
            if ("[OK]" in api_status or "sucesso" in api_status.lower()):
                # Success - green text
                row_color = QColor(255, 250, 220)  # Light yellow/cream
                text_color = QColor(27, 174, 96)   # Green text (#27ae60)
            elif ("[EXISTE]" in api_status or "já existe" in api_status.lower() or "existe" in api_status.lower()):
                # Duplicate/already exists - orange text
                row_color = QColor(255, 250, 220)  # Light yellow/cream
                text_color = QColor(243, 156, 18)  # Orange text (#f39c12)
            elif ("✗" in api_status or "[ERRO]" in api_status or "erro" in api_status.lower() or "inválido" in api_status.lower()):
                # Error - red text
                row_color = QColor(255, 250, 220)  # Light yellow/cream (same background)
                text_color = QColor(231, 76, 60)   # Red text (#e74c3c)
            else:
                # Default white/transparent for other statuses (N/A, etc.)
                row_color = None
                text_color = QColor(0, 0, 0)       # Black text
            
            # Apply color to the entire row if we have a color
            if row_color:
                for col in range(5):  # All columns (0-4)
                    if self.table.item(row, col):
                        self.table.item(row, col).setBackground(row_color)
                        self.table.item(row, col).setForeground(text_color)
            else:
                # Apply default text color for non-colored rows
                for col in range(5):
                    if self.table.item(row, col):
                        self.table.item(row, col).setForeground(text_color)
        
            self.table.setItem(row, 4, api_item)
            
            self.table.scrollToBottom()
            
            # Update statistics counters
            self.update_file_statistics(structure_status, signature_status, api_status)
            
        except Exception as e:
            print(f"Erro ao adicionar resultado à tabela: {e}")
            # Try a simple fallback
            try:
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(str(filename)))
                self.table.setItem(row, 1, QTableWidgetItem(str(structure_status)))
                self.table.setItem(row, 2, QTableWidgetItem(str(signature_status)))
                self.table.setItem(row, 3, QTableWidgetItem(str(timestamp)))
                self.table.setItem(row, 4, QTableWidgetItem(str(api_status)))
            except Exception as e2:
                print(f"Erro no fallback da tabela: {e2}")
    
    def keep_alive(self):
        """Keep app alive on macOS to prevent system from terminating it"""
        # Simple operation to keep app active
        if hasattr(self, 'table') and self.table:
            try:
                # Refresh UI periodically 
                self.table.update()
            except:
                pass
    
    def closeEvent(self, event):
        # Stop keepalive timer
        if hasattr(self, 'keepalive_timer'):
            self.keepalive_timer.stop()
        self.stop_monitoring()
        event.accept()


def main():
    app = QApplication(sys.argv)
    
    app.setApplicationName("Monitor NF-e")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("ValidaGuarda")
    
    # Forçar tema light independente do sistema
    from PySide6.QtCore import Qt
    app.setStyle("Fusion")  # Usar Fusion style que é mais consistente cross-platform
    
    # macOS specific settings to prevent app from disappearing
    if platform.system() == "Darwin":
        # Keep app active and prevent it from being terminated by system
        app.setQuitOnLastWindowClosed(True)
        # Prevent macOS App Nap from suspending the application
        try:
            import subprocess
            subprocess.run(['caffeinate', '-d'], check=False)
        except:
            pass
    
    # Set icon for dock/taskbar
    try:
        icon_path = os.path.join(os.path.dirname(__file__), "logo-validatech.png")
        if os.path.exists(icon_path):
            from PySide6.QtGui import QIcon
            app.setWindowIcon(QIcon(icon_path))
    except Exception as e:
        print(f"Não foi possível definir o ícone: {e}")
    
    window = MainWindow()
    window.show()
    
    # Keep a strong reference to prevent garbage collection
    from PySide6.QtCore import Qt
    window.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, False)
    
    # Add signal handlers for graceful shutdown
    import signal
    def signal_handler(signum, frame):
        print(f"Sinal recebido: {signum}")
        try:
            window.stop_monitoring()
        except:
            pass
        app.quit()
    
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        sys.exit(app.exec())
    except KeyboardInterrupt:
        print("Interrompido pelo usuário")
        try:
            window.stop_monitoring()
        except:
            pass
        sys.exit(0)


if __name__ == "__main__":
    main()