def embed_text(text: str) -> list[float]:
    return [float(len(text) % 10), 0.5, 0.2]
