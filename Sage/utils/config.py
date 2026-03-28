import json 
import os 
import sys

if getattr(sys, 'frozen', False):
    # running as .exe
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # running as .py
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CONFIG_PATH = os.path.join(BASE_DIR, 'config.json')

def save_config(config: dict):
    try:
        with open(CONFIG_PATH, 'w') as f:
            parsed_setting = json.dumps(config, indent=4)
            f.write(parsed_setting)
        return True
    except PermissionError:
        print("Permission denied writing config file")
        return False

def load_config():
    if not os.path.exists(CONFIG_PATH): 
        return {}
    try:
        with open(CONFIG_PATH) as f: 
            settings = json.load(f)
            return settings if settings else {}
    except json.JSONDecodeError:
        print("Config file is corrupted, returning empty config")
        return {}
