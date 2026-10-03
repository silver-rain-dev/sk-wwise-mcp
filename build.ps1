# Build the sk-wwise-mcp release bundle.
# Run from the repo root:
#   .\build.ps1
#
# Output (dist\ IS the portable bundle -- copy it anywhere and run `claude`):
#   dist\sk-wwise-mcp.exe           <- single binary; dispatches via --server
#   dist\.mcp.json                  <- Claude Code MCP config (1 entry, mounts all)
#   dist\.mcp.per-server.json       <- alt template: 12 entries, one per server
#   dist\.vscode\mcp.json           <- VS Code Copilot MCP config (mounts all)
#   dist\.vscode\mcp.per-server.json
#   dist\.claude\skills\            <- routing skills (auto-loaded by Claude CLI)
#   dist\README.md                  <- end-user "Quick start" doc
#   sk-wwise-mcp.zip                <- zipped bundle for GitHub release upload
#   sk-wwise-mcp.mcpb               <- MCP Bundle (exe + manifest + user settings)
#
# After a successful build, `cd dist && claude` registers the server with no
# further configuration. Paths in every config are relative, so the folder is
# fully portable. The default .mcp.json is a single entry -- one exe process
# mounts every server (fewest permission prompts, like sk-fmod-mcp). Swap in
# .mcp.per-server.json for one entry per server (better LLM tool-routing
# accuracy, and lets you scope access per role by deleting entries).

$ErrorActionPreference = "Stop"

$RepoRoot = $PSScriptRoot
$DistDir  = Join-Path $RepoRoot "dist"
$BuildDir = Join-Path $RepoRoot "build"
$Spec     = Join-Path $RepoRoot "sk-wwise-mcp.spec"
# Zip lives outside dist\ so it can't try to include itself in the archive.
$ZipPath  = Join-Path $RepoRoot "sk-wwise-mcp.zip"
# The MCP Bundle sits next to the zip, also outside dist\.
$McpbPath = Join-Path $RepoRoot "sk-wwise-mcp.mcpb"

# Server suffix list (kebab-case) -- must match cli.py SERVERS keys.
$Servers = @(
    "browse",
    "audition",
    "objects",
    "containers",
    "pipeline",
    "generic",
    "media-read",
    "profiling",
    "profiling-control",
    "command-line",
    "remote",
    "ui"
)

# 1. Verify pyinstaller is on PATH; install into the active interpreter if not.
if (-not (Get-Command pyinstaller -ErrorAction SilentlyContinue)) {
    Write-Host "pyinstaller not found on PATH - installing..."
    python -m pip install pyinstaller
    if ($LASTEXITCODE -ne 0) {
        throw "pip install pyinstaller failed (exit $LASTEXITCODE)."
    }
}

# 2. Clean previous build artefacts so old binaries don't linger.
if (Test-Path $DistDir)  { Remove-Item $DistDir  -Recurse -Force }
if (Test-Path $BuildDir) { Remove-Item $BuildDir -Recurse -Force }

# 3. Single PyInstaller invocation -- cli.py is the entry, every mcp_*
#    package is hidden-imported via the spec. onefile -> dist\sk-wwise-mcp.exe.
Write-Host ""
Write-Host "=== Building sk-wwise-mcp.exe ==="
pyinstaller --clean --noconfirm --distpath $DistDir --workpath $BuildDir $Spec
if ($LASTEXITCODE -ne 0) { throw "pyinstaller failed (exit $LASTEXITCODE)." }

# 4. Write dist\.mcp.json (Claude Code) and dist\.vscode\mcp.json (VS Code
#    Copilot). Both use relative paths so the folder is fully portable.
#    Default shape: a single entry, no flag -- one exe process mounts every
#    server (like sk-fmod-mcp).
$Utf8NoBom = New-Object System.Text.UTF8Encoding $false
$VsCodeDir = Join-Path $DistDir ".vscode"
New-Item -ItemType Directory -Force -Path $VsCodeDir | Out-Null

$ClaudeCfg = [ordered]@{
    mcpServers = [ordered]@{
        "sk-wwise" = [ordered]@{ command = "./sk-wwise-mcp.exe"; args = @() }
    }
}
$CopilotCfg = [ordered]@{
    servers = [ordered]@{
        "sk-wwise" = [ordered]@{ command = "./sk-wwise-mcp.exe"; args = @() }
    }
}
[IO.File]::WriteAllText((Join-Path $DistDir ".mcp.json"),
    ($ClaudeCfg | ConvertTo-Json -Depth 5), $Utf8NoBom)
[IO.File]::WriteAllText((Join-Path $VsCodeDir "mcp.json"),
    ($CopilotCfg | ConvertTo-Json -Depth 5), $Utf8NoBom)

