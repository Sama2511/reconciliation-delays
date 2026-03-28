import sys
import os
import json

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QDateEdit, QFileDialog, QLineEdit, QListWidget
)
from PyQt6.QtCore import QDate, QLocale

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    BASE_DIR = os.path.dirname(BASE_DIR)  # go up from ui/ to Ciel/

CONFIG_CIEL_PATH = os.path.join(BASE_DIR, 'config_ciel.json')


def load_config_ciel():
    if not os.path.exists(CONFIG_CIEL_PATH):
        return {'excluded_suppliers': []}
    try:
        with open(CONFIG_CIEL_PATH) as f:
            data = json.load(f)
            return data if data else {'excluded_suppliers': []}
    except json.JSONDecodeError:
        return {'excluded_suppliers': []}


def save_config_ciel(config: dict):
    try:
        with open(CONFIG_CIEL_PATH, 'w') as f:
            f.write(json.dumps(config, indent=4))
    except PermissionError:
        print("Permission denied writing config_ciel.json")


class CielScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.current_year_path = ''
        self.previous_year_paths = []
        config = load_config_ciel()
        self.build_ui()
        for supplier in config.get('excluded_suppliers', []):
            self.supplier_list.addItem(supplier)

    def build_ui(self):
        self.setStyleSheet('QLabel { font-size: 13px; }')
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 32, 30, 32)

        # Row 1: Date range
        row1 = QHBoxLayout()
        row1.setSpacing(16)

        start_col = QVBoxLayout()
        start_col.addWidget(QLabel('Début Période'))
        self.start_date_entry = QDateEdit()
        self.start_date_entry.setCalendarPopup(True)
        self.start_date_entry.setLocale(QLocale(QLocale.Language.French))
        self.start_date_entry.setDate(QDate.currentDate())
        self.start_date_entry.setDisplayFormat('yyyy-MM-dd')
        self.start_date_entry.setFixedHeight(32)
        start_col.addWidget(self.start_date_entry)
        row1.addLayout(start_col)

        end_col = QVBoxLayout()
        end_col.addWidget(QLabel('Fin Période'))
        self.end_date_entry = QDateEdit()
        self.end_date_entry.setCalendarPopup(True)
        self.end_date_entry.setLocale(QLocale(QLocale.Language.French))
        self.end_date_entry.setDate(QDate.currentDate())
        self.end_date_entry.setDisplayFormat('yyyy-MM-dd')
        self.end_date_entry.setFixedHeight(32)
        end_col.addWidget(self.end_date_entry)
        row1.addLayout(end_col)

        layout.addLayout(row1)
        layout.addSpacing(12)

        # Row 2: Current year Grand Livre
        current_year_label_col = QVBoxLayout()
        current_year_label_col.addWidget(QLabel("Grand Livre année en cours"))
        current_year_btn_row = QHBoxLayout()
        self.current_year_btn = QPushButton('Parcourir…')
        self.current_year_btn.setFixedSize(100, 32)
        self.current_year_btn.clicked.connect(self.browse_current_year)
        self.current_year_label = QLabel('Aucun fichier sélectionné')
        current_year_btn_row.addWidget(self.current_year_btn)
        current_year_btn_row.addWidget(self.current_year_label)
        current_year_btn_row.addStretch()
        current_year_label_col.addLayout(current_year_btn_row)
        layout.addLayout(current_year_label_col)

        layout.addSpacing(8)

        # Row 3: Previous years Grand Livres
        prev_years_label_col = QVBoxLayout()
        prev_years_label_col.addWidget(QLabel("Grand Livre(s) années précédentes"))
        prev_years_btn_row = QHBoxLayout()
        self.prev_years_btn = QPushButton('Parcourir…')
        self.prev_years_btn.setFixedSize(100, 32)
        self.prev_years_btn.clicked.connect(self.browse_previous_years)
        self.prev_years_label = QLabel('Aucun fichier sélectionné')
        prev_years_btn_row.addWidget(self.prev_years_btn)
        prev_years_btn_row.addWidget(self.prev_years_label)
        prev_years_btn_row.addStretch()
        prev_years_label_col.addLayout(prev_years_btn_row)
        layout.addLayout(prev_years_label_col)

        layout.addSpacing(12)

        # Excluded suppliers section
        layout.addWidget(QLabel('Fournisseurs exclus'))

        row4 = QHBoxLayout()
        row4.setSpacing(10)

        self.supplier_list = QListWidget()
        self.supplier_list.setMinimumHeight(80)
        row4.addWidget(self.supplier_list)

        supplier_controls = QVBoxLayout()
        supplier_controls.setSpacing(6)
        self.supplier_input = QLineEdit()
        self.supplier_input.setPlaceholderText('N° compte')
        self.supplier_input.setFixedHeight(32)
        add_btn = QPushButton('Ajouter')
        add_btn.setFixedHeight(32)
        add_btn.clicked.connect(self.add_supplier)
        remove_btn = QPushButton('Supprimer')
        remove_btn.setFixedHeight(32)
        remove_btn.clicked.connect(self.remove_supplier)
        supplier_controls.addWidget(self.supplier_input)
        supplier_controls.addWidget(add_btn)
        supplier_controls.addWidget(remove_btn)
        supplier_controls.addStretch()
        row4.addLayout(supplier_controls)

        layout.addLayout(row4)
        layout.addStretch()

        # Bottom row: status + generate button
        bottom_row = QHBoxLayout()
        self.status_label = QLabel('')
        bottom_row.addWidget(self.status_label)
        bottom_row.addStretch()
        self.generate_button = QPushButton('Générer le rapport')
        self.generate_button.setFixedSize(140, 40)
        self.generate_button.clicked.connect(self.on_generate)
        bottom_row.addWidget(self.generate_button)
        layout.addLayout(bottom_row)

    def browse_current_year(self):
        path, _ = QFileDialog.getOpenFileName(
            self, 'Sélectionner le Grand Livre année en cours', '', 'Fichiers Excel (*.xlsx)'
        )
        if path:
            self.current_year_path = path
            self.current_year_label.setText(os.path.basename(path))

    def browse_previous_years(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self, 'Sélectionner les Grand Livres années précédentes', '', 'Fichiers Excel (*.xlsx)'
        )
        if paths:
            self.previous_year_paths = paths
            self.prev_years_label.setText(', '.join(os.path.basename(p) for p in paths))

    def add_supplier(self):
        value = self.supplier_input.text().strip()
        if not value:
            return
        existing = [self.supplier_list.item(i).text() for i in range(self.supplier_list.count())]
        if value in existing:
            return
        self.supplier_list.addItem(value)
        self.supplier_input.clear()
        self._save_suppliers()

    def remove_supplier(self):
        selected = self.supplier_list.selectedItems()
        if not selected:
            return
        for item in selected:
            self.supplier_list.takeItem(self.supplier_list.row(item))
        self._save_suppliers()

    def _save_suppliers(self):
        suppliers = [self.supplier_list.item(i).text() for i in range(self.supplier_list.count())]
        save_config_ciel({'excluded_suppliers': suppliers})

    def on_generate(self):
        if not self.current_year_path:
            self.status_label.setStyleSheet('color: red;')
            self.status_label.setText("Veuillez sélectionner le Grand Livre de l'année en cours")
            return

        inputs = {
            'start_date': self.start_date_entry.date().toString('yyyy-MM-dd'),
            'end_date': self.end_date_entry.date().toString('yyyy-MM-dd'),
            'current_year_file': self.current_year_path,
            'previous_year_files': self.previous_year_paths,
            'excluded_suppliers': [
                self.supplier_list.item(i).text()
                for i in range(self.supplier_list.count())
            ],
        }
        print(inputs)
        self.status_label.setStyleSheet('color: gray;')
        self.status_label.setText('Prêt à générer (backend non connecté)')


if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = CielScreen()
    window.setWindowTitle('Délai de Paiement – Ciel Compta')
    window.resize(650, 480)
    window.show()
    sys.exit(app.exec())
