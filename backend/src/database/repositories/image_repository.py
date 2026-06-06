from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Caption, Image, ImageMetadata
from src.models.dto import ImageAnalysisResult, ImageQualityResult


class ImageRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_image(
        self,
        *,
        object_key: str,
        bucket: str,
        file_name: str,
        file_ext: str = "",
        mime_type: str = "",
        file_size: int | None = None,
        sha256: str | None = None,
        source: str | None = None,
    ) -> Image:
        image = Image(
            object_key=object_key,
            bucket=bucket,
            file_name=file_name,
            file_ext=file_ext,
            mime_type=mime_type,
            file_size=file_size,
            sha256=sha256,
            source=source,
        )
        self.session.add(image)
        await self.session.flush()
        return image

    async def get_by_id(self, image_id: str) -> Image | None:
        result = await self.session.execute(select(Image).where(Image.id == image_id))
        return result.scalar_one_or_none()

    async def save_analysis(
        self,
        image_id: str,
        analysis: ImageAnalysisResult,
        quality: ImageQualityResult,
        *,
        model_name: str,
        version: str = "v1",
    ) -> None:
        self.session.add(
            Caption(
                image_id=image_id,
                model_name=model_name,
                caption=analysis.caption,
                dense_caption=analysis.dense_caption,
                version=version,
            )
        )
        self.session.add(
            ImageMetadata(
                image_id=image_id,
                objects={"items": analysis.objects},
                scene={"items": analysis.scene},
                actions={"items": analysis.actions},
                emotion={"items": analysis.emotion},
                context={"items": analysis.context},
                ocr_text=analysis.ocr_text,
                ocr_blocks={"items": analysis.ocr_blocks},
                quality=quality.model_dump(),
                aesthetic_score=quality.aesthetic_score,
                raw_analysis=analysis.raw_analysis,
                model_name=model_name,
                version=version,
            )
        )

