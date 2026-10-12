param([int]$AcquisitionPid, [string]$AcquisitionStarted)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $projectRoot
$statusPath = Join-Path $projectRoot 'data/name-research/held-poi-addresses/followup-status.json'
$expectedStarted = [DateTimeOffset]::Parse($AcquisitionStarted)
try {
    while (-not (Test-Path -LiteralPath 'data/name-research/held-poi-addresses/all.json')) {
        $sourceProcess = Get-Process -Id $AcquisitionPid -ErrorAction SilentlyContinue
        if (-not $sourceProcess -or [Math]::Abs(($sourceProcess.StartTime.ToUniversalTime() - $expectedStarted.UtcDateTime).TotalSeconds) -gt 1) {
            throw 'Acquisition stopped before verified address cache completed.'
        }
        Start-Sleep -Seconds 10
    }
    # Allow the small completion metadata write to finish before reading it.
    Start-Sleep -Seconds 2
    & '.venv/Scripts/python.exe' 'scripts/audit_held_peak_addresses.py'
    if ($LASTEXITCODE -ne 0) { throw 'Address audit validation failed.' }
    @{status='complete'; completedAt=[DateTimeOffset]::Now.ToString('o'); report='docs/held-peak-address-audit.md'} | ConvertTo-Json | Set-Content -LiteralPath $statusPath -Encoding utf8
} catch {
    # No upstream error details or credentials are available to this worker.
    @{status='failed'; completedAt=[DateTimeOffset]::Now.ToString('o'); reason=$_.Exception.Message} | ConvertTo-Json | Set-Content -LiteralPath $statusPath -Encoding utf8
    exit 1
}
