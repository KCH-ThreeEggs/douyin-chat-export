# Desktop runtime

`desktop.main` is the PyInstaller entry point.

It supports two process modes:

- GUI: starts the embedded FastAPI server and opens `/panel` in PyWebView.
- Worker: accepts `--worker extract ...` and the legacy frozen command shape `-u extract.py ...` used by the upstream control panel.

The launcher sets these variables before importing the application:

```text
DOUYIN_CHAT_RESOURCE_DIR
DOUYIN_CHAT_DATA_DIR
DOUYIN_CHAT_FRONTEND_DIST
PLAYWRIGHT_BROWSERS_PATH
```

This keeps immutable package resources separate from writable user data.
