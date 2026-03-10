from __future__ import annotations

import hashlib
import math
import re


class LocalEmbeddingService:
    def __init__(self, dimensions: int = 64) -> None:
        self.dimensions = dimensions

    def _tokens(self, text: str) -> list[str]:
        normalized = re.sub(r"\s+", " ", text.lower()).strip()
        cleaned = re.sub(r"[^\w\sа-яё-]", " ", normalized)
        return [token for token in cleaned.split() if token]

    def embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        for token in self._tokens(text):
            digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
            index = int(digest[:8], 16) % self.dimensions
            vector[index] += 1.0

        norm = math.sqrt(sum(value * value for value in vector))
        if norm == 0:
            return vector
        return [round(value / norm, 8) for value in vector]
