from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QLabel, QProgressBar
)
from gui.theme import get_loader_widget_style, Theme

class LoaderWidget(QFrame):
    """
    Loader and status indicator widget displayed during conversion.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("LoaderWidget")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 16, 8, 16)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.title_label = QLabel("⚙️ Conversione in PDF/A in corso...")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate animated pulsing mode
        self.progress_bar.setTextVisible(False)

        self.status_label = QLabel("Avvio di Ghostscript...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.title_label)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.status_label)

    def set_status(self, text: str):
        self.status_label.setText(text)

    def apply_theme(self, theme: str):
        self.setStyleSheet(get_loader_widget_style(theme))
        if theme == Theme.DARK:
            self.title_label.setStyleSheet("font-size: 15px; font-weight: bold; color: #F8FAFC;")
            self.status_label.setStyleSheet("font-size: 12px; color: #94A3B8;")
        else:
            self.title_label.setStyleSheet("font-size: 15px; font-weight: bold; color: #1E293B;")
            self.status_label.setStyleSheet("font-size: 12px; color: #64748B;")
        self.style().unpolish(self)
        self.style().polish(self)

