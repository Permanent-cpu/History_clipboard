from PySide6.QtCore import QTimer, QObject, Signal
from PySide6.QtGui import QClipboard
from PySide6.QtWidgets import QApplication
from storage import Storage


class ClipboardMonitor(QObject):
    content_changed = Signal(object)  # ClipItem

    def __init__(self, storage: Storage, interval_ms: int = 500):
        super().__init__()
        self.storage = storage
        self.clipboard = QApplication.clipboard()
        self._last_content: str | None = None

        self.timer = QTimer()
        self.timer.setInterval(interval_ms)
        self.timer.timeout.connect(self._check_clipboard)

    def start(self):
        self._last_content = self._get_clipboard_text()
        self.timer.start()

    def stop(self):
        self.timer.stop()

    def _check_clipboard(self):
        current = self._get_clipboard_text()
        if current and current != self._last_content:
            self._last_content = current
            content_type = self._detect_type()
            item = self.storage.add_item(current, content_type)
            if item:
                self.content_changed.emit(item)

    def _get_clipboard_text(self) -> str | None:
        mime = self.clipboard.mimeData()
        if mime.hasText():
            return mime.text()
        elif mime.hasImage():
            return "[图片内容]"
        elif mime.hasUrls():
            urls = [u.toLocalFile() for u in mime.urls()]
            return "\n".join(urls)
        return None

    def _detect_type(self) -> str:
        mime = self.clipboard.mimeData()
        if mime.hasImage():
            return "image"
        elif mime.hasUrls():
            return "files"
        elif mime.hasHtml():
            return "html"
        else:
            return "text"
