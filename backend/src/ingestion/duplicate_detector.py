import hashlib
from pathlib import Path


class DuplicateDetector:
    async def detect(self, image_path: str) -> dict:
        sha256 = hashlib.sha256(Path(image_path).read_bytes()).hexdigest()
        return {"sha256": sha256, "duplicate": False}
