# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

from PyInstaller.utils.hooks import collect_submodules

project_root = Path(SPECPATH).resolve().parents[1]
frontend_dist = project_root / "frontend" / "dist"
panel_static = project_root / "backend" / "panel" / "static"
playwright_browsers = project_root / "build" / "ms-playwright"

missing = [
    str(path)
    for path in (frontend_dist, panel_static, playwright_browsers)
    if not path.exists()
]
if missing:
    raise SystemExit("Missing build resources: " + ", ".join(missing))

hiddenimports = sorted(set(
    collect_submodules("backend")
    + collect_submodules("common")
    + collect_submodules("extractor")
    + collect_submodules("playwright")
    + collect_submodules("webview")
))

datas = [
    (str(frontend_dist), "frontend/dist"),
    (str(panel_static), "backend/panel/static"),
    (str(playwright_browsers), "ms-playwright"),
]

a = Analysis(
    [str(project_root / "desktop" / "main.py")],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="DouyinChatExporter",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch="x86_64",
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="DouyinChatExporter",
)
