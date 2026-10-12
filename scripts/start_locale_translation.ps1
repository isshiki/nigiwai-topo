$ErrorActionPreference='Stop'
$projectRoot=Split-Path $PSScriptRoot -Parent
$jobFolder=Join-Path $projectRoot 'data/name-translation/world'
$pidFile=Join-Path $jobFolder 'locale-process.json'
if(Test-Path $pidFile) {
    $previous=Get-Content $pidFile -Raw | ConvertFrom-Json
    $running=Get-Process -Id $previous.pid -ErrorAction SilentlyContinue
    if($running -and $running.StartTime.ToUniversalTime().ToString('o') -eq $previous.start_time) {throw 'Locale translation already running'}
}
$process=Start-Process -FilePath (Join-Path $projectRoot '.venv/Scripts/python.exe') -ArgumentList @('-u','scripts/translate_locale_names.py','--run') -WorkingDirectory $projectRoot -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $jobFolder 'locale.log') -RedirectStandardError (Join-Path $jobFolder 'locale.err.log')
@{pid=$process.Id;start_time=$process.StartTime.ToUniversalTime().ToString('o')} | ConvertTo-Json | Set-Content $pidFile -Encoding utf8
Write-Output "Started locale candidate PID $($process.Id)"
