# Roblox Luau Engine

Run Roblox-style Luau scripts outside Roblox Studio on Windows x64.

This experimental runtime combines an adapter for a specific Studio build's Luau
VM with a growing implementation of Roblox Engine APIs. It supports Script,
LocalScript and ModuleScript execution, instance trees, selected services, model
imports, HTTP, and nested interpreters.

**Compatibility is partial.** The runner requires a separately supplied matching
Studio executable. There is no renderer, full physics solver, real client/server
replication, or complete API compatibility. Class and enum catalogs describe
names; they do not imply implemented behavior.

## Build and run

Requirements: Windows x64, Python 3.14+, Rust with the MSVC toolchain, Visual
Studio C++ x64 build tools, Windows SDK, and the matching Studio executable.
Build all three native components locally. Cargo downloads locked dependencies
on the first build. Ordinary execution needs no additional Python packages.

```powershell
git clone https://github.com/MoonshinE-Api/Roblox-Luau-Engine.git
cd Roblox-Luau-Engine
powershell -File .\build.ps1
powershell -File .\compiler\build.ps1
powershell -File .\asset-codec\build.ps1

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

Names are case-sensitive, as in Studio: `Instance.new("Part")`, `Clone`, and
`GetService`. Use `python .\run.py --help` for execution options.

## Current implementation

- Instance parenting, lookup, cloning, destruction, attributes, tags, signals,
  cooperative tasks, module caching, and selected local Bindable/Remote behavior.
- Vector2/3, CFrame, Color3, UDim/UDim2, sequences, query parameters, tweens,
  Random, BrickColor, DateTime, PhysicalProperties, Font, and other partial types.
- Vector component operations, signed angles and relative FuzzyEq; Color3 HSV/hex
  conversion; batched CFrame transforms; native VM integer conversion for UDim.
- Vector2int16/Vector3int16 with wrapping arithmetic; Region3 construction and
  grid expansion with float32 operations; Region3int16 boundaries.
  Other geometry calculations use doubles; engine-wide float32 rounding is not emulated.
- CFrame quaternion construction, all six Euler rotation orders and decomposition,
  orientation aliases, axis-angle conversion, and lookAlong with parallel-up fallback.
- BasePart Orientation (YXZ) and Rotation (XYZ) in degrees, three-decimal display
  rounding, transform change signals, cloning, model import, and orientation tweens.
  Weld/motor adjustment and physics side effects of transform writes are not simulated.
- HTTP and JSON, Base64/Zstandard, hashes, authenticated asset delivery, and
  `require(id)` for supported assets and contexts.
- XML and compressed RBXM imports with an explicit class/property schema;
  supported references and typed attributes are restored before script execution.
- Material variants, density-based mass for supported primitive shapes, bounds,
  and spatial queries. These calculations do not provide dynamic physics.
- 199 typed UI configuration declarations across 25 class definitions, with
  inherited defaults, change signals, cloning, focus, and XML/RBXM import.
- Headless UDim2 geometry, anchors, UIScale, padding, size/aspect constraints, clipping,
  scrolling offsets, and GUI hit ordering. No window or text renderer is created.
- Camera viewport/screen projection, inverse rays, FOV modes, and Ray closest
  point/distance methods. Projection uses semantic double-precision math.
- UIListLayout and UIGridLayout: sorting, alignment, wrapping, cell spans,
  content-size notifications, container AutomaticSize, and AutomaticCanvasSize.
- Local DataStoreService: JSON values, metadata/user IDs, key versions, scopes,
  cached reads, atomic UpdateAsync retries, ordered stores, and paginated lists.
- Process-local MemoryStore hash/sorted maps and queues: expiration, update
  callbacks, sorted ranges, priorities, read leases, and waiting readers.
- Client render-step bindings with priority ordering, duplicate-name removal,
  callback context, owner cleanup, and PreRender/RenderStepped in `both` mode.
  These are headless frame callbacks; equal-priority ties use registration order.

```powershell
python .\run.py .\examples\headless_ui.luau --binary $studio --mode client
python .\run.py .\examples\projected_target.luau --binary $studio --mode client
python .\run.py .\examples\orbit_camera.luau --binary $studio --mode client --duration 1.2
```

Set the simulated viewport with `--viewport-width` and `--viewport-height`
(defaults: 1280 by 720). UI defaults are sourced from reflection build 741;
the underlying VM remains build 735. AutomaticSize supports containers; intrinsic
text sizing, flex grow/shrink and item-line alignment, page/table layouts, text
measurement, hardware input, rotated GUI hit testing, VR and occlusion are not
implemented. Cyclic/non-converging automatic-size dependencies produce an error.
UI configuration storage does not imply visual rendering.
Camera near-plane offset defaults to -0.5 studs in this headless environment.

Int16 constructors truncate toward zero, convert through native VM int32 rules,
and keep the low 16 bits. Build 735 Vector3int16 scalar multiplication truncates
the scalar before multiplying. Vector2int16 uses the fixed
`FixVector2int16WithFloatMult` behavior in both operand orders; runtime flag
configuration is not simulated. These vector types have no Magnitude/Unit properties.
Region3 preserves signed sizes and does not sort its constructor bounds.
Use `GetPartBoundsInBox(region.CFrame, region.Size)` for nonnegative regions;
legacy `FindPartsInRegion3` and terrain voxel APIs are not implemented.

## Local storage

Data stores are isolated and in memory by default. Supply an explicit SQLite
file to keep data across runner invocations:

```powershell
python .\run.py .\examples\local_inventory.luau --binary $studio --duration 5 --data-store "$env:TEMP\roblox-engine-inventory.sqlite3"
python .\run.py .\examples\layout_gallery.luau --binary $studio
```

These services do not read or write Roblox cloud data. SQLite keeps every local
write as a version; Roblox request budgets, throttling and version-retention
policies are not simulated. Values are limited to 4 MiB of UTF-8 JSON, ordered
values to exact Luau integers, and listing snapshots to 10,000 entries. Update
callbacks cannot yield. GetAsync uses a four-second cache with optional bypass.

MemoryStore data lives in one VM and expires using the simulated scheduler clock
(wall-paced with `--realtime`). It is not shared across separate runner processes.
Queue reads make items temporarily invisible; removal after the lease expires
does not remove the item. Local memory-store values are limited to 32 KiB.

`--duration` controls simulated scheduler time; `--realtime` paces it against a
monotonic clock. `--memory-mb` limits VM backing allocations. `--wall-timeout N`
stops the worker process tree after N real seconds, including initialization and
compilation, and returns exit code 124. A non-yielding loop is not stopped by
`--duration` alone. This runtime is not a security sandbox.

## Source layout

| Path | Purpose |
| --- | --- |
| `engine/` | Engine API implementation in Luau |
| `native/` | Rust VM bridge and native helpers |
| `compiler/` | Compiler using upstream Luau 0.740 |
| `asset-codec/` | XML/RBXM codec using rbx-dom |
| Root Python modules | VM loading, projects, models, HTTP, and assets |
| `data/` | Required catalogs, schemas, and version-specific VM metadata |
| `tests/` | Validation runner, differential checks, integration tests, and fixtures |
| `examples/` | Runnable scripts and a small sample project |
| `tools/` | Metadata extraction, reconstruction, and VM inspection utilities |

Compiled programs, build archives, disassembly listings, and generated test
reports are excluded from version control.

## Required original executable

The adapter runs the original interpreter and garbage collector through a Rust
Windows/System V x86-64 ABI bridge. Engine behavior lives in `engine/*.luau`;
Python supplies loading and orchestration. The compiler emits bytecode version 9.

The Studio executable is **not included or downloaded**. The adapter targets
build `0.735.19.7351131`, with SHA-256:

```text
6b01d19b7fdfab0528621680e0b8760aa10c54fc917c79bf1f1f6eb92c373b6d
```

An arbitrary current executable will not work. This project contains
reconstruction work and extracted metadata; it is not a clean-room
implementation or an official Roblox source release.

## Tests

After building the native components, install the analysis dependencies and run:

```powershell
python -m pip install -r .\tools\requirements.txt
powershell -File .\tests\validate.ps1 -Binary $studio
```

Validation covers 10 differential suites and 59 runtime/CLI scenarios, including
HTTP against local fixtures, model imports, nested Fiu execution, memory limits,
worker timeouts, all 199 UI property declarations, UI model import, 200 camera
projection round trips, layout/autosizing, concurrent SQLite updates, persistence
across processes, memory-store TTLs, queue leases, and render callback contexts,
ordering, lifecycle and error propagation, randomized vector/color math, batched
CFrame transforms, 285 integer conversions against the original VM, and 609
region/grid comparisons against unchanged original machine functions, 3,108 Euler
decompositions and 206 lookAlong comparisons with native math, plus orientation
signals and camera/tween integration. Passing these checks does
not establish compatibility with
every Roblox script. Generated diagnostics remain local and are ignored by Git.
The optional external vLua model is not bundled. Metadata reconstruction tools in `tools/`
may additionally require original source artifacts; ordinary execution uses the
checked-in `data/` files.

## Licensing

This unofficial project is not affiliated with Roblox Corporation.
Project-owned contributions use the [MIT license](LICENSE). Third-party
components and reference data retain their own terms; see [NOTICE.md](NOTICE.md).
The project license does not grant rights in the separately supplied executable.
