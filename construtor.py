import os
import base64
import json
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet

class Construtor:
    def __init__(self, password: bytes = b'632514gfdhkjsiutr', salt: bytes = b'salt_fixo_para_audio_123'):
        self.password = password
        self.salt = salt
        self._cipher = Fernet(self._generate_key())

    def _generate_key(self):
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=390000,
            backend=default_backend()
        )
        return base64.urlsafe_b64encode(kdf.derive(self.password))

    def build_sounds_dat(self, input_dir: str, output_file: str = "sounds.dat"):
        data = {}
        for fname in os.listdir(input_dir):
            path = os.path.join(input_dir, fname)
            if not os.path.isfile(path):
                continue
            with open(path, "rb") as f:
                raw = f.read()
            data[fname] = base64.b64encode(raw).decode("utf-8")
        json_bytes = json.dumps(data).encode("utf-8")
        encrypted = self._cipher.encrypt(json_bytes)
        with open(output_file, "wb") as f:
            f.write(encrypted)
        print(f"{output_file} gerado com {len(data)} sons.")

    def desencriptar(self, input_file, output_file):
        with open(input_file, "rb") as f:
            encrypted = f.read()
        decrypted = self._cipher.decrypt(encrypted)
        with open(output_file, "wb") as f:
            f.write(decrypted)
