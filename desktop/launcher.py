"""Windows desktop runtime bootstrap for the bundled application."""
from __future__ import annotations

import logging
import os
import socket
import sys
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Callable, Final

APP_NAME: Final = "DouyinChatExporter"
APP_TITLE: Final = "抖音聊天导出工具"


def is_frozen() -> bool:
    return bool(getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"))


def resource_dir() -> Path:
    if is_frozen():
        return Path(sys._MEIPASS).resolve()  # type: ignore[attr-defined]
    return Path(__file__).resolve().parents[1]


def application_dir() -> Path:
    local_app_data = os.environ.get("LOCALAPPDATA", "").strip()
    base = Path(local_app_data) if local_app_data else Path.home() / "AppData" / "Local"
    return (base / APP_NAME).resolve()


def configure_environment() -> tuple[Path, Path]:
    resources = resource_dir()
    app_dir = application_dir()
    data_dir = app_dir / "data"

    for path in (
        app_dir,
        data_dir,
        data_dir / "media",
        data_dir / "browser_profile",
        app_dir / "logs",
    ):
        path.mkdir(parents=True, exist_ok=True)

    os.environ.setdefault("DOUYIN_CHAT_RESOURCE_DIR", str(resources))
    os.environ.setdefault("DOUYIN_CHAT_DATA_DIR", str(data_dir))
    os.environ.setdefault(
        "DOUYIN_CHAT_FRONTEND_DIST",
        str(resources / "frontend" / "dist"),
    )

    bundled_browsers = resources / "ms-playwright"
    if bundled_browsers.exists():
        os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", str(bundled_browsers))

    os.environ.setdefault("PYTHONUTF8", "1")
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    os.environ.setdefault("PYTHONUNBUFFERED", "1")

    # Existing scripts still resolve a few relative paths. Keeping the resource
    # directory as cwd preserves source behavior while writable state is routed
    # through DOUYIN_CHAT_DATA_DIR.
    os.chdir(resources)
    return resources, app_dir


def worker_command(*args: str) -> list[str]:
    """Build a subprocess command that works in source and PyInstaller modes."""
    if is_frozen():
        return [sys.executable, "--worker", "extract", *args]
    return [sys.executable, "-u", str(resource_dir() / "extract.py"), *args]


def _redirect_frozen_legacy_paths() -> None:
    """Redirect remaining ``__file__/../../data`` lookups to user data.

    The upstream control panel still has a few legacy path expressions inside
    function bodies. In a frozen build those expressions are evaluated at call
    time, so replacing the module's ``__file__`` with a harmless synthetic path
    makes them resolve to ``%LOCALAPPDATA%/DouyinChatExporter/data`` without
    changing Docker/source behavior.
    """
    if not is_frozen():
        return

    import backend.control_panel as control_panel

    synthetic_file = application_dir() / "backend" / "control_panel.py"
    control_panel.__file__ = str(synthetic_file)


def reserve_local_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def wait_until_ready(
    url: str,
    timeout: float = 20.0,
    failure_check: Callable[[], BaseException | None] | None = None,
) -> None:
    deadline = time.monotonic() + timeout
    last_error: Exception | None = None

    while time.monotonic() < deadline:
        if failure_check is not None:
            failure = failure_check()
            if failure is not None:
                raise RuntimeError("本地服务启动失败") from failure

        try:
            with urllib.request.urlopen(url, timeout=1.0) as response:
                if response.status < 500:
                    return
        except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
            last_error = exc

        time.sleep(0.15)

    raise RuntimeError(f"本地服务启动超时: {last_error}")


class DesktopServer:
    def __init__(self, host: str = "127.0.0.1") -> None:
        self.host = host
        self.port = reserve_local_port()
        self._thread: threading.Thread | None = None
        self._server = None
        self._thread_error: BaseException | None = None

    @property
    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}"

    def _run_server(self) -> None:
        try:
            self._server.run()
        except BaseException as error:
            self._thread_error = error
            logging.exception("Local Uvicorn server thread crashed")

    def _server_failure(self) -> BaseException | None:
        if self._thread_error is not None:
            return self._thread_error
        if self._thread is not None and not self._thread.is_alive():
            return RuntimeError("本地服务线程提前退出")
        return None

    def start(self) -> None:
        logging.info("Importing Uvicorn and FastAPI application")
        import uvicorn
        from backend.main import app

        logging.info("Redirecting frozen legacy paths")
        _redirect_frozen_legacy_paths()

        config = uvicorn.Config(
            app,
            host=self.host,
            port=self.port,
            log_level="info",
            access_log=False,
        )
        self._server = uvicorn.Server(config)
        self._thread = threading.Thread(
            target=self._run_server,
            name="douyin-chat-backend",
            daemon=True,
        )
        self._thread.start()
        wait_until_ready(
            f"{self.base_url}/api/stats",
            failure_check=self._server_failure,
        )

    def stop(self, *_args: object) -> None:
        if self._server is not None:
            self._server.should_exit = True
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5.0)
