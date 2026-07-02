; Inno Setup 安装脚本
; 编译: iscc installer.iss

#define MyAppName "EasyLink"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "EasyLink"
#define MyAppExeName "EasyLink.exe"

[Setup]
AppId={{8A7E4B2C-3D5F-4E6A-9B8C-1D2E3F4A5B6C}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
OutputDir=.\dist
OutputBaseFilename=EasyLink_Setup
Compression=lzma
SolidCompression=yes
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
SetupIconFile=.\dist\EasyLink.exe
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName}

[Languages]
Name: "chinesesimplified"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式"; GroupDescription: "快捷方式:"; Flags: checkedonce
Name: "startupicon"; Description: "开机自动启动"; GroupDescription: "快捷方式:"; Flags: checkedonce

[Files]
Source: ".\dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: ".\extension\*"; DestDir: "{app}\extension"; Flags: ignoreversion recursesubdirs
Source: ".\data\stock-data.json"; DestDir: "{app}\data"; Flags: ignoreversion

[Icons]
Name: "{userprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{userdesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userstartup}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: startupicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "启动 {#MyAppName}"; Flags: postinstall nowait skipifsilent

[UninstallRun]
Filename: "{app}\{#MyAppExeName}"; Parameters: "--uninstall";

[Code]
function InitializeUninstall: Boolean;
begin
  Result := True;
end;