# 5. Write the per-server variant of each config as a sibling template: one
#    entry per server (--server <name>). Better tool-routing accuracy, and
#    lets users scope role-based access by deleting entries.
$ClaudePerServer  = [ordered]@{ mcpServers = [ordered]@{} }
$CopilotPerServer = [ordered]@{ servers    = [ordered]@{} }
foreach ($srv in $Servers) {
    $entry = [ordered]@{
        command = "./sk-wwise-mcp.exe"
        args    = @("--server", $srv)
    }
    $ClaudePerServer.mcpServers["sk-wwise-$srv"] = $entry
    $CopilotPerServer.servers["sk-wwise-$srv"]   = $entry
}
[IO.File]::WriteAllText((Join-Path $DistDir ".mcp.per-server.json"),
    ($ClaudePerServer | ConvertTo-Json -Depth 5), $Utf8NoBom)
[IO.File]::WriteAllText((Join-Path $VsCodeDir "mcp.per-server.json"),
    ($CopilotPerServer | ConvertTo-Json -Depth 5), $Utf8NoBom)

# 6. Copy wwise-* Agent Skills into the bundle so Claude CLI auto-loads
#    routing guidance. eval-* skills are test-only -- skip them.
$SkillsSrc  = Join-Path $RepoRoot ".claude\skills"
$SkillsDest = Join-Path $DistDir  ".claude\skills"
if (Test-Path $SkillsSrc) {
    New-Item -ItemType Directory -Force -Path $SkillsDest | Out-Null
    Get-ChildItem $SkillsSrc -Directory |
        Where-Object { $_.Name -like "wwise-*" } |
        ForEach-Object { Copy-Item $_.FullName $SkillsDest -Recurse -Force }
} else {
    Write-Host "warning: $SkillsSrc not found - bundle will ship without .claude\skills."
}

# 7. Copy the end-user README into the bundle.
$ReleaseReadme = Join-Path $RepoRoot "release\README.md"
if (Test-Path $ReleaseReadme) {
    Copy-Item $ReleaseReadme (Join-Path $DistDir "README.md") -Force
}

# 8. Zip the bundle contents for GitHub release upload (exe at archive root).
if (Test-Path $ZipPath) { Remove-Item $ZipPath -Force }
Compress-Archive -Path (Join-Path $DistDir "*") -DestinationPath $ZipPath

# 9. Build the MCP Bundle (.mcpb): exe + generated manifest. The manifest comes
#    from release\build_mcpb.py so the profile list follows core\profiles.py.
#    Validated with the official mcpb CLI when npx is available; the unit
#    tests validate against the vendored schema either way.
if (Test-Path $McpbPath) { Remove-Item $McpbPath -Force }
python (Join-Path $RepoRoot "release\build_mcpb.py") --exe (Join-Path $DistDir "sk-wwise-mcp.exe") --out $McpbPath
if ($LASTEXITCODE -ne 0) { throw "build_mcpb.py failed (exit $LASTEXITCODE)." }
if (Get-Command npx -ErrorAction SilentlyContinue) {
    $McpbCheck = Join-Path $BuildDir "mcpb-check"
    if (Test-Path $McpbCheck) { Remove-Item $McpbCheck -Recurse -Force }
    # Expand-Archive only accepts .zip, so extract with .NET.
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    [IO.Compression.ZipFile]::ExtractToDirectory($McpbPath, $McpbCheck)
    npx --yes @anthropic-ai/mcpb validate (Join-Path $McpbCheck "manifest.json")
    if ($LASTEXITCODE -ne 0) { throw "mcpb validate failed (exit $LASTEXITCODE)." }
} else {
    Write-Host "note: npx not found - skipped official mcpb validate."
}

# 10. Print a summary so the operator sees bundle size.
Write-Host ""
Write-Host "=== Build complete ==="
$Exe = Get-Item (Join-Path $DistDir "sk-wwise-mcp.exe")
$TotalMB = [math]::Round(($Exe.Length / 1MB), 1)
Write-Host ("Bundle:  {0}" -f $DistDir)
Write-Host ("Binary:  sk-wwise-mcp.exe ({0} MB)" -f $TotalMB)
Write-Host ("Zip:     {0}" -f $ZipPath)
Write-Host ("Mcpb:    {0}" -f $McpbPath)
Write-Host ""
Write-Host "Smoke test (no Wwise needed):"
Write-Host "  & '$DistDir\sk-wwise-mcp.exe' --server browse  # boots and hangs on stdio"
Write-Host ""
Write-Host "Real test (Wwise running with WAAPI enabled):"
Write-Host "  cd $DistDir"
Write-Host "  claude"
