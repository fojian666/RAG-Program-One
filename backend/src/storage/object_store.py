from pathlib import Path
from typing import Any


class ObjectStore:
    def __init__(self, client: Any, bucket: str):
        self.client = client
        self.bucket = bucket

    async def put_image(self, image_path: str, object_key: str | None = None) -> str:
        path = Path(image_path)
        key = object_key or path.name
        self.client.fput_object(self.bucket, key, str(path))
        return key

