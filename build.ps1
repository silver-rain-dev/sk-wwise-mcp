# Build sk-wwise-mcp release bundle.
# Run from the repo root:
#   .\build.ps1
#
# Output:
#   dist\sk-wwise-mcp\           <- ready-to-zip folder (exe + .mcp.json + .claude\skills + README)
#   dist\sk-wwise-mcp.zip        <- zipped bundle for GitHub release upload

$ErrorActionPreference = "Stop"

$BundleDir = ".\dist\sk-wwise-mcp"
$ZipPath   = ".\dist\sk-wwise-mcp.zip"

if (-not (Get-Command pyinstaller -ErrorAction SilentlyContinue)) {
    Write-Host "Installing pyinstaller..."
    pip install pyinstaller
}

# 1. Build the exe straight into the bundle folder.
if (Test-Path $BundleDir) { Remove-Item $BundleDir -Recurse -Force }
pyinstaller --clean --distpath $BundleDir .\sk-wwise-mcp.spec
if ($LASTEXITCODE -ne 0) { throw "pyinstaller failed (exit $LASTEXITCODE)" }

# 2. Copy the bundle's .mcp.json (relative paths, all 12 servers).
Copy-Item .\release\mcp.json (Join-Path $BundleDir ".mcp.json") -Force

# 3. Copy the README.
Copy-Item .\release\README.md (Join-Path $BundleDir "README.md") -Force

# 4. Copy wwise-* skills into the bundle's .claude\skills\ so Claude CLI auto-loads
#    them. Skip eval-* (test-only, not for end users).
$SkillsDest = Join-Path $BundleDir ".claude\skills"
New-Item -ItemType Directory -Force -Path $SkillsDest | Out-Null
Copy-Item .\.claude\skills\wwise-* $SkillsDest -Recurse -Force

# 5. Zip it.
if (Test-Path $ZipPath) { Remove-Item $ZipPath -Force }
Compress-Archive -Path $BundleDir -DestinationPath $ZipPath

Write-Host ""
Write-Host "Bundle:  $BundleDir"
Write-Host "Zip:     $ZipPath"
Write-Host ""
Write-Host "Smoke test:"
Write-Host "  $BundleDir\sk-wwise-mcp.exe --help"
