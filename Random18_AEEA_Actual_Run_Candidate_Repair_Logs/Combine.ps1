$ErrorActionPreference = 'Stop'
$manifest = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'SHA256.json') -Raw | ConvertFrom-Json
$target = Join-Path $PSScriptRoot 'Random18_AEEA_Actual_Run_Candidate_Repair_Logs.zip'
if (Test-Path -LiteralPath $target) { throw 'Output ZIP already exists; it will not be overwritten.' }
foreach ($part in $manifest.parts) {
    $partPath = Join-Path $PSScriptRoot $part.name
    if ((Get-FileHash -LiteralPath $partPath -Algorithm SHA256).Hash.ToLower() -ne $part.sha256) { throw "Checksum failed: $($part.name)" }
}
$outputStream = [System.IO.File]::Open($target, [System.IO.FileMode]::CreateNew)
try {
    foreach ($part in $manifest.parts) {
        $inputStream = [System.IO.File]::OpenRead((Join-Path $PSScriptRoot $part.name))
        try { $inputStream.CopyTo($outputStream) } finally { $inputStream.Dispose() }
    }
} finally { $outputStream.Dispose() }
if ((Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash.ToLower() -ne $manifest.combined_sha256) { throw 'Combined checksum failed.' }
Write-Host 'ZIP combined and verified. You can now extract it.'
