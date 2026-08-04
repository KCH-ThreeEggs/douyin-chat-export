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


def _worker_args_from_process_argv(argv: list[str]) -> list[str] | None:
    if len(argv) >= 2 and argv[0] == "--worker":
        return argv[1:]

    # Existing control-panel code launches:
    #   [sys.executable, "-u", "extract.py", ...]
    # In a PyInstaller build sys.executable is this GUI executable, so accept
    # the legacy Python command shape and route it to the bundled worker.
    if len(argv) >= 2 and argv[0] == "-u" and argv[1].endswith("extract.py"):
        return ["extract", *argv[2:]]
    if argv and argv[0].endswith("extract.py"):
        return ["extract", *argv[1:]]
    return None


def run_desktop() -> int:
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
    worker_args = _worker_args_from_process_argv(sys.argv[1:])
    if worker_args is not None:
        return run_worker(worker_args)

    try:
        return run_desktop()
    except Exception:
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    multiprocessing.freeze_support()
    raise SystemExit(main())
