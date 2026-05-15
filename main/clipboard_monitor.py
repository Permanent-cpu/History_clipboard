import os
import hashlib
import time
from PySide6 import QtCore
from PySide6.QtCore import QTimer, QObject, Signal
from PySide6.QtGui import QClipboard
from PySide6.QtWidgets import QApplication
from main.storage import Storage, IMAGE_DIR


class ClipboardMonitor(QObject):
    content_changed = Signal(object)  # ClipItem

    def __init__(self, storage: Storage, interval_ms: int = 500):
        super().__init__()
        self.storage = storage
        self.clipboard = QApplication.clipboard()
        self._last_hash: str | None = None

        self.timer = QTimer()
        self.timer.setInterval(interval_ms)
        self.timer.timeout.connect(self._check_clipboard)

    def start(self):
        self._last_hash = self._get_content_hash()
        self.timer.start()

    def stop(self):
        self.timer.stop()

    def _check_clipboard(self):
        current_type = self._detect_type()
        current_hash = self._get_content_hash()

        if current_hash and current_hash != self._last_hash:
            self._last_hash = current_hash
            content = self._extract_content(current_type)
            if content:
                item = self.storage.add_item(content, current_type)
                if item:
                    self.content_changed.emit(item)

    def _get_content_hash(self) -> str | None:
        mime = self.clipboard.mimeData()
        if mime.hasText():
            return hashlib.md5(mime.text().encode()).hexdigest()
        elif mime.hasImage():
            img = mime.imageData()
            if img:
                ba = QtCore.QByteArray()
                buf = QtCore.QBuffer(ba)
                buf.open(QtCore.QBuffer.OpenModeFlag.WriteOnly)
                img.save(buf, "PNG")
                return hashlib.md5(ba.data()).hexdigest()
            return None
        elif mime.hasUrls():
            urls = "\n".join([u.toLocalFile() for u in mime.urls()])
            return hashlib.md5(urls.encode()).hexdigest()
        return None

    def _extract_content(self, content_type: str) -> str | None:
        mime = self.clipboard.mimeData()
        if content_type == "image":
            img = mime.imageData()
            if img:
                os.makedirs(IMAGE_DIR, exist_ok=True)
                filename = f"clip_{int(time.time() * 1000)}.png"
                filepath = os.path.join(IMAGE_DIR, filename)
                img.save(filepath, "PNG")
                return filepath
            return None
        elif content_type == "files":
            urls = [u.toLocalFile() for u in mime.urls()]
            return "\n".join(urls) if urls else None
        else:
            return mime.text()

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
