import asyncio
import tempfile
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, File, Form, UploadFile
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import func, select

PROJECT_ROOT = Path(__file__).resolve().parent.parent

from src.caption.qwen_vl_captioner import BailianVisionAnalyzer
from src.config.logging import configure_logging
from src.config.settings import get_settings
from src.database.models import Base, Caption, Image
from src.database.repositories.image_repository import ImageRepository
from src.database.session import AsyncSessionFactory, engine
from src.embeddings.text_embedder import BailianTextEmbedder
from src.graph.query_graph import build_query_graph
from src.ingestion.pipeline import ImageIngestionPipeline
from src.ingestion.quality_detector import ImageQualityDetector
from src.storage.local_store import LocalObjectStore
from src.storage.minio_client import build_minio_client
from src.storage.object_store import ObjectStore
from src.vector_store.indexer import VectorIndexer
from src.vector_store.local_client import LocalVectorClient
from src.vector_store.qdrant_client import build_qdrant_client

_DEFAULT_FILE = File(...)
_DEFAULT_PATHS = Form(...)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    settings = get_settings()
    # Auto-create tables for SQLite so users don't need alembic
    if settings.db_backend == "sqlite":
        db_path = Path(settings.database_url.replace("sqlite+aiosqlite:///", ""))
        db_path.parent.mkdir(parents=True, exist_ok=True)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    # Warn about missing API keys (don't block startup — user may only browse existing data)
    if not (settings.embedding_api_key or settings.llm_api_key):
        import logging
        logging.getLogger(__name__).warning(
            "BAILIAN_API_KEY not configured. Text search and ingestion will fail. "
            "Set it in .env (EMBEDDING_API_KEY or LLM_API_KEY)."
        )

    yield
    # Cleanup: remove uploaded temp files on shutdown
    uploads_dir = PROJECT_ROOT / "data" / "uploads"
    if uploads_dir.exists():
        for f in uploads_dir.iterdir():
            try:
                f.unlink()
            except OSError:
                pass


app = FastAPI(
    title="Agentic Image RAG",
    version="0.1.0",
    lifespan=lifespan,
)

