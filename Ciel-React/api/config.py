import json
import os

DEFAULT_CONFIG = {
    "journal_factures": [],
    "journal_paiements": [],
    "journal_report": [],
    "condition_default": 60,
    "conditions_fournisseur": [],
    "fournisseurs_exclus": []
}

CONFIG_DIR = os.path.join(os.environ['APPDATA'], 'DelaiPaiement')
CONFIG_PATH = os.path.join(CONFIG_DIR, 'config.json')

def load_config():
    try:
        with open(CONFIG_PATH) as file:
            config_file = json.load(file)
        config_file = {**DEFAULT_CONFIG, **config_file}
        return config_file
    except FileNotFoundError:
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(CONFIG_PATH, 'w') as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
        return DEFAULT_CONFIG
    except json.JSONDecodeError:
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(CONFIG_PATH, 'w') as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
        return DEFAULT_CONFIG

def save_config(config):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=4)