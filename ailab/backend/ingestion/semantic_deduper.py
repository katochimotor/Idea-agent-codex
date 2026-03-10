from __future__ import annotations

import hashlib
import math
import re
from collections import Counter
from difflib import SequenceMatcher


def _normalize(text: str) -> str:
    cleaned = re.sub(r"\s+", " ", text.lower()).strip()
    return re.sub(r"[^\w\sа-яё-]", " ", cleaned)


def _tokens(text: str) -> list[str]:
    return [token for token in _normalize(text).split() if token]


def _trigrams(text: str) -> list[str]:
    normalized = _normalize(text).replace(" ", "")
    if len(normalized) < 3:
        return [normalized] if normalized else []
    return [normalized[index : index + 3] for index in range(len(normalized) - 2)]


def _cosine_similarity(left: Counter[str], right: Counter[str]) -> float:
    if not left or not right:
        return 0.0

    shared = set(left) & set(right)
    numerator = sum(left[token] * right[token] for token in shared)
    left_norm = math.sqrt(sum(value * value for value in left.values()))
    right_norm = math.sqrt(sum(value * value for value in right.values()))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return numerator / (left_norm * right_norm)


class SemanticDeduplicationEngine:
    """Local heuristic deduper for MVP use before embeddings are wired in."""

    def fingerprint(self, text: str) -> str:
        return hashlib.sha256(_normalize(text).encode("utf-8")).hexdigest()

    def similarity(self, left: str, right: str) -> float:
        left_tokens = set(_tokens(left))
        right_tokens = set(_tokens(right))
        token_overlap = len(left_tokens & right_tokens) / max(len(left_tokens | right_tokens), 1)
        trigram_similarity = _cosine_similarity(Counter(_trigrams(left)), Counter(_trigrams(right)))
        sequence_similarity = SequenceMatcher(None, _normalize(left), _normalize(right)).ratio()
        return round((token_overlap * 0.45) + (trigram_similarity * 0.35) + (sequence_similarity * 0.2), 4)

    def is_duplicate(self, candidate: str, existing: str, threshold: float = 0.82) -> bool:
        if self.fingerprint(candidate) == self.fingerprint(existing):
            return True
        return self.similarity(candidate, existing) >= threshold

    def rank_duplicates(self, candidate: str, existing_texts: list[str], threshold: float = 0.82) -> list[dict]:
        matches = []
        for index, existing in enumerate(existing_texts):
            similarity = self.similarity(candidate, existing)
            if similarity >= threshold:
                matches.append({"index": index, "similarity": similarity, "text": existing})
        return sorted(matches, key=lambda item: item["similarity"], reverse=True)
