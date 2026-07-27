import os
import subprocess
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFileDialog, QComboBox, QMessageBox, QGroupBox,
    QStyledItemDelegate, QFrame
)
from core.config import ConfigManager
from core.utils import find_ghostscript_executable, find_system_icc_profile
from gui.theme import get_settings_dialog_style, Theme

class SettingsDialog(QDialog):
    """
    Configuration dialog to customize Ghostscript executable path, ICC profile path, parameters, and UI Theme.
    """
    def __init__(self, config_manager: ConfigManager, parent=None):
        super().__init__(parent)
        self.config = config_manager
        self.setWindowTitle("Configurazione PDF/A Converter")
        self.setMinimumWidth(620)
        
        # Apply stylesheet based on current theme setting
        self.setStyleSheet(get_settings_dialog_style(self.config.theme))

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(10, 20, 10, 20)

        # 1. Path Configuration Section
        paths_group = QGroupBox("Percorsi di Sistema")
        paths_layout = QVBoxLayout(paths_group)
        paths_layout.setSpacing(14)
        paths_layout.setContentsMargins(8, 20, 8, 16)

        # Ghostscript path row
        gs_field_layout = QVBoxLayout()
        gs_label = QLabel("Eseguibile Ghostscript (gs / gswin64c.exe):")
        
        self.gs_edit = QLineEdit(self.config.ghostscript_path)
        self.gs_edit.setPlaceholderText("Es. /usr/bin/gs oppure C:\\Program Files\\gs\\...\\gswin64c.exe")
        
        gs_browse_btn = QPushButton("Sfoglia...")
        gs_browse_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        gs_browse_btn.clicked.connect(self._browse_gs_path)

        gs_auto_btn = QPushButton("Rileva")
        gs_auto_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        gs_auto_btn.setToolTip("Rileva automaticamente il percorso di Ghostscript nel sistema")
        gs_auto_btn.clicked.connect(self._auto_detect_gs)

        gs_test_btn = QPushButton("Test Eseguibile")
        gs_test_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        gs_test_btn.setToolTip("Testa l'eseguibile Ghostscript specificato")
        gs_test_btn.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6;
                color: white;
                font-weight: bold;
                padding: 9px 16px;
                border-radius: 6px;
                border: none;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #2563EB;
            }
            QPushButton:pressed {
                background-color: #1D4ED8;
            }
        """)
        gs_test_btn.clicked.connect(self._test_ghostscript)

        gs_box = QHBoxLayout()
        gs_box.setSpacing(8)
        gs_box.addWidget(self.gs_edit, stretch=1)
        gs_box.addWidget(gs_browse_btn)
        gs_box.addWidget(gs_auto_btn)
        gs_box.addWidget(gs_test_btn)

        gs_field_layout.addWidget(gs_label)
        gs_field_layout.addLayout(gs_box)
        paths_layout.addLayout(gs_field_layout)

        # ICC Profile path row
        icc_field_layout = QVBoxLayout()
        icc_label = QLabel("Profilo Colore ICC (sRGB):")
        
        self.icc_edit = QLineEdit(self.config.icc_profile_path)
        self.icc_edit.setPlaceholderText("Es. /usr/share/color/icc/sRGB.icc")

        icc_browse_btn = QPushButton("Sfoglia...")
        icc_browse_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        icc_browse_btn.clicked.connect(self._browse_icc_path)

        icc_auto_btn = QPushButton("Rileva")
        icc_auto_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        icc_auto_btn.setToolTip("Rileva automaticamente il profilo sRGB del sistema")
        icc_auto_btn.clicked.connect(self._auto_detect_icc)

        icc_box = QHBoxLayout()
        icc_box.setSpacing(8)
        icc_box.addWidget(self.icc_edit, stretch=1)
        icc_box.addWidget(icc_browse_btn)
        icc_box.addWidget(icc_auto_btn)

        icc_field_layout.addWidget(icc_label)
        icc_field_layout.addLayout(icc_box)
        paths_layout.addLayout(icc_field_layout)

        main_layout.addWidget(paths_group)

        # 2. Conversion Options Section
        options_group = QGroupBox("Opzioni di Conversione")
        options_layout = QVBoxLayout(options_group)
        options_layout.setSpacing(14)
        options_layout.setContentsMargins(8, 20, 8, 16)

        # PDF/A version selection row
        pdfa_field_layout = QVBoxLayout()
        pdfa_label = QLabel("Standard PDF/A:")
        
        self.pdfa_combo = QComboBox()
        self.pdfa_combo.setItemDelegate(QStyledItemDelegate(self.pdfa_combo))
        
        # Remove inner QFrame margins from combo popup view
        combo_view = self.pdfa_combo.view()
        if combo_view:
            combo_view.setFrameShape(QFrame.Shape.NoFrame)
            combo_view.setLineWidth(0)
            combo_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.pdfa_combo.addItem("PDF/A-1b (Consigliato PA / Standard)", "1b")
        self.pdfa_combo.addItem("PDF/A-2b (Supporta Trasparenze)", "2b")
        
        current_level = self.config.pdfa_level
        index = self.pdfa_combo.findData(current_level)
        if index >= 0:
            self.pdfa_combo.setCurrentIndex(index)

        pdfa_field_layout.addWidget(pdfa_label)
        pdfa_field_layout.addWidget(self.pdfa_combo)
        options_layout.addLayout(pdfa_field_layout)

        # Output Suffix row
        suffix_field_layout = QVBoxLayout()
        suffix_label = QLabel("Suffisso File Convertiti:")
        
        self.suffix_edit = QLineEdit(self.config.output_suffix)
        self.suffix_edit.setPlaceholderText("Es. -pdfa oppure _pdfa")

        suffix_field_layout.addWidget(suffix_label)
        suffix_field_layout.addWidget(self.suffix_edit)
        options_layout.addLayout(suffix_field_layout)

        # Extra Ghostscript args row
        extra_field_layout = QVBoxLayout()
        extra_label = QLabel("Argomenti Extra Ghostscript:")
        
        self.extra_args_edit = QLineEdit(self.config.extra_gs_args)
        self.extra_args_edit.setPlaceholderText("Es. -dPDFSETTINGS=/prepress")

        extra_field_layout.addWidget(extra_label)
        extra_field_layout.addWidget(self.extra_args_edit)
        options_layout.addLayout(extra_field_layout)

        main_layout.addWidget(options_group)

        # 3. UI Theme Section
        theme_group = QGroupBox("Interfaccia e Tema")
        theme_layout = QVBoxLayout(theme_group)
        theme_layout.setSpacing(14)
        theme_layout.setContentsMargins(8, 20, 8, 16)

        theme_field_layout = QVBoxLayout()
        theme_label = QLabel("Tema Grafico Interfaccia:")
        
        self.theme_combo = QComboBox()
        self.theme_combo.setItemDelegate(QStyledItemDelegate(self.theme_combo))
        theme_view = self.theme_combo.view()
        if theme_view:
            theme_view.setFrameShape(QFrame.Shape.NoFrame)
            theme_view.setLineWidth(0)
            theme_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.theme_combo.addItem("Tema Chiaro (Light)", Theme.LIGHT)
        self.theme_combo.addItem("Tema Scuro (Dark)", Theme.DARK)

        current_theme = self.config.theme
        t_index = self.theme_combo.findData(current_theme)
        if t_index >= 0:
            self.theme_combo.setCurrentIndex(t_index)

        self.theme_combo.currentIndexChanged.connect(self._on_theme_changed)

        theme_field_layout.addWidget(theme_label)
        theme_field_layout.addWidget(self.theme_combo)
        theme_layout.addLayout(theme_field_layout)

        main_layout.addWidget(theme_group)

        # 4. Bottom Utility Actions & Dialog Buttons
        bottom_layout = QHBoxLayout()
        
        reset_btn = QPushButton("Ripristina Predefiniti")
        reset_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        reset_btn.clicked.connect(self._reset_defaults)

        bottom_layout.addWidget(reset_btn)
        bottom_layout.addStretch()

        cancel_btn = QPushButton("Annulla")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)

        save_btn = QPushButton("Salva Impostazioni")
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.clicked.connect(self._save_settings)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6;
                color: white;
                font-weight: bold;
                padding: 9px 16px;
                border-radius: 6px;
                border: none;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #2563EB;
            }
            QPushButton:pressed {
                background-color: #1D4ED8;
            }
        """)

        bottom_layout.addWidget(cancel_btn)
        bottom_layout.addWidget(save_btn)

        main_layout.addLayout(bottom_layout)

    def _on_theme_changed(self):
        selected_theme = self.theme_combo.currentData()
        self.setStyleSheet(get_settings_dialog_style(selected_theme))

    def _browse_gs_path(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Seleziona Eseguibile Ghostscript", "", "Eseguibile (* *exe *gs*);;Tutti i File (*)"
        )
        if file_path:
            self.gs_edit.setText(file_path)

    def _auto_detect_gs(self):
        detected = find_ghostscript_executable()
        if detected:
            self.gs_edit.setText(detected)
            QMessageBox.information(self, "Ghostscript Rilevato", f"Trovato Ghostscript in:\n{detected}")
        else:
            QMessageBox.warning(self, "Non Trovato", "Impossibile trovare Ghostscript automaticamente nei percorsi standard.")

    def _browse_icc_path(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Seleziona Profilo Colore ICC", "", "Profilo ICC (*.icc *.icm);;Tutti i File (*)"
        )
        if file_path:
            self.icc_edit.setText(file_path)

    def _auto_detect_icc(self):
        detected = find_system_icc_profile()
        if detected:
            self.icc_edit.setText(detected)
            QMessageBox.information(self, "Profilo ICC Rilevato", f"Trovato profilo ICC in:\n{detected}")
        else:
            QMessageBox.warning(self, "Non Trovato", "Impossibile trovare un profilo ICC sRGB standard nel sistema.")

    def _test_ghostscript(self):
        gs_path = self.gs_edit.text().strip()
        if not gs_path or not os.path.isfile(gs_path):
            QMessageBox.critical(self, "Errore", "Il percorso di Ghostscript specificato non è un file valido.")
            return

        try:
            res = subprocess.run([gs_path, "--version"], capture_output=True, text=True, timeout=5)
            if res.returncode == 0:
                ver = res.stdout.strip()
                QMessageBox.information(self, "Test Ghostscript Riuscito", f"Ghostscript funziona correttamente!\n\nVersione rilevata: {ver}")
            else:
                QMessageBox.warning(self, "Test Fallito", f"Ghostscript ha risposto con errore:\n{res.stderr}")
        except Exception as e:
            QMessageBox.critical(self, "Errore di Esecuzione", f"Impossibile eseguire Ghostscript:\n{str(e)}")

    def _reset_defaults(self):
        self.config.reset_to_defaults()
        self.gs_edit.setText(self.config.ghostscript_path)
        self.icc_edit.setText(self.config.icc_profile_path)
        self.pdfa_combo.setCurrentIndex(0)
        self.suffix_edit.setText(self.config.output_suffix)
        self.extra_args_edit.setText("")
        self.theme_combo.setCurrentIndex(0)

    def _save_settings(self):
        self.config.ghostscript_path = self.gs_edit.text().strip()
        self.config.icc_profile_path = self.icc_edit.text().strip()
        self.config.pdfa_level = self.pdfa_combo.currentData()
        self.config.output_suffix = self.suffix_edit.text().strip() or "-pdfa"
        self.config.extra_gs_args = self.extra_args_edit.text().strip()
        self.config.theme = self.theme_combo.currentData()
        if self.parent() and hasattr(self.parent(), "apply_theme"):
            self.parent().apply_theme(self.config.theme)
        self.accept()

