from pathlib import Path


class ImagePreprocessor:
    async def inspect(self, image_path: str) -> dict:
        path = Path(image_path)
        stat = path.stat()
        return {
            "file_name": path.name,
            "file_ext": path.suffix.lstrip(".").lower(),
            "file_size": stat.st_size,
        }
