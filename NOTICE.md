# Provenance and third-party notices

Roblox Luau Engine is an unofficial experimental project. It is not affiliated
with, endorsed by, or an official release from Roblox Corporation.

## Original artifacts

The execution adapter targets a separately supplied Studio 0.735.19.7351131
executable. Neither that executable nor the decompiled source tree, fonts,
textures, account data, or private working notes are distributed here.
Some source reconstructs behavior from those artifacts; extracted class/enum
catalogs, offsets, hashes, and reviewed instruction metadata are included.
These components are not represented as a clean-room recreation.

Project-owned contributions use the repository's MIT license. That grant only
covers rights held by the project contributors. Third-party and proprietary
material is not relicensed, and rights in the original executable are not granted.

## Open-source dependencies

- [Luau](https://github.com/luau-lang/luau) and the Rust mlua/luau-src toolchain
  provide the source-to-bytecode compiler. Upstream copyright and license texts
  are preserved under `licenses/`, including the luau0-src package notice.
- [rbx-dom](https://github.com/rojo-rbx/rbx-dom) supplies the XML/binary asset codec
  and an independent attribute-format reference. Relevant crate license texts
  and locked dependency versions are retained.
- [Fiu](https://github.com/rce-incorporated/Fiu) is a vendored MIT-licensed test
  interpreter. Its license is in `licenses/Fiu/LICENSE`.
- Rust compiler/codec dependencies, including BLAKE3 and compression libraries,
  retain their individual notices under `licenses/`. Inclusion of a notice does
  not mean every optional dependency is linked into every binary.

## Official API reference

The API inventory derives from [Roblox creator-docs](https://github.com/Roblox/creator-docs)
at revision `46be165f526ec23305394ac0c56a95edd2d7f7d9`, published under
[Creative Commons Attribution 4.0](https://creativecommons.org/licenses/by/4.0/).
Roblox Corporation and the upstream contributors are credited for that reference.
The inventory extracts signatures and interface facts into JSON; generated
coverage reports add runtime observations and are not upstream documentation.
No upstream endorsement is implied. The license text and its warranty disclaimer
are included in `licenses/Roblox-creator-docs/CC-BY-4.0.txt`.
