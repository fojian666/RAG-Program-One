from src.models.dto import ImageAnalysisResult


class VisionAnalysisParser:
    def parse(self, payload: dict) -> ImageAnalysisResult:
        return ImageAnalysisResult(**payload)

