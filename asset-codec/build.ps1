param([switch]$Offline)
$ErrorActionPreference='Stop'
$arguments=@('build','--release','--locked','--manifest-path',"$PSScriptRoot\Cargo.toml")
if ($Offline) { $arguments+='--offline' }
& cargo @arguments
if ($LASTEXITCODE -ne 0) { throw 'Asset codec build failed' }
$metadata=& cargo metadata --no-deps --format-version 1 --manifest-path "$PSScriptRoot\Cargo.toml" | ConvertFrom-Json
if ($LASTEXITCODE -ne 0) { throw 'Cargo metadata failed' }
$built=Join-Path $metadata.target_directory 'release\recovery-asset-codec.exe'
Copy-Item -LiteralPath $built -Destination (Join-Path (Split-Path $PSScriptRoot -Parent) 'recovery-asset-codec.exe')
