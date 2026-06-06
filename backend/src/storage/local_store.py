import shutil
from pathlib import Path

from src.config.settings import get_settings


class LocalObjectStore:
    """Filesystem-based object store. No external dependencies."""

    def __init__(self, base_path: str | None = None):
        settings = get_settings()
        self.base_path = Path(base_path or settings.local_storage_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def fput_object(self, bucket: str, key: str, file_path: str) -> None:
        bucket_path = self.base_path / bucket
        bucket_path.mkdir(parents=True, exist_ok=True)
        dest = bucket_path / key
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file_path, dest)

    def fget_object(self, bucket: str, key: str, file_path: str) -> None:
        src = self.base_path / bucket / key
        shutil.copy2(src, file_path)

    def remove_object(self, bucket: str, key: str) -> None:
        target = self.base_path / bucket / key
        if target.exists():
            target.unlink()

    def stat_object(self, bucket: str, key: str) -> dict | None:
        target = self.base_path / bucket / key
        if not target.exists():
            return None
        return {
            "bucket_name": bucket,
            "object_name": key,
            "size": target.stat().st_size,
        }

    def list_objects(self, bucket: str, prefix: str = "") -> list[dict]:
        bucket_path = self.base_path / bucket
        if not bucket_path.exists():
            return []
        results = []
        for item in bucket_path.rglob("*"):
            if item.is_file():
                rel = item.relative_to(bucket_path).as_posix()
                if rel.startswith(prefix):
                    results.append({
                        "object_name": rel,
                        "size": item.stat().st_size,
                    })
        return results
