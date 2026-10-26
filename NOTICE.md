# Provenance and third-party notices

Roblox Luau Engine is an unofficial experimental project. It is not affiliated
with, endorsed by, or an official release from Roblox Corporation.

## Original artifacts

The execution adapter targets a separately supplied Studio 0.735.19.7351131
executable. Neither that executable nor the decompiled source tree, fonts,
textures, account data, or private working notes are distributed here.
Some source reconstructs behavior from those artifacts. Required class/enum
catalogs, offsets, hashes, and reviewed instruction metadata are included in
`data/` and `tests/fixtures/`. These components are not represented as a clean-room recreation.

Project-owned contributions use the repository's MIT license. That grant only
covers rights held by the project contributors. Third-party and proprietary
material is not relicensed, and rights in the original executable are not granted.

## Open-source dependencies

- [Luau](https://github.com/luau-lang/luau) and the Rust mlua/luau-src toolchain
  provide the source-to-bytecode compiler.
- [rbx-dom](https://github.com/rojo-rbx/rbx-dom) supplies the XML/binary asset
  codec and an independent attribute-format reference.
  `data/ui_property_catalog.json` and `data/environment_property_catalog.json`
  also contain selected, typed extractions of
  defaults from its `rbx_reflection_database` 3.0.1+roblox-741 database, revision
  `03a3e1f63db883c42a2d0929c6058234d0f0785d`. The source version and SHA-256 are
  recorded in each catalog. Its MIT notice is retained in
  `licenses/rbx-reflection-database/LICENSE`.
- [Fiu](https://github.com/rce-incorporated/Fiu) is a vendored MIT-licensed test
  interpreter. Its license is preserved in `licenses/Fiu/LICENSE`.
- [Parry](https://github.com/dimforge/parry), by the Dimforge contributors,
  supplies convex spatial queries through `parry3d-f64` 0.25.1. It is licensed
  under Apache-2.0; its license is retained in `licenses/Parry/LICENSE`.
  The native VM bridge now uses Cargo with locked dependencies in `native/`.
- Compiler and codec dependencies are downloaded by Cargo rather than vendored
  here. Versions are pinned in their respective `Cargo.lock` files. Their
  upstream licenses continue to apply to those dependencies and built programs.

## Official API reference

The compact inheritance reference in `data/hierarchy_reference.json` derives
from [Roblox creator-docs](https://github.com/Roblox/creator-docs) at revision
`46be165f526ec23305394ac0c56a95edd2d7f7d9`, published under
[Creative Commons Attribution 4.0](https://creativecommons.org/licenses/by/4.0/).
Roblox Corporation and the upstream contributors are credited for that reference.
The extracted data retains class inheritance facts; other documentation and
generated coverage reports are omitted. No upstream endorsement is implied.
The license text and warranty disclaimer are included in
`licenses/Roblox-creator-docs/CC-BY-4.0.txt`.
