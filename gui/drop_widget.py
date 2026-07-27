import os
from pathlib import Path
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog, QSizePolicy
)
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QColor

from gui.theme import get_drop_widget_style, Theme

class DropAreaWidget(QFrame):
    """
    Drag & Drop file area widget for PDF files.
    """
    file_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.current_file_path = ""
        
        self.setObjectName("DropAreaWidget")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(12, 80, 12, 80)
        self.layout.setSpacing(0)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Empty state container
        self.empty_container = QFrame()
        self.empty_container.setStyleSheet("background: transparent;")
        empty_layout = QVBoxLayout(self.empty_container)
        empty_layout.setContentsMargins(0, 0, 0, 0)
        empty_layout.setSpacing(6)
        empty_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.icon_label = QLabel("📄")
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setStyleSheet("font-size: 32px; background: transparent;")

        self.main_text = QLabel("Trascina e rilascia qui il tuo file PDF")
        self.main_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_text.setStyleSheet("font-size: 15px; font-weight: bold; color: #1E293B; background: transparent;")

        self.sub_text = QLabel("oppure")
        self.sub_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sub_text.setStyleSheet("font-size: 12px; color: #64748B; background: transparent;")

        self.browse_btn = QPushButton("Sfoglia File...")
        self.browse_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.browse_btn.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6;
                color: white;
                font-weight: bold;
                padding: 6px 16px;
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
        self.browse_btn.clicked.connect(self._open_file_dialog)

        empty_layout.addWidget(self.icon_label)
        empty_layout.addWidget(self.main_text)
        empty_layout.addWidget(self.sub_text)
        empty_layout.addWidget(self.browse_btn)

        # Loaded state widgets (hidden initially)
        self.file_card = QFrame()
        self.file_card.setStyleSheet("background: transparent;")
        file_card_layout = QHBoxLayout(self.file_card)
        file_card_layout.setContentsMargins(0, 0, 0, 0)
        
        self.file_icon = QLabel("✅")
        self.file_icon.setStyleSheet("font-size: 32px;")
        
        file_info_layout = QVBoxLayout()
        self.file_name_label = QLabel("")
        self.file_name_label.setStyleSheet("font-size: 15px; font-weight: bold; color: #065F46;")
        self.file_path_label = QLabel("")
        self.file_path_label.setStyleSheet("font-size: 12px; color: #047857;")
        file_info_layout.addWidget(self.file_name_label)
        file_info_layout.addWidget(self.file_path_label)

        self.remove_btn = QPushButton("✕ Rimuovi")
        self.remove_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.remove_btn.setStyleSheet("""
            QPushButton {
                background-color: #EF4444;
                color: white;
                font-weight: bold;
                padding: 6px 14px;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover {
                background-color: #DC2626;
            }
        """)
        self.remove_btn.clicked.connect(self.clear_file)

        file_card_layout.addWidget(self.file_icon)
        file_card_layout.addLayout(file_info_layout, stretch=1)
        file_card_layout.addWidget(self.remove_btn)
        self.file_card.setVisible(False)

        # Add to layout
        self.layout.addWidget(self.empty_container)
        self.layout.addWidget(self.file_card)

    def _open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Seleziona File PDF", "", "File PDF (*.pdf)"
        )
        if file_path:
            self.set_file(file_path)

    def set_file(self, file_path: str):
        if not file_path or not file_path.lower().endswith(".pdf") or not os.path.isfile(file_path):
            return
        
        self.current_file_path = file_path
        path_obj = Path(file_path)
        size_mb = os.path.getsize(file_path) / (1024 * 1024)

        self.file_name_label.setText(path_obj.name)
        self.file_path_label.setText(f"{path_obj.parent} ({size_mb:.2f} MB)")

        # Toggle UI views
        self.empty_container.hide()
        self.file_card.show()
        self.layout.setContentsMargins(16, 14, 16, 14)

        self.setProperty("hasFile", True)
        self.style().unpolish(self)
        self.style().polish(self)
        self.updateGeometry()

        self.file_selected.emit(file_path)

    def clear_file(self):
        self.current_file_path = ""
        self.file_card.hide()
        self.empty_container.show()
        self.layout.setContentsMargins(12, 30, 12, 30)

        self.setProperty("hasFile", False)
        self.style().unpolish(self)
        self.style().polish(self)
        self.updateGeometry()

        self.file_selected.emit("")

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.toLocalFile().lower().endswith(".pdf"):
                    event.acceptProposedAction()
                    self.setProperty("dragOver", True)
                    self.style().unpolish(self)
                    self.style().polish(self)
                    return
        event.ignore()

    def dragLeaveEvent(self, event):
        self.setProperty("dragOver", False)
        self.style().unpolish(self)
        self.style().polish(self)
        event.accept()

    def dropEvent(self, event: QDropEvent):
        self.setProperty("dragOver", False)
        self.style().unpolish(self)
        self.style().polish(self)
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if file_path.lower().endswith(".pdf"):
                    self.set_file(file_path)
                    event.acceptProposedAction()
                    return
        event.ignore()

    def apply_theme(self, theme: str):
        self.setStyleSheet(get_drop_widget_style(theme))
        if theme == Theme.DARK:
            self.main_text.setStyleSheet("font-size: 15px; font-weight: bold; color: #F8FAFC; background: transparent;")
            self.sub_text.setStyleSheet("font-size: 12px; color: #94A3B8; background: transparent;")
            self.file_name_label.setStyleSheet("font-size: 15px; font-weight: bold; color: #6EE7B7;")
            self.file_path_label.setStyleSheet("font-size: 12px; color: #A7F3D0;")
        else:
            self.main_text.setStyleSheet("font-size: 15px; font-weight: bold; color: #1E293B; background: transparent;")
            self.sub_text.setStyleSheet("font-size: 12px; color: #64748B; background: transparent;")
            self.file_name_label.setStyleSheet("font-size: 15px; font-weight: bold; color: #065F46;")
            self.file_path_label.setStyleSheet("font-size: 12px; color: #047857;")
        self.style().unpolish(self)
        self.style().polish(self)
