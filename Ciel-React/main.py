import webview
from api.config import load_config, save_config

class API:
    def load_config(self):
        return load_config()
    def save_config(self, config):
        return save_config(config)

if __name__ == '__main__':
    api = API()
    window = webview.create_window('Test', 'http://localhost:5173/', width=1100, height=650, js_api=api)
    webview.start(debug=True)