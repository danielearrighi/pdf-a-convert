import sys
import os
from PyQt6.QtWidgets import QApplication, QStyleFactory
from PyQt6.QtGui import QIcon
from core.utils import get_asset_path, register_desktop_entry_linux
from gui.main_window import MainWindow

def main():
    # Register desktop launcher for Linux/Wayland taskbar icon recognition
    register_desktop_entry_linux()

    # Enable High DPI scaling
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    
    app = QApplication(sys.argv)
    app.setApplicationName("PDF/A Converter PA")
    app.setOrganizationName("PDFAConvert")
    app.setDesktopFileName("pdfa-converter")

    # Set Application Icon
    icon_path = get_asset_path("app_icon.png")
    if os.path.exists(icon_path):
        app_icon = QIcon(icon_path)
        app.setWindowIcon(app_icon)

    # Apply clean cross-platform Fusion style to avoid native theme popup glitches on Linux
    fusion_style = QStyleFactory.create("Fusion")
    if fusion_style:
        app.setStyle(fusion_style)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()

