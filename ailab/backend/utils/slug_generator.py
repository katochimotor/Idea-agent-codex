import re


def slugify(value: str) -> str:
    lowered = value.lower().strip()
    ascii_like = lowered.replace(" ", "-")
    return re.sub(r"[^a-z0-9а-яё-]+", "", ascii_like)
