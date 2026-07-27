import os
from pathlib import Path
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog,
    QSizePolicy, QScrollArea, QWidget
)
from PyQt6.QtGui import QDragEnterEvent, QDropEvent

from gui.theme import get_drop_widget_style, Theme

class FileItemWidget(QFrame):
    """
    Individual card widget for a selected PDF file in the drop area list.
    """
    remove_requested = pyqtSignal(str)

    def __init__(self, file_path: str, theme: str = Theme.LIGHT, parent=None):
        super().__init__(parent)
        self.setObjectName("FileItemWidget")
        self.file_path = file_path
        self.theme = theme
        
        path_obj = Path(file_path)
        size_mb = os.path.getsize(file_path) / (1024 * 1024) if os.path.isfile(file_path) else 0.0

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(8)

        icon_label = QLabel("📄")
        icon_label.setStyleSheet("font-size: 18px; background: transparent; border: none;")

        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)

        self.name_label = QLabel(path_obj.name)
        self.path_label = QLabel(f"{path_obj.parent} ({size_mb:.2f} MB)")

        info_layout.addWidget(self.name_label)
        info_layout.addWidget(self.path_label)

        remove_btn = QPushButton("✕")
        remove_btn.setToolTip("Rimuovi questo file")
        remove_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        remove_btn.setFixedSize(24, 24)
        remove_btn.clicked.connect(lambda: self.remove_requested.emit(self.file_path))

        layout.addWidget(icon_label)
        layout.addLayout(info_layout, stretch=1)
        layout.addWidget(remove_btn)

        self.apply_theme(theme)

    def apply_theme(self, theme: str):
        self.theme = theme
        if theme == Theme.DARK:
            self.setStyleSheet("""
                #FileItemWidget {
                    background-color: #064E3B;
                    border: 1px solid #10B981;
                    border-radius: 8px;
                }
                QPushButton {
                    background-color: #047857;
                    color: #A7F3D0;
                    border: none;
                    border-radius: 12px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #EF4444;
                    color: white;
                }
            """)
            self.name_label.setStyleSheet("font-size: 13px; font-weight: bold; color: #6EE7B7; background: transparent; border: none;")
            self.path_label.setStyleSheet("font-size: 11px; color: #A7F3D0; background: transparent; border: none;")
        else:
            self.setStyleSheet("""
                #FileItemWidget {
                    background-color: #F0FDF4;
                    border: 1px solid #10B981;
                    border-radius: 8px;
                }
                QPushButton {
                    background-color: #DCFCE7;
                    color: #166534;
                    border: 1px solid #86EFAC;
                    border-radius: 12px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #EF4444;
                    color: white;
                    border: none;
                }
            """)
            self.name_label.setStyleSheet("font-size: 13px; font-weight: bold; color: #065F46; background: transparent; border: none;")
            self.path_label.setStyleSheet("font-size: 11px; color: #047857; background: transparent; border: none;")

