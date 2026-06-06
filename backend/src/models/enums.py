from enum import StrEnum


class ImageStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    INDEXED = "indexed"
    FAILED = "failed"


class IntentType(StrEnum):
    SEMANTIC_SEARCH = "semantic_search"
    BATCH_ACTION = "batch_action"
    OCR_SEARCH = "ocr_search"
    STATISTICS = "statistics"


class RetrievalRoute(StrEnum):
    IMAGE_VECTOR = "image_vector"
    CAPTION_VECTOR = "caption_vector"
    METADATA = "metadata"
    CAPTION_TEXT = "caption_text"
    OCR_TEXT = "ocr_text"


class BatchTaskType(StrEnum):
    ARCHIVE = "archive"
    TAGGING = "tagging"
    DEDUPLICATE = "deduplicate"
    OCR_FILTER = "ocr_filter"
    BLUR_FILTER = "blur_filter"
    STATISTICS = "statistics"


class TaskStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

