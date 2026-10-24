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
- HTTP and JSON, Base64/Zstandard, hashes, authenticated asset delivery, and
  `require(id)` for supported assets and contexts.
- XML and compressed RBXM imports with an explicit class/property schema;
  supported references and typed attributes are restored before script execution.
- Material variants, density-based mass for supported primitive shapes, bounds,
  and spatial queries. These calculations do not provide dynamic physics.

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
| `tests/` | Differential checks, integration tests, and fixtures |
| `examples/` | Runnable scripts and a small sample project |
| `extract_*.py`, `recover.py`, `inspect_vm.py` | Metadata reconstruction tools |

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
python -m pip install -r .\requirements.txt
powershell -File .\validate.ps1 -Binary $studio
```

Validation covers 8 differential suites and 35 runtime/CLI scenarios, including
HTTP against local fixtures, model imports, nested Fiu execution, memory limits,
and worker timeouts. Passing these checks does not establish compatibility with
every Roblox script. Generated diagnostics remain local and are ignored by Git.
The optional external vLua model is not bundled. Metadata reconstruction tools
may additionally require original source artifacts; ordinary execution uses the
checked-in `data/` files.

## Licensing

This unofficial project is not affiliated with Roblox Corporation.
Project-owned contributions use the [MIT license](LICENSE). Third-party
components and reference data retain their own terms; see [NOTICE.md](NOTICE.md).
The project license does not grant rights in the separately supplied executable.
