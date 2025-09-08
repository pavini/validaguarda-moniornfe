from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QLabel, QFileDialog, QLineEdit, QMessageBox, 
                               QFormLayout, QGroupBox, QCheckBox)
from PySide6.QtCore import Qt
from pathlib import Path

from domain.entities.configuration import Configuration


class ConfigDialog(QDialog):
    """Configuration dialog UI component"""
    
    def __init__(self, current_config: Configuration, parent=None):
        super().__init__(parent)
        self.current_config = current_config
        self.setWindowTitle("Configurações")
        self.setModal(True)
        self.resize(500, 400)
        self.setup_ui()
        self.load_current_config()
    
    def setup_ui(self):
        """Setup UI components"""
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
        
        # Token visibility and test buttons
        token_buttons_layout = QHBoxLayout()
        show_token_btn = QPushButton("Mostrar/Ocultar Token")
        show_token_btn.clicked.connect(self.toggle_token_visibility)
        token_buttons_layout.addWidget(show_token_btn)
        
        test_api_btn = QPushButton("Testar API")
        test_api_btn.clicked.connect(self.test_api_connection)
        token_buttons_layout.addWidget(test_api_btn)
        
        api_layout.addRow("", token_buttons_layout)
        
        layout.addWidget(api_group)
        
        # Dialog buttons
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
        self.monitor_folder_input.setText(self.current_config.monitor_folder or '')
        self.output_folder_input.setText(self.current_config.output_folder or '')
        self.token_input.setText(self.current_config.token or '')
        self.auto_organize_check.setChecked(self.current_config.auto_organize)
    
    def browse_monitor_folder(self):
        """Browse for monitor folder"""
        folder = QFileDialog.getExistingDirectory(self, "Selecionar Pasta de Monitoramento")
        if folder:
            self.monitor_folder_input.setText(folder)
    
    def browse_output_folder(self):
        """Browse for output folder"""
        folder = QFileDialog.getExistingDirectory(self, "Selecionar Pasta de Saída")
        if folder:
            self.output_folder_input.setText(folder)
    
    def toggle_token_visibility(self):
        """Toggle token visibility"""
        if self.token_input.echoMode() == QLineEdit.EchoMode.Password:
            self.token_input.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.token_input.setEchoMode(QLineEdit.EchoMode.Password)
    
    def test_api_connection(self):
        """Test API connection with current token"""
        token = self.token_input.text().strip()
        if not token:
            QMessageBox.warning(self, "Aviso", "Por favor, informe o token da API primeiro.")
            return
        
        # TODO: Implement API connection test using use cases
        # For now, show a placeholder message
        QMessageBox.information(
            self, 
            "Teste de API", 
            "Funcionalidade de teste será implementada na integração final."
        )
    
    def test_folders(self):
        """Test if folders exist and are accessible"""
        monitor_folder = self.monitor_folder_input.text().strip()
        output_folder = self.output_folder_input.text().strip()
        
        messages = []
        
        # Test monitor folder
        if monitor_folder:
            monitor_path = Path(monitor_folder)
            if monitor_path.exists() and monitor_path.is_dir():
                messages.append(f"✅ Pasta de monitoramento: OK")
            else:
                messages.append(f"❌ Pasta de monitoramento: Não encontrada ou não é uma pasta")
        else:
            messages.append("⚠️  Pasta de monitoramento não configurada")
        
        # Test output folder
        if output_folder:
            output_path = Path(output_folder)
            if output_path.exists() and output_path.is_dir():
                messages.append(f"✅ Pasta de saída: OK")
                
                # Test write access
                try:
                    test_file = output_path / ".test_write"
                    test_file.touch()
                    test_file.unlink()
                    messages.append(f"✅ Permissão de escrita: OK")
                except:
                    messages.append(f"❌ Permissão de escrita: Sem permissão")
            else:
                messages.append(f"❌ Pasta de saída: Não encontrada ou não é uma pasta")
        else:
            messages.append("⚠️  Pasta de saída não configurada")
        
        QMessageBox.information(
            self,
            "Teste de Pastas",
            "\n".join(messages)
        )
    
    def save_config(self):
        """Save configuration and close dialog"""
        # Validate required fields
        monitor_folder = self.monitor_folder_input.text().strip()
        output_folder = self.output_folder_input.text().strip()
        token = self.token_input.text().strip()
        
        if not monitor_folder:
            QMessageBox.warning(self, "Erro", "Pasta de monitoramento é obrigatória.")
            return
        
        if not output_folder:
            QMessageBox.warning(self, "Erro", "Pasta de saída é obrigatória.")
            return
        
        if not token:
            QMessageBox.warning(self, "Erro", "Token da API é obrigatório.")
            return
        
        # Validate paths
        monitor_path = Path(monitor_folder)
        if not monitor_path.exists():
            QMessageBox.warning(self, "Erro", f"Pasta de monitoramento não existe: {monitor_folder}")
            return
        
        output_path = Path(output_folder)
        if not output_path.exists():
            try:
                output_path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                QMessageBox.warning(self, "Erro", f"Não foi possível criar pasta de saída: {e}")
                return
        
        # Update configuration
        self.current_config.monitor_folder = monitor_folder
        self.current_config.output_folder = output_folder
        self.current_config.token = token
        self.current_config.auto_organize = self.auto_organize_check.isChecked()
        
        self.accept()
    
    def get_configuration(self) -> Configuration:
        """Get updated configuration"""
        return self.current_config