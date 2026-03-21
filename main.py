import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton
from ui.main_screen import MainScreen
from ui.settings_screen import SettingsDialog
from utils.config import load_config


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Délai de Paiement')
        self.setFixedSize(500, 450)

        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Navigation bar
        nav = QWidget()
        nav_layout = QHBoxLayout(nav)
        nav_layout.setContentsMargins(24, 0, 10, 0)

        nav_layout.addStretch()

        self.settings_btn = QPushButton('⚙')
        self.settings_btn.setFixedSize(30, 30)
        self.settings_btn.setToolTip('Parametre')
        self.settings_btn.clicked.connect(self.open_settings)
        nav_layout.addWidget(self.settings_btn)

        root_layout.addWidget(nav)

        # Main screen
        self.main_screen = MainScreen()
        root_layout.addWidget(self.main_screen)

        if not load_config():
            self.open_settings()

    def open_settings(self):
        dialog = SettingsDialog(self)
        dialog.exec()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec())
