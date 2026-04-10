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

    def delete_file(self, absolute_path: str) -> None:
        """Remove file and clean up empty parent directories."""
        p = Path(absolute_path)
        try:
            p.unlink(missing_ok=True)
            # Remove empty parent dirs up to but not including base
            parent = p.parent
            while parent != self.base and parent.is_dir():
                try:
                    parent.rmdir()
                    parent = parent.parent
                except OSError:
                    break
        except Exception:
            pass


storage = LocalStorage(settings.UPLOAD_DIR)