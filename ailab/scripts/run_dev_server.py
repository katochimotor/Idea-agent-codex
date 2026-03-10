import subprocess
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]


def main() -> None:
    subprocess.run([sys.executable, "-m", "uvicorn", "backend.main:app", "--reload", "--port", "8000"], cwd=ROOT_DIR, check=True)


if __name__ == "__main__":
    main()
