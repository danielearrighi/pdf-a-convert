import os
from pathlib import Path
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QMessageBox, QTextEdit, QDialog, QSizePolicy
)
from PyQt6.QtGui import QIcon, QFont

from core.config import ConfigManager
from core.converter import PDFConverterThread
from core.utils import open_file, open_folder, get_asset_path
from gui.drop_widget import DropAreaWidget
from gui.loader_widget import LoaderWidget
from gui.settings_dialog import SettingsDialog
from gui.theme import get_main_window_style, apply_app_palette, Theme

class LogDetailsDialog(QDialog):
    """Modal dialog to show detailed Ghostscript execution output logs."""
    def __init__(self, log_text: str, theme: str = Theme.LIGHT, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Dettagli Log Conversione")
        self.setMinimumSize(600, 400)
        
        if theme == Theme.DARK:
            self.setStyleSheet("QDialog { background-color: #0F172A; color: #F8FAFC; } QTextEdit { background-color: #1E293B; color: #F8FAFC; border: 1px solid #334155; } QPushButton { background-color: #334155; color: #F8FAFC; border: 1px solid #475569; padding: 6px 14px; border-radius: 6px; }")
        
        layout = QVBoxLayout(self)
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setFont(QFont("Monospace", 9))
        text_edit.setPlainText(log_text)
        layout.addWidget(text_edit)
        
        close_btn = QPushButton("Chiudi")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignRight)

