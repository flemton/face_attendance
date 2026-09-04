# Pack Face Attendance for Windows. Requires Python, VS C++ tools, and CMake.
# See docs/WINDOWS.md.

$ErrorActionPreference = "Stop"
$Root = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $Root

Write-Host "Build root: $Root"
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw "Python is not on PATH. Install Python 3.10+ (64-bit)."
}
if (-not (Get-Command cmake -ErrorAction SilentlyContinue)) {
    throw "CMake is not on PATH. Install CMake and reopen the terminal. See docs/WINDOWS.md."
}

$Venv = Join-Path $Root ".venv"
$Py = Join-Path $Venv "Scripts\python.exe"
if (-not (Test-Path $Py)) {
    python -m venv $Venv
}
& $Py -m pip install --upgrade pip
& $Py -m pip install -r (Join-Path $Root "requirements.txt")
& $Py -m pip install "mysql-connector-python>=8.0.33" pyinstaller tzdata

$Spec = Join-Path $Root "packaging\FaceAttendance.spec"
& $Py -m PyInstaller $Spec --noconfirm --clean
if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller failed. If dlib failed to compile, install Visual C++ Build Tools and CMake (docs/WINDOWS.md)."
}

$Iscc = Get-Command iscc -ErrorAction SilentlyContinue
if (-not $Iscc) {
    $Guess = "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe"
    if (Test-Path $Guess) { $IsccPath = $Guess } else { $IsccPath = $null }
} else {
    $IsccPath = $Iscc.Source
}

if ($IsccPath) {
    & $IsccPath (Join-Path $Root "packaging\windows\FaceAttendance.iss")
    Write-Host "Installer written under packaging\windows\output\"
} else {
    Write-Host "Inno Setup not found — portable folder is dist\FaceAttendance\"
}

Write-Host "Portable app: dist\FaceAttendance\FaceAttendance.exe"