# Global exception handlers — return unified JSON error format
@app.exception_handler(Exception)
async def _generic_exception_handler(request, exc):
    import logging
    logging.getLogger(__name__).exception("Unhandled exception: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)},
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Only expose image directories, not the entire data folder (which contains .db and .json files)
app.mount("/data/images", StaticFiles(directory=str(PROJECT_ROOT / "data" / "images")), name="images")
app.mount("/data/uploads", StaticFiles(directory=str(PROJECT_ROOT / "data" / "uploads")), name="uploads")


def _build_pipeline(session) -> ImageIngestionPipeline:
    settings = get_settings()

    if settings.storage_backend == "local":
        minio_client = LocalObjectStore()
    else:
        minio_client = build_minio_client()
    object_store = ObjectStore(minio_client, settings.minio_bucket)

    if settings.vector_backend == "local":
        qdrant_client = LocalVectorClient()
    else:
        qdrant_client = build_qdrant_client()
    vector_indexer = VectorIndexer(qdrant_client)

    text_embedder = BailianTextEmbedder()
    # Image embedder (SigLIP) is optional
    image_embedder = None
    return ImageIngestionPipeline(
        object_store=object_store,
        image_repository=ImageRepository(session),
        image_embedder=image_embedder,
        text_embedder=text_embedder,
        analyzer=BailianVisionAnalyzer(),
        vector_indexer=vector_indexer,
        quality_detector=ImageQualityDetector(),
    )


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.post("/api/v1/query")
async def query(
    q: str = Form(..., description="Natural language image query"),
) -> JSONResponse:
    """Run the agentic query graph."""
    graph = build_query_graph()
    result = await graph.ainvoke({"query": q})
    return JSONResponse(
        content={
            "query": q,
            "intent": result.get("intent"),
            "expanded_query": result.get("expanded_query"),
            "plan": result.get("plan"),
            "results": result.get("final_results", []),
            "explanations": result.get("explanations", []),
            "errors": result.get("errors", []),
        }
    )


@app.post("/api/v1/ingest")
async def ingest(
    file: UploadFile = _DEFAULT_FILE,
) -> JSONResponse:
    """Ingest a single image into the knowledge base."""
    suffix = Path(file.filename or "upload.jpg").suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        async with AsyncSessionFactory() as session:
            pipeline = _build_pipeline(session)
            image_id = await pipeline.ingest(tmp_path)
            await session.commit()
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    return JSONResponse(
        content={
            "image_id": image_id,
            "filename": file.filename,
            "status": "ingested",
        }
    )


@app.post("/api/v1/ingest/batch")
async def ingest_batch(
    paths: list[str] = _DEFAULT_PATHS,
) -> JSONResponse:
    """Batch ingest images with controlled concurrency."""
    settings = get_settings()
    concurrency = settings.ingestion_concurrency
    max_retries = settings.ingestion_max_retries
    semaphore = asyncio.Semaphore(concurrency)

    results = {"success": [], "failed": []}

    async def _ingest_one(image_path: str) -> None:
        for attempt in range(max_retries):
            try:
                async with semaphore:
                    async with AsyncSessionFactory() as session:
                        pipeline = _build_pipeline(session)
                        image_id = await pipeline.ingest(image_path)
                        await session.commit()
                results["success"].append(
                    {"path": image_path, "image_id": image_id}
                )
                return
            except Exception as exc:
                if attempt == max_retries - 1:
                    results["failed"].append(
                        {"path": image_path, "error": str(exc)}
                    )
                else:
                    await asyncio.sleep(1)

    await asyncio.gather(*[_ingest_one(p) for p in paths])

    return JSONResponse(
        content={
            "total": len(paths),
            "success_count": len(results["success"]),
            "failed_count": len(results["failed"]),
            "results": results,
        }
    )


@app.get("/api/v1/images")
async def list_images(
    page: int = 1,
    size: int = 12,
    source: str | None = None,
    q: str = "",
) -> JSONResponse:
    """List ingested images with pagination and optional source filter."""
    async with AsyncSessionFactory() as session:
        # Build base query joining Image + latest Caption
        stmt = (
            select(Image, Caption.caption)
            .outerjoin(Caption, Image.id == Caption.image_id)
            .order_by(Image.created_at.desc())
        )
        count_stmt = select(func.count(Image.id))

        if source:
            stmt = stmt.where(Image.bucket == f"{source}_images")
            count_stmt = count_stmt.where(Image.bucket == f"{source}_images")
        if q:
            like = f"%{q}%"
            stmt = stmt.where(
                (Image.object_key.ilike(like))
                | (Caption.caption.ilike(like))
            )
            count_stmt = count_stmt.where(
                (Image.object_key.ilike(like))
                | (Caption.caption.ilike(like))
            )

        total_res = await session.execute(count_stmt)
        total = total_res.scalar() or 0

        stmt = stmt.offset((page - 1) * size).limit(size)
        result = await session.execute(stmt)
        rows = result.all()

        items = []
        for image, caption in rows:
            items.append({
                "id": image.id,
                "object_key": image.object_key,
                "source": image.bucket.replace("_images", ""),
                "caption": caption or "",
                "created_at": image.created_at.isoformat() if image.created_at else None,
                "preview_url": f"/data/images/{image.bucket}/{image.object_key}",
            })

    return JSONResponse(
        content={"total": total, "page": page, "size": size, "items": items}
    )


class SearchRequest(BaseModel):
    query: str | None = None
    image_path: str | None = None
    threshold: float = 0.0
    source: str | None = None
    limit: int = 20


@app.post("/api/v1/search")
async def api_search(req: SearchRequest) -> JSONResponse:
    """Semantic similarity search across vector collections."""
    vector_client = LocalVectorClient()
    embedder = BailianTextEmbedder()

    # Determine query vector
    if req.query:
        try:
            query_vector = await embedder.embed_text(req.query)
        except ValueError as exc:
            return JSONResponse(
                content={"results": [], "message": str(exc)},
                status_code=503,
            )
    elif req.image_path:
        # For image-based search we'd need image embedder; fallback to text for now
        return JSONResponse(
            content={"results": [], "message": "Image-based search requires image embedder"},
            status_code=400,
        )
    else:
        return JSONResponse(
            content={"results": [], "message": "Provide query or image_path"},
            status_code=400,
        )

    collections = ["t1_caption_embeddings", "t2_caption_embeddings"]
    if req.source:
        collections = [f"{req.source}_caption_embeddings"]

    all_results = []
    for col in collections:
        hits = await vector_client.search(col, query_vector, limit=req.limit)
        for hit in hits:
            if hit["score"] >= req.threshold:
                payload = hit.get("payload", {})
                all_results.append({
                    "id": hit["id"],
                    "score": hit["score"],
                    "source": col.replace("_caption_embeddings", ""),
                    "caption": payload.get("caption", ""),
                })

    all_results.sort(key=lambda x: x["score"], reverse=True)
    all_results = all_results[:req.limit]

    # Enrich with DB info
    async with AsyncSessionFactory() as session:
        enriched = []
        for r in all_results:
            img = await session.execute(
                select(Image).where(Image.id == r["id"])
            )
            image = img.scalar_one_or_none()
            if image:
                enriched.append({
                    "id": r["id"],
                    "object_key": image.object_key,
                    "source": r["source"],
                    "caption": r["caption"],
                    "score": r["score"],
                    "preview_url": f"/data/images/{image.bucket}/{image.object_key}",
                })
            else:
                enriched.append({
                    "id": r["id"],
                    "object_key": "",
                    "source": r["source"],
                    "caption": r["caption"],
                    "score": r["score"],
                    "preview_url": "",
                })

    return JSONResponse(content={"results": enriched})


# Allowed image MIME types and max upload size (10 MB)
_ALLOWED_IMAGE_TYPES = {
    "image/png",
    "image/jpeg",
    "image/jpg",
    "image/webp",
    "image/tiff",
    "image/gif",
}
_MAX_UPLOAD_SIZE = 10 * 1024 * 1024


@app.post("/api/v1/upload")
async def api_upload(
    file: UploadFile = _DEFAULT_FILE,
) -> JSONResponse:
    """Upload a reference image for similarity search."""
    # Validate content type
    content_type = file.content_type or ""
    if content_type not in _ALLOWED_IMAGE_TYPES:
        return JSONResponse(
            content={
                "error": f"Unsupported file type: {content_type}. Allowed: {', '.join(_ALLOWED_IMAGE_TYPES)}"
            },
            status_code=415,
        )

    content = await file.read()

    # Validate size
    if len(content) > _MAX_UPLOAD_SIZE:
        return JSONResponse(
            content={"error": f"File too large. Max size: {_MAX_UPLOAD_SIZE // 1024 // 1024}MB"},
            status_code=413,
        )

    # Sanitize filename to prevent path traversal
    safe_name = Path(file.filename or "upload.jpg").name
    dest_dir = PROJECT_ROOT / "data" / "uploads"
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / f"ref_{safe_name}"

    with open(dest_path, "wb") as f:
        f.write(content)

    return JSONResponse(
        content={"path": str(dest_path)}
    )


@app.get("/api/v1/pairs")
async def api_pairs() -> JSONResponse:
    """List all T1/T2 image pairs by matching object_key (stripped prefix)."""
    async with AsyncSessionFactory() as session:
        result = await session.execute(select(Image).order_by(Image.object_key))
        images = result.scalars().all()

        # Group by stripped object key
        groups: dict[str, dict[str, dict]] = {}
        for img in images:
            stripped = img.object_key
            if stripped.startswith("t1_"):
                stripped = stripped[3:]
            elif stripped.startswith("t2_"):
                stripped = stripped[3:]
            if stripped not in groups:
                groups[stripped] = {}
            groups[stripped][img.bucket.replace("_images", "")] = {
                "id": img.id,
                "object_key": img.object_key,
                "bucket": img.bucket,
                "preview_url": f"/data/images/{img.bucket}/{img.object_key}",
            }

        pairs = []
        for key, sides in groups.items():
            if "t1" in sides and "t2" in sides:
                pairs.append({
                    "pair_id": key,
                    "t1": sides["t1"],
                    "t2": sides["t2"],
                })

        return JSONResponse(content={"pairs": pairs, "total": len(pairs)})


@app.get("/api/v1/pairs/{pair_id}/similarity")
async def api_pair_similarity(pair_id: str) -> JSONResponse:
    """Compute cosine similarity between T1 and T2 caption vectors."""
    vector_client = LocalVectorClient()
    async with AsyncSessionFactory() as session:
        result = await session.execute(
            select(Image).where(Image.object_key == f"t1_{pair_id}")
        )
        t1_img = result.scalar_one_or_none()
        result = await session.execute(
            select(Image).where(Image.object_key == f"t2_{pair_id}")
        )
        t2_img = result.scalar_one_or_none()

        if not t1_img or not t2_img:
            return JSONResponse(
                content={"error": "Pair not found"}, status_code=404
            )

        t1_vec = vector_client.get("t1_caption_embeddings", str(t1_img.id))
        t2_vec = vector_client.get("t2_caption_embeddings", str(t2_img.id))

        if not t1_vec or not t2_vec:
            return JSONResponse(
                content={"error": "Vectors not found"}, status_code=404
            )

        similarity = LocalVectorClient._cosine_similarity(
            t1_vec["vector"], t2_vec["vector"]
        )

        return JSONResponse(
            content={
                "pair_id": pair_id,
                "similarity": round(similarity, 4),
                "t1_id": str(t1_img.id),
                "t2_id": str(t2_img.id),
            }
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
