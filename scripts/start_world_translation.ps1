param([string]$Model='qwen3.5:9b',[ValidateRange(1,50)][int]$BatchSize=10)
$ErrorActionPreference='Stop'
if ($Model -notmatch '^[A-Za-z0-9._:-]+$') {throw 'Invalid model name'}
$projectRoot=Split-Path $PSScriptRoot -Parent
$jobFolder=Join-Path $projectRoot 'data/name-translation/world'
$pidFile=Join-Path $jobFolder 'translation-process.json'
if(Test-Path $pidFile) {
    $previous=Get-Content $pidFile -Raw | ConvertFrom-Json
    $running=Get-Process -Id $previous.pid -ErrorAction SilentlyContinue
    if($running -and $running.StartTime.ToUniversalTime().ToString('o') -eq $previous.start_time) {throw 'World translation already running'}
}
$process=Start-Process -FilePath (Join-Path $projectRoot '.venv/Scripts/python.exe') -ArgumentList @('-u','scripts/translate_world_names.py','--run','--limit','0','--model',$Model,'--batch-size',$BatchSize) -WorkingDirectory $projectRoot -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $jobFolder 'translation.log') -RedirectStandardError (Join-Path $jobFolder 'translation.err.log')
@{pid=$process.Id;model=$Model;start_time=$process.StartTime.ToUniversalTime().ToString('o')} | ConvertTo-Json | Set-Content $pidFile -Encoding utf8
Write-Output "Started world candidates PID $($process.Id)"
