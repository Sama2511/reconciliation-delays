import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QPushButton
)
from PyQt6.QtCore import QThread, pyqtSignal
from db.connection import test_connection_win_auth, test_connection_sql_auth
from utils.config import save_config, load_config


class ConnectionWorker(QThread):
    finished = pyqtSignal(bool, str)

    def __init__(self, server, auth, username, password):
        super().__init__()
        self.server = server
        self.auth = auth
        self.username = username
        self.password = password

    def run(self):
        if self.auth == 'SQL Server Authentication':
            conn = test_connection_sql_auth('master', self.server, self.username, self.password)
        else:
            conn = test_connection_win_auth('master', self.server)

        if conn:
            conn.close()
            self.finished.emit(True, f'Connected to {self.server}')
        else:
            self.finished.emit(False, f"Can't connect to {self.server}")


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Parametre')
        self.setFixedSize(380, 280)
        self.worker = None
        self.build_ui()
        self.load_settings()

    def build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(8)

        # Server name
        layout.addWidget(QLabel('Nom Serveur'))
        self.entry_server_name = QLineEdit()
        self.entry_server_name.setPlaceholderText('e.g. SERVERNAME\\SQLEXPRESS')
        layout.addWidget(self.entry_server_name)

        # Authentication
        layout.addWidget(QLabel('Authentication'))
        self.authentication_entry = QComboBox()
        self.authentication_entry.addItems(['Windows Authentication', 'SQL Server Authentication'])
        self.authentication_entry.currentTextChanged.connect(self.toggle_auth_fields)
        layout.addWidget(self.authentication_entry)

        # Username | Password row
        creds_row = QHBoxLayout()

        user_col = QVBoxLayout()
        self.username_label = QLabel('Identifiant')
        user_col.addWidget(self.username_label)
        self.username_entry = QLineEdit()
        self.username_entry.setPlaceholderText('Identifiant')
        user_col.addWidget(self.username_entry)
        creds_row.addLayout(user_col)

        pass_col = QVBoxLayout()
        self.password_label = QLabel('Mot de passe')
        pass_col.addWidget(self.password_label)
        self.password_entry = QLineEdit()
        self.password_entry.setPlaceholderText('Mot de passe')
        self.password_entry.setEchoMode(QLineEdit.EchoMode.Password)
        pass_col.addWidget(self.password_entry)
        creds_row.addLayout(pass_col)

        layout.addLayout(creds_row)

        layout.addStretch()

        # Status
        self.status_label = QLabel('')
        layout.addWidget(self.status_label)

        # Buttons row
        btn_row = QHBoxLayout()
        self.test_button = QPushButton('Test')
        self.test_button.clicked.connect(self.test_connection)
        btn_row.addWidget(self.test_button)

        self.save_button = QPushButton('Enregistrer')
        self.save_button.clicked.connect(self.save_settings)
        btn_row.addWidget(self.save_button)

        self.cancel_button = QPushButton('Annuler')
        self.cancel_button.clicked.connect(self.reject)
        btn_row.addWidget(self.cancel_button)

        layout.addLayout(btn_row)

        self.toggle_auth_fields('Windows Authentication')

    def toggle_auth_fields(self, choice):
        visible = choice == 'SQL Server Authentication'
        self.username_label.setVisible(visible)
        self.username_entry.setVisible(visible)
        self.password_label.setVisible(visible)
        self.password_entry.setVisible(visible)

    def load_settings(self):
        config = load_config()
        if not config:
            return
        self.entry_server_name.setText(config.get('server', ''))
        auth_type = config.get('auth_type', 'Windows Authentication')
        index = self.authentication_entry.findText(auth_type)
        if index >= 0:
            self.authentication_entry.setCurrentIndex(index)
        self.username_entry.setText(config.get('username', ''))
        self.password_entry.setText(config.get('password', ''))

    def save_settings(self):
        setting = {
            'server': self.entry_server_name.text(),
            'auth_type': self.authentication_entry.currentText(),
            'username': self.username_entry.text(),
            'password': self.password_entry.text(),
        }
        save_config(setting)
        self.status_label.setText('Parametres Enregistrés')

    def test_connection(self):
        server = self.entry_server_name.text()
        auth = self.authentication_entry.currentText()

        if not server:
            self.entry_server_name.setFocus()
            return

        if auth == 'SQL Server Authentication':
            if not self.username_entry.text():
                self.username_entry.setFocus()
                return
            if not self.password_entry.text():
                self.password_entry.setFocus()
                return

        self.status_label.setText('Testing...')
        self.test_button.setEnabled(False)
        self.save_button.setEnabled(False)

        self.worker = ConnectionWorker(
            server=server,
            auth=auth,
            username=self.username_entry.text(),
            password=self.password_entry.text()
        )
        self.worker.finished.connect(self.on_test_done)
        self.worker.start()

    def on_test_done(self, _, message):
        self.status_label.setText(message)
        self.test_button.setEnabled(True)
        self.save_button.setEnabled(True)
