# config.py
import json
import os

class MSAConfig:
    def __init__(self, config_file='msa_config.json'):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self):
        """Load MSA connection details"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {}
    
    def save_config(self, host, username, password):
        """Save connection details (consider encrypting password)"""
        config = {
            'host': host,
            'username': username,
            'password': password  # TODO: Encrypt this!
        }
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
        self.config = config
    
    def get_connection_params(self):
        return self.config