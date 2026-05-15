from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction, QCursor
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QLabel, QApplication, QMenu,
)
from storage import Storage
from models import ClipItem
from utils import format_time


class MainWindow(QWidget):
    request_hide = Signal()

    def __init__(self, storage: Storage):
        super().__init__()
        self.storage = storage
        self._setup_ui()
        self._setup_shortcuts()
        self.refresh_list()

    def _setup_ui(self):
        self.setWindowTitle("History_pasteboard")
        self.setMinimumSize(380, 300)
        self.resize(420, 500)
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool
        )
        self.setStyleSheet("QWidget { background-color: #ffffff; color: #333333; }")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 6)

        # title bar
        title_layout = QHBoxLayout()
        self.title_label = QLabel("History_pasteboard")
        self.title_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #222222; background: transparent;")
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()
        layout.addLayout(title_layout)

        # list
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("""
            QListWidget {
                border: 1px solid #e0e0e0; border-radius: 4px;
                background-color: #fafafa;
            }
            QListWidget::item {
                padding: 8px 10px; border-bottom: 1px solid #eeeeee;
                background-color: #fafafa;
            }
            QListWidget::item:hover { background-color: #f0f0f0; }
            QListWidget::item:selected { background-color: #e5e5e5; }
        """)
        self.list_widget.itemClicked.connect(self._on_item_clicked)
        self.list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self._show_context_menu)
        self.list_widget.setAlternatingRowColors(True)
        layout.addWidget(self.list_widget)

        # bottom bar
        bottom_layout = QHBoxLayout()
        self.count_label = QLabel()
        self.count_label.setStyleSheet("color: #888888; background: transparent;")
        bottom_layout.addWidget(self.count_label)
        bottom_layout.addStretch()

        clear_btn = QPushButton("清空全部")
        clear_btn.setFixedWidth(80)
        clear_btn.clicked.connect(self._clear_all)
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #e57373; color: white; border: none;
                border-radius: 3px; padding: 4px 12px;
            }
            QPushButton:hover { background-color: #ef5350; }
        """)
        bottom_layout.addWidget(clear_btn)
        layout.addLayout(bottom_layout)

    def _setup_shortcuts(self):
        pass  # placeholder for global hotkey later

    def refresh_list(self):
        self.list_widget.clear()
        items = self.storage.get_all()
        for item in items:
            self._add_list_item(item)
        self.count_label.setText(f"共 {len(items)} 条")

    def _add_list_item(self, item: ClipItem):
        widget_item = QListWidgetItem()
        widget_item.setData(Qt.ItemDataRole.UserRole, item.id)
        display = f"{item.preview}\n{format_time(item.created_at)}"
        widget_item.setText(display)
        widget_item.setToolTip(item.content if item.content_type != "image" else item.preview)
        self.list_widget.insertItem(0, widget_item)

    def _on_item_clicked(self, widget_item: QListWidgetItem):
        item_id = widget_item.data(Qt.ItemDataRole.UserRole)
        items = self.storage.get_all()
        target = next((i for i in items if i.id == item_id), None)
        if target:
            clipboard = QApplication.clipboard()
            if target.content_type in ("text", "html"):
                clipboard.setText(target.content)
            elif target.content_type == "files":
                from PySide6.QtCore import QUrl
                from PySide6.QtGui import QMimeData
                mime = QMimeData()
                mime.setUrls([QUrl.fromLocalFile(p.strip()) for p in target.content.split("\n") if p.strip()])
                clipboard.setMimeData(mime)
        self.request_hide.emit()

    def _show_context_menu(self, pos):
        item = self.list_widget.itemAt(pos)
        if not item:
            return
        item_id = item.data(Qt.ItemDataRole.UserRole)
        menu = QMenu(self)
        delete_action = QAction("删除", self)
        delete_action.triggered.connect(lambda: self._delete_item(item_id))
        menu.addAction(delete_action)
        menu.exec(QCursor.pos())

    def _delete_item(self, item_id: int):
        self.storage.delete_item(item_id)
        self.refresh_list()

    def _clear_all(self):
        self.storage.clear_all()
        self.refresh_list()

    def add_item_and_refresh(self, item: ClipItem):
        # insert at top without full refresh
        self._add_list_item(item)
        self.count_label.setText(f"共 {self.storage.count()} 条")

    def closeEvent(self, event):
        event.ignore()
        self.hide()
