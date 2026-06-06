from pathlib import Path


class LocalImageLoader:
    def iter_images(self, root: str):
        for path in Path(root).rglob("*"):
            if path.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}:
                yield str(path)

