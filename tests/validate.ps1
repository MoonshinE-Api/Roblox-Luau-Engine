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
foreach ($script in @('oracle.py', 'bootstrap_oracle.py', 'allocator_oracle.py', 'initialization_oracle.py', 'random_oracle.py', 'brickcolor_oracle.py', 'datetime_oracle.py', 'physical_oracle.py', 'region_oracle.py', 'rotation_oracle.py', 'lighting_oracle.py', 'sky_oracle.py', 'player_oracle.py', 'humanoid_oracle.py', 'team_oracle.py', 'geometry_oracle.py')) {
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
& python "$ProjectRoot\run.py" "$ProjectRoot\tests\render_steps.luau" --binary $Binary --mode client --duration 0.5
if ($LASTEXITCODE -ne 0) { throw 'Client render bindings failed' }
& python "$ProjectRoot\run.py" "$ProjectRoot\tests\render_steps.luau" --binary $Binary --mode server --duration 0.1
if ($LASTEXITCODE -ne 0) { throw 'Server render restrictions failed' }
& python "$ProjectRoot\run.py" "$ProjectRoot\tests\render_contexts" --binary $Binary --mode both --duration 0.3
if ($LASTEXITCODE -ne 0) { throw 'Both-mode render contexts failed' }
& python "$ProjectRoot\tests\render_checks.py" --binary $Binary
if ($LASTEXITCODE -ne 0) { throw 'Render callback error/yield checks failed' }
& python "$ProjectRoot\run.py" "$ProjectRoot\tests\datatype_math.luau" --binary $Binary --duration 0.1
if ($LASTEXITCODE -ne 0) { throw 'Vector/color/CFrame/UDim math checks failed' }
& python "$ProjectRoot\tests\numeric_conversion_checks.py" --binary $Binary
if ($LASTEXITCODE -ne 0) { throw 'Original VM integer conversion checks failed' }
& python "$ProjectRoot\run.py" "$ProjectRoot\tests\regions.luau" --binary $Binary --duration 0.1
if ($LASTEXITCODE -ne 0) { throw 'Int16 vectors/region/grid invariant checks failed' }
& python "$ProjectRoot\run.py" "$ProjectRoot\tests\cframe_rotation.luau" --binary $Binary --duration 0.1
if ($LASTEXITCODE -ne 0) { throw 'CFrame rotation/axis-angle/quaternion checks failed' }
& python "$ProjectRoot\run.py" "$ProjectRoot\tests\part_transforms.luau" --binary $Binary --duration 1
if ($LASTEXITCODE -ne 0) { throw 'BasePart rotation/orientation/signal checks failed' }
& python "$ProjectRoot\run.py" "$ProjectRoot\examples\orbit_camera.luau" --binary $Binary --mode client --duration 1.2
if ($LASTEXITCODE -ne 0) { throw 'Orbit camera/orientation tween example failed' }
foreach ($case in @('attachments','environment','sky')) {
    & python "$ProjectRoot\run.py" "$ProjectRoot\tests\$case.luau" --binary $Binary --duration 0.5
    if ($LASTEXITCODE -ne 0) { throw "Attachment/environment checks failed: $case" }
}
& python "$ProjectRoot\tests\environment_model_checks.py" --binary $Binary
if ($LASTEXITCODE -ne 0) { throw 'Environment XML/RBXM model checks failed' }
& python "$ProjectRoot\run.py" "$ProjectRoot\examples\animated_environment.luau" --binary $Binary --duration 0.8
if ($LASTEXITCODE -ne 0) { throw 'Animated environment example failed' }
& python "$ProjectRoot\tests\nested_geometry_checks.py" --binary $Binary
if ($LASTEXITCODE -ne 0) { throw 'Nested geometry/attachment/environment suites failed' }
& python "$ProjectRoot\tests\headless_checks.py" --binary $Binary
if ($LASTEXITCODE -ne 0) { throw 'Continuous host and player-free server checks failed' }
& python "$ProjectRoot\run.py" "$ProjectRoot\examples\headless_server.luau" --binary $Binary --no-player --duration 2.2
if ($LASTEXITCODE -ne 0) { throw 'Headless server day/night cycle example failed' }
& python "$ProjectRoot\run.py" "$ProjectRoot\tests\callbacks.luau" --binary $Binary --duration 1
if ($LASTEXITCODE -ne 0) { throw 'Yielding callback queues/results/lifecycle checks failed' }
& python "$ProjectRoot\run.py" "$ProjectRoot\tests\callback_contexts" --binary $Binary --mode both --duration 0.5
if ($LASTEXITCODE -ne 0) { throw 'Queued remote and per-side bindable callback contexts failed' }
& python "$ProjectRoot\tests\callback_checks.py" --binary $Binary
if ($LASTEXITCODE -ne 0) { throw 'Callback error/source-location/suspended-invocation checks failed' }
foreach ($side in @('server','client')) {
    & python "$ProjectRoot\run.py" "$ProjectRoot\tests\shutdown.luau" --binary $Binary --mode $side --duration 0.1
    if ($LASTEXITCODE -ne 0) { throw "Close callback lifecycle check failed: $side" }
}
& python "$ProjectRoot\tests\shutdown_checks.py" --binary $Binary
if ($LASTEXITCODE -ne 0) { throw 'Shutdown persistence/interrupt/deadline checks failed' }
& python "$ProjectRoot\run.py" "$ProjectRoot\examples\saved_server.luau" --binary $Binary --no-player --duration 2.2
if ($LASTEXITCODE -ne 0) { throw 'Saved headless world example failed' }
foreach ($side in @('server','client')) {
    & python "$ProjectRoot\run.py" "$ProjectRoot\tests\players.luau" --binary $Binary --mode $side --duration 0.1
    if ($LASTEXITCODE -ne 0) { throw "Player roster/character check failed: $side" }
}
& python "$ProjectRoot\run.py" "$ProjectRoot\tests\players.luau" --binary $Binary --no-player --duration 0.1
if ($LASTEXITCODE -ne 0) { throw 'Initially empty player roster check failed' }
& python "$ProjectRoot\run.py" "$ProjectRoot\tests\player_contexts" --binary $Binary --mode both --duration 0.2
if ($LASTEXITCODE -ne 0) { throw 'Player server/client signal and broadcast contexts failed' }
& python "$ProjectRoot\run.py" "$ProjectRoot\examples\player_sessions.luau" --binary $Binary --duration 0.1
if ($LASTEXITCODE -ne 0) { throw 'Player session/character/save example failed' }
foreach ($side in @('server','client')) {
    & python "$ProjectRoot\run.py" "$ProjectRoot\tests\humanoids.luau" --binary $Binary --mode $side --duration 0.3
    if ($LASTEXITCODE -ne 0) { throw "Humanoid health/force field/death check failed: $side" }
}
& python "$ProjectRoot\run.py" "$ProjectRoot\tests\humanoid_contexts" --binary $Binary --mode both --duration 0.2
if ($LASTEXITCODE -ne 0) { throw 'Humanoid peer flags/death/waiter contexts failed' }
& python "$ProjectRoot\tests\humanoid_model_checks.py" --binary $Binary
if ($LASTEXITCODE -ne 0) { throw 'Humanoid/force field model import checks failed' }
& python "$ProjectRoot\run.py" "$ProjectRoot\examples\damage_arena.luau" --binary $Binary --duration 0.1
if ($LASTEXITCODE -ne 0) { throw 'Damage/heal/protection/death example failed' }
foreach ($side in @('server','client')) {
    & python "$ProjectRoot\run.py" "$ProjectRoot\tests\teams.luau" --binary $Binary --mode $side --duration 0.1
    if ($LASTEXITCODE -ne 0) { throw "Team membership/assignment checks failed: $side" }
}
& python "$ProjectRoot\run.py" "$ProjectRoot\tests\teams.luau" --binary $Binary --no-player --duration 0.1
if ($LASTEXITCODE -ne 0) { throw 'Team joins with an initially empty roster failed' }
& python "$ProjectRoot\run.py" "$ProjectRoot\tests\team_contexts" --binary $Binary --mode both --duration 0.15
if ($LASTEXITCODE -ne 0) { throw 'Team callback server/client contexts failed' }
& python "$ProjectRoot\tests\team_model_checks.py" --binary $Binary
if ($LASTEXITCODE -ne 0) { throw 'Team/player model import checks failed' }
& python "$ProjectRoot\run.py" "$ProjectRoot\examples\team_round.luau" --binary $Binary --duration 0.1
if ($LASTEXITCODE -ne 0) { throw 'Local team round/damage/save example failed' }
foreach ($side in @('server','client')) {
    & python "$ProjectRoot\run.py" "$ProjectRoot\tests\bulk_movement.luau" --binary $Binary --mode $side --duration 0.1
    if ($LASTEXITCODE -ne 0) { throw "Bulk movement/event mode checks failed: $side" }
}
& python "$ProjectRoot\run.py" "$ProjectRoot\examples\bulk_fleet.luau" --binary $Binary --no-player --duration 0.3
if ($LASTEXITCODE -ne 0) { throw 'Headless bulk movement fleet example failed' }
& python "$ProjectRoot\tests\bulk_movement_checks.py" --binary $Binary
if ($LASTEXITCODE -ne 0) { throw 'Realtime/Fiu fleet movement and shutdown persistence failed' }
& python "$ProjectRoot\tests\geometry_kernel_checks.py"
if ($LASTEXITCODE -ne 0) { throw 'Analytic convex query/reference/packet checks failed' }
foreach ($side in @('server','client')) {
    & python "$ProjectRoot\run.py" "$ProjectRoot\tests\geometry.luau" --binary $Binary --mode $side --duration 0.1
    if ($LASTEXITCODE -ne 0) { throw "Convex query API and filter checks failed: $side" }
}
& python "$ProjectRoot\run.py" "$ProjectRoot\examples\projectile_arena.luau" --binary $Binary --no-player --duration 1.2 --wall-timeout 60
if ($LASTEXITCODE -ne 0) { throw 'Continuous projectile arena example failed' }
& python "$ProjectRoot\tests\geometry_checks.py" --binary $Binary
if ($LASTEXITCODE -ne 0) { throw 'Nested convex arena, model imports and shutdown persistence failed' }
& python "$ProjectRoot\tests\validation_inputs.py" finish
if ($LASTEXITCODE -ne 0) { throw 'Validation inputs changed during checks' }
Write-Host 'All sixteen differential checks and ninety-nine runtime/CLI checks passed.'
