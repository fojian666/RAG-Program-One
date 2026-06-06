import json
import logging
import math
from pathlib import Path

from src.config.settings import get_settings

logger = logging.getLogger(__name__)


class LocalVectorClient:
    """Pure-python in-memory vector store with JSON file persistence.

    No external dependencies (no FAISS, no Qdrant server).
    Suitable for small-to-medium datasets (< 50k vectors).
    """

    def __init__(self, data_path: str | None = None):
        settings = get_settings()
        self.data_path = Path(data_path or settings.local_vector_path)
        self.data_path.mkdir(parents=True, exist_ok=True)
        self._store: dict[str, dict[str, dict]] = {}
        self._load_all()

    def _file_for(self, collection: str) -> Path:
        return self.data_path / f"{collection}.json"

    def _load(self, collection: str) -> dict[str, dict]:
        file_path = self._file_for(collection)
        if not file_path.exists():
            return {}
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return {item["id"]: item for item in data.get("vectors", [])}
        except (json.JSONDecodeError, KeyError, TypeError) as exc:
            logger.warning("Vector file corrupted for collection '%s': %s", collection, exc)
            return {}

    def _load_all(self) -> None:
        for file_path in self.data_path.glob("*.json"):
            collection = file_path.stem
            self._store[collection] = self._load(collection)

    def _save(self, collection: str) -> None:
        file_path = self._file_for(collection)
        data = {"vectors": list(self._store.get(collection, {}).values())}
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)

    async def upsert(
        self,
        collection_name: str,
        points: list[dict],
    ) -> None:
        if collection_name not in self._store:
            self._store[collection_name] = {}
        for point in points:
            self._store[collection_name][point["id"]] = point
        self._save(collection_name)

    def get(self, collection_name: str, point_id: str) -> dict | None:
        if collection_name not in self._store:
            return None
        return self._store[collection_name].get(point_id)

    async def search(
        self,
        collection_name: str,
        query_vector: list[float],
        limit: int = 10,
        query_filter: dict | None = None,
        with_payload: bool = True,
    ) -> list[dict]:
        if collection_name not in self._store:
            return []

        vectors = list(self._store[collection_name].values())
        scored = []
        for item in vectors:
            vec = item["vector"]
            score = self._cosine_similarity(query_vector, vec)
            # Simple payload filter
            if query_filter and not self._match_filter(item.get("payload", {}), query_filter):
                continue
            scored.append((score, item))

        scored.sort(key=lambda x: x[0], reverse=True)
        results = []
        for score, item in scored[:limit]:
            result = {"id": item["id"], "score": score}
            if with_payload:
                result["payload"] = item.get("payload", {})
            results.append(result)
        return results

    @staticmethod
    def _cosine_similarity(a: list[float], b: list[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(x * x for x in b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

    @staticmethod
    def _match_filter(payload: dict, query_filter: dict) -> bool:
        # Supports simple "must" list of {key, match:{any:[values]}} structures
        must_conditions = query_filter.get("must", [])
        for condition in must_conditions:
            key = condition.get("key", "")
            match = condition.get("match", {})
            any_values = match.get("any", [])
            # key may be like "metadata.scene"
            keys = key.split(".")
            value = payload
            for k in keys:
                if isinstance(value, dict):
                    value = value.get(k, {})
                else:
                    value = {}
            if isinstance(value, list):
                if not any(v in value for v in any_values):
                    return False
            else:
                if value not in any_values:
                    return False
        return True
