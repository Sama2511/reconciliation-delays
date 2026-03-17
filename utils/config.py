import json 
import os 

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'config.json')

def save_config(config: dict):
    with open(CONFIG_PATH, 'w') as f:
        parsed_setting = json.dumps(config, indent=4)
        f.write(parsed_setting)
        
def load_config():
    if not os.path.exists(CONFIG_PATH): return {}

    with open(CONFIG_PATH) as f: 
        settings = json.load(f)
        if not settings:
            return {}
        else:
            return settings
