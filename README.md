# Roblox Luau Engine

Run Roblox-style Luau scripts outside Roblox Studio on Windows x64.

This experimental project combines an adapter for the original Luau VM from a
specific Studio build with a growing implementation of Roblox Engine APIs.
It supports Script, LocalScript and ModuleScript execution, instance trees,
selected services, model imports, HTTP, and nested interpreters.

**This is not a complete Roblox engine or a fully independent VM.** The runner
requires a separately supplied, matching Studio executable. There is no renderer,
full physics solver, real client/server replication, or complete API compatibility.
Class and enum catalogs describe names; they do not imply implemented behavior.

## Quick start

Requirements: Windows x64, Python 3.14+, and the matching original executable.
The repository bundles the built native bridge, Luau compiler, asset codec, and
large generated metadata in compact archives. Run `bootstrap.py` once to restore
them locally. It verifies their SHA-256 hashes and does not download Studio.
No extra Python packages are required for ordinary execution.

```powershell
git clone https://github.com/MoonshinE-Api/Roblox-Luau-Engine.git
cd Roblox-Luau-Engine
python .\bootstrap.py
$studio = 'C:\path\to\RobloxStudio'
python .\run.py .\examples\instance_parent.luau --binary $studio
python .\run.py .\examples\materials_fonts.luau --binary $studio --wall-timeout 30
python .\run.py .\examples\project --binary $studio --mode both --duration 1
```

For example, save this as `example.luau`:

```lua
local part = Instance.new("Part", workspace)
part.Name = "Example"
part.Size = Vector3.new(2, 4, 6)
part.CustomPhysicalProperties = PhysicalProperties.new(3, 0.5, 0.2)

local copy = part:Clone()
copy.Parent = game:GetService("ServerStorage")
print(copy.Name, copy.Parent, copy:GetMass()) -- Example, ServerStorage, 144
```

```powershell
python .\run.py .\example.luau --binary $studio --wall-timeout 30
```

Names are case-sensitive, just as in Studio: `Instance.new("Part")`, `Clone`,
and `GetService` are the supported spellings.

## Current implementation

- Instance parenting, lookup, cloning, destruction, attributes, tags, signals,
  cooperative tasks, module caching, and selected local Bindable/Remote behavior.
- Vector2/3, CFrame, Color3, UDim/UDim2, sequences, query parameters, tweens,
  Random, BrickColor, DateTime, PhysicalProperties, Font, and other partial types.
- HTTP and JSON, Base64/Zstandard, hashes, authenticated asset delivery, and
  `require(id)` for supported assets and contexts.
- XML and compressed RBXM imports with an explicit class/property schema;
  supported references and typed attributes are restored before script execution.
- Material variants, density-based mass for supported primitive shapes, bounds
  and spatial queries. These calculations are not a dynamic physics simulation.

See [CAPABILITIES.md](CAPABILITIES.md) for behavior and limits,
[RUNTIME_INVENTORY.md](RUNTIME_INVENTORY.md) for observed declarations, and
[API_STATUS.md](API_STATUS.md) for comparison with the official API inventory.

## Execution limits

`--duration` controls simulated scheduler time. `--realtime` paces the scheduler
against a monotonic clock. `--memory-mb` limits VM backing allocations.
`--wall-timeout N` uses a separate worker and Windows Job to stop the VM process
tree after N real seconds, including initialization and compilation; timeout
returns exit code 124. A non-yielding loop is not stopped by `--duration` alone.

This runtime is not a security sandbox. Process termination does not undo HTTP
requests or other effects already performed.

## Architecture and required binary

The current execution path runs the original interpreter and garbage collector
through a Rust Windows/System V x86-64 ABI bridge. Engine behavior is implemented
in `engine/*.luau`; Python supplies project loading, transport, and orchestration.
The open-source Luau 0.740 compiler emits bytecode version 9.

The original executable is **not included or downloaded** by this repository.
The adapter is pinned to Studio build `0.735.19.7351131` and SHA-256:

```text
6b01d19b7fdfab0528621680e0b8760aa10c54fc917c79bf1f1f6eb92c373b6d
```

The source contains reconstruction work and extracted metadata from local
artifacts; it is not presented as a clean-room implementation or official Roblox
source release. Do not assume an arbitrary current Studio executable will work.

## Build and validate

Rust and the MSVC x64 build tools are required to rebuild the native components.

```powershell
powershell -File .\build.ps1
powershell -File .\compiler\build.ps1
powershell -File .\asset-codec\build.ps1
powershell -File .\validate.ps1 -Binary $studio
python .\bundle_runtime.py
```

The tested baseline passed 8 differential suites and 35 runtime/CLI scenarios,
followed by 20 checks of its extracted distribution. These results describe the
tested cases, not compatibility with every Roblox script. Regenerating extraction
reports requires additional tooling and source artifacts; normal execution uses
the checked-in metadata. The external vLua test model is not bundled.

## Provenance and licensing

This is an unofficial project and is not affiliated with Roblox Corporation.
Upstream Luau, Fiu, rbx-dom, Rust dependencies, and the official API reference are
credited in [NOTICE.md](NOTICE.md); their license texts are in `licenses/`.
Project-owned contributions use the [MIT license](LICENSE) selected for this
repository. It does not relicense upstream or proprietary material, or grant
rights in the separately supplied Studio executable.
