$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
    & rustc --edition 2024 --crate-type cdylib -O .\native\vm0735.rs -o .\vm0735.dll
    if ($LASTEXITCODE -ne 0) { throw 'Native slice build failed' }
} finally { Pop-Location }
