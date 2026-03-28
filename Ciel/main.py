import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from ui.main_window_ciel import CielScreen


if __name__ == '__main__':
    import ctypes
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('delai.paiement.ciel')
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(os.path.join(BASE_DIR, 'appIcon.ico')))
    window = CielScreen()
    window.setWindowTitle('Délai de Paiement – Ciel Compta')
    window.setWindowIcon(QIcon(os.path.join(BASE_DIR, 'appIcon.ico')))
    window.resize(650, 480)
    window.show()
    sys.exit(app.exec())
