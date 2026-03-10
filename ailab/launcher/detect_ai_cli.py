import shutil


def detect_ai_cli() -> list[str]:
    return [name for name in ("qwen", "gpt", "claude") if shutil.which(name)]
