from pathlib import Path


def main() -> None:
    build_dir = Path(__file__).resolve().parents[1] / "build"
    build_dir.mkdir(parents=True, exist_ok=True)
    print("PyInstaller/Tauri build integration placeholder")


if __name__ == "__main__":
    main()
