import base64
import os
from pathlib import Path

from cryptography.fernet import Fernet


class SecureConfig:
    def __init__(self):
        self.config_dir = Path.home() / ".error_management"
        self.config_dir.mkdir(exist_ok=True)
        self.key_file = self.config_dir / ".key"
        self.config_file = self.config_dir / ".config"
        self._init_encryption()

    def _init_encryption(self):
        if not self.key_file.exists():
            key = Fernet.generate_key()
            self.key_file.write_bytes(key)
        self.fernet = Fernet(self.key_file.read_bytes())

    def store_api_key(self, api_key: str = None):
        """Store API key from environment variable or parameter."""
        if api_key is None:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        encrypted_key = self.fernet.encrypt(api_key.encode())
        self.config_file.write_bytes(encrypted_key)

    def get_api_key(self) -> str:
        """Get API key from environment or stored config."""
        # First try environment variable
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if api_key:
            return api_key

        # Fall back to stored config
        if not self.config_file.exists():
            return None
        encrypted_key = self.config_file.read_bytes()
        return self.fernet.decrypt(encrypted_key).decode()

    def clear_api_key(self):
        if self.config_file.exists():
            self.config_file.unlink()


secure_config = SecureConfig()
