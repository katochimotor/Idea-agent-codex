import os
import webbrowser


def open_browser(url: str) -> None:
    if hasattr(os, "startfile"):
        os.startfile(url)  # type: ignore[attr-defined]
        return
    webbrowser.open(url)
