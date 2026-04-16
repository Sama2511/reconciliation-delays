
import json

DEFAULT_CONFIG = {
    "journal_factures": [],
    "journal_paiements": [],
    "journal_report": [],
    "condition_default": 60,
    "conditions_fournisseur": [],
    "fournisseurs_exclus": []
}

def load_config():

    try:
        with open("config.json") as file:
            config_file = json.load(file)
        config_file = {**DEFAULT_CONFIG, **config_file}
        return config_file
    except FileNotFoundError:
        with open('config.json', 'w') as f :
            json.dump(DEFAULT_CONFIG, f, indent=4)
        return DEFAULT_CONFIG
    except json.JSONDecodeError:
        with open('config.json', 'w') as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
        return DEFAULT_CONFIG


def save_config(config):
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=4)


