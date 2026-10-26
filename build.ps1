param([switch]$Offline)
$ErrorActionPreference = 'Stop'
$arguments=@('build','--release','--locked','--manifest-path',"$PSScriptRoot\native\Cargo.toml")
if ($Offline) { $arguments+='--offline' }
& cargo @arguments
if ($LASTEXITCODE -ne 0) { throw 'Native VM/geometry build failed' }
$metadata=& cargo metadata --no-deps --format-version 1 --manifest-path "$PSScriptRoot\native\Cargo.toml" | ConvertFrom-Json
if ($LASTEXITCODE -ne 0) { throw 'Cargo metadata failed' }
Copy-Item -LiteralPath (Join-Path $metadata.target_directory 'release\vm0735.dll') -Destination (Join-Path $PSScriptRoot 'vm0735.dll')
