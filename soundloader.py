import os
import io
import base64
import json
import tempfile
import contextlib
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
import pygame

class SoundLoader:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(SoundLoader, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, dat_path="sounds.dat",
                 password=b'632514gfdhkjsiutr',
                 salt=b'salt_fixo_para_audio_123'):
        if self._initialized:
            return
            
        self.dat_path = dat_path
        self.password = password
        self.salt = salt
        self.sounds = {}
        self.raw_data = {}
        self._load()
        self._initialized = True

    def _derive_key(self):
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=390000,
            backend=default_backend()
        )
        return base64.urlsafe_b64encode(kdf.derive(self.password))

    def _load(self):
        if not os.path.exists(self.dat_path):
            return
        key = self._derive_key()
        f = Fernet(key)
        with open(self.dat_path, "rb") as fp:
            encrypted = fp.read()
        decrypted = f.decrypt(encrypted)
        data = json.loads(decrypted.decode("utf-8"))
        for name, b64 in data.items():
            raw = base64.b64decode(b64)
            self.raw_data[name] = raw
            self.sounds[name] = pygame.mixer.Sound(io.BytesIO(raw))

    def get_sound(self, name):
        return self.sounds.get(name)

    @contextlib.contextmanager
    def get_file(self, name):
        if name not in self.raw_data:
            yield None
            return
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".ogg")
        try:
            tmp.write(self.raw_data[name])
            tmp.close()
            yield tmp.name
        finally:
            try:
                os.remove(tmp.name)
            except FileNotFoundError:
                pass