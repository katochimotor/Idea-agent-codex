import shutil


class RunnerAgent:
    def detect_available_clis(self) -> list[str]:
        candidates = ["qwen", "claude", "gpt"]
        return [name for name in candidates if shutil.which(name)]
