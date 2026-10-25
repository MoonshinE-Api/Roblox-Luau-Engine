param(
    [string]$Binary = 'D:\Release-RobloxStudioApp\RobloxStudio.app\Contents\MacOS\RobloxStudio',
    [switch]$Build
)
$ErrorActionPreference = 'Stop'
$ProjectRoot = Split-Path -Parent $PSScriptRoot
if (-not (Test-Path -LiteralPath $Binary -PathType Leaf)) { throw "Missing supplied Mach-O: $Binary" }
if ($Build) { & "$ProjectRoot\build.ps1" }
& python "$ProjectRoot\tests\validation_inputs.py" start
if ($LASTEXITCODE -ne 0) { throw 'Validation input snapshot failed' }
foreach ($script in @('oracle.py', 'bootstrap_oracle.py', 'allocator_oracle.py', 'initialization_oracle.py', 'random_oracle.py', 'brickcolor_oracle.py', 'datetime_oracle.py', 'physical_oracle.py')) {
    & python "$ProjectRoot\tests\$script" --binary $Binary
    if ($LASTEXITCODE -ne 0) { throw "Comparison failed: $script" }
}
foreach ($case in @('tests\integration.luau', 'tests\documented_types.luau', 'tests\random.luau', 'tests\brickcolor.luau', 'tests\datetime.luau', 'tests\http_json.luau', 'tests\vm_errors.luau', 'tests\services.luau', 'tests\spatial.luau', 'tests\calendar.luau', 'tests\contexts', 'examples\instance_parent.luau', 'examples\project', 'examples\seeded_colors.luau')) {
    & python "$ProjectRoot\run.py" "$ProjectRoot\$case" --binary $Binary --mode both --duration 0.5
    if ($LASTEXITCODE -ne 0) { throw "Runtime check failed: $case" }
}
& python "$ProjectRoot\run.py" "$ProjectRoot\examples\ready_build_showcase.luau" --binary $Binary --duration 2
if ($LASTEXITCODE -ne 0) { throw 'Ready-build showcase failed' }
& python "$ProjectRoot\run.py" "$ProjectRoot\tests\tweens.luau" --binary $Binary --duration 2
if ($LASTEXITCODE -ne 0) { throw 'Tween/CFrame interpolation checks failed' }
& python "$ProjectRoot\run.py" "$ProjectRoot\tests\oom.luau" --binary $Binary --memory-mb 8 --duration 0.1
if ($LASTEXITCODE -ne 0) { throw 'OOM recovery check failed' }
& python "$ProjectRoot\tests\cli_checks.py" --binary $Binary
if ($LASTEXITCODE -ne 0) { throw 'CLI/source-location/module project checks failed' }
& python "$ProjectRoot\run.py" "$ProjectRoot\tests\realtime.luau" --binary $Binary --realtime --duration 0.5
if ($LASTEXITCODE -ne 0) { throw 'Realtime clock/scheduler checks failed' }
& python "$ProjectRoot\tests\http_checks.py" --binary $Binary
if ($LASTEXITCODE -ne 0) { throw 'HTTP/JSON/transport/OOM checks failed' }
& python "$ProjectRoot\tests\nested_vm_checks.py" --binary $Binary
if ($LASTEXITCODE -ne 0) { throw 'Nested Luau interpreter/Engine API/HTTP check failed' }
& python "$ProjectRoot\tests\model_xml_checks.py" --binary $Binary
if ($LASTEXITCODE -ne 0) { throw 'XML script tree/context/source checks failed' }
& python "$ProjectRoot\tests\asset_checks.py" --binary $Binary
if ($LASTEXITCODE -ne 0) { throw 'Asset XML/binary/compile/require/cache checks failed' }
& python "$ProjectRoot\tests\asset_auth_checks.py" --binary $Binary
if ($LASTEXITCODE -ne 0) { throw 'Asset auth/DPAPI/redirect/VM checks failed' }
& python "$ProjectRoot\tests\encoding_checks.py" --binary $Binary
if ($LASTEXITCODE -ne 0) { throw 'Encoding formats/VM/OOM checks failed' }
& python "$ProjectRoot\tests\model_attribute_checks.py" --binary $Binary
if ($LASTEXITCODE -ne 0) { throw 'Serialized model attributes/roundtrip/VM checks failed' }
& python "$ProjectRoot\tests\model_geometry_checks.py" --binary $Binary
if ($LASTEXITCODE -ne 0) { throw 'Model properties/geometry/references/binary checks failed' }
& python "$ProjectRoot\run.py" "$ProjectRoot\tests\model_bounds.luau" --binary $Binary --duration 0.5
if ($LASTEXITCODE -ne 0) { throw 'Model bounds/pivot/primary-part checks failed' }
foreach ($case in @('physical','font')) {
    & python "$ProjectRoot\run.py" "$ProjectRoot\tests\$case.luau" --binary $Binary --mode both --duration 0.5
    if ($LASTEXITCODE -ne 0) { throw "Value checks failed: $case" }
}
foreach ($case in @('hierarchy_checks','physical_model_checks','font_checks')) {
    & python "$ProjectRoot\tests\$case.py" --binary $Binary
    if ($LASTEXITCODE -ne 0) { throw "Model/catalog checks failed: $case" }
}
& python "$ProjectRoot\tests\host_limit_checks.py" --binary $Binary
if ($LASTEXITCODE -ne 0) { throw 'Host deadline/process-tree checks failed' }
& python "$ProjectRoot\run.py" "$ProjectRoot\examples\materials_fonts.luau" --binary $Binary --mode both --duration 0.5
if ($LASTEXITCODE -ne 0) { throw 'Material/Font combined example failed' }
foreach ($case in @('ui','camera')) {
    & python "$ProjectRoot\run.py" "$ProjectRoot\tests\$case.luau" --binary $Binary --mode both --duration 1
    if ($LASTEXITCODE -ne 0) { throw "UI/camera value checks failed: $case" }
}
foreach ($case in @('ui_model_checks','ui_camera_checks')) {
    & python "$ProjectRoot\tests\$case.py" --binary $Binary
    if ($LASTEXITCODE -ne 0) { throw "UI import/viewport checks failed: $case" }
}
foreach ($case in @('headless_ui','projected_target')) {
    & python "$ProjectRoot\run.py" "$ProjectRoot\examples\$case.luau" --binary $Binary --mode client --duration 1
    if ($LASTEXITCODE -ne 0) { throw "UI/camera example failed: $case" }
}
& python "$ProjectRoot\run.py" "$ProjectRoot\tests\ui_layout.luau" --binary $Binary --duration 1
if ($LASTEXITCODE -ne 0) { throw 'List/grid/automatic layout checks failed' }
& python "$ProjectRoot\run.py" "$ProjectRoot\tests\datastore.luau" --binary $Binary --duration 10
if ($LASTEXITCODE -ne 0) { throw 'Data store API checks failed' }
& python "$ProjectRoot\run.py" "$ProjectRoot\tests\datastore.luau" --binary $Binary --mode client --duration 1
if ($LASTEXITCODE -ne 0) { throw 'Client data store restriction failed' }
& python "$ProjectRoot\tests\datastore_checks.py" --binary $Binary
if ($LASTEXITCODE -ne 0) { throw 'SQLite atomicity/persistence checks failed' }
& python "$ProjectRoot\run.py" "$ProjectRoot\tests\memory_store.luau" --binary $Binary --duration 5
if ($LASTEXITCODE -ne 0) { throw 'Memory store map/queue checks failed' }
& python "$ProjectRoot\run.py" "$ProjectRoot\tests\memory_store.luau" --binary $Binary --mode client --duration 1
if ($LASTEXITCODE -ne 0) { throw 'Client memory store restriction failed' }
foreach ($case in @('layout_gallery','local_inventory')) {
    & python "$ProjectRoot\run.py" "$ProjectRoot\examples\$case.luau" --binary $Binary --duration 5
    if ($LASTEXITCODE -ne 0) { throw "Layout/storage example failed: $case" }
}
& python "$ProjectRoot\tests\validation_inputs.py" finish
if ($LASTEXITCODE -ne 0) { throw 'Validation inputs changed during checks' }
Write-Host 'All eight differential checks and forty-nine runtime/CLI checks passed.'
