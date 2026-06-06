from PIL import Image

from src.models.dto import ImageQualityResult


class ImageQualityDetector:
    async def detect(self, image_path: str) -> ImageQualityResult:
        with Image.open(image_path) as img:
            width, height = img.size
        return ImageQualityResult(
            width=width,
            height=height,
            blur_score=None,
            aesthetic_score=None,
            extra={},
        )
