import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
sys.path.append(BASE_DIR)

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton
from PyQt6.QtGui import QIcon
from ui.main_screen import MainScreen
from ui.settings_screen import SettingsDialog
from utils.config import load_config

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Délai de Paiement')
        self.setFixedSize(650, 300)
        self.setWindowIcon(QIcon(os.path.join(BASE_DIR, 'appIcon.ico')))

        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Navigation bar
        nav = QWidget()
        nav_layout = QHBoxLayout(nav)
        nav_layout.setContentsMargins(24, 8, 10, 0)

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

    def open_settings(self):
        dialog = SettingsDialog(self)
        dialog.setting_saved.connect(self.main_screen.get_dbs)
        dialog.exec()


if __name__ == '__main__':
    import ctypes
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('delai.paiement')
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(os.path.join(BASE_DIR, 'appIcon.ico')))
    window = App()
    window.show()
    if not load_config():
        window.open_settings()
    sys.exit(app.exec())
