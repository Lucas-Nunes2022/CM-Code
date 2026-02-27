import os
import sys
import base64
import json
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet

class Construtor:
    def __init__(self, password: bytes = b'632514gfdhkjsiutr', salt: bytes = b'salt_fixo_para_audio_123'):
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=390000,
            backend=default_backend()
        )
        self._cipher = Fernet(base64.urlsafe_b64encode(kdf.derive(password)))

    def build_sounds_dat(self, input_dir: str, output_file: str = "sounds.dat"):
        data = {
            fname: base64.b64encode(open(os.path.join(input_dir, fname), "rb").read()).decode("utf-8")
            for fname in os.listdir(input_dir)
            if os.path.isfile(os.path.join(input_dir, fname))
        }
        with open(output_file, "wb") as f:
            f.write(self._cipher.encrypt(json.dumps(data).encode("utf-8")))
        print(f"{output_file} gerado com {len(data)} sons.")

    def desencriptar(self, input_file: str, output_file: str):
        with open(input_file, "rb") as f_in, open(output_file, "wb") as f_out:
            f_out.write(self._cipher.decrypt(f_in.read()))

construtor = Construtor()
    
pasta_alvo = sys.argv[1] if len(sys.argv) > 1 else "sounds"
    
construtor.build_sounds_dat(pasta_alvo)