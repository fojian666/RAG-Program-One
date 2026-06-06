from typing import Protocol


class ImageEmbedder(Protocol):
    async def embed_image(self, image_path: str) -> list[float]:
        ...


class TextEmbedder(Protocol):
    async def embed_text(self, text: str) -> list[float]:
        ...

