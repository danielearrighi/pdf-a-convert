"""
Theme management module for PDF/A Converter GUI.
Provides stylesheets and palettes for Light and Dark themes.
"""

from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtWidgets import QApplication

class Theme:
    LIGHT = "light"
    DARK = "dark"

def apply_app_palette(app: QApplication, theme: str):
    """Apply system palette for native message boxes and dialogs."""
    if not app:
        return
    if theme == Theme.DARK:
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#0F172A"))
        palette.setColor(QPalette.ColorRole.WindowText, QColor("#F8FAFC"))
        palette.setColor(QPalette.ColorRole.Base, QColor("#1E293B"))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#0F172A"))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#1E293B"))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#F8FAFC"))
        palette.setColor(QPalette.ColorRole.Text, QColor("#F8FAFC"))
        palette.setColor(QPalette.ColorRole.Button, QColor("#1E293B"))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor("#F8FAFC"))
        palette.setColor(QPalette.ColorRole.BrightText, QColor("#EF4444"))
        palette.setColor(QPalette.ColorRole.Link, QColor("#3B82F6"))
        palette.setColor(QPalette.ColorRole.Highlight, QColor("#2563EB"))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#FFFFFF"))
        palette.setColor(QPalette.ColorRole.PlaceholderText, QColor("#94A3B8"))
        app.setPalette(palette)
    else:
        app.setPalette(app.style().standardPalette())

def get_main_window_style(theme: str) -> str:
    if theme == Theme.DARK:
        return """
            QMainWindow {
                background-color: #0F172A;
            }
            #HeaderFrame {
                background-color: #1E3A8A;
                border: 1px solid #3B82F6;
                border-radius: 16px;
                padding: 16px 14px;
            }
            #MainContainer {
                background-color: #1E293B;
                border: 1px solid #334155;
                border-radius: 16px;
                padding: 24px 12px;
            }
            #ConvertBtn {
                background-color: #2563EB;
                color: #FFFFFF;
                font-weight: bold;
                font-size: 16px;
                padding: 14px;
                border-radius: 10px;
                border: none;
            }
            #ConvertBtn:hover {
                background-color: #3B82F6;
            }
            #ConvertBtn:disabled {
                background-color: #475569;
                color: #94A3B8;
            }
            #SuccessBanner {
                background-color: #064E3B;
                border: 1px solid #10B981;
                border-radius: 12px;
                padding: 16px 14px;
            }
            #ErrorBanner {
                background-color: #7F1D1D;
                border: 1px solid #EF4444;
                border-radius: 12px;
                padding: 16px 14px;
            }
        """
    else:
        return """
            QMainWindow {
                background-color: #F1F5F9;
            }
            #HeaderFrame {
                background-color: #2563EB;
                border: 1px solid #1D4ED8;
                border-radius: 16px;
                padding: 16px 14px;
            }
            #MainContainer {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 16px;
                padding: 24px 12px;
            }
            #ConvertBtn {
                background-color: #2563EB;
                color: white;
                font-weight: bold;
                font-size: 16px;
                padding: 14px;
                border-radius: 10px;
                border: none;
            }
            #ConvertBtn:hover {
                background-color: #1D4ED8;
            }
            #ConvertBtn:disabled {
                background-color: #94A3B8;
            }
            #SuccessBanner {
                background-color: #F0FDF4;
                border: 1px solid #86EFAC;
                border-radius: 12px;
                padding: 16px 14px;
            }
            #ErrorBanner {
                background-color: #FEF2F2;
                border: 1px solid #FCA5A5;
                border-radius: 12px;
                padding: 16px 14px;
            }
        """