class DropAreaWidget(QFrame):
    """
    Drag & Drop multi-file selection area widget for PDF files.
    """
    files_selected = pyqtSignal(list)  # emits list[str] of file paths
    file_selected = pyqtSignal(str)    # backward compatibility signal emitting first file or ""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.current_files: list[str] = []
        self.current_theme = Theme.LIGHT
        
        self.setObjectName("DropAreaWidget")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(12, 20, 12, 20)
        self.main_layout.setSpacing(10)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 1. Empty State Container
        self.empty_container = QFrame()
        self.empty_container.setStyleSheet("background: transparent;")
        self.empty_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        empty_layout = QVBoxLayout(self.empty_container)
        empty_layout.setContentsMargins(0, 20, 0, 20)
        empty_layout.setSpacing(8)
        empty_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.icon_label = QLabel("📄")
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setStyleSheet("font-size: 36px; background: transparent;")

        self.main_text = QLabel("Trascina e rilascia qui i tuoi file PDF")
        self.main_text.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.sub_text = QLabel("oppure")
        self.sub_text.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.browse_btn = QPushButton("Sfoglia File...")
        self.browse_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.browse_btn.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6;
                color: white;
                font-weight: bold;
                padding: 7px 18px;
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

        # 2. Loaded State Container (hidden initially)
        self.loaded_container = QFrame()
        self.loaded_container.setStyleSheet("background: transparent;")
        self.loaded_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        loaded_layout = QVBoxLayout(self.loaded_container)
        loaded_layout.setContentsMargins(0, 0, 0, 0)
        loaded_layout.setSpacing(8)

        # Header with summary and batch actions
        header_layout = QHBoxLayout()
        self.summary_label = QLabel("📁 0 file PDF selezionati")
        self.summary_label.setStyleSheet("font-weight: bold; font-size: 14px;")

        self.add_more_btn = QPushButton("Aggiungi File...")
        self.add_more_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_more_btn.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6;
                color: white;
                font-weight: bold;
                padding: 4px 12px;
                border-radius: 6px;
                border: none;
                font-size: 12px;
            }
            QPushButton:hover { background-color: #2563EB; }
        """)
        self.add_more_btn.clicked.connect(self._open_file_dialog)

        self.clear_all_btn = QPushButton("Rimuovi Tutti")
        self.clear_all_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clear_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #EF4444;
                color: white;
                font-weight: bold;
                padding: 4px 12px;
                border-radius: 6px;
                border: none;
                font-size: 12px;
            }
            QPushButton:hover { background-color: #DC2626; }
        """)
        self.clear_all_btn.clicked.connect(self.clear_files)

        header_layout.addWidget(self.summary_label, stretch=1)
        header_layout.addWidget(self.add_more_btn)
        header_layout.addWidget(self.clear_all_btn)

        # Scroll Area for File Cards (espandibile dinamicamente per riempire lo spazio)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setStyleSheet("background: transparent;")

        self.scroll_widget = QWidget()
        self.scroll_widget.setStyleSheet("background: transparent;")
        self.items_layout = QVBoxLayout(self.scroll_widget)
        self.items_layout.setContentsMargins(0, 0, 0, 0)
        self.items_layout.setSpacing(6)
        self.items_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.scroll_area.setWidget(self.scroll_widget)

        loaded_layout.addLayout(header_layout)
        loaded_layout.addWidget(self.scroll_area, stretch=1)

        self.loaded_container.setVisible(False)

        # Add containers to main layout
        self.main_layout.addWidget(self.empty_container)
        self.main_layout.addWidget(self.loaded_container)

    @property
    def current_file_path(self) -> str:
        """Property for single-file backwards compatibility."""
        return self.current_files[0] if self.current_files else ""

    def _open_file_dialog(self):
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "Seleziona File PDF", "", "File PDF (*.pdf)"
        )
        if file_paths:
            self.add_files(file_paths)

    def add_files(self, file_paths: list[str]):
        added = False
        for path in file_paths:
            if path and path.lower().endswith(".pdf") and os.path.isfile(path):
                if path not in self.current_files:
                    self.current_files.append(path)
                    added = True

        if added or self.current_files:
            self._update_ui_state()

    def remove_file(self, file_path: str):
        if file_path in self.current_files:
            self.current_files.remove(file_path)
            self._update_ui_state()

    def clear_files(self):
        self.current_files.clear()
        self._update_ui_state()

    def clear_file(self):
        """Backwards compatibility alias for clear_files."""
        self.clear_files()

    def set_file(self, file_path: str):
        """Backwards compatibility method setting a single file."""
        if file_path:
            self.current_files = [file_path]
            self._update_ui_state()
        else:
            self.clear_files()

    def _update_ui_state(self):
        # Clear previous item widgets from items_layout
        while self.items_layout.count():
            item = self.items_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        if self.current_files:
            total_size_mb = sum(
                (os.path.getsize(p) / (1024 * 1024)) for p in self.current_files if os.path.isfile(p)
            )
            count = len(self.current_files)
            plural = "file" if count == 1 else "file"
            self.summary_label.setText(f"{count} {plural} PDF selezionati ({total_size_mb:.2f} MB totali)")

            for file_path in self.current_files:
                item_card = FileItemWidget(file_path, theme=self.current_theme, parent=self.scroll_widget)
                item_card.remove_requested.connect(self.remove_file)
                self.items_layout.addWidget(item_card)

            self.empty_container.hide()
            self.loaded_container.show()
            self.main_layout.setContentsMargins(12, 12, 12, 12)
            self.setProperty("hasFile", True)
        else:
            self.loaded_container.hide()
            self.empty_container.show()
            self.main_layout.setContentsMargins(12, 20, 12, 20)
            self.setProperty("hasFile", False)

        self.style().unpolish(self)
        self.style().polish(self)
        self.updateGeometry()

        self.files_selected.emit(self.current_files)
        self.file_selected.emit(self.current_file_path)

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
            new_paths = []
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if file_path.lower().endswith(".pdf"):
                    new_paths.append(file_path)
            if new_paths:
                self.add_files(new_paths)
                event.acceptProposedAction()
                return
        event.ignore()

    def apply_theme(self, theme: str):
        self.current_theme = theme
        self.setStyleSheet(get_drop_widget_style(theme))

        if theme == Theme.DARK:
            self.main_text.setStyleSheet("font-size: 15px; font-weight: bold; color: #F8FAFC; background: transparent;")
            self.sub_text.setStyleSheet("font-size: 12px; color: #94A3B8; background: transparent;")
            self.summary_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #F8FAFC;")
        else:
            self.main_text.setStyleSheet("font-size: 15px; font-weight: bold; color: #1E293B; background: transparent;")
            self.sub_text.setStyleSheet("font-size: 12px; color: #64748B; background: transparent;")
            self.summary_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #1E293B;")

        # Update existing file item cards theme
        for i in range(self.items_layout.count()):
            widget = self.items_layout.itemAt(i).widget()
            if isinstance(widget, FileItemWidget):
                widget.apply_theme(theme)

        self.style().unpolish(self)
        self.style().polish(self)
