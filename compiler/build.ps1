param([switch]$Offline)
$ErrorActionPreference='Stop'
$arguments=@('build','--release','--locked','--manifest-path',"$PSScriptRoot\Cargo.toml")
if ($Offline) { $arguments+='--offline' }
& cargo @arguments
if ($LASTEXITCODE -ne 0) { throw 'Luau compiler build failed' }
$metadata=& cargo metadata --no-deps --format-version 1 --manifest-path "$PSScriptRoot\Cargo.toml" | ConvertFrom-Json
if ($LASTEXITCODE -ne 0) { throw 'Cargo metadata failed' }
$built=Join-Path $metadata.target_directory 'release\recovery-luau-compile.exe'
Copy-Item -LiteralPath $built -Destination (Join-Path (Split-Path $PSScriptRoot -Parent) 'recovery-luau-compile.exe')
