from __future__ import annotations

import json
from pathlib import Path

from backend.settings import settings
from backend.search.similarity import cosine_similarity


class LocalVectorIndex:
    def __init__(self) -> None:
        settings.vector_index_dir.mkdir(parents=True, exist_ok=True)

    def _path(self, collection_key: str) -> Path:
        return settings.vector_index_dir / f"{collection_key}.json"

    def load(self, collection_key: str) -> dict[str, list[float]]:
        path = self._path(collection_key)
        if not path.exists():
            return {}
        return json.loads(path.read_text(encoding="utf-8"))

    def save(self, collection_key: str, vectors: dict[str, list[float]]) -> Path:
        path = self._path(collection_key)
        path.write_text(json.dumps(vectors, ensure_ascii=False), encoding="utf-8")
        return path

    def upsert_many(self, collection_key: str, vectors: dict[str, list[float]]) -> Path:
        existing = self.load(collection_key)
        existing.update(vectors)
        return self.save(collection_key, existing)

    def query(self, collection_key: str, query_vector: list[float], top_k: int = 5) -> list[dict]:
        vectors = self.load(collection_key)
        ranked = [
            {"vector_key": vector_key, "score": cosine_similarity(query_vector, vector)}
            for vector_key, vector in vectors.items()
        ]
        ranked.sort(key=lambda item: item["score"], reverse=True)
        return ranked[:top_k]
