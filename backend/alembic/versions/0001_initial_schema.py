"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-06-04
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0001_initial_schema"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "images",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("object_key", sa.String(length=1024), nullable=False),
        sa.Column("bucket", sa.String(length=255), nullable=False),
        sa.Column("file_name", sa.String(length=512), nullable=False),
        sa.Column("file_ext", sa.String(length=32), nullable=False),
        sa.Column("mime_type", sa.String(length=128), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=True),
        sa.Column("width", sa.Integer(), nullable=True),
        sa.Column("height", sa.Integer(), nullable=True),
        sa.Column("phash", sa.String(length=128), nullable=True),
        sa.Column("sha256", sa.String(length=128), nullable=True),
        sa.Column("source", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("object_key"),
    )
    op.create_index(op.f("ix_images_phash"), "images", ["phash"])
    op.create_index(op.f("ix_images_sha256"), "images", ["sha256"])
    op.create_index(op.f("ix_images_status"), "images", ["status"])

    op.create_table(
        "captions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("image_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("model_name", sa.String(length=255), nullable=False),
        sa.Column("caption", sa.Text(), nullable=False),
        sa.Column("dense_caption", sa.Text(), nullable=False),
        sa.Column("language", sa.String(length=16), nullable=False),
        sa.Column("version", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["image_id"], ["images.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_captions_image_id"), "captions", ["image_id"])

    op.create_table(
        "metadata",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("image_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("objects", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("scene", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("actions", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("emotion", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("context", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("colors", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("people", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("animals", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("ocr_text", sa.Text(), nullable=False),
        sa.Column("ocr_blocks", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("quality", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("aesthetic_score", sa.Float(), nullable=True),
        sa.Column("safety_labels", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("raw_analysis", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("model_name", sa.String(length=255), nullable=False),
        sa.Column("version", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["image_id"], ["images.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_metadata_image_id"), "metadata", ["image_id"])
    op.create_index("ix_metadata_objects_gin", "metadata", ["objects"], postgresql_using="gin")
    op.create_index("ix_metadata_scene_gin", "metadata", ["scene"], postgresql_using="gin")
    op.create_index("ix_metadata_emotion_gin", "metadata", ["emotion"], postgresql_using="gin")

    op.create_table(
        "image_tags",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("image_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("tag", sa.String(length=255), nullable=False),
        sa.Column("tag_type", sa.String(length=32), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("created_by", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["image_id"], ["images.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("image_id", "tag", "tag_type", name="uq_image_tag_type"),
    )
    op.create_index(op.f("ix_image_tags_image_id"), "image_tags", ["image_id"])
    op.create_index(op.f("ix_image_tags_tag"), "image_tags", ["tag"])

    op.create_table(
        "query_history",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("query_text", sa.Text(), nullable=False),
        sa.Column("intent", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("expanded_query", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("plan", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("filters", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("result_count", sa.Integer(), nullable=False),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "query_results",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("query_id", sa.Integer(), nullable=False),
        sa.Column("image_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("rank", sa.Integer(), nullable=False),
        sa.Column("explanation", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["image_id"], ["images.id"]),
        sa.ForeignKeyConstraint(["query_id"], ["query_history.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_query_results_image_id"), "query_results", ["image_id"])
    op.create_index(op.f("ix_query_results_query_id"), "query_results", ["query_id"])

    op.create_table(
        "batch_tasks",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("task_type", sa.String(length=64), nullable=False),
        sa.Column("user_instruction", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("plan", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("total_items", sa.Integer(), nullable=False),
        sa.Column("processed_items", sa.Integer(), nullable=False),
        sa.Column("success_items", sa.Integer(), nullable=False),
        sa.Column("failed_items", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_batch_tasks_status"), "batch_tasks", ["status"])
    op.create_index(op.f("ix_batch_tasks_task_type"), "batch_tasks", ["task_type"])

    op.create_table(
        "task_logs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("task_id", sa.Integer(), nullable=False),
        sa.Column("image_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("agent_name", sa.String(length=255), nullable=False),
        sa.Column("action", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["image_id"], ["images.id"]),
        sa.ForeignKeyConstraint(["task_id"], ["batch_tasks.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_task_logs_image_id"), "task_logs", ["image_id"])
    op.create_index(op.f("ix_task_logs_task_id"), "task_logs", ["task_id"])

    op.create_table(
        "image_collections",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("collection_type", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "image_collection_items",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("collection_id", sa.Integer(), nullable=False),
        sa.Column("image_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["collection_id"], ["image_collections.id"]),
        sa.ForeignKeyConstraint(["image_id"], ["images.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("collection_id", "image_id", name="uq_collection_image"),
    )
    op.create_index(
        op.f("ix_image_collection_items_collection_id"),
        "image_collection_items",
        ["collection_id"],
    )
    op.create_index(
        op.f("ix_image_collection_items_image_id"),
        "image_collection_items",
        ["image_id"],
    )


def downgrade() -> None:
    op.drop_table("image_collection_items")
    op.drop_table("image_collections")
    op.drop_table("task_logs")
    op.drop_table("batch_tasks")
    op.drop_table("query_results")
    op.drop_table("query_history")
    op.drop_table("image_tags")
    op.drop_table("metadata")
    op.drop_table("captions")
    op.drop_table("images")
