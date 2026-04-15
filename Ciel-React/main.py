import webview
from api.config import load_config, save_config
from api.run_query import run_query
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
            run_query(current_year_file, past_year_files, excluded_suppliers, start, end_date, output_path=save_path[0])
    
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
    window = webview.create_window('Délai de Paiement', 'http://localhost:5173/', width=1100, height=900, js_api=api)
    webview.start(debug=True)