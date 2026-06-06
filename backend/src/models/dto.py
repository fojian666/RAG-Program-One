from pydantic import BaseModel, Field


class ImageAnalysisResult(BaseModel):
    caption: str
    dense_caption: str = ""
    objects: list[str] = Field(default_factory=list)
    scene: list[str] = Field(default_factory=list)
    actions: list[str] = Field(default_factory=list)
    emotion: list[str] = Field(default_factory=list)
    context: list[str] = Field(default_factory=list)
    ocr_text: str = ""
    ocr_blocks: list[dict] = Field(default_factory=list)
    raw_analysis: dict = Field(default_factory=dict)


class ImageQualityResult(BaseModel):
    blur_score: float | None = None
    aesthetic_score: float | None = None
    width: int | None = None
    height: int | None = None
    extra: dict = Field(default_factory=dict)

