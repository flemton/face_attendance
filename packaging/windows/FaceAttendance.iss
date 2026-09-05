#define MyAppName "Face Attendance"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Flemton Tech"
#define MyAppExeName "FaceAttendance.exe"

[Setup]
AppId={{8E7C2F11-4B3A-4F0E-9C1A-FACEATTEND001}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\Flemton Tech\Face Attendance
DefaultGroupName=Flemton Tech
DisableProgramGroupPage=yes
OutputDir=output
OutputBaseFilename=FaceAttendance-1.0.0-Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesInstallIn64BitMode=x64
SetupLogging=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Shortcuts:"

[Files]
Source: "..\..\dist\FaceAttendance\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Start Face Attendance"; Flags: nowait postinstall skipifsilent
