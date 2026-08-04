# Windows 桌面安装版

本分支提供无需 Docker、Python 或 Node.js 的 Windows 11 x64 桌面安装包。

## 用户数据

应用资源与用户数据分离：

- 程序目录：`%LOCALAPPDATA%\Programs\DouyinChatExporter`
- 用户数据：`%LOCALAPPDATA%\DouyinChatExporter\data`
- 数据库：`%LOCALAPPDATA%\DouyinChatExporter\data\chat.db`
- 登录态：`%LOCALAPPDATA%\DouyinChatExporter\data\browser_profile`
- 媒体：`%LOCALAPPDATA%\DouyinChatExporter\data\media`

卸载程序不会主动删除用户数据。

## 本地构建

在 Windows 11 x64 PowerShell 中执行：

```powershell
python -m pip install -r requirements-desktop.txt

Push-Location frontend
npm ci
npm run build
Pop-Location

$env:PLAYWRIGHT_BROWSERS_PATH = "$PWD\build\ms-playwright"
python -m playwright install chromium
python -m PyInstaller --clean --noconfirm packaging\windows\douyin-chat-export.spec

& "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" `
  "/DAppVersion=0.1.0" `
  "packaging\windows\installer.iss"
```

输出文件：

```text
dist\installer\DouyinChatExporter-Setup-x64.exe
```

## 自动构建

GitHub Actions 工作流：

```text
.github/workflows/build-windows.yml
```

在功能分支推送、针对 `main` 的 Pull Request 或手动运行工作流时，自动构建并上传安装包 Artifact。
