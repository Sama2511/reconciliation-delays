import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QDateEdit, QFileDialog, QLineEdit
)
from PyQt6.QtCore import QDate, QThread, pyqtSignal, QLocale
from db.query import run_query
from db.fetch_databases import fetch_dbs
from export.excel import export_to_excel
from db.ref_year import get_ref_year


class ReportWorker(QThread):
    finished = pyqtSignal(bool, str)

    def __init__(self, database, start_date, end_date, year_date, file_path):
        super().__init__()
        self.database = database
        self.start_date = start_date
        self.end_date = end_date
        self.year_date = year_date
        self.file_path = file_path

    def run(self):
        print(self.database, self.year_date)
        data = run_query(self.database, self.start_date, self.end_date)
        if data is None:
            self.finished.emit(False, 'Erreur lors de la récupération des données')
            return
        if data.empty:
            self.finished.emit(False, 'Aucune donnée trouvée pour les dates sélectionnées')
            return
        result = export_to_excel(data, self.file_path)
        if not result:
            self.finished.emit(False, 'Erreur lors de la sauvegarde du fichier Excel')
            return
        self.finished.emit(True, 'Rapport généré avec succès')

    
  

class MainScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.worker = None
        self.build_ui()
        self.get_dbs()

    def closeEvent(self, event):
        if self.worker and self.worker.isRunning():
            self.worker.quit()
            self.worker.wait()
        super().closeEvent(event)

    def build_ui(self):
        self.setStyleSheet('QLabel { font-size: 13px; }')
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 32, 30, 32)

        # Row 1: Database | Year
        row1 = QHBoxLayout()

        db_col = QVBoxLayout()
        db_col.addWidget(QLabel('Base de données / Société'))
        self.database_dropdown = QComboBox()
        self.database_dropdown.setFixedHeight(32)
        self.database_dropdown.currentTextChanged.connect(self.ref_year)
        db_col.addWidget(self.database_dropdown)
        row1.addLayout(db_col, 2)

        year_col = QVBoxLayout()
        year_label_row = QHBoxLayout()
        year_label_row.addWidget(QLabel('Début Année Référence'))
        info = QLabel('ⓘ')
        info.setToolTip('Si la date affichée est incorrecte,\nmerci de la modifier via\nParamètres société – module « Identification »')
        year_label_row.addWidget(info)
        year_label_row.addStretch()
        year_col.addLayout(year_label_row)
        self.year_entry = QLineEdit()
        self.year_entry.setFixedHeight(32)
        self.year_entry.setReadOnly(True)
        self.year_entry.setToolTip('Si la date affichée est incorrecte,\nmerci de la modifier via\nParamètres société – module « Identification »')
        year_col.addWidget(self.year_entry)
        row1.addLayout(year_col, 1)

        layout.addLayout(row1)

        layout.addSpacing(12)

        # Row 2: Start date | End date
        row2 = QHBoxLayout()
        row2.setSpacing(16)

        start_col = QVBoxLayout()
        start_col.addWidget(QLabel('Début Période'))
        self.start_date_entry = QDateEdit()
        self.start_date_entry.setCalendarPopup(True)
        self.start_date_entry.setLocale(QLocale(QLocale.Language.French))
        self.start_date_entry.setDate(QDate.currentDate())
        self.start_date_entry.setDisplayFormat('yyyy-MM-dd')
        self.start_date_entry.setFixedHeight(32)
        start_col.addWidget(self.start_date_entry)
        row2.addLayout(start_col)

        end_col = QVBoxLayout()
        end_col.addWidget(QLabel('Fin Période'))
        self.end_date_entry = QDateEdit()
        self.end_date_entry.setCalendarPopup(True)
        self.end_date_entry.setLocale(QLocale(QLocale.Language.French))
        self.end_date_entry.setDate(QDate.currentDate())
        self.end_date_entry.setDisplayFormat('yyyy-MM-dd')
        self.end_date_entry.setFixedHeight(32)
        end_col.addWidget(self.end_date_entry)
        row2.addLayout(end_col)

        layout.addLayout(row2)

        layout.addStretch()

        # Row 4: Status left | Generate button right
        bottom_row = QHBoxLayout()
        self.status_label = QLabel('')
        bottom_row.addWidget(self.status_label)
        bottom_row.addStretch()
        self.generate_button = QPushButton('Générer Rapport')
        self.generate_button.setFixedSize(130, 40)
        self.generate_button.clicked.connect(self.start_generate)
        bottom_row.addWidget(self.generate_button)
        layout.addLayout(bottom_row)

    def get_dbs(self):
        self.database_dropdown.clear()
        dbs = fetch_dbs()
        if dbs:
            self.database_dropdown.addItems(dbs)
        else:
            self.database_dropdown.addItem('Aucune base de données trouvée')

    def ref_year(self, _=None):
        database = self.database_dropdown.currentText()
        year = get_ref_year(database)
        if not year:
            self.year_entry.setText('Année introuvable')
        else:
            self.year_entry.setText(year[0][0])



    def start_generate(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, 'Enregistrer le rapport sous', '', 'Fichiers Excel (*.xlsx)'
        )
        if not file_path:
            return
        if not file_path.endswith('.xlsx'):
            file_path += '.xlsx'

        self.last_file_path = file_path
        self.generate_button.setEnabled(False)
        self.status_label.setStyleSheet('color: gray;')
        self.status_label.setText('Génération en cours...')

        self.worker = ReportWorker(
            database=self.database_dropdown.currentText(),
            start_date=self.start_date_entry.date().toString('yyyy-MM-dd'),
            end_date=self.end_date_entry.date().toString('yyyy-MM-dd'),
            year_date=self.year_entry.text(),
            file_path=file_path
        )
        self.worker.finished.connect(self.on_generate_done)
        self.worker.start()
        

    def on_generate_done(self, success, message):
        self.status_label.setText(message)
        self.status_label.setStyleSheet('color: green;' if success else 'color: red;')
        self.generate_button.setEnabled(True)
        if success:
            os.startfile(self.last_file_path)
