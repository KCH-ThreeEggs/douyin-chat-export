# Windows packaging

- `douyin-chat-export.spec`: PyInstaller `onedir` build, including Vue assets, control-panel HTML and bundled Playwright Chromium.
- `installer.iss`: per-user Inno Setup installer for Windows 11 x64.

The installer writes program files to `%LOCALAPPDATA%\Programs\DouyinChatExporter`; runtime data remains under `%LOCALAPPDATA%\DouyinChatExporter\data`.
