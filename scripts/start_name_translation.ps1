param([string]$Model = 'qwen3.5:4b')
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
$jobFolder = Join-Path $projectRoot 'data/name-translation'
New-Item -ItemType Directory -Path $jobFolder -Force | Out-Null
$pidFile = Join-Path $jobFolder 'process.json'
if (Test-Path -LiteralPath $pidFile) {
    $previous = Get-Content -LiteralPath $pidFile -Raw | ConvertFrom-Json
    $running = Get-Process -Id $previous.pid -ErrorAction SilentlyContinue
    if ($running -and $running.StartTime.ToUniversalTime().ToString('o') -eq $previous.start_time) {
        throw 'Name translation is already running.'
    }
}
if ($Model -notmatch '^[A-Za-z0-9._:-]+$') { throw 'Invalid model name' }
$process = Start-Process -FilePath (Join-Path $projectRoot '.venv/Scripts/python.exe') -ArgumentList @(
    '-u','scripts/translate_names.py','--run','--model',$Model
) -WorkingDirectory $projectRoot -WindowStyle Hidden -PassThru -RedirectStandardOutput (
    Join-Path $jobFolder 'run.log'
) -RedirectStandardError (Join-Path $jobFolder 'error.log')
@{pid=$process.Id;model=$Model;start_time=$process.StartTime.ToUniversalTime().ToString('o')} |
    ConvertTo-Json | Set-Content -LiteralPath $pidFile -Encoding utf8
Write-Output "Started PID $($process.Id); log: $jobFolder/run.log"
