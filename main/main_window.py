from PySide6.QtCore import Qt, Signal, QTimer, QEvent, QSize
from PySide6.QtGui import QAction, QCursor, QPainter, QColor, QPen
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QLabel, QApplication, QMenu, QSizePolicy,
)
from main.storage import Storage
from main.models import ClipItem
from main.utils import format_time


class MainWindow(QWidget):
    request_hide = Signal()

    def __init__(self, storage: Storage):
        super().__init__()
        self.storage = storage
        self._drag_pos = None
        self._drag_active = False
        self._setup_ui()
        self._setup_resize_timer()
        self.refresh_list()

    # ── UI construction ────────────────────────────────────────────

    def _setup_ui(self):
        self.setWindowTitle("History_pasteboard")
        self.setMinimumSize(340, 260)
        self.resize(400, 500)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 10)
        layout.setSpacing(4)

        # title bar
        title_bar = QHBoxLayout()
        title_bar.setContentsMargins(8, 4, 4, 4)

        self.title_label = QLabel("History Pasteboard")
        self.title_label.setStyleSheet(
            "color: #333333; font-size: 12px; font-weight: 600; background: transparent;"
        )
        title_bar.addWidget(self.title_label)
        title_bar.addStretch()

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(26, 26)
        close_btn.setStyleSheet("""
            QPushButton {
                border: none; font-size: 15px; color: #aaaaaa;
                background: transparent; border-radius: 4px;
            }
            QPushButton:hover { color: #555555; background: rgba(0,0,0,0.07); }
        """)
        close_btn.clicked.connect(self.hide)
        title_bar.addWidget(close_btn)
        layout.addLayout(title_bar)

        # list
        self.list_widget = QListWidget()
        self.list_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.list_widget.setVerticalScrollMode(QListWidget.ScrollMode.ScrollPerPixel)
        self.list_widget.setStyleSheet("""
            QListWidget {
                border: none; background: transparent; outline: none;
            }
            QListWidget::item {
                background: transparent;
                border: 1px solid rgba(0,0,0,0.09);
                border-radius: 6px;
                margin: 1px 2px;
            }
            QListWidget::item:hover {
                background: rgba(0,0,0,0.03); border-color: rgba(0,0,0,0.10);
            }
            QListWidget::item:selected {
                background: rgba(0,0,0,0.07); border-color: rgba(0,0,0,0.14);
            }
        """)
        self.list_widget.itemClicked.connect(self._on_item_clicked)
        self.list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self._show_context_menu)
        self.list_widget.installEventFilter(self)
        layout.addWidget(self.list_widget)

        # bottom bar
        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(8, 4, 4, 2)

        self.count_label = QLabel()
        self.count_label.setStyleSheet(
            "color: #b0b0b0; font-size: 11px; background: transparent;"
        )
        bottom_layout.addWidget(self.count_label)
        bottom_layout.addStretch()

        clear_btn = QPushButton("清空")  # 清空
        clear_btn.setFixedSize(54, 24)
        clear_btn.clicked.connect(self._clear_all)
        clear_btn.setStyleSheet("""
            QPushButton {
                background: rgba(0,0,0,0.05); color: #999999;
                border: none; border-radius: 4px; font-size: 11px;
            }
            QPushButton:hover { background: rgba(0,0,0,0.10); color: #666666; }
        """)
        bottom_layout.addWidget(clear_btn)
        layout.addLayout(bottom_layout)

    def _setup_resize_timer(self):
        self._resize_timer = QTimer(self)
        self._resize_timer.setSingleShot(True)
        self._resize_timer.setInterval(60)
        self._resize_timer.timeout.connect(self._update_item_sizes)

    # ── Glass background paint ─────────────────────────────────────

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor(245, 245, 247, 210))
        painter.setPen(QPen(QColor(0, 0, 0, 20), 0.5))
        painter.drawRoundedRect(self.rect().adjusted(0, 0, -1, -1), 14, 14)

    # ── Resize → reflow word-wrap ──────────────────────────────────

    def eventFilter(self, watched, event):
        if watched is self.list_widget and event.type() == QEvent.Type.Resize:
            self._resize_timer.start()
        return super().eventFilter(watched, event)

    def _update_item_sizes(self):
        list_width = self.list_widget.viewport().width()
        if list_width <= 0:
            return
        avail = list_width - 75 - 12 - 12  # time_label + spacing + row padding
        if avail < 60:
            avail = 60

        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            row = self.list_widget.itemWidget(item)
            if row is None:
                continue
            labels = row.findChildren(QLabel)
            if not labels:
                continue
            preview_label = labels[0]
            preview_label.setMaximumWidth(avail)
            h = preview_label.heightForWidth(avail)
            item.setSizeHint(QSize(list_width, max(h + 16, 38)))

    # ── List population ────────────────────────────────────────────

    def refresh_list(self):
        self.list_widget.clear()
        for item in self.storage.get_all():
            self._add_list_item(item)
        n = len(self.storage.get_all())
        self.count_label.setText(f"{n} 条记录")  # 条记录
        QTimer.singleShot(0, self._update_item_sizes)

    def _add_list_item(self, item: ClipItem):
        widget_item = QListWidgetItem()
        widget_item.setData(Qt.ItemDataRole.UserRole, item.id)
        widget_item.setToolTip(
            item.content if item.content_type != "image" else item.preview
        )

        row = QWidget()
        row.setStyleSheet("background: transparent;")
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(6, 8, 6, 8)
        row_layout.setSpacing(12)

        preview_label = QLabel(item.preview)
        preview_label.setWordWrap(True)
        preview_label.setStyleSheet(
            "font-size: 13px; color: #1a1a1a; background: transparent;"
        )
        preview_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        preview_label.setMinimumWidth(0)

        time_label = QLabel(format_time(item.created_at))
        time_label.setStyleSheet(
            "font-size: 10px; color: #b0b0b0; background: transparent;"
        )
        time_label.setFixedWidth(75)
        time_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)

        row_layout.addWidget(preview_label, 1)
        row_layout.addWidget(time_label, 0)

        # initial size hint
        list_width = self.list_widget.viewport().width()
        if list_width <= 0:
            list_width = self.width() - 20
        avail = list_width - 75 - 12 - 12
        if avail < 60:
            avail = 60
        preview_label.setMaximumWidth(avail)
        h = preview_label.heightForWidth(avail)

        widget_item.setSizeHint(QSize(list_width, max(h + 16, 38)))
        self.list_widget.insertItem(0, widget_item)
        self.list_widget.setItemWidget(widget_item, row)

    def add_item_and_refresh(self, item: ClipItem):
        self._add_list_item(item)
        self.count_label.setText(f"{self.storage.count()} 条记录")
        QTimer.singleShot(0, self._update_item_sizes)

    # ── Clipboard actions ──────────────────────────────────────────

    def _on_item_clicked(self, widget_item: QListWidgetItem):
        item_id = widget_item.data(Qt.ItemDataRole.UserRole)
        items = self.storage.get_all()
        target = next((i for i in items if i.id == item_id), None)
        if target is None:
            return

        clipboard = QApplication.clipboard()
        if target.content_type in ("text", "html"):
            clipboard.setText(target.content)
        elif target.content_type == "image":
            from PySide6.QtGui import QPixmap
            pixmap = QPixmap(target.content)
            if not pixmap.isNull():
                clipboard.setPixmap(pixmap)
        elif target.content_type == "files":
            from PySide6.QtCore import QUrl
            from PySide6.QtGui import QMimeData
            mime = QMimeData()
            mime.setUrls([
                QUrl.fromLocalFile(p.strip())
                for p in target.content.split("\n") if p.strip()
            ])
            clipboard.setMimeData(mime)

        self._show_copied_feedback()

    def _show_copied_feedback(self):
        self.count_label.setText("✓ 已复制")  # ✓ 已复制
        self.count_label.setStyleSheet(
            "color: #4caf50; font-size: 11px; background: transparent; font-weight: 600;"
        )
        QTimer.singleShot(1500, self._restore_count_label)

    def _restore_count_label(self):
        self.count_label.setStyleSheet(
            "color: #b0b0b0; font-size: 11px; background: transparent;"
        )
        self.count_label.setText(f"{self.storage.count()} 条记录")

    # ── Context menu ───────────────────────────────────────────────

    def _show_context_menu(self, pos):
        item = self.list_widget.itemAt(pos)
        if not item:
            return
        item_id = item.data(Qt.ItemDataRole.UserRole)
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background: rgba(255,255,255,0.94);
                border: 1px solid rgba(0,0,0,0.08);
                border-radius: 8px; padding: 4px;
            }
            QMenu::item {
                padding: 6px 22px; color: #333333; background: transparent;
            }
            QMenu::item:selected {
                background: rgba(0,0,0,0.06); border-radius: 4px;
            }
        """)
        delete_action = QAction("删除", self)  # 删除
        delete_action.triggered.connect(lambda: self._delete_item(item_id))
        menu.addAction(delete_action)
        menu.exec(QCursor.pos())

    def _delete_item(self, item_id: int):
        self.storage.delete_item(item_id)
        self.refresh_list()

    def _clear_all(self):
        self.storage.clear_all()
        self.refresh_list()

    # ── Window dragging ────────────────────────────────────────────

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self._drag_active = False

    def mouseMoveEvent(self, event):
        if event.buttons() != Qt.MouseButton.LeftButton or self._drag_pos is None:
            return
        delta = event.globalPosition().toPoint() - self.frameGeometry().topLeft() - self._drag_pos
        if not self._drag_active and (abs(delta.x()) > 5 or abs(delta.y()) > 5):
            self._drag_active = True
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
        if self._drag_active:
            self.move(event.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
        self._drag_active = False

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.hide()
        super().keyPressEvent(event)

    def closeEvent(self, event):
        event.ignore()
        self.hide()
