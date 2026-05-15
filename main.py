import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor
from main.storage import Storage
from main.clipboard_monitor import ClipboardMonitor
from main.main_window import MainWindow
from main.tray_manager import TrayManager


def _make_tray_icon() -> QIcon:
    """Generate a simple clipboard icon in-memory."""
    pix = QPixmap(32, 32)
    pix.fill(QColor(0, 0, 0, 0))
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # clipboard body
    painter.setBrush(QColor("#5B9BD5"))
    painter.setPen(QColor("#3A7CC3"))
    painter.drawRoundedRect(6, 3, 20, 24, 3, 3)

    # clipboard top clip
    painter.setBrush(QColor("#3A7CC3"))
    painter.drawRoundedRect(12, 1, 8, 6, 2, 2)

    # paper lines
    painter.setPen(QColor("#ffffff"))
    painter.drawLine(9, 11, 23, 11)
    painter.drawLine(9, 15, 23, 15)
    painter.drawLine(9, 19, 18, 19)

    painter.end()
    return QIcon(pix)


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setWindowIcon(_make_tray_icon())

    storage = Storage()
    window = MainWindow(storage)

    monitor = ClipboardMonitor(storage)
    monitor.content_changed.connect(window.add_item_and_refresh)
    monitor.start()

    tray = TrayManager(window)
    tray.tray.setIcon(_make_tray_icon())
    tray.tray.show()

    window.request_hide.connect(window.hide)

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
