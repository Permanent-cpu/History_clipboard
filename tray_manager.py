from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import QSystemTrayIcon, QMenu, QApplication


class TrayManager:
    def __init__(self, main_window):
        self.main_window = main_window
        self.tray = QSystemTrayIcon()
        self.tray.setIcon(QIcon())  # placeholder — will be replaced with real icon
        self.tray.setToolTip("History_pasteboard")

        menu = QMenu()
        show_action = QAction("显示主窗口", menu)
        show_action.triggered.connect(self._show_window)
        menu.addAction(show_action)

        clear_action = QAction("清空历史", menu)
        clear_action.triggered.connect(self._clear_history)
        menu.addAction(clear_action)

        menu.addSeparator()

        quit_action = QAction("退出", menu)
        quit_action.triggered.connect(self._quit)
        menu.addAction(quit_action)

        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self._on_activated)

    def _on_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self._show_window()

    def _show_window(self):
        self.main_window.show()
        self.main_window.activateWindow()

    def _clear_history(self):
        self.main_window.storage.clear_all()
        self.main_window.refresh_list()

    def _quit(self):
        QApplication.quit()
