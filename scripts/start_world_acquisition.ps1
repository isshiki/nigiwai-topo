param([string]$EnvFile = 'C:\Projects-GitHub\geoai-open-lab\.env')
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
$jobFolder = Join-Path $projectRoot 'data/raw/foursquare-global'
New-Item -ItemType Directory -Path $jobFolder -Force | Out-Null
$pidFile = Join-Path $jobFolder 'process.json'
if (Test-Path -LiteralPath $pidFile) {
    $previous = Get-Content -LiteralPath $pidFile -Raw | ConvertFrom-Json
    $running = Get-Process -Id $previous.pid -ErrorAction SilentlyContinue
    if ($running -and $running.StartTime.ToUniversalTime().ToString('o') -eq $previous.start_time) {
        throw 'World acquisition is already running.'
    }
}
if (-not (Test-Path -LiteralPath $EnvFile -PathType Leaf)) { throw 'Token file does not exist' }
if ($EnvFile.Contains('"')) { throw 'Invalid token file path' }
$process = Start-Process -FilePath (Join-Path $projectRoot '.venv/Scripts/python.exe') -ArgumentList @(
    '-u','scripts/fetch_foursquare.py','--world','--env-file', ('"' + $EnvFile + '"')
) -WorkingDirectory $projectRoot -WindowStyle Hidden -PassThru -RedirectStandardOutput (
    Join-Path $jobFolder 'run.log'
) -RedirectStandardError (Join-Path $jobFolder 'error.log')
@{pid=$process.Id;start_time=$process.StartTime.ToUniversalTime().ToString('o')} |
    ConvertTo-Json | Set-Content -LiteralPath $pidFile -Encoding utf8
Write-Output "Started PID $($process.Id); log: $jobFolder/run.log"
