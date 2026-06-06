from src.caption.qwen_vl_captioner import QwenVLImageAnalyzer
from src.database.repositories.image_repository import ImageRepository
from src.embeddings.base import ImageEmbedder, TextEmbedder
from src.ingestion.duplicate_detector import DuplicateDetector
from src.ingestion.preprocessing import ImagePreprocessor
from src.ingestion.quality_detector import ImageQualityDetector
from src.storage.object_store import ObjectStore
from src.vector_store.indexer import VectorIndexer


class ImageIngestionPipeline:
    def __init__(
        self,
        *,
        object_store: ObjectStore,
        image_repository: ImageRepository,
        image_embedder: ImageEmbedder,
        text_embedder: TextEmbedder,
        analyzer: QwenVLImageAnalyzer,
        vector_indexer: VectorIndexer,
        preprocessor: ImagePreprocessor | None = None,
        duplicate_detector: DuplicateDetector | None = None,
        quality_detector: ImageQualityDetector | None = None,
    ):
        self.object_store = object_store
        self.image_repository = image_repository
        self.image_embedder = image_embedder
        self.text_embedder = text_embedder
        self.analyzer = analyzer
        self.vector_indexer = vector_indexer
        self.preprocessor = preprocessor or ImagePreprocessor()
        self.duplicate_detector = duplicate_detector or DuplicateDetector()
        self.quality_detector = quality_detector or ImageQualityDetector()

    async def ingest(self, image_path: str) -> str:
        file_info = await self.preprocessor.inspect(image_path)
        duplicate = await self.duplicate_detector.detect(image_path)
        object_key = await self.object_store.put_image(image_path)

        image = await self.image_repository.create_image(
            object_key=object_key,
            bucket=self.object_store.bucket,
            file_name=file_info["file_name"],
            file_ext=file_info["file_ext"],
            file_size=file_info["file_size"],
            sha256=duplicate.get("sha256"),
        )

        quality = await self.quality_detector.detect(image_path)
        analysis = await self.analyzer.analyze(image_path)
        caption_vector = await self.text_embedder.embed_text(analysis.caption)

        await self.image_repository.save_analysis(
            image.id,
            analysis,
            quality,
            model_name="qwen-vl-max",
        )

        if self.image_embedder is not None:
            image_vector = await self.image_embedder.embed_image(image_path)
            await self.vector_indexer.upsert_image_vector(
                image.id,
                image_vector,
                payload={"metadata": analysis.model_dump(), "caption": analysis.caption},
            )

        await self.vector_indexer.upsert_caption_vector(
            image.id,
            caption_vector,
            payload={"caption": analysis.caption},
        )
        return image.id
