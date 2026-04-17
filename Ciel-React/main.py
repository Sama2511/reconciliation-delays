import webview
from api.config import load_config, save_config
from api.run_query import run_query
import os
import sys
BASE_DIR = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))



class API:
    def load_config(self):
        return load_config()
    def save_config(self, config):
        return save_config(config)
    def generate_report(self, current_year_file, past_year_files, excluded_suppliers, start, end_date):
        save_path = webview.windows[0].create_file_dialog(
            webview.FileDialog.SAVE,
            file_types=('Excel (*.xlsx)',)
        )
        if save_path:
            config = load_config()
            run_query(
                current_year_file,
                past_year_files,
                excluded_suppliers,
                start,
                end_date,
                output_path=save_path[0],
                journal_achat=config['journal_factures'],
                journal_paiements=config['journal_paiements'],
                journal_report=config['journal_report'],
                condition_default=config['condition_default'],
                conditions_fournisseur=config['conditions_fournisseur'],
            )
            return True
        return False
            
    
    def pick_current_year_file(self):
        result = webview.windows[0].create_file_dialog(
            webview.FileDialog.OPEN,
            file_types=('Excel (*.xlsx)',)
        )
        if result:
            return result[0]
        return None

    def pick_past_year_file(self):
        result = webview.windows[0].create_file_dialog(
            webview.FileDialog.OPEN,
            file_types=('Excel (*.xlsx)',)
        )
        if result:
            return result[0]
        return None



if __name__ == '__main__':
    api = API()
    window = webview.create_window('Délai de Paiement', 'frontend/dist/index.html', width=1050, height=860, resizable=False, js_api=api)
    webview.start()


