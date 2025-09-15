import os
import json
from pathlib import Path
from cryptography.fernet import Fernet
from dotenv import load_dotenv

class SaveData:
    def __init__(self):
        load_dotenv()
        key = os.getenv("FERNET_KEY")
        if not key:
            raise ValueError("A chave FERNET_KEY não foi encontrada no .env")
        self._cipher = Fernet(key.encode())

        self._app_data_path = Path(os.getenv('APPDATA')) / 'Lucas Produções' / 'CM'
        self._settings_file = self._app_data_path / 'settings.dat'
        self._config = {
            'player_name': '',
            'ask_on_play': True,
            'default_size': 0,
            'menu_music_enabled': True
        }
        self._app_data_path.mkdir(parents=True, exist_ok=True)
        self._load_settings()
        self._ensure_defaults()

    def _ensure_defaults(self):
        if 'player_name' not in self._config: self._config['player_name'] = ''
        if 'ask_on_play' not in self._config: self._config['ask_on_play'] = True
        if 'default_size' not in self._config: self._config['default_size'] = 0
        if 'menu_music_enabled' not in self._config: self._config['menu_music_enabled'] = True

    def _load_settings(self):
        try:
            if self._settings_file.exists():
                with open(self._settings_file, 'rb') as f:
                    encrypted_data = f.read()
                    decrypted_data = self._cipher.decrypt(encrypted_data)
                    self._config = json.loads(decrypted_data.decode('utf-8'))
        except Exception:
            pass

    def _save_settings(self):
        try:
            data = json.dumps(self._config).encode('utf-8')
            encrypted_data = self._cipher.encrypt(data)
            with open(self._settings_file, 'wb') as f:
                f.write(encrypted_data)
        except Exception:
            pass

    def get_player_name(self):
        return self._config.get('player_name', '')

    def set_player_name(self, name):
        if name.strip():
            self._config['player_name'] = name.strip()
            self._save_settings()
            return True
        return False

    def get_setting(self, key, default=None):
        return self._config.get(key, default)

    def set_setting(self, key, value):
        self._config[key] = value
        self._save_settings()
        return True
