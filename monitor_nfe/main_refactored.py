#!/usr/bin/env python3
import sys
import locale
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, 
    QPushButton, QLabel, QTableWidget, QTableWidgetItem, QFileDialog,
    QLineEdit, QMessageBox, QHeaderView, QMenuBar, QMenu, QTextEdit, QDialog
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QColor

from config.dependency_container import DependencyContainer
from presentation.ui.config_dialog import ConfigDialog
from presentation.viewmodels.main_view_model import MainViewModel


class MainWindow(QMainWindow):
    """Refactored main window using Clean Architecture"""
    
    def __init__(self, view_model: MainViewModel):
        super().__init__()
        self.view_model = view_model
        self.setup_ui()
        self.connect_signals()
        self.update_ui_state()
    
    def setup_ui(self):
        """Setup the modern user interface"""
        self.setWindowTitle("Monitor NFe • ValidaTech")
        self.setMinimumSize(1200, 800)
        # Set initial size larger than minimum
        self.resize(1400, 900)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        central_widget.setObjectName("centralWidget")
        
        # Main layout with margins
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(24, 16, 24, 24)
        main_layout.setSpacing(20)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Modern header with cards
        self.create_header_section(main_layout)
        
        # Action buttons in modern card style
        self.create_action_buttons(main_layout)
        
        # Statistics cards
        self.create_stats_section(main_layout)
        
        # Main content area - Vertical layout (grid on top, logs on bottom)
        content_layout = QVBoxLayout()
        content_layout.setSpacing(16)
        
        # Top - Results table in card
        table_card = self.create_card()
        table_layout = QVBoxLayout(table_card)
        
        # Table header
        table_header = QLabel("📊 Resultados de Processamento")
        table_header.setObjectName("cardTitle")
        table_layout.addWidget(table_header)
        
        # Results table
        self.create_results_table()
        table_layout.addWidget(self.results_table)
        
        content_layout.addWidget(table_card, 2)  # More space for table
        
        # Bottom - Logs in card  
        logs_card = self.create_card()
        logs_layout = QVBoxLayout(logs_card)
        
        # Log header with clear button
        log_header_layout = QHBoxLayout()
        log_header = QLabel("📝 Log de Atividades")
        log_header.setObjectName("cardTitle")
        log_header_layout.addWidget(log_header)
        
        log_header_layout.addStretch()
        
        clear_log_btn = QPushButton("🗑️")
        clear_log_btn.setObjectName("iconButton")
        clear_log_btn.setToolTip("Limpar logs")
        clear_log_btn.clicked.connect(self.clear_logs)
        clear_log_btn.setFixedSize(32, 32)
        log_header_layout.addWidget(clear_log_btn)
        
        logs_layout.addLayout(log_header_layout)
        
        # Log text area
        self.log_text = QTextEdit()
        self.log_text.setObjectName("logArea")
        self.log_text.setReadOnly(True)
        logs_layout.addWidget(self.log_text)
        
        content_layout.addWidget(logs_card, 1)  # Less space for logs
        
        main_layout.addLayout(content_layout)
        
        # Apply modern styling
        self.apply_modern_styling()
    
    def create_card(self):
        """Create a modern card widget"""
        card = QWidget()
        card.setObjectName("card")
        return card
    
    def create_header_section(self, main_layout):
        """Create modern header with status cards"""
        header_card = self.create_card()
        header_layout = QHBoxLayout(header_card)
        header_layout.setContentsMargins(24, 20, 24, 20)
        
        # Left side - Title and branding
        title_section = QVBoxLayout()
        
        title_label = QLabel("ValidaGuarda - Monitor NFe")
        title_label.setObjectName("mainTitle")
        title_section.addWidget(title_label)
        
        subtitle_label = QLabel("Sistema de envio de NFe para o ValidaGuarda da ValidaTech")
        subtitle_label.setObjectName("subtitle")
        title_section.addWidget(subtitle_label)
        
        header_layout.addLayout(title_section)
        header_layout.addStretch()
        
        # Right side - Status indicator
        status_section = QVBoxLayout()
        status_section.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        self.status_indicator = QLabel("●")
        self.status_indicator.setObjectName("statusIndicator")
        self.status_indicator.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_section.addWidget(self.status_indicator)
        
        self.status_label = QLabel("Sistema Pronto")
        self.status_label.setObjectName("statusLabel")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_section.addWidget(self.status_label)
        
        header_layout.addLayout(status_section)
        
        main_layout.addWidget(header_card)
    
    def create_action_buttons(self, main_layout):
        """Create modern action buttons"""
        button_card = self.create_card()
        button_layout = QHBoxLayout(button_card)
        button_layout.setContentsMargins(24, 16, 24, 16)
        
        # Primary actions
        self.start_button = QPushButton("▶️ Iniciar Monitoramento")
        self.start_button.setObjectName("primaryButton")
        self.start_button.clicked.connect(self.start_monitoring)
        button_layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("⏹️ Parar Monitoramento")
        self.stop_button.setObjectName("secondaryButton")
        self.stop_button.clicked.connect(self.stop_monitoring)
        button_layout.addWidget(self.stop_button)
        
        button_layout.addSpacing(20)
        
        # Secondary actions
        process_file_button = QPushButton("📁 Processar Arquivo")
        process_file_button.setObjectName("actionButton")
        process_file_button.clicked.connect(self.process_file_manually)
        button_layout.addWidget(process_file_button)
        
        config_button = QPushButton("⚙️ Configurações")
        config_button.setObjectName("actionButton")
        config_button.clicked.connect(self.open_config_dialog)
        button_layout.addWidget(config_button)
        
        button_layout.addStretch()
        
        # Utility actions
        clear_button = QPushButton("🗑️ Limpar Resultados")
        clear_button.setObjectName("dangerButton")
        clear_button.clicked.connect(self.clear_results)
        button_layout.addWidget(clear_button)
        
        main_layout.addWidget(button_card)
    
    def create_stats_section(self, main_layout):
        """Create statistics cards"""
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(16)
        
        # Total files card
        self.total_card = self.create_stat_card("📊", "0", "Total Processados")
        stats_layout.addWidget(self.total_card)
        
        # Success card
        self.success_card = self.create_stat_card("✅", "0", "Sucessos")
        stats_layout.addWidget(self.success_card)
        
        # Error card
        self.error_card = self.create_stat_card("❌", "0", "Erros")
        stats_layout.addWidget(self.error_card)
        
        # Success rate card
        self.rate_card = self.create_stat_card("📈", "0%", "Taxa de Sucesso")
        stats_layout.addWidget(self.rate_card)
        
        # Reprocess card - clickable
        self.reprocess_card = self.create_stat_card("🔄", "0", "Para Reprocessar")
        self.reprocess_card.setCursor(Qt.CursorShape.PointingHandCursor)
        self.reprocess_card.mousePressEvent = self.on_reprocess_card_clicked
        stats_layout.addWidget(self.reprocess_card)
        
        stats_layout.addStretch()
        
        main_layout.addLayout(stats_layout)
    
    def create_stat_card(self, icon, value, label):
        """Create a statistic card"""
        card = self.create_card()
        card.setObjectName("statCard")
        card.setFixedHeight(80)
        card.setMinimumWidth(160)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(4)
        
        # Icon and value row
        top_layout = QHBoxLayout()
        top_layout.setSpacing(8)
        
        icon_label = QLabel(icon)
        icon_label.setObjectName("statIcon")
        top_layout.addWidget(icon_label)
        
        value_label = QLabel(value)
        value_label.setObjectName("statValue")
        top_layout.addWidget(value_label)
        
        top_layout.addStretch()
        layout.addLayout(top_layout)
        
        # Label
        label_widget = QLabel(label)
        label_widget.setObjectName("statLabel")
        layout.addWidget(label_widget)
        
        # Store value label for updates
        card.value_label = value_label
        
        return card
    
    def clear_logs(self):
        """Clear the log area"""
        self.log_text.clear()
        self.add_log_entry("📝 Logs limpos pelo usuário")
    
    def create_menu_bar(self):
        """Create application menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("Arquivo")
        
        config_action = file_menu.addAction("Configurações")
        config_action.triggered.connect(self.open_config_dialog)
        
        file_menu.addSeparator()
        
        exit_action = file_menu.addAction("Sair")
        exit_action.triggered.connect(self.close)
        
        # Tools menu
        tools_menu = menubar.addMenu("Ferramentas")
        
        process_action = tools_menu.addAction("Processar Arquivo...")
        process_action.triggered.connect(self.process_file_manually)
        
        clear_action = tools_menu.addAction("Limpar Resultados")
        clear_action.triggered.connect(self.clear_results)
        
        # Help menu
        help_menu = menubar.addMenu("Ajuda")
        
        about_action = help_menu.addAction("Sobre")
        about_action.triggered.connect(self.show_about)
    
    def create_results_table(self):
        """Create results table widget"""
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(6)
        self.results_table.setHorizontalHeaderLabels([
            "Arquivo", "Status", "Chave NFe", "Tempo (ms)", "Erros", "Data/Hora"
        ])
        
        # Configure table
        header = self.results_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Arquivo
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Status
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Chave
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Tempo
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Erros
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Data/Hora
        
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        # Set row height to ensure proper visibility of content
        self.results_table.verticalHeader().setDefaultSectionSize(35)
        
        # Optional: Make vertical header (row numbers) wider
        self.results_table.verticalHeader().setFixedWidth(50)
    
    def connect_signals(self):
        """Connect ViewModel signals to UI updates"""
        self.view_model.monitoring_started.connect(self.on_monitoring_started)
        self.view_model.monitoring_stopped.connect(self.on_monitoring_stopped)
        self.view_model.file_processed.connect(self.on_file_processed)
        self.view_model.status_updated.connect(self.on_status_updated)
        self.view_model.validation_result_added.connect(self.on_validation_result_added)
        self.view_model.configuration_changed.connect(self.on_configuration_changed)
        self.view_model.processing_progress.connect(self.on_processing_progress)
    
    def apply_modern_styling(self):
        """Apply modern styling with orange theme"""
        self.setStyleSheet("""
            /* === BASE THEME === */
            #centralWidget {
                background-color: #FAFAFA;
                color: #2C2C2C;
            }
            
            /* === CARDS === */
            #card {
                background-color: #FFFFFF;
                border: none;
                border-radius: 12px;
                padding: 0px;
            }
            
            /* === HEADER === */
            #mainTitle {
                font-size: 28px;
                font-weight: bold;
                color: #FFAB1D;
                margin: 0px;
                padding: 0px;
            }
            
            #subtitle {
                font-size: 14px;
                color: #666666;
                margin-top: 4px;
            }
            
            #statusIndicator {
                font-size: 24px;
                color: #4CAF50;
            }
            
            #statusLabel {
                font-size: 13px;
                font-weight: 600;
                color: #2C2C2C;
                margin-top: 4px;
            }
            
            /* === BUTTONS === */
            #primaryButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FFAB1D, stop:1 #FF8C00);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: 600;
                font-size: 14px;
                min-width: 140px;
            }
            #primaryButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FF8C00, stop:1 #FF7700);
            }
            #primaryButton:pressed {
                background: #FF7700;
            }
            #primaryButton:disabled {
                background-color: #CCCCCC;
                color: #888888;
            }
            
            #secondaryButton {
                background-color: #F5F5F5;
                color: #2C2C2C;
                border: 2px solid #E0E0E0;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: 600;
                font-size: 14px;
                min-width: 140px;
            }
            #secondaryButton:hover {
                background-color: #EEEEEE;
                border-color: #FFAB1D;
                color: #FFAB1D;
            }
            #secondaryButton:pressed {
                background-color: #E8E8E8;
            }
            #secondaryButton:disabled {
                background-color: #F8F8F8;
                color: #CCCCCC;
                border-color: #EEEEEE;
            }
            
            #actionButton {
                background-color: #FFFFFF;
                color: #2C2C2C;
                border: 2px solid #E0E0E0;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: 500;
                font-size: 13px;
                min-width: 120px;
            }
            #actionButton:hover {
                border-color: #FFAB1D;
                color: #FFAB1D;
                background-color: #FFF8E1;
            }
            
            #dangerButton {
                background-color: #FFFFFF;
                color: #E53E3E;
                border: 2px solid #FED7D7;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: 500;
                font-size: 13px;
                min-width: 120px;
            }
            #dangerButton:hover {
                background-color: #FFF5F5;
                border-color: #E53E3E;
            }
            
            #iconButton {
                background-color: #F7F7F7;
                color: #666666;
                border: none;
                border-radius: 6px;
                font-size: 16px;
            }
            #iconButton:hover {
                background-color: #FFAB1D;
                color: white;
            }
            
            /* === STATISTICS CARDS === */
            #statCard {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #FFFFFF, stop:1 #FFF8E1);
                border: 2px solid #FFF3E0;
                border-radius: 12px;
            }
            
            #statIcon {
                font-size: 20px;
                color: #FFAB1D;
            }
            
            #statValue {
                font-size: 24px;
                font-weight: bold;
                color: #2C2C2C;
            }
            
            #statLabel {
                font-size: 12px;
                color: #666666;
                font-weight: 500;
            }
            
            /* === CARD TITLES === */
            #cardTitle {
                font-size: 16px;
                font-weight: 600;
                color: #2C2C2C;
                margin-bottom: 12px;
                padding: 16px 20px 0px 20px;
            }
            
            /* === TABLE === */
            QTableWidget {
                background-color: transparent;
                alternate-background-color: #FAFAFA;
                selection-background-color: #FFF3E0;
                gridline-color: #E8E8E8;
                border: none;
                color: #2C2C2C;
                border-radius: 8px;
                margin: 0px 16px 16px 16px;
            }
            QTableWidget::item {
                color: #2C2C2C;
                padding: 10px 8px;
                border-bottom: 1px solid #F0F0F0;
            }
            QTableWidget::item:selected {
                background-color: #FFF3E0;
                color: #FFAB1D;
            }
            QTableWidget::item:hover {
                background-color: #FFF8E1;
            }
            QHeaderView::section {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FFF8E1, stop:1 #FFF3E0);
                color: #FFAB1D;
                padding: 12px 8px;
                border: none;
                border-bottom: 2px solid #FFAB1D;
                font-weight: 600;
                font-size: 13px;
            }
            
            /* === LOG AREA === */
            #logArea {
                background-color: #FAFAFA;
                color: #2C2C2C;
                border: 2px solid #F0F0F0;
                border-radius: 8px;
                padding: 12px;
                font-family: 'Monaco', 'Inconsolata', 'Roboto Mono', monospace;
                font-size: 12px;
                line-height: 1.4;
                margin: 0px 16px 16px 16px;
                selection-background-color: #FFF3E0;
            }
            
            /* === MENU BAR === */
            QMenuBar {
                background-color: #FAFAFA;
                color: #2C2C2C;
                border-bottom: 1px solid #E8E8E8;
                padding: 4px;
            }
            QMenuBar::item {
                background-color: transparent;
                color: #2C2C2C;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QMenuBar::item:selected {
                background-color: #FFF3E0;
                color: #FFAB1D;
            }
            QMenu {
                background-color: #FFFFFF;
                color: #2C2C2C;
                border: 1px solid #E8E8E8;
                border-radius: 8px;
                padding: 4px 0px;
            }
            QMenu::item {
                color: #2C2C2C;
                padding: 8px 16px;
            }
            QMenu::item:selected {
                background-color: #FFF3E0;
                color: #FFAB1D;
            }
        """)
    
    def update_ui_state(self):
        """Update UI state based on current configuration and monitoring status"""
        is_monitoring = self.view_model.is_monitoring_active
        can_start = self.view_model.can_start_monitoring
        
        self.start_button.setEnabled(not is_monitoring and can_start)
        self.stop_button.setEnabled(is_monitoring)
        
        # Update statistics cards
        summary = self.view_model.get_result_summary()
        
        # Update stat cards
        self.total_card.value_label.setText(str(summary['total']))
        self.success_card.value_label.setText(str(summary['successful']))
        self.error_card.value_label.setText(str(summary['failed']))
        self.rate_card.value_label.setText(f"{summary['success_rate']:.1f}%")
        
        # Update reprocess card count
        try:
            reprocess_count = self._count_reprocess_files()
            self.reprocess_card.value_label.setText(str(reprocess_count))
        except Exception as e:
            print(f"Error updating reprocess count: {e}")
            self.reprocess_card.value_label.setText("0")
        
        # Update status indicator
        if is_monitoring:
            self.status_indicator.setText("●")
            self.status_indicator.setStyleSheet("color: #4CAF50;")  # Green
            self.status_label.setText("Sistema Ativo")
        else:
            self.status_indicator.setText("●")
            self.status_indicator.setStyleSheet("color: #FF6B6B;")  # Red
            self.status_label.setText("Sistema Parado")
    
    # Event handlers
    def start_monitoring(self):
        """Start file monitoring"""
        success = self.view_model.start_monitoring()
        if not success:
            QMessageBox.warning(
                self, 
                "Erro", 
                "Não foi possível iniciar o monitoramento. Verifique as configurações."
            )
    
    def stop_monitoring(self):
        """Stop file monitoring"""
        self.view_model.stop_monitoring()
    
    def process_file_manually(self):
        """Process a file manually"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar arquivo para processar",
            "",
            "Arquivos suportados (*.xml *.zip *.rar *.7z);;Todos os arquivos (*)"
        )
        
        if file_path:
            success = self.view_model.process_file_manually(Path(file_path))
            if not success:
                QMessageBox.warning(self, "Erro", "Falha no processamento do arquivo.")
    
    def open_config_dialog(self):
        """Open configuration dialog"""
        config = self.view_model.configuration
        dialog = ConfigDialog(config, self)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            updated_config = dialog.get_configuration()
            success = self.view_model.save_configuration(updated_config)
            if success:
                QMessageBox.information(self, "Sucesso", "Configuração salva com sucesso!")
            else:
                QMessageBox.warning(self, "Erro", "Erro ao salvar configuração.")
    
    def on_reprocess_card_clicked(self, event):
        """Handle click on reprocess card"""
        try:
            reprocess_count = self._count_reprocess_files()
            
            if reprocess_count == 0:
                QMessageBox.information(self, "Info", "Nenhum arquivo na pasta de reprocessamento.")
                return
            
            reply = QMessageBox.question(
                self,
                "Reprocessar Arquivos",
                f"Deseja reprocessar {reprocess_count} arquivo(s) da pasta de reprocessamento?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self._reprocess_failed_files()
                
        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Erro ao reprocessar arquivos: {e}")
    
    def clear_results(self):
        """Clear all results"""
        reply = QMessageBox.question(
            self,
            "Confirmar",
            "Tem certeza que deseja limpar todos os resultados?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.view_model.clear_results()
            self.results_table.setRowCount(0)
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "Sobre Monitor NFe",
            "<h3>Monitor NFe - ValidaTech</h3>"
            "<p>Versão 2.0 - Clean Architecture</p>"
            "<p>Sistema para monitoramento e validação de arquivos NFe</p>"
            "<p>© 2024 ValidaTech</p>"
        )
    
    # Signal handlers
    def on_monitoring_started(self, folder_path: str):
        """Handle monitoring started signal"""
        self.status_label.setText(f"Monitorando: {Path(folder_path).name}")
        self.status_label.setStyleSheet("color: green; font-weight: bold;")
        self.update_ui_state()
        self.add_log_entry(f"✅ Monitoramento iniciado: {folder_path}")
    
    def on_monitoring_stopped(self):
        """Handle monitoring stopped signal"""
        self.status_label.setText("Monitoramento parado")
        self.status_label.setStyleSheet("color: orange; font-weight: bold;")
        self.update_ui_state()
        self.add_log_entry("🛑 Monitoramento parado")
    
    def on_file_processed(self, filename: str, success: bool):
        """Handle file processed signal"""
        status_icon = "✅" if success else "❌"
        self.add_log_entry(f"{status_icon} Arquivo processado: {filename}")
        self.update_ui_state()
    
    def on_status_updated(self, message: str):
        """Handle status update signal"""
        self.add_log_entry(f"ℹ️  {message}")
    
    def on_validation_result_added(self, result):
        """Handle validation result added signal"""
        row = self.results_table.rowCount()
        self.results_table.insertRow(row)
        
        # Filename
        filename_item = QTableWidgetItem(Path(result.document_path).name)
        self.results_table.setItem(row, 0, filename_item)
        
        # Status - with specific icons for different error types
        status_text, status_color = self._get_status_display(result)
        status_item = QTableWidgetItem(status_text)
        status_item.setForeground(QColor(status_color))
        self.results_table.setItem(row, 1, status_item)
        
        # NFe Key
        key_item = QTableWidgetItem(result.nfe_key or "N/A")
        self.results_table.setItem(row, 2, key_item)
        
        # Processing time
        time_text = f"{result.processing_time_ms or 0:.0f}" if result.processing_time_ms else "N/A"
        time_item = QTableWidgetItem(time_text)
        self.results_table.setItem(row, 3, time_item)
        
        # Error count
        error_item = QTableWidgetItem(str(result.error_count))
        self.results_table.setItem(row, 4, error_item)
        
        # Timestamp
        timestamp_item = QTableWidgetItem(result.validated_at.strftime("%H:%M:%S"))
        self.results_table.setItem(row, 5, timestamp_item)
        
        # Scroll to new row
        self.results_table.scrollToBottom()
        
        # Add detailed log entry with error information
        self._add_detailed_validation_log(result)
    
    def on_configuration_changed(self):
        """Handle configuration changed signal"""
        self.update_ui_state()
    
    def on_processing_progress(self, session_id: str, processed: int, total: int):
        """Handle parallel processing progress updates"""
        progress_msg = f"📊 Processamento paralelo ({session_id[:6]}): {processed}/{total} arquivo(s)"
        self.add_log_entry(progress_msg)
        
        # Update status bar with progress
        if total > 0:
            progress_pct = (processed / total) * 100
            self.status_bar.showMessage(f"Processando... {progress_pct:.0f}% ({processed}/{total})")
    
    def add_log_entry(self, message: str):
        """Add entry to log area"""
        from datetime import datetime
        from PySide6.QtGui import QTextCursor
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.log_text.append(log_entry)
        
        # Auto-scroll to bottom
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.log_text.setTextCursor(cursor)
    
    def _add_detailed_validation_log(self, result):
        """Add detailed validation log with error information"""
        filename = Path(result.document_path).name
        
        if result.is_valid:
            self.add_log_entry(f"✅ {filename} - Validação bem-sucedida")
            if result.nfe_key:
                self.add_log_entry(f"   🔑 Chave NFe: {result.nfe_key}")
            if result.processing_time_ms:
                self.add_log_entry(f"   ⏱️  Tempo processamento: {result.processing_time_ms:.0f}ms")
        else:
            self.add_log_entry(f"❌ {filename} - Validação FALHOU ({result.error_count} erro(s))")
            
            # Add specific error details
            for error in result.errors:
                error_icon = self._get_error_icon(error.error_type.value)
                self.add_log_entry(f"   {error_icon} {error.error_type.value.upper()}: {error.message}")
                if error.details:
                    self.add_log_entry(f"      💡 {error.details}")
                if error.line_number:
                    self.add_log_entry(f"      📍 Linha: {error.line_number}")
    
    def _get_error_icon(self, error_type: str) -> str:
        """Get appropriate icon for error type"""
        icons = {
            'SCHEMA': '📋',
            'API': '🌐', 
            'STRUCTURE': '🏗️',
            'BUSINESS': '💼',
            'DOCUMENT': '📄'
        }
        return icons.get(error_type.upper(), '⚠️')
    
    def _get_status_display(self, result) -> tuple[str, str]:
        """Get status display text and color based on validation result"""
        if result.is_valid:
            return "✅ Válido", "green"
        
        # Check for specific error types
        for error in result.errors:
            if error.error_type.value == 'api':
                # Check for "already exists" messages
                if any(keyword in error.message.lower() for keyword in ['já existe', 'already exists', 'duplicate']):
                    return "⚠️ Já enviado", "orange"
                # Check for signature/digital signature errors
                elif any(keyword in error.message.lower() for keyword in ['assinatura', 'signature', 'digital']):
                    return "🔒 Assinatura inválida", "red"
                elif any(keyword in error.message.lower() for keyword in ['servidor', 'server', 'timeout']):
                    return "🔄 Erro servidor", "purple"
                else:
                    return "🌐 Erro API", "red"
            elif error.error_type.value == 'schema':
                return "📋 Erro schema", "red"
            elif error.error_type.value == 'structure':
                # Show specific structure error message
                error_msg = error.message.lower()
                if "não encontrado" in error_msg:
                    return "📄 Arquivo não encontrado", "red"
                elif "muito pequeno" in error_msg:
                    return "📏 Arquivo pequeno", "red"
                elif "muito grande" in error_msg:
                    return "📏 Arquivo grande", "red"
                elif "encoding" in error_msg:
                    return "🔤 Erro encoding", "red"
                elif "declaração xml" in error_msg:
                    return "📋 XML inválido", "red"
                elif "conteúdo nfe" in error_msg:
                    return "📄 Não é NFe", "red"
                elif "chave nfe" in error_msg:
                    return "🔑 Chave ausente", "red"
                else:
                    return "🏗️ Erro estrutura", "red"
        
        # Default for other error types
        return "❌ Inválido", "red"
    
    def closeEvent(self, event):
        """Handle window close event"""
        if self.view_model.is_monitoring_active:
            reply = QMessageBox.question(
                self,
                "Confirmar saída",
                "O monitoramento está ativo. Deseja realmente sair?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.No:
                event.ignore()
                return
        
        # Stop monitoring and cleanup
        self.view_model.stop_monitoring()
        event.accept()
    
    def _count_reprocess_files(self) -> int:
        """Count files in reprocess folder"""
        try:
            if not self.view_model.configuration.output_path:
                return 0
            
            reprocess_folder = Path(self.view_model.configuration.output_path) / "reprocess"
            if not reprocess_folder.exists():
                return 0
            
            count = 0
            for file_path in reprocess_folder.iterdir():
                if file_path.is_file() and file_path.suffix.lower() in {'.xml', '.zip', '.rar', '.7z'}:
                    count += 1
            
            return count
        except Exception:
            return 0
    
    def _reprocess_failed_files(self):
        """Reprocess files from reprocess folder"""
        try:
            if not self.view_model.configuration.output_path:
                return
            
            reprocess_folder = Path(self.view_model.configuration.output_path) / "reprocess"
            if not reprocess_folder.exists():
                return
            
            # Get all reprocess files
            files_to_process = []
            for file_path in reprocess_folder.iterdir():
                if file_path.is_file() and file_path.suffix.lower() in {'.xml', '.zip', '.rar', '.7z'}:
                    files_to_process.append(file_path)
            
            if not files_to_process:
                return
            
            self.add_log_entry(f"🔄 Iniciando reprocessamento de {len(files_to_process)} arquivo(s)")
            
            # Process each file
            processed_count = 0
            for file_path in files_to_process:
                try:
                    self.add_log_entry(f"🔄 Reprocessando: {file_path.name}")
                    QApplication.processEvents()
                    
                    # Process the file
                    success = self.view_model.process_file_manually(file_path)
                    
                    if success:
                        # Remove from reprocess folder only if successful
                        file_path.unlink()
                        processed_count += 1
                        self.add_log_entry(f"✅ Reprocessado com sucesso: {file_path.name}")
                    else:
                        self.add_log_entry(f"❌ Falha no reprocessamento: {file_path.name}")
                    
                    QApplication.processEvents()
                    
                except Exception as e:
                    self.add_log_entry(f"❌ Erro ao reprocessar {file_path.name}: {e}")
            
            self.add_log_entry(f"✅ Reprocessamento concluído: {processed_count}/{len(files_to_process)} arquivo(s)")
            self.update_ui_state()
            
        except Exception as e:
            self.add_log_entry(f"❌ Erro no reprocessamento: {e}")


def main():
    """Main application entry point"""
    try:
        # Set Brazilian locale for date/time formatting
        try:
            locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
        except:
            try:
                locale.setlocale(locale.LC_TIME, 'pt_BR')
            except:
                pass  # Keep default if Brazilian locale not available
        
        # Create QApplication
        app = QApplication(sys.argv)
        
        # Initialize dependency container
        print("🚀 Inicializando Monitor NFe - Clean Architecture")
        
        # Find schemas folder
        schemas_folder = Path(__file__).parent / 'schemas'
        container = DependencyContainer(schemas_folder)
        
        # Initialize services
        if not container.initialize_services():
            print("❌ Falha na inicialização dos serviços")
            sys.exit(1)
        
        # Create main window
        view_model = container.get('main_view_model')
        main_window = MainWindow(view_model)
        main_window.show()
        
        print("✅ Aplicação inicializada com sucesso")
        
        # Run application
        try:
            result = app.exec()
        finally:
            # Cleanup
            container.cleanup()
            print("👋 Aplicação finalizada")
        
        return result
        
    except Exception as e:
        print(f"❌ Erro fatal na aplicação: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())