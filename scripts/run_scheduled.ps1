$ProjectRoot = "C:\Users\dflyn\Projects\paper-trader"
$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$RunScript = Join-Path $ProjectRoot "run.py"
$LogDir = Join-Path $ProjectRoot "logs"
$LogFile = Join-Path $LogDir "scheduled-run.log"

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
Add-Content -Path $LogFile -Value "`n=== Run started $timestamp ==="

Set-Location $ProjectRoot

$output = & $Python $RunScript 2>&1
$exitCode = $LASTEXITCODE

foreach ($line in $output) {
    Add-Content -Path $LogFile -Value $line
}

Add-Content -Path $LogFile -Value "=== Run finished with exit code $exitCode ==="
exit $exitCode
