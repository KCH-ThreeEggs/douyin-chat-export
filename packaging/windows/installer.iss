#define MyAppName "抖音聊天导出工具"
#define MyAppExeName "DouyinChatExporter.exe"
#ifndef AppVersion
  #define AppVersion "0.1.0"
#endif

[Setup]
AppId={{F7D32FEA-DC7E-4AC3-9B0A-1D45656A2C28}
AppName={#MyAppName}
AppVersion={#AppVersion}
AppPublisher=KCH-ThreeEggs
DefaultDirName={localappdata}\Programs\DouyinChatExporter
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
OutputDir=..\..\dist\installer
OutputBaseFilename=DouyinChatExporter-Setup-x64
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
SetupLogging=yes
UninstallDisplayIcon={app}\{#MyAppExeName}

; Chocolatey's Inno Setup package does not bundle user-contributed Chinese
; translation files. Use the built-in message file so CI is deterministic.
; The application itself remains Chinese; a localized installer can be added
; later by vendoring a reviewed .isl file in this repository.
[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式"; GroupDescription: "附加任务："; Flags: unchecked

[Files]
Source: "..\..\dist\DouyinChatExporter\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "启动 {#MyAppName}"; Flags: nowait postinstall skipifsilent
