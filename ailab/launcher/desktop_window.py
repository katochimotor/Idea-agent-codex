def open_desktop_window(url: str, title: str) -> None:
    try:
        import webview
    except ImportError as exc:
        raise RuntimeError(
            "pywebview is not installed. Run 'ailab\\scripts\\install_env.bat' or "
            "'ailab\\.venv\\Scripts\\python.exe -m pip install pywebview'."
        ) from exc

    webview.create_window(title, url=url, width=1440, height=920, min_size=(1100, 700))
    webview.start()
