import os
from pathlib import Path

from app.core.config import settings


class LocalStorage:
    def __init__(self, base_dir: str) -> None:
        self.base = Path(base_dir)

    def ensure(self) -> None:
        self.base.mkdir(parents=True, exist_ok=True)

    def save_bytes(self, relative_path: str, data: bytes) -> str:
        self.ensure()
        full = self.base / relative_path
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_bytes(data)
        return str(full)

    def open_bytes(self, absolute_path: str) -> bytes:
        return Path(absolute_path).read_bytes()


storage = LocalStorage(settings.UPLOAD_DIR)