def get_settings_dialog_style(theme: str) -> str:
    if theme == Theme.DARK:
        return """
            QDialog {
                background-color: #0F172A;
                color: #F8FAFC;
            }
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #F8FAFC;
                border: 1px solid #334155;
                border-radius: 10px;
                margin-top: 16px;
                padding: 16px 8px;
                background-color: #1E293B;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 14px;
                top: 4px;
                padding: 2px 8px;
                background-color: #1E293B;
                color: #F8FAFC;
                border-radius: 6px;
            }
            QLabel {
                color: #E2E8F0;
                font-size: 13px;
                font-weight: 600;
            }
            QLineEdit {
                padding: 8px 12px;
                border: 1px solid #475569;
                border-radius: 6px;
                background-color: #0F172A;
                color: #F8FAFC;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #3B82F6;
            }
            QComboBox {
                padding: 8px 12px;
                border: 1px solid #475569;
                border-radius: 6px;
                background-color: #0F172A;
                color: #F8FAFC;
                font-size: 13px;
                min-height: 24px;
                combobox-popup: 0;
            }
            QComboBox:focus {
                border-color: #3B82F6;
            }
            QComboBox QAbstractItemView {
                background-color: #1E293B;
                color: #F8FAFC;
                selection-background-color: #2563EB;
                selection-color: #FFFFFF;
                border: 1px solid #475569;
                border-radius: 6px;
                padding: 0px;
                margin: 0px;
                outline: none;
            }
            QComboBox QAbstractItemView::item {
                min-height: 32px;
                padding: 6px 12px;
                color: #F8FAFC;
                background-color: #1E293B;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #2563EB;
                color: #FFFFFF;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #2563EB;
                color: #FFFFFF;
            }
            QPushButton {
                padding: 8px 14px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
                border: 1px solid #475569;
                background-color: #1E293B;
                color: #F8FAFC;
            }
            QPushButton:hover {
                background-color: #334155;
            }
        """
    else:
        return """
            QDialog {
                background-color: #F8FAFC;
                color: #0F172A;
            }
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #0F172A;
                border: 1px solid #CBD5E1;
                border-radius: 10px;
                margin-top: 16px;
                padding: 16px 8px;
                background-color: #FFFFFF;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 14px;
                top: 4px;
                padding: 2px 8px;
                background-color: #FFFFFF;
                color: #0F172A;
                border-radius: 6px;
            }
            QLabel {
                color: #1E293B;
                font-size: 13px;
                font-weight: 600;
            }
            QLineEdit {
                padding: 8px 12px;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                background-color: #FFFFFF;
                color: #0F172A;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #2563EB;
            }
            QComboBox {
                padding: 8px 12px;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                background-color: #FFFFFF;
                color: #0F172A;
                font-size: 13px;
                min-height: 24px;
                combobox-popup: 0;
            }
            QComboBox:focus {
                border-color: #2563EB;
            }
            QComboBox QAbstractItemView {
                background-color: #FFFFFF;
                color: #0F172A;
                selection-background-color: #2563EB;
                selection-color: #FFFFFF;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                padding: 0px;
                margin: 0px;
                outline: none;
            }
            QComboBox QAbstractItemView::item {
                min-height: 32px;
                padding: 6px 12px;
                color: #0F172A;
                background-color: #FFFFFF;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #2563EB;
                color: #FFFFFF;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #2563EB;
                color: #FFFFFF;
            }
            QPushButton {
                padding: 8px 14px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
                border: 1px solid #CBD5E1;
                background-color: #F8FAFC;
                color: #1E293B;
            }
            QPushButton:hover {
                background-color: #E2E8F0;
            }
        """

def get_drop_widget_style(theme: str) -> str:
    if theme == Theme.DARK:
        return """
            #DropAreaWidget {
                border: 2px dashed #3B82F6;
                border-radius: 12px;
                background-color: #1E293B;
            }
            #DropAreaWidget[dragOver="true"] {
                border-color: #60A5FA;
                background-color: #1E3A8A;
            }
            #DropAreaWidget[hasFile="true"] {
                border: 2px dashed #3B82F6;
                background-color: #1E293B;
            }
        """
    else:
        return """
            #DropAreaWidget {
                border: 2px dashed #3B82F6;
                border-radius: 12px;
                background-color: #F8FAFC;
            }
            #DropAreaWidget[dragOver="true"] {
                border-color: #2563EB;
                background-color: #EFF6FF;
            }
            #DropAreaWidget[hasFile="true"] {
                border: 2px dashed #3B82F6;
                background-color: #F8FAFC;
            }
        """

def get_loader_widget_style(theme: str) -> str:
    if theme == Theme.DARK:
        return """
            #LoaderWidget {
                background-color: #1E293B;
                border: 1px solid #334155;
                border-radius: 12px;
                padding: 16px 8px;
            }
            QProgressBar {
                border: none;
                background-color: #334155;
                border-radius: 7px;
                height: 14px;
                text-align: center;
                margin-left: 8px;
                margin-right: 8px;
                font-size: 11px;
                font-weight: bold;
                color: #F8FAFC;
            }
            QProgressBar::chunk {
                background-color: #3B82F6;
                border-radius: 7px;
            }
        """
    else:
        return """
            #LoaderWidget {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 12px;
                padding: 16px 8px;
            }
            QProgressBar {
                border: none;
                background-color: #E2E8F0;
                border-radius: 7px;
                height: 14px;
                text-align: center;
                margin-left: 8px;
                margin-right: 8px;
                font-size: 11px;
                font-weight: bold;
                color: #1E293B;
            }
            QProgressBar::chunk {
                background-color: #3B82F6;
                border-radius: 7px;
            }
        """
