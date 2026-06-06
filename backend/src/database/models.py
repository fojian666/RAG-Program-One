from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from src.models.enums import ImageStatus, TaskStatus


def utcnow() -> datetime:
    return datetime.now(UTC)


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        onupdate=utcnow,
    )


class Image(Base, TimestampMixin):
    __tablename__ = "images"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    object_key: Mapped[str] = mapped_column(String(1024), nullable=False, unique=True)
    bucket: Mapped[str] = mapped_column(String(255), nullable=False)
    file_name: Mapped[str] = mapped_column(String(512), nullable=False)
    file_ext: Mapped[str] = mapped_column(String(32), default="")
    mime_type: Mapped[str] = mapped_column(String(128), default="")
    file_size: Mapped[int | None] = mapped_column(Integer)
    width: Mapped[int | None] = mapped_column(Integer)
    height: Mapped[int | None] = mapped_column(Integer)
    phash: Mapped[str | None] = mapped_column(String(128), index=True)
    sha256: Mapped[str | None] = mapped_column(String(128), index=True)
    source: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(32), default=ImageStatus.PENDING.value, index=True)

    captions: Mapped[list["Caption"]] = relationship(back_populates="image")
    metadata_entries: Mapped[list["ImageMetadata"]] = relationship(back_populates="image")
    tags: Mapped[list["ImageTag"]] = relationship(back_populates="image")


class Caption(Base):
    __tablename__ = "captions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    image_id: Mapped[str] = mapped_column(String(36), ForeignKey("images.id"), index=True)
    model_name: Mapped[str] = mapped_column(String(255), nullable=False)
    caption: Mapped[str] = mapped_column(Text, nullable=False)
    dense_caption: Mapped[str] = mapped_column(Text, default="")
    language: Mapped[str] = mapped_column(String(16), default="zh")
    version: Mapped[str] = mapped_column(String(64), default="v1")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    image: Mapped[Image] = relationship(back_populates="captions")


class ImageMetadata(Base, TimestampMixin):
    __tablename__ = "metadata"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    image_id: Mapped[str] = mapped_column(String(36), ForeignKey("images.id"), index=True)
    objects: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    scene: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    actions: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    emotion: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    context: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    colors: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    people: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    animals: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    ocr_text: Mapped[str] = mapped_column(Text, default="")
    ocr_blocks: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    quality: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    aesthetic_score: Mapped[float | None] = mapped_column(Float)
    safety_labels: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    raw_analysis: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    model_name: Mapped[str] = mapped_column(String(255), nullable=False)
    version: Mapped[str] = mapped_column(String(64), default="v1")

    image: Mapped[Image] = relationship(back_populates="metadata_entries")

    __table_args__ = (
        Index("ix_metadata_objects", "objects"),
        Index("ix_metadata_scene", "scene"),
        Index("ix_metadata_emotion", "emotion"),
    )


class ImageTag(Base):
    __tablename__ = "image_tags"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    image_id: Mapped[str] = mapped_column(String(36), ForeignKey("images.id"), index=True)
    tag: Mapped[str] = mapped_column(String(255), index=True)
    tag_type: Mapped[str] = mapped_column(String(32), default="auto")
    confidence: Mapped[float | None] = mapped_column(Float)
    created_by: Mapped[str] = mapped_column(String(255), default="system")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    image: Mapped[Image] = relationship(back_populates="tags")

    __table_args__ = (UniqueConstraint("image_id", "tag", "tag_type", name="uq_image_tag_type"),)


class QueryHistory(Base):
    __tablename__ = "query_history"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    query_text: Mapped[str] = mapped_column(Text, nullable=False)
    intent: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    expanded_query: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    plan: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    filters: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    result_count: Mapped[int] = mapped_column(Integer, default=0)
    latency_ms: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class QueryResult(Base):
    __tablename__ = "query_results"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    query_id: Mapped[int] = mapped_column(ForeignKey("query_history.id"), index=True)
    image_id: Mapped[str] = mapped_column(String(36), ForeignKey("images.id"), index=True)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    explanation: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class BatchTask(Base, TimestampMixin):
    __tablename__ = "batch_tasks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    task_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    user_instruction: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default=TaskStatus.PENDING.value, index=True)
    plan: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    total_items: Mapped[int] = mapped_column(Integer, default=0)
    processed_items: Mapped[int] = mapped_column(Integer, default=0)
    success_items: Mapped[int] = mapped_column(Integer, default=0)
    failed_items: Mapped[int] = mapped_column(Integer, default=0)


class TaskLog(Base):
    __tablename__ = "task_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("batch_tasks.id"), index=True)
    image_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("images.id"),
        index=True,
    )
    agent_name: Mapped[str] = mapped_column(String(255), nullable=False)
    action: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    message: Mapped[str] = mapped_column(Text, default="")
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class ImageCollection(Base, TimestampMixin):
    __tablename__ = "image_collections"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(Text, default="")
    collection_type: Mapped[str] = mapped_column(String(32), default="agent")


class ImageCollectionItem(Base):
    __tablename__ = "image_collection_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    collection_id: Mapped[int] = mapped_column(ForeignKey("image_collections.id"), index=True)
    image_id: Mapped[str] = mapped_column(String(36), ForeignKey("images.id"), index=True)
    reason: Mapped[str] = mapped_column(Text, default="")
    score: Mapped[float | None] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    __table_args__ = (UniqueConstraint("collection_id", "image_id", name="uq_collection_image"),)
