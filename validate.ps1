param(
    [string]$Binary = 'D:\Release-RobloxStudioApp\RobloxStudio.app\Contents\MacOS\RobloxStudio',
    [switch]$Build
)
$ErrorActionPreference = 'Stop'
if (-not (Test-Path -LiteralPath $Binary -PathType Leaf)) { throw "Missing supplied Mach-O: $Binary" }
if ($Build) { & "$PSScriptRoot\build.ps1" }
& python "$PSScriptRoot\validation_inputs.py" start
if ($LASTEXITCODE -ne 0) { throw 'Validation input snapshot failed' }
foreach ($script in @('oracle.py', 'bootstrap_oracle.py', 'allocator_oracle.py', 'initialization_oracle.py', 'random_oracle.py', 'brickcolor_oracle.py', 'datetime_oracle.py', 'physical_oracle.py')) {
    & python "$PSScriptRoot\$script" --binary $Binary
    if ($LASTEXITCODE -ne 0) { throw "Comparison failed: $script" }
}
foreach ($case in @('tests\integration.luau', 'tests\documented_types.luau', 'tests\random.luau', 'tests\brickcolor.luau', 'tests\datetime.luau', 'tests\http_json.luau', 'tests\vm_errors.luau', 'tests\services.luau', 'tests\spatial.luau', 'tests\calendar.luau', 'tests\contexts', 'examples\instance_parent.luau', 'examples\project', 'examples\seeded_colors.luau')) {
    & python "$PSScriptRoot\run.py" "$PSScriptRoot\$case" --binary $Binary --mode both --duration 0.5
    if ($LASTEXITCODE -ne 0) { throw "Runtime check failed: $case" }
}
& python "$PSScriptRoot\run.py" "$PSScriptRoot\examples\ready_build_showcase.luau" --binary $Binary --duration 2
if ($LASTEXITCODE -ne 0) { throw 'Ready-build showcase failed' }
& python "$PSScriptRoot\run.py" "$PSScriptRoot\tests\tweens.luau" --binary $Binary --duration 2
if ($LASTEXITCODE -ne 0) { throw 'Tween/CFrame interpolation checks failed' }
& python "$PSScriptRoot\run.py" "$PSScriptRoot\tests\oom.luau" --binary $Binary --memory-mb 8 --duration 0.1
if ($LASTEXITCODE -ne 0) { throw 'OOM recovery check failed' }
& python "$PSScriptRoot\tests\cli_checks.py" --binary $Binary
if ($LASTEXITCODE -ne 0) { throw 'CLI/source-location/module project checks failed' }
& python "$PSScriptRoot\run.py" "$PSScriptRoot\tests\realtime.luau" --binary $Binary --realtime --duration 0.5
if ($LASTEXITCODE -ne 0) { throw 'Realtime clock/scheduler checks failed' }
& python "$PSScriptRoot\tests\http_checks.py" --binary $Binary
if ($LASTEXITCODE -ne 0) { throw 'HTTP/JSON/transport/OOM checks failed' }
& python "$PSScriptRoot\tests\nested_vm_checks.py" --binary $Binary
if ($LASTEXITCODE -ne 0) { throw 'Nested Luau interpreter/Engine API/HTTP check failed' }
& python "$PSScriptRoot\tests\model_xml_checks.py" --binary $Binary
if ($LASTEXITCODE -ne 0) { throw 'XML script tree/context/source checks failed' }
& python "$PSScriptRoot\tests\asset_checks.py" --binary $Binary
if ($LASTEXITCODE -ne 0) { throw 'Asset XML/binary/compile/require/cache checks failed' }
& python "$PSScriptRoot\tests\asset_auth_checks.py" --binary $Binary
if ($LASTEXITCODE -ne 0) { throw 'Asset auth/DPAPI/redirect/VM checks failed' }
& python "$PSScriptRoot\tests\encoding_checks.py" --binary $Binary
if ($LASTEXITCODE -ne 0) { throw 'Encoding formats/VM/OOM checks failed' }
& python "$PSScriptRoot\tests\model_attribute_checks.py" --binary $Binary
if ($LASTEXITCODE -ne 0) { throw 'Serialized model attributes/roundtrip/VM checks failed' }
& python "$PSScriptRoot\tests\model_geometry_checks.py" --binary $Binary
if ($LASTEXITCODE -ne 0) { throw 'Model properties/geometry/references/binary checks failed' }
& python "$PSScriptRoot\run.py" "$PSScriptRoot\tests\model_bounds.luau" --binary $Binary --duration 0.5
if ($LASTEXITCODE -ne 0) { throw 'Model bounds/pivot/primary-part checks failed' }
foreach ($case in @('physical','font')) {
    & python "$PSScriptRoot\run.py" "$PSScriptRoot\tests\$case.luau" --binary $Binary --mode both --duration 0.5
    if ($LASTEXITCODE -ne 0) { throw "Value checks failed: $case" }
}
foreach ($case in @('hierarchy_checks','physical_model_checks','font_checks')) {
    & python "$PSScriptRoot\tests\$case.py" --binary $Binary
    if ($LASTEXITCODE -ne 0) { throw "Model/catalog checks failed: $case" }
}
& python "$PSScriptRoot\tests\host_limit_checks.py" --binary $Binary
if ($LASTEXITCODE -ne 0) { throw 'Host deadline/process-tree checks failed' }
& python "$PSScriptRoot\run.py" "$PSScriptRoot\examples\materials_fonts.luau" --binary $Binary --mode both --duration 0.5
if ($LASTEXITCODE -ne 0) { throw 'Material/Font combined example failed' }
& python "$PSScriptRoot\validation_inputs.py" finish
if ($LASTEXITCODE -ne 0) { throw 'Validation inputs changed during checks' }
Write-Host 'All eight differential checks and thirty-five runtime/CLI checks passed.'
