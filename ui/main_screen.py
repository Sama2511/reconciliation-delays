import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QDateEdit, QFileDialog
)
from PyQt6.QtCore import QDate, QThread, pyqtSignal
from db.query import run_query
from db.fetch_databases import fetch_dbs
from export.excel import export_to_excel


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
        data = run_query(self.database, self.year_date, self.start_date, self.end_date)
        if data is None:
            self.finished.emit(False, 'Error fetching data from database')
            return
        if data.empty:
            self.finished.emit(False, 'No data found for the selected dates')
            return
        result = export_to_excel(data, self.file_path)
        if not result:
            self.finished.emit(False, 'Error saving Excel file')
            return
        self.finished.emit(True, 'Report generated successfully')


class MainScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.worker = None
        self.build_ui()
        self.get_dbs()

    def build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 32, 30, 32)

        # Database | Year row
        db_row = QHBoxLayout()

        db_col = QVBoxLayout()
        db_col.addWidget(QLabel('Base de données / Société'))
        self.database_dropdown = QComboBox()
        self.database_dropdown.setFixedHeight(32)
        db_col.addWidget(self.database_dropdown)
        db_row.addLayout(db_col, 3)

        year_col = QVBoxLayout()
        year_col.addWidget(QLabel('Début Année Référence'))
        self.year_entry = QDateEdit()
        self.year_entry.setCalendarPopup(True)
        self.year_entry.setDate(QDate.currentDate())
        self.year_entry.setDisplayFormat('yyyy-MM-dd')
        self.year_entry.setFixedHeight(32)
        year_col.addWidget(self.year_entry)
        db_row.addLayout(year_col, 1)

        layout.addLayout(db_row)

        # Start date | End date row
        date_row = QHBoxLayout()

        start_col = QVBoxLayout()
        start_col.addWidget(QLabel('Début Période'))
        self.start_date_entry = QDateEdit()
        self.start_date_entry.setCalendarPopup(True)
        self.start_date_entry.setDate(QDate.currentDate())
        self.start_date_entry.setDisplayFormat('yyyy-MM-dd')
        self.start_date_entry.setFixedHeight(32)
        start_col.addWidget(self.start_date_entry)
        date_row.addLayout(start_col)

        end_col = QVBoxLayout()
        end_col.addWidget(QLabel('Fin Période'))
        self.end_date_entry = QDateEdit()
        self.end_date_entry.setCalendarPopup(True)
        self.end_date_entry.setDate(QDate.currentDate())
        self.end_date_entry.setDisplayFormat('yyyy-MM-dd')
        self.end_date_entry.setFixedHeight(32)
        end_col.addWidget(self.end_date_entry)
        date_row.addLayout(end_col)

        layout.addLayout(date_row)

        layout.addStretch()

        # Generate button
        self.generate_button = QPushButton('Générer Rapport')
        self.generate_button.setFixedSize(130, 40)
        self.generate_button.clicked.connect(self.start_generate)
        layout.addWidget(self.generate_button)

        # Status
        self.status_label = QLabel('')
        layout.addWidget(self.status_label)

    def get_dbs(self):
        dbs = fetch_dbs()
        if dbs:
            self.database_dropdown.addItems(dbs)
        else:
            self.database_dropdown.addItem('No databases found')

    def start_generate(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, 'Save report as', '', 'Excel files (*.xlsx)'
        )
        if not file_path:
            return
        if not file_path.endswith('.xlsx'):
            file_path += '.xlsx'

        self.generate_button.setEnabled(False)
        self.status_label.setText('Generating...')

        self.worker = ReportWorker(
            database=self.database_dropdown.currentText(),
            start_date=self.start_date_entry.date().toString('yyyy-MM-dd'),
            end_date=self.end_date_entry.date().toString('yyyy-MM-dd'),
            year_date=self.year_entry.date().toString('yyyy-MM-dd'),
            file_path=file_path
        )
        self.worker.finished.connect(self.on_generate_done)
        self.worker.start()
        

    def on_generate_done(self, success, message):
        self.status_label.setText(message)
        self.generate_button.setEnabled(True)