class MainWindow(QMainWindow):
    """
    Main Application Window for PDF/A Converter.
    """
    def __init__(self):
        super().__init__()
        self.config = ConfigManager()
        self.converter_thread = None
        self.last_output_file = ""

        self.setWindowTitle("PDF/A Converter - Pubblica Amministrazione")
        self.setMinimumSize(540, 520)
        self.resize(600, 580)

        icon_path = get_asset_path("app_icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Central Widget & Main Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 20, 10, 20)
        main_layout.setSpacing(16)

        # 1. Header Bar
        header_frame = QFrame()
        header_frame.setObjectName("HeaderFrame")
        header_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 0, 0)

        header_titles = QVBoxLayout()
        self.title_label = QLabel("PDF/A Converter")
        self.subtitle_label = QLabel("Conversione Standard PDF/A-1b per la Pubblica Amministrazione")
        header_titles.addWidget(self.title_label)
        header_titles.addWidget(self.subtitle_label)

        self.settings_btn = QPushButton("⚙️ Impostazioni")
        self.settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.settings_btn.clicked.connect(self._open_settings)

        header_layout.addLayout(header_titles, stretch=1)
        header_layout.addWidget(self.settings_btn)

        main_layout.addWidget(header_frame, 0)

        # 2. Main Content Container
        content_container = QFrame()
        content_container.setObjectName("MainContainer")
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(8, 16, 8, 16)
        content_layout.setSpacing(16)

        # Drop Area
        self.drop_widget = DropAreaWidget()
        self.drop_widget.file_selected.connect(self._on_file_selected)
        content_layout.addWidget(self.drop_widget)

        # Loader Widget (Hidden by default)
        self.loader_widget = LoaderWidget()
        self.loader_widget.hide()
        content_layout.addWidget(self.loader_widget)

        # Action Convert Button
        self.convert_btn = QPushButton("Converti in PDF/A-1b")
        self.convert_btn.setObjectName("ConvertBtn")
        self.convert_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.convert_btn.setEnabled(False)
        self.convert_btn.clicked.connect(self._start_conversion)
        content_layout.addWidget(self.convert_btn)

        # 3. Success Banner (Hidden by default)
        self.success_banner = QFrame()
        self.success_banner.setObjectName("SuccessBanner")
        success_layout = QVBoxLayout(self.success_banner)
        success_layout.setContentsMargins(8, 16, 8, 16)
        success_layout.setSpacing(10)
        
        self.success_title = QLabel("🎉 Conversione completata con successo!")
        self.success_title.setStyleSheet("font-weight: bold; font-size: 16px; color: #166534;")
        
        self.success_path_label = QLabel("")
        self.success_path_label.setStyleSheet("font-size: 13px; color: #15803D; margin-top: 2px; margin-bottom: 4px;")
        self.success_path_label.setWordWrap(True)
        self.success_path_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        success_actions = QHBoxLayout()
        open_file_btn = QPushButton("📄 Apri File")
        open_file_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        open_file_btn.setStyleSheet("""
            QPushButton {
                background-color: #166534; color: white; font-weight: bold;
                border-radius: 6px; padding: 6px 12px; border: none;
            }
            QPushButton:hover { background-color: #14532D; }
        """)
        open_file_btn.clicked.connect(self._open_output_file)

        open_folder_btn = QPushButton("📁 Apri Cartella")
        open_folder_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        open_folder_btn.setStyleSheet("""
            QPushButton {
                background-color: #DCFCE7; color: #166534; font-weight: bold;
                border-radius: 6px; padding: 6px 12px; border: 1px solid #86EFAC;
            }
            QPushButton:hover { background-color: #BBF7D0; }
        """)
        open_folder_btn.clicked.connect(self._open_output_folder)

        convert_new_btn = QPushButton("🔄 Converti nuovo")
        convert_new_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        convert_new_btn.setStyleSheet("""
            QPushButton {
                background-color: #DCFCE7; color: #166534; font-weight: bold;
                border-radius: 6px; padding: 6px 12px; border: 1px solid #86EFAC;
            }
            QPushButton:hover { background-color: #BBF7D0; }
        """)
        convert_new_btn.clicked.connect(self._reset_ui)

        success_actions.addWidget(open_file_btn)
        success_actions.addWidget(open_folder_btn)
        success_actions.addWidget(convert_new_btn)
        success_actions.addStretch()

        success_layout.addWidget(self.success_title)
        success_layout.addWidget(self.success_path_label)
        success_layout.addLayout(success_actions)
        self.success_banner.hide()

        content_layout.addWidget(self.success_banner)

        # 4. Error Banner (Hidden by default)
        self.error_banner = QFrame()
        self.error_banner.setObjectName("ErrorBanner")
        error_layout = QVBoxLayout(self.error_banner)
        error_layout.setContentsMargins(8, 16, 8, 16)
        error_layout.setSpacing(10)

        self.error_title = QLabel("❌ Errore durante la conversione")
        self.error_title.setStyleSheet("font-weight: bold; font-size: 16px; color: #991B1B;")

        self.error_desc_label = QLabel("")
        self.error_desc_label.setStyleSheet("font-size: 13px; color: #B91C1C; margin-top: 2px; margin-bottom: 4px;")
        self.error_desc_label.setWordWrap(True)
        self.error_desc_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        error_actions = QHBoxLayout()
        self.log_btn = QPushButton("📋 Dettagli Log")
        self.log_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.log_btn.setStyleSheet("""
            QPushButton {
                background-color: #991B1B; color: white; font-weight: bold;
                border-radius: 6px; padding: 6px 12px; border: none;
            }
            QPushButton:hover { background-color: #7F1D1D; }
        """)
        self.last_log_output = ""
        self.log_btn.clicked.connect(self._show_log_dialog)

        error_actions.addWidget(self.log_btn)

        convert_new_err_btn = QPushButton("🔄 Converti nuovo")
        convert_new_err_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        convert_new_err_btn.setStyleSheet("""
            QPushButton {
                background-color: #FEF2F2; color: #991B1B; font-weight: bold;
                border-radius: 6px; padding: 6px 12px; border: 1px solid #FCA5A5;
            }
            QPushButton:hover { background-color: #FEE2E2; }
        """)
        convert_new_err_btn.clicked.connect(self._reset_ui)
        error_actions.addWidget(convert_new_err_btn)

        error_actions.addStretch()

        error_layout.addWidget(self.error_title)
        error_layout.addWidget(self.error_desc_label)
        error_layout.addLayout(error_actions)
        self.error_banner.hide()

        content_layout.addWidget(self.error_banner)

        main_layout.addWidget(content_container, stretch=1)

        # Apply saved user theme preference on startup
        self.apply_theme(self.config.theme)

    def apply_theme(self, theme: str):
        from PyQt6.QtWidgets import QApplication
        apply_app_palette(QApplication.instance(), theme)
        self.setStyleSheet(get_main_window_style(theme))
        self.drop_widget.apply_theme(theme)
        self.loader_widget.apply_theme(theme)

        if theme == Theme.DARK:
            self.title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #F8FAFC;")
            self.subtitle_label.setStyleSheet("font-size: 12px; color: #94A3B8;")
            self.settings_btn.setStyleSheet("""
                QPushButton {
                    background-color: #1E293B;
                    color: #F8FAFC;
                    border: 1px solid #475569;
                    border-radius: 8px;
                    padding: 8px 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #334155;
                }
            """)
            self.success_title.setStyleSheet("font-weight: bold; font-size: 16px; color: #A7F3D0;")
            self.success_path_label.setStyleSheet("font-size: 13px; color: #D1FAE5; margin-top: 2px; margin-bottom: 4px;")
            self.error_title.setStyleSheet("font-weight: bold; font-size: 16px; color: #FECACA;")
            self.error_desc_label.setStyleSheet("font-size: 13px; color: #FCA5A5; margin-top: 2px; margin-bottom: 4px;")
        else:
            self.title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #0F172A;")
            self.subtitle_label.setStyleSheet("font-size: 12px; color: #64748B;")
            self.settings_btn.setStyleSheet("""
                QPushButton {
                    background-color: #F8FAFC;
                    color: #334155;
                    border: 1px solid #CBD5E1;
                    border-radius: 8px;
                    padding: 8px 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #E2E8F0;
                }
            """)
            self.success_title.setStyleSheet("font-weight: bold; font-size: 16px; color: #166534;")
            self.success_path_label.setStyleSheet("font-size: 13px; color: #15803D; margin-top: 2px; margin-bottom: 4px;")
            self.error_title.setStyleSheet("font-weight: bold; font-size: 16px; color: #991B1B;")
            self.error_desc_label.setStyleSheet("font-size: 13px; color: #B91C1C; margin-top: 2px; margin-bottom: 4px;")

    def _on_file_selected(self, file_path: str):
        self.success_banner.hide()
        self.error_banner.hide()
        self.convert_btn.setEnabled(bool(file_path))

    def _open_settings(self):
        dialog = SettingsDialog(self.config, self)
        dialog.exec()

    def _start_conversion(self):
        input_file = self.drop_widget.current_file_path
        if not input_file or not os.path.isfile(input_file):
            QMessageBox.warning(self, "Attenzione", "Seleziona un file PDF valido prima di procedere.")
            return

        gs_path = self.config.ghostscript_path
        if not gs_path or not os.path.isfile(gs_path):
            QMessageBox.critical(
                self,
                "Ghostscript Non Trovato",
                "Impossibile trovare l'eseguibile Ghostscript.\n\n"
                "Apri le Impostazioni per specificare il percorso di Ghostscript."
            )
            self._open_settings()
            return

        # UI state during conversion
        self.drop_widget.hide()
        self.convert_btn.hide()
        self.success_banner.hide()
        self.error_banner.hide()

        self.loader_widget.set_status("Avvio del processo Ghostscript...")
        self.loader_widget.show()

        # Launch worker thread
        self.converter_thread = PDFConverterThread(
            input_file=input_file,
            gs_path=gs_path,
            icc_path=self.config.icc_profile_path,
            pdfa_level=self.config.pdfa_level,
            extra_args=self.config.extra_gs_args,
            parent=self
        )
        self.converter_thread.progress.connect(self.loader_widget.set_status)
        self.converter_thread.finished.connect(self._on_conversion_finished)
        self.converter_thread.start()

    def _on_conversion_finished(self, success: bool, output_file: str, log_message: str):
        self.loader_widget.hide()
        self.drop_widget.show()
        self.convert_btn.show()

        if success:
            self.last_output_file = output_file
            self.success_path_label.setText(f"File salvato in:\n{output_file}")
            self.success_banner.show()
        else:
            self.last_log_output = log_message
            # Display first 200 chars of error message
            short_msg = log_message.split("\nLog:")[0] if "\nLog:" in log_message else log_message
            self.error_desc_label.setText(short_msg[:300])
            self.error_banner.show()

    def _open_output_file(self):
        if self.last_output_file and os.path.isfile(self.last_output_file):
            open_file(self.last_output_file)

    def _open_output_folder(self):
        if self.last_output_file:
            open_folder(self.last_output_file)

    def _show_log_dialog(self):
        if self.last_log_output:
            dialog = LogDetailsDialog(self.last_log_output, theme=self.config.theme, parent=self)
            dialog.exec()

    def _reset_ui(self):
        self.drop_widget.clear_file()
        self.drop_widget.show()
        self.loader_widget.hide()
        self.convert_btn.show()
        self.convert_btn.setEnabled(False)
        self.success_banner.hide()
        self.error_banner.hide()
        self.last_output_file = ""
        self.last_log_output = ""


