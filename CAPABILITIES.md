# Capabilities and limits

This document describes the current implementation. It does not promise complete
Roblox behavior. The runtime targets build 0.735; its comparison documentation is
pinned to a different build, 0.744. Every represented datatype remains partial.

## Scripts and instances

Projects may contain Script, LocalScript, and ModuleScript files. Server/client
suffixes select script kinds; `--mode` selects execution contexts. Modules use
separate environments and caches, with source labels preserved in diagnostics.
Server and client contexts share one local runtime rather than real replication.

Instance trees support parenting, ancestry, lookup, Clone/Destroy, selected
properties, attributes, tags, signals, and connections. Unknown members produce
errors. Class names and inherited relationships are more extensive than actual
class implementations; native creation restrictions remain incomplete.

Signals and task scheduling are cooperative. Non-yielding code blocks that VM.
The optional CLI process deadline can terminate its worker but is not an internal
instruction budget. Signal ordering and derived-property notifications do not
fully match Studio.

## Datatypes and animation

The runtime partially represents 31 documented datatypes, including vectors,
CFrame, Color3, dimensions, ranges, sequences, query parameters, RaycastResult,
Random, BrickColor, DateTime, PhysicalProperties, Font, enums, and signal types.
The complete observed list is generated in [RUNTIME_INVENTORY.md](RUNTIME_INVENTORY.md).

Random and BrickColor have separate native differential checks. DateTime supports
UTC/local conversion, ISO forms, and selected formatting/locales; its parsers,
locale fallback, and platform date behavior are not exhaustive native replicas.

TweenService supports selected easing, play/pause/cancel, repeats/reversal/delay,
completion signals, property conflicts, and interpolation for supported values.
CFrame interpolation uses quaternion SLERP. Native float precision and exact
engine scheduling are not guaranteed to match every case.

## Materials, mass, and Font

PhysicalProperties accepts a Material or 3/5/6 numerical arguments and exposes
Density, Friction, Elasticity, FrictionWeight, ElasticityWeight, and
AcousticAbsorption. Finite constructor values, clamping, 45 material mappings,
and primitive geometry coefficients have native comparisons. Warning text and
nonnumeric/NaN bridge coercions are not comprehensively compared.

Part, WedgePart, and CornerWedgePart mass uses density and supported geometry.
Ball uses its minimum axis; Cylinder uses X length and the smaller Y/Z diameter.
MaterialVariant and MaterialService overrides affect current physical properties.
Assembly mass/root/center currently describe the individual part; there is no
joint assembly solver, contact simulation, or geometry-derived mesh/CSG mass.

Font supports new/fromEnum/fromName/fromId, with mutable Family/Weight/Style/Bold.
All 52 builtin mappings are recovered. Font attributes are copied on set/get,
GetAttributes, and Clone, so mutating a returned value does not change stored data.
Font.fromId intentionally follows the 0.735 bridge's int32 conversion behavior;
use Font.new with a URI string for large IDs. Font metadata does not load or
render glyphs. ContentId normalization and Font equality lack a dynamic native
oracle covering every edge case.

## Geometry and models

Supported spatial operations include raycasts and selected box/radius/part
queries. Bounding-box calculations use oriented part corners. Shape and terrain
support are incomplete; bounding-box approximations do not equal a full collision
engine. Model bounds/pivot and PrimaryPart behavior have dedicated checks.

`--model` accepts supported XML RBXMX and compressed binary RBXM models. The
current schema contains 25 classes and 116 property declarations. Instance
references are connected after tree creation; multiple imports have separate
reference namespaces. Unsupported classes, properties, malformed data, and
unsupported capabilities fail explicitly. Full places/RBXL are not implemented.

AttributesSerialize supports byte strings, booleans/numbers, dimensions,
BrickColor/Color3, vectors, CFrame, ranges/rectangles, sequences, and Font.
Font cached-face metadata is preserved internally. EnumItem attributes and
nonfinite numeric attributes are rejected. Attribute names allow ASCII letters,
digits, underscore, period, slash, and hyphen, up to 100 bytes; RBX names are
reserved. Limits include a 16 MiB serialized payload, 1024 imported attributes,
and 2..20 sequence keypoints. The importer validates bounded input.

## HTTP, encoding, and asset delivery

HttpService has asynchronous host transport, JSON, GUID generation, URL encoding,
and selected binary response handling. Python transport workers do not call Lua
directly. Header/redirect behavior, JSON native precision, error wording, and
compression output are not fully identical to Studio.

EncodingService supplies Base64, Zstandard buffer operations, size inspection,
and Blake2b-256/Blake3-256/MD5/SHA1/SHA256 hashes. String hashes return raw bytes.
Zstandard requires Python 3.14's compression.zstd. The host input/output limit is
50 MiB; decoding requires one known-size frame without unsupported dictionaries
or oversized windows. Compatibility aliases do not prove native API presence.

Supported asset paths include server require(id), InsertService loading,
AssetService:LoadAssetAsync, and GetObjects for supported model data. Modules run
on require; imported asset Script/LocalScript activation remains incomplete.
Cloud rights, experience context, and Studio capabilities are not recreated by
logging into an account.

Optional asset authentication is host-side and CurrentUser-DPAPI protected.
Credentials are not exposed as Luau globals or forwarded to unrelated HTTP
requests. Cookie and Open Cloud modes are context-dependent. Synthetic transport
and credential tests pass; successful real account-authenticated delivery has
not been verified. Supply credentials through the supported host login prompt or
environment, never source files or repository commits.

## Evidence and interpretation

The tested distribution passed 8 differential suites, 35 runtime/CLI scenarios,
and 20 checks after extracting its archive. Native numerical comparisons and
semantic/format tests are separate kinds of evidence; a semantic test is not a
claim of native equivalence. Results and their stated limits are in `evidence/`.

The official inventory contains 4861 class-member names; the implementation
declares 234 of those names. This is declaration coverage, not an overall engine
completion percentage. Catalogs do not stand in for implementation.
