import asyncio
import shutil
import tempfile
from pathlib import Path

from src.caption.qwen_vl_captioner import BailianVisionAnalyzer
from src.config.settings import get_settings
from src.database.repositories.image_repository import ImageRepository
from src.database.session import AsyncSessionFactory, engine
from src.database.models import Base
from src.embeddings.text_embedder import BailianTextEmbedder
from src.ingestion.pipeline import ImageIngestionPipeline
from src.ingestion.quality_detector import ImageQualityDetector
from src.storage.local_store import LocalObjectStore
from src.storage.object_store import ObjectStore
from src.vector_store.indexer import VectorIndexer
from src.vector_store.local_client import LocalVectorClient


async def ingest_folder(folder: Path, bucket: str, prefix: str):
    """Ingest all images from a folder into a dedicated bucket & vector collection."""
    settings = get_settings()

    # Build backend clients with isolated namespaces
    storage_client = LocalObjectStore()
    object_store = ObjectStore(storage_client, bucket)
    vector_client = LocalVectorClient()
    vector_indexer = VectorIndexer(vector_client, collection_prefix=prefix)
    text_embedder = BailianTextEmbedder()

    async with AsyncSessionFactory() as session:
        pipeline = ImageIngestionPipeline(
            object_store=object_store,
            image_repository=ImageRepository(session),
            image_embedder=None,  # SigLIP not configured
            text_embedder=text_embedder,
            analyzer=BailianVisionAnalyzer(),
            vector_indexer=vector_indexer,
            quality_detector=ImageQualityDetector(),
        )

        images = sorted(folder.glob("*.png"))
        print(f"[{prefix}] Found {len(images)} images in {folder}")

        with tempfile.TemporaryDirectory() as tmpdir:
            for img_path in images:
                try:
                    # Prefix filename so object_key is unique across T1/T2
                    prefixed_name = f"{prefix}{img_path.name}"
                    temp_path = Path(tmpdir) / prefixed_name
                    shutil.copy(img_path, temp_path)
                    image_id = await pipeline.ingest(str(temp_path))
                    print(f"  ✓ {img_path.name} -> {image_id}")
                except Exception as exc:
                    print(f"  ✗ {img_path.name} -> {exc}")

        await session.commit()
        print(f"[{prefix}] Committed {len(images)} images to DB")


async def main():
    # Ensure SQLite tables exist
    settings = get_settings()
    if settings.db_backend == "sqlite":
        db_path = Path(settings.database_url.replace("sqlite+aiosqlite:///", ""))
        db_path.parent.mkdir(parents=True, exist_ok=True)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    project_root = Path(__file__).parent.parent

    # Ingest T1
    await ingest_folder(project_root / "T1_30", bucket="t1_images", prefix="t1_")

    # Ingest T2
    await ingest_folder(project_root / "T2_30", bucket="t2_images", prefix="t2_")

    print("\nDone. Data layout:")
    print("  Storage : data/images/t1_images/  &  data/images/t2_images/")
    print("  Vectors : data/vectors/t1_caption_embeddings.json  &  t2_caption_embeddings.json")
    print("  Database: data/agentic_image_rag.db (images table with bucket=t1_images/t2_images)")


if __name__ == "__main__":
    asyncio.run(main())
