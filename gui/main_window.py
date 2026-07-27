import os
from pathlib import Path
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QMessageBox, QTextEdit, QDialog, QSizePolicy
)
from PyQt6.QtGui import QIcon, QFont, QPixmap

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
        self.setMinimumSize(540, 580)
        self.resize(600, 620)

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
        header_layout.setContentsMargins(12, 10, 12, 10)
        header_layout.setSpacing(14)

        if os.path.exists(icon_path):
            self.header_icon = QLabel()
            pixmap = QPixmap(icon_path)
            self.header_icon.setPixmap(
                pixmap.scaled(44, 44, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            )
            header_layout.addWidget(self.header_icon, 0, Qt.AlignmentFlag.AlignVCenter)

        header_titles = QVBoxLayout()
        header_titles.setSpacing(2)
        self.title_label = QLabel("PDF/A Converter")
        self.subtitle_label = QLabel("Conversione Standard PDF/A-1b per la PA")
        header_titles.addWidget(self.title_label)
        header_titles.addWidget(self.subtitle_label)

        self.settings_btn = QPushButton("⚙️ Impostazioni")
        self.settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.settings_btn.clicked.connect(self._open_settings)

        header_layout.addLayout(header_titles, stretch=1)
        header_layout.addWidget(self.settings_btn, 0, Qt.AlignmentFlag.AlignVCenter)

        main_layout.addWidget(header_frame, 0)

        # 2. Main Content Container
        content_container = QFrame()
        content_container.setObjectName("MainContainer")
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(8, 16, 8, 16)
        content_layout.setSpacing(16)

        # Drop Area (Espandibile per riempire lo spazio verticale fino al pulsante)
        self.drop_widget = DropAreaWidget()
        self.drop_widget.files_selected.connect(self._on_files_selected)
        content_layout.addWidget(self.drop_widget, stretch=1)

        # Loader Widget (Hidden by default)
        self.loader_widget = LoaderWidget()
        self.loader_widget.hide()
        content_layout.addWidget(self.loader_widget, stretch=1)

        # 3. Success Banner (Hidden by default, allineato in alto)
        self.success_banner = QFrame()
        self.success_banner.setObjectName("SuccessBanner")
        self.success_banner.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.success_banner.setMaximumHeight(250)
        success_layout = QVBoxLayout(self.success_banner)
        success_layout.setContentsMargins(14, 12, 14, 12)
        success_layout.setSpacing(8)
        
        self.success_title = QLabel("🎉 Conversione completata con successo!")
        self.success_title.setStyleSheet("font-weight: bold; font-size: 15px; color: #166534;")
        
        self.success_path_label = QLabel("")
        self.success_path_label.setStyleSheet("font-size: 12px; color: #15803D; margin-top: 1px; margin-bottom: 2px;")
        self.success_path_label.setWordWrap(True)
        self.success_path_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        success_actions = QHBoxLayout()
        self.open_file_btn = QPushButton("📄 Apri File")
        self.open_file_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.open_file_btn.setStyleSheet("""
            QPushButton {
                background-color: #166534; color: white; font-weight: bold;
                border-radius: 6px; padding: 5px 12px; border: none; font-size: 12px;
            }
            QPushButton:hover { background-color: #14532D; }
        """)
        self.open_file_btn.clicked.connect(self._open_output_file)

        self.open_folder_btn = QPushButton("📁 Apri Cartella")
        self.open_folder_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.open_folder_btn.setStyleSheet("""
            QPushButton {
                background-color: #DCFCE7; color: #166534; font-weight: bold;
                border-radius: 6px; padding: 5px 12px; border: 1px solid #86EFAC; font-size: 12px;
            }
            QPushButton:hover { background-color: #BBF7D0; }
        """)
        self.open_folder_btn.clicked.connect(self._open_output_folder)

        success_actions.addWidget(self.open_file_btn)
        success_actions.addWidget(self.open_folder_btn)
        success_actions.addStretch()

        success_layout.addWidget(self.success_title)
        success_layout.addWidget(self.success_path_label)
        success_layout.addLayout(success_actions)
        self.success_banner.hide()

        content_layout.addWidget(self.success_banner, stretch=0)

        # 4. Error Banner (Hidden by default, allineato in alto)
        self.error_banner = QFrame()
        self.error_banner.setObjectName("ErrorBanner")
        self.error_banner.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.error_banner.setMaximumHeight(250)
        error_layout = QVBoxLayout(self.error_banner)
        error_layout.setContentsMargins(14, 12, 14, 12)
        error_layout.setSpacing(8)

        self.error_title = QLabel("❌ Errore durante la conversione")
        self.error_title.setStyleSheet("font-weight: bold; font-size: 15px; color: #991B1B;")

        self.error_desc_label = QLabel("")
        self.error_desc_label.setStyleSheet("font-size: 12px; color: #B91C1C; margin-top: 1px; margin-bottom: 2px;")
        self.error_desc_label.setWordWrap(True)
        self.error_desc_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        error_actions = QHBoxLayout()
        self.log_btn = QPushButton("📋 Dettagli Log")
        self.log_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.log_btn.setStyleSheet("""
            QPushButton {
                background-color: #991B1B; color: white; font-weight: bold;
                border-radius: 6px; padding: 5px 12px; border: none; font-size: 12px;
            }
            QPushButton:hover { background-color: #7F1D1D; }
        """)
        self.last_log_output = ""
        self.log_btn.clicked.connect(self._show_log_dialog)

        error_actions.addWidget(self.log_btn)
        error_actions.addStretch()

        error_layout.addWidget(self.error_title)
        error_layout.addWidget(self.error_desc_label)
        error_layout.addLayout(error_actions)
        self.error_banner.hide()

        content_layout.addWidget(self.error_banner, stretch=0)

        # Dynamic Spacer shown only during banner display to push convert_btn to bottom
        self.banner_spacer = QWidget()
        self.banner_spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.banner_spacer.hide()
        content_layout.addWidget(self.banner_spacer, stretch=1)

        # Action Convert Button (Blue)
        self.convert_btn = QPushButton("Converti in PDF/A")
        self.convert_btn.setObjectName("ConvertBtn")
        self.convert_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.convert_btn.setEnabled(False)
        self.convert_btn.clicked.connect(self._on_convert_btn_clicked)
        content_layout.addWidget(self.convert_btn, stretch=0)

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
            self.title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #FFFFFF;")
            self.subtitle_label.setStyleSheet("font-size: 12px; color: #93C5FD;")
            self.settings_btn.setStyleSheet("""
                QPushButton {
                    background-color: #FFFFFF;
                    color: #1E3A8A;
                    border: none;
                    border-radius: 8px;
                    padding: 8px 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #DBEAFE;
                    color: #1E40AF;
                }
            """)
            self.success_title.setStyleSheet("font-weight: bold; font-size: 16px; color: #A7F3D0;")
            self.success_path_label.setStyleSheet("font-size: 13px; color: #D1FAE5; margin-top: 2px; margin-bottom: 4px;")
            self.error_title.setStyleSheet("font-weight: bold; font-size: 16px; color: #FECACA;")
            self.error_desc_label.setStyleSheet("font-size: 13px; color: #FCA5A5; margin-top: 2px; margin-bottom: 4px;")
        else:
            self.title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #FFFFFF;")
            self.subtitle_label.setStyleSheet("font-size: 12px; color: #DBEAFE;")
            self.settings_btn.setStyleSheet("""
                QPushButton {
                    background-color: #FFFFFF;
                    color: #1D4ED8;
                    border: none;
                    border-radius: 8px;
                    padding: 8px 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #EFF6FF;
                    color: #1E40AF;
                }
            """)
            self.success_title.setStyleSheet("font-weight: bold; font-size: 16px; color: #166534;")
            self.success_path_label.setStyleSheet("font-size: 13px; color: #15803D; margin-top: 2px; margin-bottom: 4px;")
            self.error_title.setStyleSheet("font-weight: bold; font-size: 16px; color: #991B1B;")
            self.error_desc_label.setStyleSheet("font-size: 13px; color: #B91C1C; margin-top: 2px; margin-bottom: 4px;")

    def _on_files_selected(self, file_paths: list[str]):
        self.success_banner.hide()
        self.error_banner.hide()
        self.banner_spacer.hide()
        count = len(file_paths)
        if count == 0:
            self.convert_btn.setText("Converti in PDF/A")
            self.convert_btn.setEnabled(False)
        elif count == 1:
            self.convert_btn.setText("Converti in PDF/A")
            self.convert_btn.setEnabled(True)
        else:
            self.convert_btn.setText(f"Converti File in PDF/A ({count})")
            self.convert_btn.setEnabled(True)

    def _on_convert_btn_clicked(self):
        if self.success_banner.isVisible() or self.error_banner.isVisible():
            self._reset_ui()
        else:
            self._start_conversion()

    def _open_settings(self):
        dialog = SettingsDialog(self.config, self)
        dialog.exec()

    def _start_conversion(self):
        input_files = self.drop_widget.current_files
        if not input_files:
            QMessageBox.warning(self, "Attenzione", "Seleziona almeno un file PDF valido prima di procedere.")
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
        self.banner_spacer.hide()

        count = len(input_files)
        status_init = f"Avvio conversione per {count} file..." if count > 1 else "Avvio del processo Ghostscript..."
        self.loader_widget.set_progress_step(0, count, status_init)
        self.loader_widget.show()

        # Launch worker thread
        self.converter_thread = PDFConverterThread(
            input_files=input_files,
            gs_path=gs_path,
            icc_path=self.config.icc_profile_path,
            pdfa_level=self.config.pdfa_level,
            extra_args=self.config.extra_gs_args,
            output_suffix=self.config.output_suffix,
            parent=self
        )
        self.converter_thread.progress.connect(self.loader_widget.set_status)
        self.converter_thread.progress_step.connect(self.loader_widget.set_progress_step)
        self.converter_thread.finished.connect(self._on_conversion_finished)
        self.converter_thread.start()

    def _on_conversion_finished(self, success: bool, output_files: list[str], log_message: str):
        self.loader_widget.hide()
        self.drop_widget.hide()
        self.banner_spacer.show()

        if success:
            self.last_output_files = output_files
            self.last_output_file = output_files[0] if output_files else ""
            num_files = len(output_files)
            
            if num_files == 1:
                self.success_title.setText("🎉 Conversione completata con successo!")
                self.success_path_label.setText(f"File salvato in:\n{output_files[0]}")
                self.success_path_label.show()
                self.open_file_btn.show()
            else:
                self.success_title.setText(f"🎉 Conversione di {num_files} file completata con successo!")
                self.success_path_label.setText("")
                self.success_path_label.hide()
                self.open_file_btn.hide()

            # Show 'Apri Cartella' button ONLY if all converted files belong to the same parent directory
            parent_folders = {str(Path(f).parent) for f in output_files if f}
            self.open_folder_btn.setVisible(len(parent_folders) == 1)

            self.success_banner.show()
        else:
            self.last_log_output = log_message
            self.last_output_file = output_files[0] if output_files else ""
            short_msg = log_message.split("\nLog:")[0] if "\nLog:" in log_message else log_message
            self.error_desc_label.setText(short_msg[:300])
            self.error_banner.show()

        # Show blue ConvertBtn outside banner to reset UI and convert more files
        self.convert_btn.setText("🔄 Converti Altri Files...")
        self.convert_btn.setEnabled(True)
        self.convert_btn.show()

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
        self.drop_widget.clear_files()
        self.drop_widget.show()
        self.loader_widget.hide()
        self.convert_btn.show()
        self.convert_btn.setText("Converti in PDF/A")
        self.convert_btn.setEnabled(False)
        self.success_banner.hide()
        self.error_banner.hide()
        self.banner_spacer.hide()
        self.last_output_file = ""
        self.last_log_output = ""


