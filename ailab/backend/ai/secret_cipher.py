from __future__ import annotations

import os
from pathlib import Path

from cryptography.fernet import Fernet

from backend.settings import settings


class SecretCipher:
    def __init__(self) -> None:
        self._cipher = Fernet(self._load_key())

    def _key_path(self) -> Path:
        return settings.data_dir / ".secret.key"

    def _load_key(self) -> bytes:
        env_key = os.getenv("AILAB_MASTER_KEY")
        if env_key:
            return env_key.encode("utf-8")

        key_path = self._key_path()
        key_path.parent.mkdir(parents=True, exist_ok=True)
        if key_path.exists():
            return key_path.read_bytes()

        key = Fernet.generate_key()
        key_path.write_bytes(key)
        return key

    def encrypt(self, raw_value: str) -> str:
        return self._cipher.encrypt(raw_value.encode("utf-8")).decode("utf-8")

    def decrypt(self, encrypted_value: str) -> str:
        return self._cipher.decrypt(encrypted_value.encode("utf-8")).decode("utf-8")
