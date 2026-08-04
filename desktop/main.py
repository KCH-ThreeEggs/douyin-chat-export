"""Executable entry point for the Windows desktop build."""
from __future__ import annotations

import asyncio
import multiprocessing
import sys
import traceback

from desktop.launcher import APP_TITLE, DesktopServer, configure_environment


def run_worker(argv: list[str]) -> int:
    if not argv or argv[0] != "extract":
        print("[-] 未知 worker 类型", file=sys.stderr)
        return 2

    # Recreate the source CLI contract expected by extract._parse_args().
    sys.argv = ["extract.py", *argv[1:]]
    import extract

    return int(asyncio.run(extract.run()) or 0)


def run_desktop() -> int:
    configure_environment()

    from extractor.models import init_db

    init_db()
    server = DesktopServer()
    server.start()

    import webview

    window = webview.create_window(
        APP_TITLE,
        f"{server.base_url}/panel",
        width=1280,
        height=820,
        min_size=(980, 680),
        text_select=True,
    )
    window.events.closed += server.stop

    try:
        webview.start(debug=False)
    finally:
        server.stop()
    return 0


def main() -> int:
    configure_environment()
    if len(sys.argv) >= 2 and sys.argv[1] == "--worker":
        return run_worker(sys.argv[2:])

    try:
        return run_desktop()
    except Exception:
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    multiprocessing.freeze_support()
    raise SystemExit(main())
