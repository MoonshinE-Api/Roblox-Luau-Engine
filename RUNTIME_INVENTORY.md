# Current runtime declaration inventory

Observed from a running VM. A declared name does not guarantee full Roblox semantics.
Behavior and limits: CAPABILITIES.md.

## Global names

`Axes`, `BrickColor`, `CFrame`, `Color3`, `ColorSequence`, `ColorSequenceKeypoint`, `DateTime`, `Enum`, `Faces`, `Font`, `Instance`, `NumberRange`, `NumberSequence`, `NumberSequenceKeypoint`, `OverlapParams`, `PathWaypoint`, `PhysicalProperties`, `Random`, `Ray`, `RaycastParams`, `Rect`, `TweenInfo`, `UDim`, `UDim2`, `Vector2`, `Vector3`, `_G`, `_VERSION`, `assert`, `bit32`, `buffer`, `collectgarbage`, `coroutine`, `debug`, `delay`, `error`, `game`, `gcinfo`, `getfenv`, `getmetatable`, `ipairs`, `math`, `newproxy`, `next`, `os`, `pairs`, `pcall`, `print`, `rawequal`, `rawget`, `rawlen`, `rawset`, `require`, `script`, `select`, `setfenv`, `setmetatable`, `shared`, `spawn`, `string`, `table`, `task`, `tick`, `time`, `tonumber`, `tostring`, `type`, `typeof`, `unpack`, `utf8`, `vector`, `wait`, `warn`, `workspace`, `xpcall`.

## Libraries: observed members

### bit32

`arshift`, `band`, `bnot`, `bor`, `btest`, `bxor`, `byteswap`, `countlz`, `countrz`, `extract`, `lrotate`, `lshift`, `replace`, `rrotate`, `rshift`.

### buffer

`copy`, `create`, `fill`, `fromstring`, `len`, `readbits`, `readf32`, `readf64`, `readi16`, `readi32`, `readi8`, `readstring`, `readu16`, `readu32`, `readu8`, `tostring`, `writebits`, `writef32`, `writef64`, `writei16`, `writei32`, `writei8`, `writestring`, `writeu16`, `writeu32`, `writeu8`.

### coroutine

`close`, `create`, `isyieldable`, `resume`, `running`, `status`, `wrap`, `yield`.

### debug

`info`, `traceback`.

### math

`abs`, `acos`, `asin`, `atan`, `atan2`, `ceil`, `clamp`, `cos`, `cosh`, `deg`, `e`, `exp`, `floor`, `fmod`, `frexp`, `huge`, `isfinite`, `isinf`, `isnan`, `ldexp`, `lerp`, `log`, `log10`, `map`, `max`, `min`, `modf`, `nan`, `noise`, `phi`, `pi`, `pow`, `rad`, `random`, `randomseed`, `round`, `sign`, `sin`, `sinh`, `sqrt`, `sqrt2`, `tan`, `tanh`, `tau`.

### os

`clock`, `date`, `difftime`, `time`.

### string

`byte`, `char`, `find`, `format`, `gmatch`, `gsub`, `len`, `lower`, `match`, `pack`, `packsize`, `rep`, `reverse`, `split`, `sub`, `unpack`, `upper`.

### table

`clear`, `clone`, `concat`, `create`, `find`, `foreach`, `foreachi`, `freeze`, `getn`, `insert`, `isfrozen`, `maxn`, `move`, `pack`, `remove`, `sort`, `unpack`.

### task

`cancel`, `defer`, `delay`, `spawn`, `wait`.

### utf8

`char`, `charpattern`, `codepoint`, `codes`, `len`, `offset`.

### vector

`abs`, `angle`, `ceil`, `clamp`, `create`, `cross`, `dot`, `floor`, `lerp`, `magnitude`, `max`, `min`, `normalize`, `one`, `sign`, `zero`.

## Exported datatype constructors and constants

- **Axes**: `new`.
- **BrickColor**: `Black`, `Blue`, `DarkGray`, `Gray`, `Green`, `New`, `Random`, `Red`, `White`, `Yellow`, `new`, `palette`, `random`.
- **CFrame**: `Angles`, `fromEulerAnglesXYZ`, `fromMatrix`, `identity`, `lookAt`, `new`.
- **Color3**: `fromHSV`, `fromRGB`, `new`.
- **ColorSequence**: `new`.
- **ColorSequenceKeypoint**: `new`.
- **DateTime**: `fromIsoDate`, `fromLocalTime`, `fromUniversalTime`, `fromUnixTimestamp`, `fromUnixTimestampMillis`, `now`.
- **Faces**: `new`.
- **Font**: `fromEnum`, `fromId`, `fromName`, `new`.
- **NumberRange**: `new`.
- **NumberSequence**: `new`.
- **NumberSequenceKeypoint**: `new`.
- **OverlapParams**: `new`.
- **PathWaypoint**: `new`.
- **PhysicalProperties**: `new`.
- **Random**: `new`.
- **Ray**: `new`.
- **RaycastParams**: `new`.
- **Rect**: `new`.
- **TweenInfo**: `new`.
- **UDim**: `new`.
- **UDim2**: `fromOffset`, `fromScale`, `new`.
- **Vector2**: `new`, `one`, `xAxis`, `yAxis`, `zero`.
- **Vector3**: `new`, `one`, `xAxis`, `yAxis`, `zAxis`, `zero`.

## Methods, getters, setters, and events by owner

This lists explicit declarations. Inheritance adds shared Instance members.
Events such as Touched/PlayerAdded may be declared without a physics/network producer.

### AssetService

- method: `LoadAssetAsync`.

### BasePart

- method: `GetMass`, `GetPivot`, `PivotTo`, `getMass`.
- getter: `AssemblyCenterOfMass`, `AssemblyMass`, `AssemblyRootPart`, `BrickColor`, `CenterOfMass`, `CurrentPhysicalProperties`, `Mass`, `Position`.
- setter: `BrickColor`, `CollisionGroup`, `Color`, `Position`.
- event: `TouchEnded`, `Touched`.

### BindableEvent

- method: `Fire`.
- event: `Event`.

### BindableFunction

- method: `Invoke`.
- getter: `OnInvoke`.
- setter: `OnInvoke`.

### CollectionService

- method: `AddTag`, `GetAllTags`, `GetInstanceAddedSignal`, `GetInstanceRemovedSignal`, `GetTagged`, `GetTags`, `HasTag`, `RemoveTag`.

### DataModel

- method: `BindToClose`, `GetObjects`, `IsLoaded`.
- getter: `CreatorId`, `GameId`, `JobId`, `PlaceId`.

### Debris

- method: `AddItem`.

### EncodingService

- method: `Base64Decode`, `Base64Encode`, `CompressBuffer`, `CompressBufferZstd`, `ComputeBufferHash`, `ComputeStringHash`, `DecompressBuffer`, `DecompressBufferZstd`, `GetDecompressedBufferSize`, `GetDecompressedBufferSizeZstd`.

### HttpService

- method: `GenerateGUID`, `GetAsync`, `JSONDecode`, `JSONEncode`, `PostAsync`, `RequestAsync`, `UrlEncode`.

### InsertService

- method: `LoadAsset`, `LoadAssetVersion`, `loadAsset`.

### Instance

- instance: `AddTag`, `ClearAllChildren`, `Clone`, `Destroy`, `FindFirstAncestor`, `FindFirstAncestorOfClass`, `FindFirstAncestorWhichIsA`, `FindFirstChild`, `FindFirstChildOfClass`, `FindFirstChildWhichIsA`, `GetAttribute`, `GetAttributeChangedSignal`, `GetAttributes`, `GetChildren`, `GetDescendants`, `GetFullName`, `GetPropertyChangedSignal`, `GetTags`, `HasTag`, `IsA`, `IsAncestorOf`, `IsDescendantOf`, `Remove`, `RemoveTag`, `SetAttribute`, `WaitForChild`, `children`, `destroy`, `findFirstChild`, `getChildren`, `isA`, `remove`.

### MaterialService

- method: `GetBaseMaterialOverride`, `GetMaterialVariant`, `SetBaseMaterialOverride`.

### Model

- method: `GetBoundingBox`, `GetExtentsSize`, `GetPivot`, `MoveTo`, `PivotTo`.
- getter: `WorldPivot`.
- setter: `PrimaryPart`, `WorldPivot`.

### PhysicsService

- method: `CollisionGroupContainsPart`, `CollisionGroupSetCollidable`, `CollisionGroupsAreCollidable`, `CreateCollisionGroup`, `GetCollisionGroupId`, `GetCollisionGroupName`, `GetCollisionGroups`, `GetMaxCollisionGroups`, `GetRegisteredCollisionGroups`, `IsCollisionGroupRegistered`, `RegisterCollisionGroup`, `RemoveCollisionGroup`, `RenameCollisionGroup`, `SetPartCollisionGroup`, `UnregisterCollisionGroup`.

### Player

- event: `CharacterAdded`, `CharacterRemoving`.

### Players

- method: `GetPlayerByUserId`, `GetPlayerFromCharacter`, `GetPlayers`.
- getter: `LocalPlayer`.
- event: `PlayerAdded`, `PlayerRemoving`.

### RemoteEvent

- method: `FireAllClients`, `FireClient`, `FireServer`.
- event: `OnClientEvent`, `OnServerEvent`.

### RemoteFunction

- method: `InvokeClient`, `InvokeServer`.
- getter: `OnClientInvoke`, `OnServerInvoke`.
- setter: `OnClientInvoke`, `OnServerInvoke`.

### RunService

- method: `IsClient`, `IsEdit`, `IsRunning`, `IsServer`, `IsStudio`.
- event: `Heartbeat`, `PostSimulation`, `PreRender`, `PreSimulation`, `RenderStepped`, `Stepped`.

### ServiceProvider

- method: `FindService`, `GetService`, `service`.

### Tween

- getter: `Instance`, `TweenInfo`.

### TweenBase

- method: `Cancel`, `Pause`, `Play`.
- getter: `PlaybackState`.
- event: `Completed`.

### TweenService

- method: `Create`, `GetValue`.

### WorldRoot

- method: `GetPartBoundsInBox`, `GetPartBoundsInRadius`, `GetPartsInPart`, `Raycast`.

## Service names accepted by GetService

Most are containers. This list does not imply implemented APIs for every service.

`AssetService`, `BadgeService`, `Chat`, `CollectionService`, `ContentProvider`, `ContextActionService`, `DataStoreService`, `Debris`, `EncodingService`, `GroupService`, `GuiService`, `HttpService`, `InsertService`, `Lighting`, `LocalizationService`, `LogService`, `MarketplaceService`, `MaterialService`, `MemoryStoreService`, `MessagingService`, `PathfindingService`, `PhysicsService`, `Players`, `PolicyService`, `ReplicatedFirst`, `ReplicatedStorage`, `RunService`, `ServerScriptService`, `ServerStorage`, `SoundService`, `StarterGui`, `StarterPack`, `StarterPlayer`, `Stats`, `Teams`, `TeleportService`, `TestService`, `TextChatService`, `TextService`, `TweenService`, `UserInputService`, `VRService`, `Workspace`.

## Known classes and implemented properties

This combines class metadata with runtime fields. Many classes only have Instance behavior.
Native creation rules, abstractness, and defaults remain incomplete.

### Accessory

Parent class: `Accoutrement`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### AccessoryDescription

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### AccountService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### Accoutrement

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### AchievementService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### ActivityHistoryEventService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### Actor

Parent class: `Model`; creation: permitted by current runtime (native rules incomplete).

| Property | Current type/default |
| --- | --- |
| `PrimaryPart` | `Instance? = nil` |
| `WorldPivot` | `CFrame = 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1` |

### AdGui

Parent class: `SurfaceGuiBase`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### AdPortal

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### AdvLuaDragger

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### AirController

Parent class: `ControllerBase`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### AlignOrientation

Parent class: `Constraint`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### AlignPosition

Parent class: `Constraint`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### AnalyticsService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### AngularVelocity

Parent class: `Constraint`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### Animation

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### AnimationClip

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### AnimationClipProvider

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### AnimationConstraint

Parent class: `Constraint`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### AnimationController

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### AnimationFromVideoCreatorService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### AnimationGraphDefinition

Parent class: `AnimationClip`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### AnimationNodeDefinition

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### AnimationRigData

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### AnimationStreamTrack

Parent class: `BaseAnimationTrack`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### AnimationTrack

Parent class: `BaseAnimationTrack`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### Animator

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### Annotation

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### AnnotationsService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### AppAgeSignalsService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### AppLifecycleObserverService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### AppRatingPromptService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### AppStorageService

Parent class: `LocalStorageService`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### AppUpdateService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### ArcHandles

Parent class: `HandlesBase`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### AssetCounterService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### AssetDeliveryProxy

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### AssetImportSession

Parent class: `ImportSession`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### AssetPatchSettings

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### AssetQualityService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### AssetService

Parent class: `ServiceInstance`; creation: not directly creatable.

Only base Instance properties and separately declared members/getters.

### Atmosphere

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### AtmosphereSensor

Parent class: `SensorBase`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### Attachment

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### AudioAnalyzer

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### AudioChannelMixer

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### AudioChannelSplitter

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### AudioChorus

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### AudioCompressor

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### AudioDeviceInput

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### AudioDeviceOutput

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### AudioDistortion

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### AudioEcho

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### AudioEmitter

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### AudioEqualizer

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### AudioFDNReverb

Parent class: ``; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### AudioFader

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### AudioFilter

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### AudioFlanger

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### AudioFocusService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### AudioGate

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### AudioLimiter

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### AudioListener

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### AudioPages

Parent class: `Pages`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### AudioPitchShifter

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### AudioPlayer

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### AudioRecorder

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### AudioReverb

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### AudioSearchParams

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### AudioSpeechToText

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### AudioTextToSpeech

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### AudioTremolo

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### AudioWindSynthesizer

Parent class: ``; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### AuroraScript

Parent class: `LuaSourceContainer`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### AuroraScriptObject

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### AuroraScriptService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### AuroraService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### AvatarAbilityRules

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### AvatarAccessoryRules

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### AvatarAnimationRules

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### AvatarBodyRules

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### AvatarChatService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### AvatarClothingRules

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### AvatarCollisionRules

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### AvatarCreationService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### AvatarEditorService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### AvatarRules

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### AvatarSettings

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### Backpack

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### BackpackItem

Parent class: `Model`; creation: permitted by current runtime (native rules incomplete).

| Property | Current type/default |
| --- | --- |
| `PrimaryPart` | `Instance? = nil` |
| `WorldPivot` | `CFrame = 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1` |

### BadgeService

Parent class: `ServiceInstance`; creation: not directly creatable.

Only base Instance properties and separately declared members/getters.

### BallSocketConstraint

Parent class: `Constraint`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### BanHistoryPages

Parent class: `Pages`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### BaseCoreGuiConfiguration

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### BasePart

Parent class: `PVInstance`; creation: not directly creatable.

| Property | Current type/default |
| --- | --- |
| `Anchored` | `boolean = false` |
| `AssemblyAngularVelocity` | `Vector3 = 0, 0, 0` |
| `AssemblyLinearVelocity` | `Vector3 = 0, 0, 0` |
| `BackSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `BottomSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `CFrame` | `CFrame = 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1` |
| `CanCollide` | `boolean = true` |
| `CanQuery` | `boolean = true` |
| `CanTouch` | `boolean = true` |
| `CastShadow` | `boolean = true` |
| `CollisionGroup` | `string = Default` |
| `Color` | `Color3 = 0.6392156862745098, 0.6352941176470588, 0.6470588235294118` |
| `CustomPhysicalProperties` | `PhysicalProperties? = nil` |
| `FrontSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `LeftSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `Locked` | `boolean = false` |
| `Massless` | `boolean = false` |
| `Material` | `Enum.Material = Enum.Material.Plastic` |
| `MaterialVariant` | `string = ` |
| `PivotOffset` | `CFrame = 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1` |
| `Reflectance` | `number = 0` |
| `RightSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `RootPriority` | `number = 0` |
| `RotVelocity` | `Vector3 = 0, 0, 0` |
| `Size` | `Vector3 = 4, 1.2, 2` |
| `TopSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `Transparency` | `number = 0` |
| `Velocity` | `Vector3 = 0, 0, 0` |

### BasePlayerGui

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### BaseRemoteEvent

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### BaseScript

Parent class: `LuaSourceContainer`; creation: not directly creatable.

| Property | Current type/default |
| --- | --- |
| `Disabled` | `boolean = false` |
| `Enabled` | `boolean = true` |
| `RunContext` | `Enum.RunContext = Enum.RunContext.Legacy` |

### BaseWrap

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### Beam

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### BevelMesh

Parent class: `DataModelMesh`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### BillboardGui

Parent class: `GuiLayerCollector`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### BinaryStringValue

Parent class: `ValueBase`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### BindableEvent

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### BindableFunction

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### BlockMesh

Parent class: `BevelMesh`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### BloomEffect

Parent class: `PostEffect`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### BlurEffect

Parent class: `PostEffect`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### BodyAngularVelocity

Parent class: `BodyMover`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### BodyColors

Parent class: `LegacyCharacterAppearance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### BodyForce

Parent class: `BodyMover`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### BodyGyro

Parent class: `BodyMover`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### BodyMover

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### BodyPartDescription

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### BodyPosition

Parent class: `BodyMover`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### BodyThrust

Parent class: `BodyMover`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### BodyVelocity

Parent class: `BodyMover`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### Bone

Parent class: `Attachment`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### BoneInstance

Parent class: `Attachment`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### BoolValue

Parent class: `ValueBase`; creation: permitted by current runtime (native rules incomplete).

| Property | Current type/default |
| --- | --- |
| `Value` | `boolean = false` |

### BoxHandleAdornment

Parent class: `HandleAdornment`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### BranchService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### BrickColorValue

Parent class: `ValueBase`; creation: permitted by current runtime (native rules incomplete).

| Property | Current type/default |
| --- | --- |
| `Value` | `BrickColor = Medium stone grey` |

### BrowserService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### BubbleChatConfiguration

Parent class: `TextChatConfigurations`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### BubbleChatMessageProperties

Parent class: `TextChatMessagePropertiesClass`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### BugReporterService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### BuoyancySensor

Parent class: `SensorBase`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### CFramePose

Parent class: `PoseBase`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### CFrameValue

Parent class: `ValueBase`; creation: permitted by current runtime (native rules incomplete).

| Property | Current type/default |
| --- | --- |
| `Value` | `CFrame = 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1` |

### CSGDictionaryService

Parent class: `FlyweightService`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### CacheableContentProvider

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### Camera

Parent class: `PVInstance`; creation: permitted by current runtime (native rules incomplete).

| Property | Current type/default |
| --- | --- |
| `CFrame` | `CFrame = 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1` |
| `CameraSubject` | `Instance? = nil` |
| `FieldOfView` | `number = 70` |
| `Focus` | `CFrame = 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1` |

### CanvasGroup

Parent class: `GuiObject`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### Capture

Parent class: `Object`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### CaptureService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### CapturesPages

Parent class: `Pages`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### CapturesViewConfiguration

Parent class: `BaseCoreGuiConfiguration`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### ChangeHistoryService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### ChangeHistoryStreamingService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### ChannelTabsConfiguration

Parent class: `TextChatConfigurations`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### CharacterMesh

Parent class: `CharacterAppearance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### Chat

Parent class: `Instance`; creation: not directly creatable.

Only base Instance properties and separately declared members/getters.

### ChatInputBarConfiguration

Parent class: `TextChatConfigurations`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### ChatService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### ChatWindowConfiguration

Parent class: `TextChatConfigurations`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### ChatWindowMessageProperties

Parent class: `TextChatMessagePropertiesClass`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### ChorusSoundEffect

Parent class: ``; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### ClickDetector

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### ClientStorageService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### ClimbController

Parent class: `ControllerBase`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### Clothing

Parent class: `CharacterAppearance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### CloudCRUDService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### CloudExecutionService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### Clouds

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### Collaborator

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### CollaboratorsService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### CollectionService

Parent class: `ServiceInstance`; creation: not directly creatable.

Only base Instance properties and separately declared members/getters.

### Color3Value

Parent class: `ValueBase`; creation: permitted by current runtime (native rules incomplete).

| Property | Current type/default |
| --- | --- |
| `Value` | `Color3 = 0, 0, 0` |

### ColorCorrectionEffect

Parent class: `PostEffect`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### ColorGradingEffect

Parent class: `PostEffect`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### CommerceService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### CompositeValueCurve

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### CompressorSoundEffect

Parent class: ``; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### ConeHandleAdornment

Parent class: `HandleAdornment`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### ConfigService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### ConfigSnapshot

Parent class: `Object`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### Configuration

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### ConfigureServerService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### ConnectivityService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### Constraint

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### ContentProvider

Parent class: `ServiceInstance`; creation: not directly creatable.

Only base Instance properties and separately declared members/getters.

### ContextActionService

Parent class: `ServiceInstance`; creation: not directly creatable.

Only base Instance properties and separately declared members/getters.

### Controller

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### ControllerBase

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### ControllerManager

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### ControllerPartSensor

Parent class: `ControllerSensor`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### ControllerSensor

Parent class: `SensorBase`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### ControllerService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### CookiesService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### CoreGui

Parent class: `BasePlayerGui`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### CoreGuiConfiguration

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### CoreGuiService

Parent class: `BasePlayerGui`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### CorePackages

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### CoreScript

Parent class: `BaseScript`; creation: permitted by current runtime (native rules incomplete).

| Property | Current type/default |
| --- | --- |
| `Disabled` | `boolean = false` |
| `Enabled` | `boolean = true` |
| `RunContext` | `Enum.RunContext = Enum.RunContext.Legacy` |

### CoreScriptSyncService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### CornerWedgeInstance

Parent class: `BasePart`; creation: permitted by current runtime (native rules incomplete).

| Property | Current type/default |
| --- | --- |
| `Anchored` | `boolean = false` |
| `AssemblyAngularVelocity` | `Vector3 = 0, 0, 0` |
| `AssemblyLinearVelocity` | `Vector3 = 0, 0, 0` |
| `BackSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `BottomSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `CFrame` | `CFrame = 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1` |
| `CanCollide` | `boolean = true` |
| `CanQuery` | `boolean = true` |
| `CanTouch` | `boolean = true` |
| `CastShadow` | `boolean = true` |
| `CollisionGroup` | `string = Default` |
| `Color` | `Color3 = 0.6392156862745098, 0.6352941176470588, 0.6470588235294118` |
| `CustomPhysicalProperties` | `PhysicalProperties? = nil` |
| `FrontSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `LeftSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `Locked` | `boolean = false` |
| `Massless` | `boolean = false` |
| `Material` | `Enum.Material = Enum.Material.Plastic` |
| `MaterialVariant` | `string = ` |
| `PivotOffset` | `CFrame = 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1` |
| `Reflectance` | `number = 0` |
| `RightSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `RootPriority` | `number = 0` |
| `RotVelocity` | `Vector3 = 0, 0, 0` |
| `Size` | `Vector3 = 4, 1.2, 2` |
| `TopSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `Transparency` | `number = 0` |
| `Velocity` | `Vector3 = 0, 0, 0` |

### CornerWedgePart

Parent class: `BasePart`; creation: permitted by current runtime (native rules incomplete).

| Property | Current type/default |
| --- | --- |
| `Anchored` | `boolean = false` |
| `AssemblyAngularVelocity` | `Vector3 = 0, 0, 0` |
| `AssemblyLinearVelocity` | `Vector3 = 0, 0, 0` |
| `BackSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `BottomSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `CFrame` | `CFrame = 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1` |
| `CanCollide` | `boolean = true` |
| `CanQuery` | `boolean = true` |
| `CanTouch` | `boolean = true` |
| `CastShadow` | `boolean = true` |
| `CollisionGroup` | `string = Default` |
| `Color` | `Color3 = 0.6392156862745098, 0.6352941176470588, 0.6470588235294118` |
| `CustomPhysicalProperties` | `PhysicalProperties? = nil` |
| `FrontSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `LeftSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `Locked` | `boolean = false` |
| `Massless` | `boolean = false` |
| `Material` | `Enum.Material = Enum.Material.Plastic` |
| `MaterialVariant` | `string = ` |
| `PivotOffset` | `CFrame = 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1` |
| `Reflectance` | `number = 0` |
| `RightSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `RootPriority` | `number = 0` |
| `RotVelocity` | `Vector3 = 0, 0, 0` |
| `Size` | `Vector3 = 4, 1.2, 2` |
| `TopSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `Transparency` | `number = 0` |
| `Velocity` | `Vector3 = 0, 0, 0` |

### CreationDBService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### CurveAnimation

Parent class: `AnimationClip`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### CustomEvent

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### CustomEventReceiver

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### CustomLog

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### CustomParticleEmitter

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### CylinderHandleAdornment

Parent class: `HandleAdornment`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### CylinderMesh

Parent class: `BevelMesh`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### CylindricalConstraint

Parent class: `SlidingBallConstraint`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### DataModel

Parent class: `ServiceProvider`; creation: not directly creatable.

Only base Instance properties and separately declared members/getters.

### DataModelDiff

Parent class: `Object`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### DataModelMesh

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### DataModelPatchService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### DataStore

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### DataStore2

Parent class: `DataStore`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### DataStoreGetOptions

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### DataStoreIncrementOptions

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### DataStoreInfo

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### DataStoreKey

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### DataStoreKeyInfo

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### DataStoreKeyPages

Parent class: `Pages`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### DataStoreListingPages

Parent class: `Pages`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### DataStoreObjectVersionInfo

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### DataStoreOptions

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### DataStorePages

Parent class: `Pages`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### DataStoreService

Parent class: `ServiceInstance`; creation: not directly creatable.

Only base Instance properties and separately declared members/getters.

### DataStoreSetOptions

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### DataStoreVersionPages

Parent class: `Pages`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### Debris

Parent class: `Instance`; creation: not directly creatable.

Only base Instance properties and separately declared members/getters.

### DebrisService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### DebugSettings

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### DebuggerBreakpoint

Parent class: ``; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### DebuggerManager

Parent class: ``; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### DebuggerWatch

Parent class: ``; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### Decal

Parent class: `FaceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### DecalTexture

Parent class: `Decal`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### DeferredAssetManagerService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### DepthOfFieldEffect

Parent class: `PostEffect`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### DesignFoundationsService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### DeviceDisplayService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### DeviceIdService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### Dialog

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### DialogChoice

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### DialogRoot

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### DigitsRigDescription

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### DisplayWakeLock

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### DistortionSoundEffect

Parent class: ``; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### DockWidgetPluginGui

Parent class: `PluginGui`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### DoubleConstrainedValue

Parent class: `ValueBase`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### DoublePose

Parent class: `PoseBase`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### DoubleValue

Parent class: `ValueBase`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### DraftsService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### DragDetector

Parent class: `ClickDetector`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### DraggerService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### DynamicRotate

Parent class: `JointInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### EchoSoundEffect

Parent class: ``; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### EditableImage

Parent class: `Object`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### EditableMesh

Parent class: `Object`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### EditableService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### EditorSourceService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### EncodingService

Parent class: `ServiceInstance`; creation: not directly creatable.

Only base Instance properties and separately declared members/getters.

### EqualizerSoundEffect

Parent class: ``; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### EulerRotationCurve

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### EventIngestService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### ExampleV2Service

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### ExperienceAuthService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### ExperienceInviteOptions

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### ExperienceNotificationService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### ExperienceService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### ExperienceStateCaptureService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### ExplorerServiceVisibilityService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### Explosion

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### ExtrudedPartInstance

Parent class: `BasePart`; creation: permitted by current runtime (native rules incomplete).

| Property | Current type/default |
| --- | --- |
| `Anchored` | `boolean = false` |
| `AssemblyAngularVelocity` | `Vector3 = 0, 0, 0` |
| `AssemblyLinearVelocity` | `Vector3 = 0, 0, 0` |
| `BackSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `BottomSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `CFrame` | `CFrame = 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1` |
| `CanCollide` | `boolean = true` |
| `CanQuery` | `boolean = true` |
| `CanTouch` | `boolean = true` |
| `CastShadow` | `boolean = true` |
| `CollisionGroup` | `string = Default` |
| `Color` | `Color3 = 0.6392156862745098, 0.6352941176470588, 0.6470588235294118` |
| `CustomPhysicalProperties` | `PhysicalProperties? = nil` |
| `FrontSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `LeftSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `Locked` | `boolean = false` |
| `Massless` | `boolean = false` |
| `Material` | `Enum.Material = Enum.Material.Plastic` |
| `MaterialVariant` | `string = ` |
| `PivotOffset` | `CFrame = 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1` |
| `Reflectance` | `number = 0` |
| `RightSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `RootPriority` | `number = 0` |
| `RotVelocity` | `Vector3 = 0, 0, 0` |
| `Size` | `Vector3 = 4, 1.2, 2` |
| `TopSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `Transparency` | `number = 0` |
| `Velocity` | `Vector3 = 0, 0, 0` |

### FaceAnimatorService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### FaceControls

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### FaceInstance

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### FacialAgeEstimationService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### FacialAnimationStreamingServiceStats

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### FacialAnimationStreamingServiceV2

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### FacialAnimationStreamingSubsessionStats

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### Feature

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### FeatureRestrictionManager

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### File

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### FileManagerService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### FileMesh

Parent class: `DataModelMesh`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### FileSyncItem

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### FileSyncReplicationService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### FileSyncService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### Fire

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### Flag

Parent class: `Tool`; creation: permitted by current runtime (native rules incomplete).

| Property | Current type/default |
| --- | --- |
| `PrimaryPart` | `Instance? = nil` |
| `WorldPivot` | `CFrame = 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1` |

### FlagStand

Parent class: `Part`; creation: permitted by current runtime (native rules incomplete).

| Property | Current type/default |
| --- | --- |
| `Anchored` | `boolean = false` |
| `AssemblyAngularVelocity` | `Vector3 = 0, 0, 0` |
| `AssemblyLinearVelocity` | `Vector3 = 0, 0, 0` |
| `BackSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `BottomSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `CFrame` | `CFrame = 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1` |
| `CanCollide` | `boolean = true` |
| `CanQuery` | `boolean = true` |
| `CanTouch` | `boolean = true` |
| `CastShadow` | `boolean = true` |
| `CollisionGroup` | `string = Default` |
| `Color` | `Color3 = 0.6392156862745098, 0.6352941176470588, 0.6470588235294118` |
| `CustomPhysicalProperties` | `PhysicalProperties? = nil` |
| `FrontSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `LeftSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `Locked` | `boolean = false` |
| `Massless` | `boolean = false` |
| `Material` | `Enum.Material = Enum.Material.Plastic` |
| `MaterialVariant` | `string = ` |
| `PivotOffset` | `CFrame = 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1` |
| `Reflectance` | `number = 0` |
| `RightSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `RootPriority` | `number = 0` |
| `RotVelocity` | `Vector3 = 0, 0, 0` |
| `Size` | `Vector3 = 4, 1.2, 2` |
| `TopSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `Transparency` | `number = 0` |
| `Velocity` | `Vector3 = 0, 0, 0` |

### FlagStandService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### FlangeSoundEffect

Parent class: ``; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### FloatCurve

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### FloorWire

Parent class: `GuiBase3d`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### FluidForceSensor

Parent class: `SensorBase`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### FlyweightService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### Folder

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### ForceField

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### FormFactorPart

Parent class: `BasePart`; creation: not directly creatable.

| Property | Current type/default |
| --- | --- |
| `Anchored` | `boolean = false` |
| `AssemblyAngularVelocity` | `Vector3 = 0, 0, 0` |
| `AssemblyLinearVelocity` | `Vector3 = 0, 0, 0` |
| `BackSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `BottomSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `CFrame` | `CFrame = 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1` |
| `CanCollide` | `boolean = true` |
| `CanQuery` | `boolean = true` |
| `CanTouch` | `boolean = true` |
| `CastShadow` | `boolean = true` |
| `CollisionGroup` | `string = Default` |
| `Color` | `Color3 = 0.6392156862745098, 0.6352941176470588, 0.6470588235294118` |
| `CustomPhysicalProperties` | `PhysicalProperties? = nil` |
| `FrontSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `LeftSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `Locked` | `boolean = false` |
| `Massless` | `boolean = false` |
| `Material` | `Enum.Material = Enum.Material.Plastic` |
| `MaterialVariant` | `string = ` |
| `PivotOffset` | `CFrame = 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1` |
| `Reflectance` | `number = 0` |
| `RightSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `RootPriority` | `number = 0` |
| `RotVelocity` | `Vector3 = 0, 0, 0` |
| `Size` | `Vector3 = 4, 1.2, 2` |
| `TopSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `Transparency` | `number = 0` |
| `Velocity` | `Vector3 = 0, 0, 0` |

### Frame

Parent class: `GuiObject`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### FriendPages

Parent class: `Pages`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### FriendService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### FunctionalTest

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### GamePassService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### GameSettings

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### GamepadService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### GeneratedFolder

Parent class: `Folder`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### GenerationService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### GenericChallengeService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### GeometryService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### GeometryService_Deprecated

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### GlobalAdvancedSettings

Parent class: `Settings`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### GlobalBasicSettings

Parent class: `Settings`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### GlobalDataStore

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### GlobalSettings

Parent class: ``; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### Glue

Parent class: `JointInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### GongService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### GroundController

Parent class: `ControllerBase`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### GroupService

Parent class: `ServiceInstance`; creation: not directly creatable.

Only base Instance properties and separately declared members/getters.

### GuiBase

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### GuiBase2d

Parent class: `GuiBase`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### GuiBase3d

Parent class: `GuiBase`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### GuiButton

Parent class: `GuiObject`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### GuiImageButton

Parent class: `GuiButton`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### GuiLabel

Parent class: `GuiObject`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### GuiLayerCollector

Parent class: `GuiBase2d`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### GuiMain

Parent class: `ScreenGui`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### GuiObject

Parent class: `GuiBase2d`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### GuiService

Parent class: `ServiceInstance`; creation: not directly creatable.

Only base Instance properties and separately declared members/getters.

### GuiTextButton

Parent class: `GuiButton`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### GuidRegistryService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### HSRDataContentProvider

Parent class: `CacheableContentProvider`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### HandRigDescription

Parent class: ``; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### HandleAdornment

Parent class: `PVAdornment`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### Handles

Parent class: `HandlesBase`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### HandlesBase

Parent class: `PartAdornment`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### HapticEffect

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### HapticService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### HarmonyService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### Hat

Parent class: `Accoutrement`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### HeapProfilerService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### HeatmapQueryService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### HeatmapService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### HeightmapImporterService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### HiddenSurfaceRemovalAsset

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### Highlight

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### HingeConstraint

Parent class: `Constraint`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### Hint

Parent class: `Message`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### Hole

Parent class: `Feature`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### Hopper

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### HopperBin

Parent class: `BackpackItem`; creation: permitted by current runtime (native rules incomplete).

| Property | Current type/default |
| --- | --- |
| `PrimaryPart` | `Instance? = nil` |
| `WorldPivot` | `CFrame = 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1` |

### HttpRbxApiService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### HttpRequestWrapper

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### HttpService

Parent class: `ServiceInstance`; creation: not directly creatable.

| Property | Current type/default |
| --- | --- |
| `HttpEnabled` | `boolean = false` |

### Humanoid

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

| Property | Current type/default |
| --- | --- |
| `Health` | `number = 100` |
| `JumpHeight` | `number = 7.2` |
| `JumpPower` | `number = 50` |
| `MaxHealth` | `number = 100` |
| `UseJumpPower` | `boolean = true` |
| `WalkSpeed` | `number = 16` |

### HumanoidController

Parent class: `Controller`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### HumanoidDescription

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### HumanoidRigDescription

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### IKControl

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### IXPService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### IkControl

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### ImageButton

Parent class: `GuiButton`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### ImageHandleAdornment

Parent class: `HandleAdornment`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### ImageLabel

Parent class: `GuiLabel`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### ImageScreenCaptureService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### ImportSession

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### IncrementalPatchBuilder

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### InputAction

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### InputActionLabel

Parent class: `GuiObject`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### InputBinding

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### InputContext

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### InputObject

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### InsertService

Parent class: `ServiceInstance`; creation: not directly creatable.

Only base Instance properties and separately declared members/getters.

### Instance

Parent class: ``; creation: not directly creatable.

Only base Instance properties and separately declared members/getters.

### InstanceAdornment

Parent class: `GuiBase3d`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### InstanceExtensionsService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### InstanceFileSyncService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### IntConstrainedValue

Parent class: `ValueBase`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### IntValue

Parent class: `ValueBase`; creation: permitted by current runtime (native rules incomplete).

| Property | Current type/default |
| --- | --- |
| `Value` | `number = 0` |

### IntentService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### InternalMessagingService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### InternalMessagingServiceVerifier

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### IntersectOperation

Parent class: `PartOperation`; creation: permitted by current runtime (native rules incomplete).

| Property | Current type/default |
| --- | --- |
| `Anchored` | `boolean = false` |
| `AssemblyAngularVelocity` | `Vector3 = 0, 0, 0` |
| `AssemblyLinearVelocity` | `Vector3 = 0, 0, 0` |
| `BackSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `BottomSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `CFrame` | `CFrame = 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1` |
| `CanCollide` | `boolean = true` |
| `CanQuery` | `boolean = true` |
| `CanTouch` | `boolean = true` |
| `CastShadow` | `boolean = true` |
| `CollisionGroup` | `string = Default` |
| `Color` | `Color3 = 0.6392156862745098, 0.6352941176470588, 0.6470588235294118` |
| `CustomPhysicalProperties` | `PhysicalProperties? = nil` |
| `FrontSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `LeftSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `Locked` | `boolean = false` |
| `Massless` | `boolean = false` |
| `Material` | `Enum.Material = Enum.Material.Plastic` |
| `MaterialVariant` | `string = ` |
| `PivotOffset` | `CFrame = 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1` |
| `Reflectance` | `number = 0` |
| `RightSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `RootPriority` | `number = 0` |
| `RotVelocity` | `Vector3 = 0, 0, 0` |
| `Size` | `Vector3 = 4, 1.2, 2` |
| `TopSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `Transparency` | `number = 0` |
| `Velocity` | `Vector3 = 0, 0, 0` |

### InventoryPages

Parent class: `Pages`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### Item

Parent class: ``; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### JointInstance

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### JointsService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### KeyboardService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### Keyframe

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### KeyframeMarker

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### KeyframeSequence

Parent class: `AnimationClip`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### LanguageService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### LayerCollector

Parent class: `GuiBase2d`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### LegacyHopperService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### Light

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### Lighting

Parent class: `ServiceInstance`; creation: not directly creatable.

Only base Instance properties and separately declared members/getters.

### LineForce

Parent class: `Constraint`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### LineHandleAdornment

Parent class: `HandleAdornment`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### LinearVelocity

Parent class: `Constraint`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### LinkingService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### LiveSyncService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### LocalBackpack

Parent class: ``; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### LocalBackpackItem

Parent class: ``; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### LocalScript

Parent class: `Script`; creation: permitted by current runtime (native rules incomplete).

| Property | Current type/default |
| --- | --- |
| `Disabled` | `boolean = false` |
| `Enabled` | `boolean = true` |
| `RunContext` | `Enum.RunContext = Enum.RunContext.Legacy` |

### LocalStorageService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### LocalizationService

Parent class: `ServiceInstance`; creation: not directly creatable.

Only base Instance properties and separately declared members/getters.

### LocalizationTable

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### LodDataEntity

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### LodDataService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### LogReporterService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### LogService

Parent class: `ServiceInstance`; creation: not directly creatable.

Only base Instance properties and separately declared members/getters.

### Logger

Parent class: `Object`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### LoginService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### LuaDragger

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### LuaSourceContainer

Parent class: `Instance`; creation: not directly creatable.

Only base Instance properties and separately declared members/getters.

### LuaWebService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### LuauExpressionBridge

Parent class: `Object`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### LuauExpressionService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### MLModelDeliveryService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### MLService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### MLSession

Parent class: `Object`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### MakeupDescription

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### ManualGlue

Parent class: `ManualSurfaceJointInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### ManualSurfaceJointInstance

Parent class: `JointInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### ManualWeld

Parent class: `ManualSurfaceJointInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### MarkerCurve

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### MarketplaceService

Parent class: `ServiceInstance`; creation: not directly creatable.

Only base Instance properties and separately declared members/getters.

### MatchmakingService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### MaterialService

Parent class: `ServiceInstance`; creation: not directly creatable.

Only base Instance properties and separately declared members/getters.

### MaterialVariant

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

| Property | Current type/default |
| --- | --- |
| `BaseMaterial` | `Enum.Material = Enum.Material.Plastic` |
| `CustomPhysicalProperties` | `PhysicalProperties? = nil` |

### MemStorageConnection

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### MemStorageService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### MemoryStoreDistributedCounter

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### MemoryStoreHashMap

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### MemoryStoreHashMapPages

Parent class: `Pages`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### MemoryStoreQueue

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### MemoryStoreService

Parent class: `ServiceInstance`; creation: not directly creatable.

Only base Instance properties and separately declared members/getters.

### MemoryStoreSortedMap

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### MeshContentProvider

Parent class: `CacheableContentProvider`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### MeshPart

Parent class: `TriangleMeshPart`; creation: permitted by current runtime (native rules incomplete).

| Property | Current type/default |
| --- | --- |
| `Anchored` | `boolean = false` |
| `AssemblyAngularVelocity` | `Vector3 = 0, 0, 0` |
| `AssemblyLinearVelocity` | `Vector3 = 0, 0, 0` |
| `BackSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `BottomSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `CFrame` | `CFrame = 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1` |
| `CanCollide` | `boolean = true` |
| `CanQuery` | `boolean = true` |
| `CanTouch` | `boolean = true` |
| `CastShadow` | `boolean = true` |
| `CollisionGroup` | `string = Default` |
| `Color` | `Color3 = 0.6392156862745098, 0.6352941176470588, 0.6470588235294118` |
| `CustomPhysicalProperties` | `PhysicalProperties? = nil` |
| `FrontSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `LeftSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `Locked` | `boolean = false` |
| `Massless` | `boolean = false` |
| `Material` | `Enum.Material = Enum.Material.Plastic` |
| `MaterialVariant` | `string = ` |
| `PivotOffset` | `CFrame = 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1` |
| `Reflectance` | `number = 0` |
| `RightSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `RootPriority` | `number = 0` |
| `RotVelocity` | `Vector3 = 0, 0, 0` |
| `Size` | `Vector3 = 4, 1.2, 2` |
| `TopSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `Transparency` | `number = 0` |
| `Velocity` | `Vector3 = 0, 0, 0` |

### Message

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### MessageBusService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### MessagingService

Parent class: `ServiceInstance`; creation: not directly creatable.

Only base Instance properties and separately declared members/getters.

### MicroProfilerService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### Model

Parent class: `PVInstance`; creation: permitted by current runtime (native rules incomplete).

| Property | Current type/default |
| --- | --- |
| `PrimaryPart` | `Instance? = nil` |
| `WorldPivot` | `CFrame = 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1` |

### ModerationService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### ModuleScript

Parent class: `LuaSourceContainer`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### Motor

Parent class: `JointInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### Motor6D

Parent class: `Motor`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### MotorFeature

Parent class: `Feature`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### Mouse

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### MouseService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### NegateOperation

Parent class: `PartOperation`; creation: permitted by current runtime (native rules incomplete).

| Property | Current type/default |
| --- | --- |
| `Anchored` | `boolean = false` |
| `AssemblyAngularVelocity` | `Vector3 = 0, 0, 0` |
| `AssemblyLinearVelocity` | `Vector3 = 0, 0, 0` |
| `BackSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `BottomSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `CFrame` | `CFrame = 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1` |
| `CanCollide` | `boolean = true` |
| `CanQuery` | `boolean = true` |
| `CanTouch` | `boolean = true` |
| `CastShadow` | `boolean = true` |
| `CollisionGroup` | `string = Default` |
| `Color` | `Color3 = 0.6392156862745098, 0.6352941176470588, 0.6470588235294118` |
| `CustomPhysicalProperties` | `PhysicalProperties? = nil` |
| `FrontSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `LeftSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `Locked` | `boolean = false` |
| `Massless` | `boolean = false` |
| `Material` | `Enum.Material = Enum.Material.Plastic` |
| `MaterialVariant` | `string = ` |
| `PivotOffset` | `CFrame = 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1` |
| `Reflectance` | `number = 0` |
| `RightSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `RootPriority` | `number = 0` |
| `RotVelocity` | `Vector3 = 0, 0, 0` |
| `Size` | `Vector3 = 4, 1.2, 2` |
| `TopSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `Transparency` | `number = 0` |
| `Velocity` | `Vector3 = 0, 0, 0` |

### NetworkClient

Parent class: `NetworkPeer`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### NetworkMarker

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### NetworkPeer

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### NetworkReplicator

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### NetworkServer

Parent class: `NetworkPeer`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### NetworkSettings

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### NoCollisionConstraint

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### Noise

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### NonReplicatedCSGDictionaryService

Parent class: `FlyweightService`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### NotificationService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### NumberPose

Parent class: `PoseBase`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### NumberValue

Parent class: `ValueBase`; creation: permitted by current runtime (native rules incomplete).

| Property | Current type/default |
| --- | --- |
| `Value` | `number = 0` |

### ObjectValue

Parent class: `ValueBase`; creation: permitted by current runtime (native rules incomplete).

| Property | Current type/default |
| --- | --- |
| `Value` | `Instance? = nil` |

### OmniRecommendationsService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### OpenCloudApiV1

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### OpenCloudService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### OperationGraph

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### OrderedDataStore

Parent class: `DataStore`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### OutfitPages

Parent class: `Pages`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### PVAdornment

Parent class: `GuiBase3d`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### PVInstance

Parent class: `Instance`; creation: not directly creatable.

Only base Instance properties and separately declared members/getters.

### PackageLink

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### PackageService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### PackageUIService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### Packages

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### Pages

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### Pants

Parent class: `Clothing`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### ParabolaAdornment

Parent class: `PVAdornment`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### ParallelRampPart

Parent class: ``; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### Part

Parent class: `FormFactorPart`; creation: permitted by current runtime (native rules incomplete).

| Property | Current type/default |
| --- | --- |
| `Anchored` | `boolean = false` |
| `AssemblyAngularVelocity` | `Vector3 = 0, 0, 0` |
| `AssemblyLinearVelocity` | `Vector3 = 0, 0, 0` |
| `BackSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `BottomSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `CFrame` | `CFrame = 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1` |
| `CanCollide` | `boolean = true` |
| `CanQuery` | `boolean = true` |
| `CanTouch` | `boolean = true` |
| `CastShadow` | `boolean = true` |
| `CollisionGroup` | `string = Default` |
| `Color` | `Color3 = 0.6392156862745098, 0.6352941176470588, 0.6470588235294118` |
| `CustomPhysicalProperties` | `PhysicalProperties? = nil` |
| `FrontSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `LeftSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `Locked` | `boolean = false` |
| `Massless` | `boolean = false` |
| `Material` | `Enum.Material = Enum.Material.Plastic` |
| `MaterialVariant` | `string = ` |
| `PivotOffset` | `CFrame = 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1` |
| `Reflectance` | `number = 0` |
| `RightSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `RootPriority` | `number = 0` |
| `RotVelocity` | `Vector3 = 0, 0, 0` |
| `Shape` | `Enum.PartType = Enum.PartType.Block` |
| `Size` | `Vector3 = 4, 1.2, 2` |
| `TopSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `Transparency` | `number = 0` |
| `Velocity` | `Vector3 = 0, 0, 0` |

### PartAdornment

Parent class: `GuiBase3d`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### PartOperation

Parent class: `TriangleMeshPart`; creation: permitted by current runtime (native rules incomplete).

| Property | Current type/default |
| --- | --- |
| `Anchored` | `boolean = false` |
| `AssemblyAngularVelocity` | `Vector3 = 0, 0, 0` |
| `AssemblyLinearVelocity` | `Vector3 = 0, 0, 0` |
| `BackSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `BottomSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `CFrame` | `CFrame = 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1` |
| `CanCollide` | `boolean = true` |
| `CanQuery` | `boolean = true` |
| `CanTouch` | `boolean = true` |
| `CastShadow` | `boolean = true` |
| `CollisionGroup` | `string = Default` |
| `Color` | `Color3 = 0.6392156862745098, 0.6352941176470588, 0.6470588235294118` |
| `CustomPhysicalProperties` | `PhysicalProperties? = nil` |
| `FrontSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `LeftSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `Locked` | `boolean = false` |
| `Massless` | `boolean = false` |
| `Material` | `Enum.Material = Enum.Material.Plastic` |
| `MaterialVariant` | `string = ` |
| `PivotOffset` | `CFrame = 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1` |
| `Reflectance` | `number = 0` |
| `RightSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `RootPriority` | `number = 0` |
| `RotVelocity` | `Vector3 = 0, 0, 0` |
| `Size` | `Vector3 = 4, 1.2, 2` |
| `TopSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `Transparency` | `number = 0` |
| `Velocity` | `Vector3 = 0, 0, 0` |

### PartOperationAsset

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### PartPairLasso

Parent class: ``; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### ParticleEmitter

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### PartyEmulatorService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### PatchBundlerFileWatch

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### PatchMapping

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### Path

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### Path2D

Parent class: `GuiBase`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### Path3D

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### PathfindingLink

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### PathfindingModifier

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### PathfindingService

Parent class: `ServiceInstance`; creation: not directly creatable.

Only base Instance properties and separately declared members/getters.

### PerformanceControlService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### PermissionsService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### PhysicsService

Parent class: `ServiceInstance`; creation: not directly creatable.

Only base Instance properties and separately declared members/getters.

### PinShortcutService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### PitchShiftSoundEffect

Parent class: ``; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### PlaceAssetIdsService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### PlaceStats

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### Plane

Parent class: `PlaneConstraint`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### PlaneConstraint

Parent class: `Constraint`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### Platform

Parent class: `Part`; creation: permitted by current runtime (native rules incomplete).

| Property | Current type/default |
| --- | --- |
| `Anchored` | `boolean = false` |
| `AssemblyAngularVelocity` | `Vector3 = 0, 0, 0` |
| `AssemblyLinearVelocity` | `Vector3 = 0, 0, 0` |
| `BackSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `BottomSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `CFrame` | `CFrame = 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1` |
| `CanCollide` | `boolean = true` |
| `CanQuery` | `boolean = true` |
| `CanTouch` | `boolean = true` |
| `CastShadow` | `boolean = true` |
| `CollisionGroup` | `string = Default` |
| `Color` | `Color3 = 0.6392156862745098, 0.6352941176470588, 0.6470588235294118` |
| `CustomPhysicalProperties` | `PhysicalProperties? = nil` |
| `FrontSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `LeftSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `Locked` | `boolean = false` |
| `Massless` | `boolean = false` |
| `Material` | `Enum.Material = Enum.Material.Plastic` |
| `MaterialVariant` | `string = ` |
| `PivotOffset` | `CFrame = 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1` |
| `Reflectance` | `number = 0` |
| `RightSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `RootPriority` | `number = 0` |
| `RotVelocity` | `Vector3 = 0, 0, 0` |
| `Size` | `Vector3 = 4, 1.2, 2` |
| `TopSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `Transparency` | `number = 0` |
| `Velocity` | `Vector3 = 0, 0, 0` |

### PlatformCloudStorageService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### PlatformFriendsService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### PlatformLibraries

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### Player

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

| Property | Current type/default |
| --- | --- |
| `Character` | `Instance? = nil` |
| `DisplayName` | `string = LocalPlayer` |
| `UserId` | `number = 1` |

### PlayerControlState

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### PlayerData

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### PlayerDataRecord

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### PlayerDataRecordConfig

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### PlayerDataService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### PlayerEmulatorService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### PlayerGui

Parent class: `BasePlayerGui`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### PlayerHydrationService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### PlayerListConfiguration

Parent class: `BaseCoreGuiConfiguration`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### PlayerMouse

Parent class: `Mouse`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### PlayerScripts

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### PlayerViewService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### Players

Parent class: `ServiceInstance`; creation: not directly creatable.

Only base Instance properties and separately declared members/getters.

### Plugin

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### PluginAction

Parent class: `PluginUIElement`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### PluginCapabilities

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### PluginDebugService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### PluginDragEvent

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### PluginGui

Parent class: `GuiLayerCollector`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### PluginGuiService

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### PluginManager

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### PluginManagerInterface

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### PluginMenu

Parent class: `PluginUIElement`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### PluginMouse

Parent class: `Mouse`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### PluginToolbar

Parent class: `PluginUIElement`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### PluginToolbarButton

Parent class: `PluginUIElement`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### PointLight

Parent class: `Light`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### PointsService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### PolicyService

Parent class: `ServiceInstance`; creation: not directly creatable.

Only base Instance properties and separately declared members/getters.

### PopLatencyService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### Pose

Parent class: `PoseBase`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### PoseBase

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### PostEffect

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### Preloaded

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### PrismPart

Parent class: ``; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### PrismaticConstraint

Parent class: `SlidingBallConstraint`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### ProceduralBehaviorSchedulerService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### ProceduralModel

Parent class: `Model`; creation: permitted by current runtime (native rules incomplete).

| Property | Current type/default |
| --- | --- |
| `PrimaryPart` | `Instance? = nil` |
| `WorldPivot` | `CFrame = 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1` |

### ProcessInstancePhysicsService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### ProfilingItem

Parent class: ``; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### ProximityPrompt

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### ProximityPromptService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### PublishService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### PyramidHandleAdornment

Parent class: `HandleAdornment`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### PyramidPart

Parent class: ``; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### QWidgetPluginGui

Parent class: `PluginGui`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### RESTRICTED_ILegacyStudioBridge

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### RESTRICTED_LegacyStudioBridge

Parent class: `RESTRICTED_ILegacyStudioBridge`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### RESTRICTED_StudioService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### RayValue

Parent class: `ValueBase`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### RbxAnalyticsService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### RealtimeMedia

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### RecommendationPages

Parent class: `Pages`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### RecommendationService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### ReflectionService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### RelativeGui

Parent class: `GuiObject`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### RemoteEvent

Parent class: `BaseRemoteEvent`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### RemoteFunction

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### RenderSettings

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### RenderingTest

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### ReplicatedFirst

Parent class: `ServiceInstance`; creation: not directly creatable.

Only base Instance properties and separately declared members/getters.

### ReplicatedStorage

Parent class: `ServiceInstance`; creation: not directly creatable.

Only base Instance properties and separately declared members/getters.

### ReverbSoundEffect

Parent class: ``; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### RightAngleRampPart

Parent class: ``; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### RigidConstraint

Parent class: `Constraint`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### RobloxPluginGuiService

Parent class: `PluginGuiServiceBase`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### RobloxReplicatedStorage

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### RobloxSerializableInstance

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### RobloxServerStorage

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### Rocket

Parent class: `BodyMover`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### RocketPropulsion

Parent class: `BodyMover`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### RodConstraint

Parent class: `Constraint`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### RolloutValidation

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### RolloutValidationService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### RomarkRbxAnalyticsService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### RomarkService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### RootInstance

Parent class: ``; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### RopeConstraint

Parent class: `Constraint`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### Rotate

Parent class: `JointInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### RotateP

Parent class: `DynamicRotate`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### RotateV

Parent class: `DynamicRotate`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### RotationCurve

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### RtMessagingService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### RunService

Parent class: `ServiceInstance`; creation: not directly creatable.

Only base Instance properties and separately declared members/getters.

### RuntimeContentService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### SceneAnalysisService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### ScreenGui

Parent class: `GuiLayerCollector`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### ScreenshotCapture

Parent class: `Capture`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### ScreenshotHud

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### Script

Parent class: `BaseScript`; creation: permitted by current runtime (native rules incomplete).

| Property | Current type/default |
| --- | --- |
| `Disabled` | `boolean = false` |
| `Enabled` | `boolean = true` |
| `RunContext` | `Enum.RunContext = Enum.RunContext.Legacy` |

### ScriptBuilder

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### ScriptChangeService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### ScriptContext

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### ScriptDebugger

Parent class: ``; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### ScriptProfilerService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### ScriptRegistrationService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### ScriptScannerService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### ScriptService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### ScrollingFrame

Parent class: `GuiObject`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### Seat

Parent class: `Part`; creation: permitted by current runtime (native rules incomplete).

| Property | Current type/default |
| --- | --- |
| `Anchored` | `boolean = false` |
| `AssemblyAngularVelocity` | `Vector3 = 0, 0, 0` |
| `AssemblyLinearVelocity` | `Vector3 = 0, 0, 0` |
| `BackSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `BottomSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `CFrame` | `CFrame = 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1` |
| `CanCollide` | `boolean = true` |
| `CanQuery` | `boolean = true` |
| `CanTouch` | `boolean = true` |
| `CastShadow` | `boolean = true` |
| `CollisionGroup` | `string = Default` |
| `Color` | `Color3 = 0.6392156862745098, 0.6352941176470588, 0.6470588235294118` |
| `CustomPhysicalProperties` | `PhysicalProperties? = nil` |
| `FrontSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `LeftSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `Locked` | `boolean = false` |
| `Massless` | `boolean = false` |
| `Material` | `Enum.Material = Enum.Material.Plastic` |
| `MaterialVariant` | `string = ` |
| `PivotOffset` | `CFrame = 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1` |
| `Reflectance` | `number = 0` |
| `RightSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `RootPriority` | `number = 0` |
| `RotVelocity` | `Vector3 = 0, 0, 0` |
| `Size` | `Vector3 = 4, 1.2, 2` |
| `TopSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `Transparency` | `number = 0` |
| `Velocity` | `Vector3 = 0, 0, 0` |

### Selection

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### SelectionBox

Parent class: `InstanceAdornment`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### SelectionHighlightManager

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### SelectionLasso

Parent class: `GuiBase3d`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### SelectionPartLasso

Parent class: `SelectionLasso`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### SelectionPointLasso

Parent class: `SelectionLasso`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### SelectionSphere

Parent class: `PVAdornment`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### SelfViewConfiguration

Parent class: `BaseCoreGuiConfiguration`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### SensorBase

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### SerializationService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### ServerScriptService

Parent class: `ServiceInstance`; creation: not directly creatable.

Only base Instance properties and separately declared members/getters.

### ServerStorage

Parent class: `ServiceInstance`; creation: not directly creatable.

Only base Instance properties and separately declared members/getters.

### ServiceProvider

Parent class: `Instance`; creation: not directly creatable.

Only base Instance properties and separately declared members/getters.

### ServiceVisibilityService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### SessionCheckService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### SessionService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### Settings

Parent class: `ServiceProvider`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### SharedTableRegistry

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### Shirt

Parent class: `Clothing`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### ShirtGraphic

Parent class: `LegacyCharacterAppearance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### SkateboardController

Parent class: `Controller`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### SkateboardPlatform

Parent class: `Part`; creation: permitted by current runtime (native rules incomplete).

| Property | Current type/default |
| --- | --- |
| `Anchored` | `boolean = false` |
| `AssemblyAngularVelocity` | `Vector3 = 0, 0, 0` |
| `AssemblyLinearVelocity` | `Vector3 = 0, 0, 0` |
| `BackSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `BottomSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `CFrame` | `CFrame = 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1` |
| `CanCollide` | `boolean = true` |
| `CanQuery` | `boolean = true` |
| `CanTouch` | `boolean = true` |
| `CastShadow` | `boolean = true` |
| `CollisionGroup` | `string = Default` |
| `Color` | `Color3 = 0.6392156862745098, 0.6352941176470588, 0.6470588235294118` |
| `CustomPhysicalProperties` | `PhysicalProperties? = nil` |
| `FrontSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `LeftSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `Locked` | `boolean = false` |
| `Massless` | `boolean = false` |
| `Material` | `Enum.Material = Enum.Material.Plastic` |
| `MaterialVariant` | `string = ` |
| `PivotOffset` | `CFrame = 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1` |
| `Reflectance` | `number = 0` |
| `RightSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `RootPriority` | `number = 0` |
| `RotVelocity` | `Vector3 = 0, 0, 0` |
| `Size` | `Vector3 = 4, 1.2, 2` |
| `TopSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `Transparency` | `number = 0` |
| `Velocity` | `Vector3 = 0, 0, 0` |

### Skin

Parent class: `LegacyCharacterAppearance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### Sky

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### SlidingBallConstraint

Parent class: `Constraint`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### SlimAnimationDataEntity

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### SlimAnimationReplicationService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### SlimContentProvider

Parent class: `CacheableContentProvider`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### SlimReplicationService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### SlimService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### Smoke

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### SmoothVoxelsUpgraderService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### Snap

Parent class: `JointInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### SocialService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### SolidModelContentProvider

Parent class: `CacheableContentProvider`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### Sound

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### SoundGroup

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### SoundService

Parent class: `Instance`; creation: not directly creatable.

Only base Instance properties and separately declared members/getters.

### Sparkles

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### SpawnLocation

Parent class: `Part`; creation: permitted by current runtime (native rules incomplete).

| Property | Current type/default |
| --- | --- |
| `Anchored` | `boolean = false` |
| `AssemblyAngularVelocity` | `Vector3 = 0, 0, 0` |
| `AssemblyLinearVelocity` | `Vector3 = 0, 0, 0` |
| `BackSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `BottomSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `CFrame` | `CFrame = 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1` |
| `CanCollide` | `boolean = true` |
| `CanQuery` | `boolean = true` |
| `CanTouch` | `boolean = true` |
| `CastShadow` | `boolean = true` |
| `CollisionGroup` | `string = Default` |
| `Color` | `Color3 = 0.6392156862745098, 0.6352941176470588, 0.6470588235294118` |
| `CustomPhysicalProperties` | `PhysicalProperties? = nil` |
| `FrontSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `LeftSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `Locked` | `boolean = false` |
| `Massless` | `boolean = false` |
| `Material` | `Enum.Material = Enum.Material.Plastic` |
| `MaterialVariant` | `string = ` |
| `PivotOffset` | `CFrame = 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1` |
| `Reflectance` | `number = 0` |
| `RightSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `RootPriority` | `number = 0` |
| `RotVelocity` | `Vector3 = 0, 0, 0` |
| `Size` | `Vector3 = 4, 1.2, 2` |
| `TopSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `Transparency` | `number = 0` |
| `Velocity` | `Vector3 = 0, 0, 0` |

### SpawnerService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### SpecialMesh

Parent class: `FileMesh`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### SpecialShape

Parent class: `FileMesh`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### SphereHandleAdornment

Parent class: `HandleAdornment`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### SpotLight

Parent class: `Light`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### SpringConstraint

Parent class: `Constraint`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### StandalonePluginScripts

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### StandardPages

Parent class: `Pages`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### StarterCharacterScripts

Parent class: `StarterPlayerScripts`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### StarterGear

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### StarterGui

Parent class: `BasePlayerGui`; creation: not directly creatable.

Only base Instance properties and separately declared members/getters.

### StarterGuiService

Parent class: `BasePlayerGui`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### StarterPack

Parent class: `Instance`; creation: not directly creatable.

Only base Instance properties and separately declared members/getters.

### StarterPackService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### StarterPlayer

Parent class: `Instance`; creation: not directly creatable.

Only base Instance properties and separately declared members/getters.

### StarterPlayerScripts

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### StarterPlayerService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### StartupMessageService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### Stats

Parent class: ``; creation: not directly creatable.

Only base Instance properties and separately declared members/getters.

### StatsItem

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### Status

Parent class: `Model`; creation: permitted by current runtime (native rules incomplete).

| Property | Current type/default |
| --- | --- |
| `PrimaryPart` | `Instance? = nil` |
| `WorldPivot` | `CFrame = 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1` |

### StatusInstance

Parent class: `Model`; creation: permitted by current runtime (native rules incomplete).

| Property | Current type/default |
| --- | --- |
| `PrimaryPart` | `Instance? = nil` |
| `WorldPivot` | `CFrame = 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1` |

### StockSound

Parent class: ``; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### StopWatchReporter

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### StringValue

Parent class: `ValueBase`; creation: permitted by current runtime (native rules incomplete).

| Property | Current type/default |
| --- | --- |
| `Value` | `string = ` |

### Studio

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### StudioCameraService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### StudioCaptureService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### StudioData

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### StudioDeviceEmulatorService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### StudioDeviceSimulatorService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### StudioPublishService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### StudioScreenshotCapture

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### StudioService

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### StyleBase

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### StyleDerive

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### StyleLink

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### StyleQuery

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### StyleRule

Parent class: `StyleBase`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### StyleSheet

Parent class: `StyleBase`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### SunRaysEffect

Parent class: `PostEffect`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### SurfaceAppearance

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### SurfaceGui

Parent class: `SurfaceGuiBase`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### SurfaceGuiBase

Parent class: `GuiLayerCollector`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### SurfaceLight

Parent class: `Light`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### SurfaceSelection

Parent class: `PartAdornment`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### SwimController

Parent class: `ControllerBase`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### SystemThemeService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### TaskScheduler

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### Team

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### TeamCreateData

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### TeamCreatePublishService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### Teams

Parent class: `ServiceInstance`; creation: not directly creatable.

Only base Instance properties and separately declared members/getters.

### TelemetryService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### TeleportAsyncResult

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### TeleportOptions

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### TeleportService

Parent class: `ServiceInstance`; creation: not directly creatable.

Only base Instance properties and separately declared members/getters.

### TemporaryCageMeshProvider

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### TemporaryScriptService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### Terrain

Parent class: `BasePart`; creation: permitted by current runtime (native rules incomplete).

| Property | Current type/default |
| --- | --- |
| `Anchored` | `boolean = false` |
| `AssemblyAngularVelocity` | `Vector3 = 0, 0, 0` |
| `AssemblyLinearVelocity` | `Vector3 = 0, 0, 0` |
| `BackSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `BottomSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `CFrame` | `CFrame = 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1` |
| `CanCollide` | `boolean = true` |
| `CanQuery` | `boolean = true` |
| `CanTouch` | `boolean = true` |
| `CastShadow` | `boolean = true` |
| `CollisionGroup` | `string = Default` |
| `Color` | `Color3 = 0.6392156862745098, 0.6352941176470588, 0.6470588235294118` |
| `CustomPhysicalProperties` | `PhysicalProperties? = nil` |
| `FrontSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `LeftSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `Locked` | `boolean = false` |
| `Massless` | `boolean = false` |
| `Material` | `Enum.Material = Enum.Material.Plastic` |
| `MaterialVariant` | `string = ` |
| `PivotOffset` | `CFrame = 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1` |
| `Reflectance` | `number = 0` |
| `RightSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `RootPriority` | `number = 0` |
| `RotVelocity` | `Vector3 = 0, 0, 0` |
| `Size` | `Vector3 = 4, 1.2, 2` |
| `TopSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `Transparency` | `number = 0` |
| `Velocity` | `Vector3 = 0, 0, 0` |

### TerrainDetail

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### TerrainIterateOperation

Parent class: `Object`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### TerrainModifyOperation

Parent class: `Object`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### TerrainReadOperation

Parent class: `Object`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### TerrainRegion

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### TerrainWriteOperation

Parent class: `Object`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### TestCase

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### TestService

Parent class: `ServiceInstance`; creation: not directly creatable.

Only base Instance properties and separately declared members/getters.

### TextBox

Parent class: `GuiObject`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### TextBoxService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### TextButton

Parent class: `GuiButton`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### TextChannel

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### TextChannelWindow

Parent class: `GuiObject`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### TextChatCommand

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### TextChatConfigurations

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### TextChatMessage

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### TextChatMessagePropertiesClass

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### TextChatService

Parent class: `ServiceInstance`; creation: not directly creatable.

Only base Instance properties and separately declared members/getters.

### TextFilterResultInstance

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### TextFilterTranslatedResultInstance

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### TextGenerator

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### TextLabel

Parent class: `GuiLabel`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### TextService

Parent class: `ServiceInstance`; creation: not directly creatable.

Only base Instance properties and separately declared members/getters.

### TextSource

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### Texture

Parent class: `Decal`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### ThirdPartyUserService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### TimerService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### Tool

Parent class: `BackpackItem`; creation: permitted by current runtime (native rules incomplete).

| Property | Current type/default |
| --- | --- |
| `PrimaryPart` | `Instance? = nil` |
| `WorldPivot` | `CFrame = 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1` |

### Torque

Parent class: `Constraint`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### TorsionSpringConstraint

Parent class: `Constraint`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### TouchInputService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### TouchTransmitter

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### TraceRouteService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### TracerService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### TrackerLodController

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### TrackerStreamAnimation

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### Trail

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### TranslatorInstance

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### TremoloSoundEffect

Parent class: ``; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### TriangleMeshPart

Parent class: `BasePart`; creation: permitted by current runtime (native rules incomplete).

| Property | Current type/default |
| --- | --- |
| `Anchored` | `boolean = false` |
| `AssemblyAngularVelocity` | `Vector3 = 0, 0, 0` |
| `AssemblyLinearVelocity` | `Vector3 = 0, 0, 0` |
| `BackSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `BottomSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `CFrame` | `CFrame = 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1` |
| `CanCollide` | `boolean = true` |
| `CanQuery` | `boolean = true` |
| `CanTouch` | `boolean = true` |
| `CastShadow` | `boolean = true` |
| `CollisionGroup` | `string = Default` |
| `Color` | `Color3 = 0.6392156862745098, 0.6352941176470588, 0.6470588235294118` |
| `CustomPhysicalProperties` | `PhysicalProperties? = nil` |
| `FrontSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `LeftSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `Locked` | `boolean = false` |
| `Massless` | `boolean = false` |
| `Material` | `Enum.Material = Enum.Material.Plastic` |
| `MaterialVariant` | `string = ` |
| `PivotOffset` | `CFrame = 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1` |
| `Reflectance` | `number = 0` |
| `RightSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `RootPriority` | `number = 0` |
| `RotVelocity` | `Vector3 = 0, 0, 0` |
| `Size` | `Vector3 = 4, 1.2, 2` |
| `TopSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `Transparency` | `number = 0` |
| `Velocity` | `Vector3 = 0, 0, 0` |

### TrussPart

Parent class: `BasePart`; creation: permitted by current runtime (native rules incomplete).

| Property | Current type/default |
| --- | --- |
| `Anchored` | `boolean = false` |
| `AssemblyAngularVelocity` | `Vector3 = 0, 0, 0` |
| `AssemblyLinearVelocity` | `Vector3 = 0, 0, 0` |
| `BackSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `BottomSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `CFrame` | `CFrame = 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1` |
| `CanCollide` | `boolean = true` |
| `CanQuery` | `boolean = true` |
| `CanTouch` | `boolean = true` |
| `CastShadow` | `boolean = true` |
| `CollisionGroup` | `string = Default` |
| `Color` | `Color3 = 0.6392156862745098, 0.6352941176470588, 0.6470588235294118` |
| `CustomPhysicalProperties` | `PhysicalProperties? = nil` |
| `FrontSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `LeftSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `Locked` | `boolean = false` |
| `Massless` | `boolean = false` |
| `Material` | `Enum.Material = Enum.Material.Plastic` |
| `MaterialVariant` | `string = ` |
| `PivotOffset` | `CFrame = 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1` |
| `Reflectance` | `number = 0` |
| `RightSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `RootPriority` | `number = 0` |
| `RotVelocity` | `Vector3 = 0, 0, 0` |
| `Size` | `Vector3 = 4, 1.2, 2` |
| `TopSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `Transparency` | `number = 0` |
| `Velocity` | `Vector3 = 0, 0, 0` |

### Tween

Parent class: `TweenBase`; creation: not directly creatable.

Only base Instance properties and separately declared members/getters.

### TweenBase

Parent class: `Instance`; creation: not directly creatable.

Only base Instance properties and separately declared members/getters.

### TweenService

Parent class: `ServiceInstance`; creation: not directly creatable.

Only base Instance properties and separately declared members/getters.

### UGCAvatarService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### UGCValidationService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### UIAspectRatioConstraint

Parent class: `UIConstraint`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### UIBase

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### UIComponent

Parent class: `UIBase`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### UIConstraint

Parent class: `UIComponent`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### UICorner

Parent class: `UIComponent`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### UIDragDetector

Parent class: `UIComponent`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### UIDragDetectorService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### UIFlexItem

Parent class: `UIComponent`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### UIGradient

Parent class: `UIComponent`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### UIGridLayout

Parent class: `UIGridStyleLayout`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### UIGridStyleLayout

Parent class: `UILayout`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### UILayout

Parent class: `UIComponent`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### UIListLayout

Parent class: `UIGridStyleLayout`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### UIPadding

Parent class: `UIComponent`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### UIPageLayout

Parent class: `UIGridStyleLayout`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### UIScale

Parent class: `UIComponent`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### UIShadow

Parent class: `UIComponent`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### UISizeConstraint

Parent class: `UIConstraint`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### UIStroke

Parent class: `UIComponent`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### UITableLayout

Parent class: `UIGridStyleLayout`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### UITextSizeConstraint

Parent class: `UIConstraint`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### UnionOperation

Parent class: `PartOperation`; creation: permitted by current runtime (native rules incomplete).

| Property | Current type/default |
| --- | --- |
| `Anchored` | `boolean = false` |
| `AssemblyAngularVelocity` | `Vector3 = 0, 0, 0` |
| `AssemblyLinearVelocity` | `Vector3 = 0, 0, 0` |
| `BackSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `BottomSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `CFrame` | `CFrame = 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1` |
| `CanCollide` | `boolean = true` |
| `CanQuery` | `boolean = true` |
| `CanTouch` | `boolean = true` |
| `CastShadow` | `boolean = true` |
| `CollisionGroup` | `string = Default` |
| `Color` | `Color3 = 0.6392156862745098, 0.6352941176470588, 0.6470588235294118` |
| `CustomPhysicalProperties` | `PhysicalProperties? = nil` |
| `FrontSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `LeftSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `Locked` | `boolean = false` |
| `Massless` | `boolean = false` |
| `Material` | `Enum.Material = Enum.Material.Plastic` |
| `MaterialVariant` | `string = ` |
| `PivotOffset` | `CFrame = 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1` |
| `Reflectance` | `number = 0` |
| `RightSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `RootPriority` | `number = 0` |
| `RotVelocity` | `Vector3 = 0, 0, 0` |
| `Size` | `Vector3 = 4, 1.2, 2` |
| `TopSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `Transparency` | `number = 0` |
| `Velocity` | `Vector3 = 0, 0, 0` |

### UniqueIdLookupService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### UniversalConstraint

Parent class: `Constraint`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### UnreliableRemoteEvent

Parent class: `BaseRemoteEvent`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### UnvalidatedAssetService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### UserInputService

Parent class: `ServiceInstance`; creation: not directly creatable.

Only base Instance properties and separately declared members/getters.

### UserService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### UserStorageService

Parent class: `LocalStorageService`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### VRService

Parent class: `ServiceInstance`; creation: not directly creatable.

Only base Instance properties and separately declared members/getters.

### ValueBase

Parent class: `Instance`; creation: not directly creatable.

Only base Instance properties and separately declared members/getters.

### ValueCurve

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### Vector3Curve

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### Vector3Value

Parent class: `ValueBase`; creation: permitted by current runtime (native rules incomplete).

| Property | Current type/default |
| --- | --- |
| `Value` | `Vector3 = 0, 0, 0` |

### VectorForce

Parent class: `Constraint`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### VehicleController

Parent class: `Controller`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### VehicleSeat

Parent class: `BasePart`; creation: permitted by current runtime (native rules incomplete).

| Property | Current type/default |
| --- | --- |
| `Anchored` | `boolean = false` |
| `AssemblyAngularVelocity` | `Vector3 = 0, 0, 0` |
| `AssemblyLinearVelocity` | `Vector3 = 0, 0, 0` |
| `BackSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `BottomSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `CFrame` | `CFrame = 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1` |
| `CanCollide` | `boolean = true` |
| `CanQuery` | `boolean = true` |
| `CanTouch` | `boolean = true` |
| `CastShadow` | `boolean = true` |
| `CollisionGroup` | `string = Default` |
| `Color` | `Color3 = 0.6392156862745098, 0.6352941176470588, 0.6470588235294118` |
| `CustomPhysicalProperties` | `PhysicalProperties? = nil` |
| `FrontSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `LeftSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `Locked` | `boolean = false` |
| `Massless` | `boolean = false` |
| `Material` | `Enum.Material = Enum.Material.Plastic` |
| `MaterialVariant` | `string = ` |
| `PivotOffset` | `CFrame = 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1` |
| `Reflectance` | `number = 0` |
| `RightSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `RootPriority` | `number = 0` |
| `RotVelocity` | `Vector3 = 0, 0, 0` |
| `Size` | `Vector3 = 4, 1.2, 2` |
| `TopSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `Transparency` | `number = 0` |
| `Velocity` | `Vector3 = 0, 0, 0` |

### VelocityMotor

Parent class: `JointInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### VersionControlService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### VideoCapture

Parent class: `Capture`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### VideoCaptureService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### VideoDisplay

Parent class: `GuiObject`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### VideoFrame

Parent class: `GuiObject`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### VideoPlayer

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### VideoSampler

Parent class: `Object`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### VideoScreenCaptureService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### VideoService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### ViewportCamera

Parent class: `Camera`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### ViewportFrame

Parent class: `GuiObject`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### VirtualInput

Parent class: `Object`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### VirtualInputManager

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### VirtualUser

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### Visit

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### VisualizationMode

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### VisualizationModeCategory

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### VisualizationModeService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### VoiceChatInternal

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### VoiceChatService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### VoxelBuffer

Parent class: `Object`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### WebSocketClient

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### WebSocketService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### WebStreamClient

Parent class: `Object`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### WebViewService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### WedgePart

Parent class: `FormFactorPart`; creation: permitted by current runtime (native rules incomplete).

| Property | Current type/default |
| --- | --- |
| `Anchored` | `boolean = false` |
| `AssemblyAngularVelocity` | `Vector3 = 0, 0, 0` |
| `AssemblyLinearVelocity` | `Vector3 = 0, 0, 0` |
| `BackSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `BottomSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `CFrame` | `CFrame = 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1` |
| `CanCollide` | `boolean = true` |
| `CanQuery` | `boolean = true` |
| `CanTouch` | `boolean = true` |
| `CastShadow` | `boolean = true` |
| `CollisionGroup` | `string = Default` |
| `Color` | `Color3 = 0.6392156862745098, 0.6352941176470588, 0.6470588235294118` |
| `CustomPhysicalProperties` | `PhysicalProperties? = nil` |
| `FrontSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `LeftSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `Locked` | `boolean = false` |
| `Massless` | `boolean = false` |
| `Material` | `Enum.Material = Enum.Material.Plastic` |
| `MaterialVariant` | `string = ` |
| `PivotOffset` | `CFrame = 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1` |
| `Reflectance` | `number = 0` |
| `RightSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `RootPriority` | `number = 0` |
| `RotVelocity` | `Vector3 = 0, 0, 0` |
| `Size` | `Vector3 = 4, 1.2, 2` |
| `TopSurface` | `Enum.SurfaceType = Enum.SurfaceType.Smooth` |
| `Transparency` | `number = 0` |
| `Velocity` | `Vector3 = 0, 0, 0` |

### Weld

Parent class: `JointInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### WeldConstraint

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### WindowProtocolService

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### Wire

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### WireframeHandleAdornment

Parent class: `HandleAdornment`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### Workspace

Parent class: `WorldRoot`; creation: not directly creatable.

| Property | Current type/default |
| --- | --- |
| `CurrentCamera` | `Instance? = nil` |
| `FallenPartsDestroyHeight` | `number = -500` |
| `Gravity` | `number = 196.2` |
| `PrimaryPart` | `Instance? = nil` |
| `StreamingEnabled` | `boolean = false` |
| `WorldPivot` | `CFrame = 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1` |

### WorkspaceAnnotation

Parent class: `Annotation`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### WorldModel

Parent class: `WorldRoot`; creation: permitted by current runtime (native rules incomplete).

| Property | Current type/default |
| --- | --- |
| `PrimaryPart` | `Instance? = nil` |
| `WorldPivot` | `CFrame = 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1` |

### WorldRoot

Parent class: `Model`; creation: not directly creatable.

| Property | Current type/default |
| --- | --- |
| `PrimaryPart` | `Instance? = nil` |
| `WorldPivot` | `CFrame = 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1` |

### WrapDeformMeshProvider

Parent class: `ServiceInstance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### WrapDeformer

Parent class: `BaseWrap`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### WrapLayer

Parent class: `BaseWrap`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### WrapTarget

Parent class: `BaseWrap`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

### WrapTextureTransfer

Parent class: `Instance`; creation: permitted by current runtime (native rules incomplete).

Only base Instance properties and separately declared members/getters.

## Enum catalog: names and values

620 types and 3585 items from the target build. Enum presence does not implement the related engine behavior.

### Enum.AccessModifierType

`Allow=0`, `Deny=1`.

### Enum.AccessoryType

`Unknown=0`, `Hat=1`, `Hair=2`, `Face=3`, `Neck=4`, `Shoulder=5`, `Front=6`, `Back=7`, `Waist=8`, `TShirt=9`, `Shirt=10`, `Pants=11`, `Jacket=12`, `Sweater=13`, `Shorts=14`, `LeftShoe=15`, `RightShoe=16`, `DressSkirt=17`, `Eyebrow=18`, `Eyelash=19`.

### Enum.ActionOnAutoResumeSync

`DontResume=0`, `KeepStudio=1`, `KeepLocal=2`.

### Enum.ActionOnStopSync

`AlwaysAsk=0`, `KeepLocalFiles=1`, `DeleteLocalFiles=2`.

### Enum.ActionType

`Nothing=0`, `Pause=1`, `Lose=2`, `Draw=3`, `Win=4`.

### Enum.ActivePayerStatus

`Unknown=0`, `Never=1`, `Lapsed=2`, `Casual50Percent=3`, `Intermediate35Percent=4`, `Top15Percent=5`.

### Enum.ActuatorRelativeTo

`Attachment0=0`, `Attachment1=1`, `World=2`.

### Enum.ActuatorType

`None=0`, `Motor=1`, `Servo=2`.

### Enum.AdAvailabilityResult

`IsAvailable=1`, `DeviceIneligible=2`, `ExperienceIneligible=3`, `InternalError=4`, `NoFill=5`, `PlayerIneligible=6`, `PublisherIneligible=7`.

### Enum.AdEventType

`VideoLoaded=0`, `VideoRemoved=1`, `UserCompletedVideo=2`, `RewardedAdLoaded=3`, `RewardedAdGrant=4`, `RewardedAdUnloaded=5`.

### Enum.AdFormat

`RewardedVideo=0`.

### Enum.AdShape

`HorizontalRectangle=1`.

### Enum.AdTeleportMethod

`Undefined=0`, `PortalForward=1`, `InGameMenuBackButton=2`, `UIBackButton=3`.

### Enum.AdUIEventType

`AdLabelClicked=0`, `VolumeButtonClicked=1`, `FullscreenButtonClicked=2`, `PlayButtonClicked=3`, `PauseButtonClicked=4`, `CloseButtonClicked=5`, `WhyThisAdClicked=6`, `PlayEventTriggered=7`, `PauseEventTriggered=8`.

### Enum.AdUIType

`None=0`, `Image=1`, `Video=2`.

### Enum.AdUnitStatus

`Inactive=0`, `Active=1`.

### Enum.AdornCullingMode

`Automatic=0`, `Never=1`.

### Enum.AdornShading

`Default=0`, `Shaded=1`, `XRay=2`, `XRayShaded=3`, `AlwaysOnTop=4`.

### Enum.AgeCheckStatus

`Unchecked=0`, `Checked=1`.

### Enum.AlignType

`Parallel=0`, `Perpendicular=1`, `PrimaryAxisParallel=2`, `PrimaryAxisPerpendicular=3`, `PrimaryAxisLookAt=4`, `AllAxes=5`.

### Enum.AlphaMode

`Overlay=0`, `Transparency=1`, `TintMask=2`, `Opaque=3`.

### Enum.AnalyticsCustomFieldKeys

`CustomField01=0`, `CustomField02=1`, `CustomField03=2`.

### Enum.AnalyticsEconomyAction

`Default=0`, `Acquire=1`, `Spend=2`.

### Enum.AnalyticsEconomyFlowType

`Sink=0`, `Source=1`.

### Enum.AnalyticsEconomyTransactionType

`IAP=0`, `Shop=1`, `Gameplay=2`, `ContextualPurchase=3`, `TimedReward=4`, `Onboarding=5`.

### Enum.AnalyticsLogLevel

`Trace=0`, `Debug=1`, `Information=2`, `Warning=3`, `Error=4`, `Fatal=5`.

### Enum.AnalyticsProgressionStatus

`Default=0`, `Begin=1`, `Complete=2`, `Abandon=3`, `Fail=4`.

### Enum.AnalyticsProgressionType

`Custom=0`, `Start=1`, `Fail=2`, `Complete=3`.

### Enum.AnimationClipFromVideoStatus

`Initializing=0`, `Pending=1`, `Processing=2`, `ErrorGeneric=4`, `Success=6`, `ErrorVideoTooLong=7`, `ErrorNoPersonDetected=8`, `ErrorVideoUnstable=9`, `Timeout=10`, `Cancelled=11`, `ErrorMultiplePeople=12`, `ErrorUploadingVideo=2001`.

### Enum.AnimationNodeBlend2DInputMode

`Cartesian=0`, `Polar=1`.

### Enum.AnimationNodeInterruptible

`Always=0`, `Finished=1`, `Trigger=2`.

### Enum.AnimationNodePhaseSync

`Synced=0`, `Unsynced=1`.

### Enum.AnimationNodePlayMode

`Loop=0`, `PingPong=1`, `OnceAndHold=2`, `OnceAndReset=3`.

### Enum.AnimationNodeTransitionType

`CrossFade=0`, `InertialBlend=1`, `DeadBlend=2`.

### Enum.AnimationNodeType

`InvalidNode=0`, `AddNode=1`, `OverNode=2`, `Blend1DNode=3`, `Blend2DNode=4`, `ClipNode=5`, `GraphOutput=6`, `MaskNode=7`, `PrioritySelectNode=8`, `RandomSequenceNode=9`, `SelectNode=10`, `SequenceNode=11`, `SpeedNode=12`, `SubtractNode=13`.

### Enum.AnimationNodeWaitFor

`Finished=0`, `Trigger=1`.

### Enum.AnimationPriority

`Idle=0`, `Movement=1`, `Action=2`, `Action2=3`, `Action3=4`, `Action4=5`, `Core=1000`.

### Enum.AnimatorRetargetingMode

`Default=0`, `Disabled=1`, `Enabled=2`.

### Enum.AnnotationChannelContentPreference

`None=0`, `All=1`, `Unknown=2`.

### Enum.AnnotationEditingMode

`None=0`, `PlacingNew=1`, `WritingNew=2`.

### Enum.AnnotationPlaceContentPreference

`None=0`, `All=1`, `MentionsAndReplies=2`, `Unknown=3`.

### Enum.AnnotationRequestStatus

`Success=0`, `Loading=1`, `ErrorInternalFailure=2`, `ErrorNotFound=3`, `ErrorModerated=4`.

### Enum.AnnotationRequestType

`Unknown=0`, `Create=1`, `Resolve=2`, `Delete=3`, `Edit=4`.

### Enum.AntiAliasing

`Disabled=0`, `Enabled=1`.

### Enum.AppLifecycleManagerState

`Detached=0`, `Active=1`, `Inactive=2`, `Hidden=3`.

### Enum.AppShellActionType

`None=0`, `OpenApp=1`, `TapChatTab=2`, `TapConversationEntry=3`, `TapAvatarTab=4`, `ReadConversation=5`, `TapGamePageTab=6`, `TapHomePageTab=7`, `GamePageLoaded=8`, `HomePageLoaded=9`, `AvatarEditorPageLoaded=10`, `HomePageInteractive=11`.

### Enum.AppShellFeature

`None=0`, `Chat=1`, `AvatarEditor=2`, `GamePage=3`, `HomePage=4`, `More=5`, `Landing=6`, `WatchPage=7`.

### Enum.AppUpdateStatus

`Unknown=0`, `NotSupported=1`, `Failed=2`, `NotAvailable=3`, `Available=4`, `AvailableBoundChannel=5`, `AvailableBetaProgram=6`.

### Enum.ApplyShadowMode

`Shape=0`, `Text=1`.

### Enum.ApplyStrokeMode

`Contextual=0`, `Border=1`.

### Enum.AspectType

`FitWithinMaxSize=0`, `ScaleWithParentSize=1`.

### Enum.AssetCreatorType

`User=0`, `Group=1`.

### Enum.AssetFetchStatus

`Success=0`, `Failure=1`, `None=2`, `Loading=3`, `TimedOut=4`.

### Enum.AssetRepresentation

`FullLength=0`, `ShortPreview=1`.

### Enum.AssetType

`Image=1`, `TShirt=2`, `Audio=3`, `Mesh=4`, `Lua=5`, `Hat=8`, `Place=9`, `Model=10`, `Shirt=11`, `Pants=12`, `Decal=13`, `Head=17`, `Face=18`, `Gear=19`, `Badge=21`, `Animation=24`, `Torso=27`, `RightArm=28`, `LeftArm=29`, `LeftLeg=30`, `RightLeg=31`, `Package=32`, `GamePass=34`, `Plugin=38`, `MeshPart=40`, `HairAccessory=41`, `FaceAccessory=42`, `NeckAccessory=43`, `ShoulderAccessory=44`, `FrontAccessory=45`, `BackAccessory=46`, `WaistAccessory=47`, `ClimbAnimation=48`, `DeathAnimation=49`, `FallAnimation=50`, `IdleAnimation=51`, `JumpAnimation=52`, `RunAnimation=53`, `SwimAnimation=54`, `WalkAnimation=55`, `PoseAnimation=56`, `EarAccessory=57`, `EyeAccessory=58`, `EmoteAnimation=61`, `Video=62`, `TShirtAccessory=64`, `ShirtAccessory=65`, `PantsAccessory=66`, `JacketAccessory=67`, `SweaterAccessory=68`, `ShortsAccessory=69`, `LeftShoeAccessory=70`, `RightShoeAccessory=71`, `DressSkirtAccessory=72`, `FontFamily=73`, `EyebrowAccessory=76`, `EyelashAccessory=77`, `MoodAnimation=78`, `DynamicHead=79`, `FaceMakeup=88`, `LipMakeup=89`, `EyeMakeup=90`, `AvatarBackground=92`, `TextDocument=93`.

### Enum.AssetTypeVerification

`Default=1`, `ClientOnly=2`, `Always=3`.

### Enum.AudioApiRollout

`Disabled=0`, `Automatic=1`, `Enabled=2`.

### Enum.AudioChannelLayout

`Mono=0`, `Stereo=1`, `Quad=2`, `Surround_5=3`, `Surround_5_1=4`, `Surround_7_1=5`, `Surround_7_1_4=6`.

### Enum.AudioFilterType

`Peak=0`, `LowShelf=1`, `HighShelf=2`, `Lowpass12dB=3`, `Lowpass24dB=4`, `Lowpass48dB=5`, `Highpass12dB=6`, `Highpass24dB=7`, `Highpass48dB=8`, `Bandpass=9`, `Notch=10`, `Lowpass6dB=11`.

### Enum.AudioPositionType

`Parent=0`, `Instance=1`.

### Enum.AudioSimulationFidelity

`None=0`, `Automatic=1`.

### Enum.AudioSubType

`Music=1`, `SoundEffect=2`.

### Enum.AudioWindowSize

`Small=0`, `Medium=1`, `Large=2`.

### Enum.AuthorityMode

`Server=0`, `Automatic=1`.

### Enum.AutoIndentRule

`Off=0`, `Absolute=1`, `Relative=2`.

### Enum.AutomaticSize

`None=0`, `X=1`, `Y=2`, `XY=3`.

### Enum.AvatarAssetType

`TShirt=2`, `Hat=8`, `Shirt=11`, `Pants=12`, `Head=17`, `Face=18`, `Gear=19`, `Torso=27`, `RightArm=28`, `LeftArm=29`, `LeftLeg=30`, `RightLeg=31`, `HairAccessory=41`, `FaceAccessory=42`, `NeckAccessory=43`, `ShoulderAccessory=44`, `FrontAccessory=45`, `BackAccessory=46`, `WaistAccessory=47`, `ClimbAnimation=48`, `FallAnimation=50`, `IdleAnimation=51`, `JumpAnimation=52`, `RunAnimation=53`, `SwimAnimation=54`, `WalkAnimation=55`, `EmoteAnimation=61`, `TShirtAccessory=64`, `ShirtAccessory=65`, `PantsAccessory=66`, `JacketAccessory=67`, `SweaterAccessory=68`, `ShortsAccessory=69`, `LeftShoeAccessory=70`, `RightShoeAccessory=71`, `DressSkirtAccessory=72`, `EyebrowAccessory=76`, `EyelashAccessory=77`, `MoodAnimation=78`, `DynamicHead=79`, `FaceMakeup=88`, `LipMakeup=89`, `EyeMakeup=90`, `AvatarBackground=92`.

### Enum.AvatarChatServiceFeature

`None=0`, `UniverseAudio=1`, `UniverseVideo=2`, `PlaceAudio=4`, `PlaceVideo=8`, `UserAudioEligible=16`, `UserAudio=32`, `UserVideoEligible=64`, `UserVideo=128`, `UserBanned=256`, `UserVerifiedForVoice=512`.

### Enum.AvatarContextMenuOption

`Friend=0`, `Chat=1`, `Emote=2`, `InspectMenu=3`.

### Enum.AvatarGenerationError

`None=0`, `Unknown=1`, `DownloadFailed=2`, `Canceled=3`, `Offensive=4`, `Timeout=5`, `JobNotFound=6`.

### Enum.AvatarItemType

`Asset=1`, `Bundle=2`.

### Enum.AvatarPromptResult

`Success=1`, `PermissionDenied=2`, `Failed=3`.

### Enum.AvatarSettingsAccessoryLimitMethod

`Scale=0`, `Remove=1`, `PreviewScale=2`, `PreviewRemove=3`.

### Enum.AvatarSettingsAccessoryMode

`PlayerChoice=0`, `CustomLimit=1`.

### Enum.AvatarSettingsAnimationClipsMode

`PlayerChoice=0`, `CustomClips=1`.

### Enum.AvatarSettingsAnimationPacksMode

`PlayerChoice=0`, `StandardR15=1`, `StandardR6=2`.

### Enum.AvatarSettingsAppearanceMode

`PlayerChoice=0`, `CustomParts=1`, `CustomBody=2`.

### Enum.AvatarSettingsBuildMode

`PlayerChoice=0`, `CustomBuild=1`.

### Enum.AvatarSettingsCharacterControllerMode

`LegacyHumanoid=0`, `LuaCharacterController=1`.

### Enum.AvatarSettingsClothingMode

`PlayerChoice=0`, `CustomLimit=1`.

### Enum.AvatarSettingsCollisionMode

`Default=0`, `SingleCollider=1`, `Legacy=2`.

### Enum.AvatarSettingsCustomAccessoryMode

`PlayerChoice=0`, `CustomAccessories=1`.

### Enum.AvatarSettingsCustomBodyType

`AvatarReference=0`, `BundleId=1`.

### Enum.AvatarSettingsCustomClothingMode

`PlayerChoice=0`, `CustomClothing=1`.

### Enum.AvatarSettingsHitAndTouchDetectionMode

`UseParts=0`, `UseCollider=1`.

### Enum.AvatarSettingsJumpMode

`JumpHeight=0`, `JumpPower=1`.

### Enum.AvatarSettingsLegacyCollisionMode

`R6Colliders=0`, `InnerBoxColliders=1`.

### Enum.AvatarSettingsScaleMode

`PlayerChoice=0`, `CustomScale=1`.

### Enum.AvatarThumbnailCustomizationType

`Closeup=1`, `FullBody=2`.

### Enum.AvatarUnificationMode

`Default=0`, `Disabled=1`, `Enabled=2`.

### Enum.Axis

`X=0`, `Y=1`, `Z=2`.

### Enum.BenefitType

`DeveloperProduct=0`, `AvatarAsset=1`, `AvatarBundle=2`.

### Enum.BinType

`Script=0`, `GameTool=1`, `Grab=2`, `Clone=3`, `Hammer=4`.

### Enum.BodyPart

`Head=0`, `Torso=1`, `LeftArm=2`, `RightArm=3`, `LeftLeg=4`, `RightLeg=5`.

### Enum.BodyPartR15

`Head=0`, `UpperTorso=1`, `LowerTorso=2`, `LeftFoot=3`, `LeftLowerLeg=4`, `LeftUpperLeg=5`, `RightFoot=6`, `RightLowerLeg=7`, `RightUpperLeg=8`, `LeftHand=9`, `LeftLowerArm=10`, `LeftUpperArm=11`, `RightHand=12`, `RightLowerArm=13`, `RightUpperArm=14`, `RootPart=15`, `Unknown=17`.

### Enum.BorderMode

`Outline=0`, `Middle=1`, `Inset=2`.

### Enum.BorderStrokePosition

`Outer=0`, `Center=1`, `Inner=2`.

### Enum.BreakReason

`Other=0`, `Error=1`, `SpecialBreakpoint=2`, `UserBreakpoint=3`.

### Enum.BreakpointRemoveReason

`Requested=0`, `ScriptChanged=1`, `ScriptRemoved=2`.

### Enum.BulkMoveMode

`FireAllEvents=0`, `FireCFrameChanged=1`.

### Enum.BundleType

`BodyParts=1`, `Animations=2`, `Shoes=3`, `DynamicHead=4`, `DynamicHeadAvatar=5`.

### Enum.Button

`Dismount=8`, `Jump=32`.

### Enum.ButtonStyle

`Custom=0`, `RobloxButtonDefault=1`, `RobloxButton=2`, `RobloxRoundButton=3`, `RobloxRoundDefaultButton=4`, `RobloxRoundDropdownButton=5`.

### Enum.CageType

`Inner=0`, `Outer=1`.

### Enum.CameraMode

`Classic=0`, `LockFirstPerson=1`.

### Enum.CameraNavigationModel

`Roblox=0`, `IndustryCompatible=1`.

### Enum.CameraPanMode

`Classic=0`, `EdgeBump=1`.

### Enum.CameraSpeedAdjustBinding

`None=0`, `RmbScroll=1`, `AltScroll=2`.

### Enum.CameraType

`Fixed=0`, `Attach=1`, `Watch=2`, `Track=3`, `Follow=4`, `Custom=5`, `Scriptable=6`, `Orbital=7`.

### Enum.CanCollaborateError

`Invalid=0`, `None=1`, `NotAgeVerified=2`, `OutsideAgeBucket=3`, `TooManyCollaborators=4`, `PCBlock=5`, `NotFound=6`, `OutsideOwnerAgeBucket=7`, `NotAuthorized=8`, `OutsideAgeBucketTcPc=9`, `OtherCollaboratorSettingsPreventTrust=10`, `AgeVerificationCountryBlocked=11`, `OtherUserCannotCollaborate=12`.

### Enum.CaptureGalleryPermission

`ReadAndUpload=0`.

### Enum.CaptureType

`Screenshot=1`, `Video=2`.

### Enum.CatalogCategoryFilter

`None=1`, `Featured=2`, `Collectibles=3`, `CommunityCreations=4`, `Premium=5`, `Recommended=6`.

### Enum.CatalogSortAggregation

`Past12Hours=1`, `PastDay=2`, `Past3Days=3`, `PastWeek=4`, `PastMonth=5`, `AllTime=6`.

### Enum.CatalogSortType

`Relevance=1`, `PriceHighToLow=2`, `PriceLowToHigh=3`, `MostFavorited=5`, `RecentlyCreated=6`, `Bestselling=7`.

### Enum.CellBlock

`Solid=0`, `VerticalWedge=1`, `CornerWedge=2`, `InverseCornerWedge=3`, `HorizontalWedge=4`.

### Enum.CellMaterial

`Empty=0`, `Grass=1`, `Sand=2`, `Brick=3`, `Granite=4`, `Asphalt=5`, `Iron=6`, `Aluminum=7`, `Gold=8`, `WoodPlank=9`, `WoodLog=10`, `Gravel=11`, `CinderBlock=12`, `MossyStone=13`, `Cement=14`, `RedPlastic=15`, `BluePlastic=16`, `Water=17`.

### Enum.CellOrientation

`NegZ=0`, `X=1`, `Z=2`, `NegX=3`.

### Enum.CenterDialogType

`UnsolicitedDialog=1`, `PlayerInitiatedDialog=2`, `ModalDialog=3`, `QuitDialog=4`.

### Enum.CharacterControlMode

`Default=0`, `Legacy=1`, `NoCharacterController=2`, `LuaCharacterController=3`.

### Enum.ChatCallbackType

`OnCreatingChatWindow=1`, `OnClientSendingMessage=2`, `OnClientFormattingMessage=3`, `OnServerReceivingMessage=17`.

### Enum.ChatColor

`Blue=0`, `Green=1`, `Red=2`, `White=3`.

### Enum.ChatMode

`Menu=0`, `TextAndMenu=1`.

### Enum.ChatPrivacyMode

`AllUsers=0`, `NoOne=1`, `Friends=2`.

### Enum.ChatRestrictionStatus

`Unknown=0`, `NotRestricted=1`, `Restricted=2`.

### Enum.ChatStyle

`Classic=0`, `Bubble=1`, `ClassicAndBubble=2`.

### Enum.ChatVersion

`LegacyChatService=0`, `TextChatService=1`.

### Enum.ClientAnimatorThrottlingMode

`Default=0`, `Disabled=1`, `Enabled=2`.

### Enum.CloseReason

`Unknown=0`, `RobloxMaintenance=1`, `DeveloperShutdown=2`, `DeveloperUpdate=3`, `ServerEmpty=4`, `OutOfMemory=5`, `Moderation=6`.

### Enum.CollaboratorStatus

`None=0`, `Editing3D=1`, `Scripting=2`, `PrivateScripting=3`.

### Enum.CollisionFidelity

`Default=0`, `Hull=1`, `Box=2`, `PreciseConvexDecomposition=3`, `Scalable=4`.

### Enum.CommandPermission

`Plugin=0`, `LocalUser=1`.

### Enum.CompileTarget

`Client=0`, `CoreScript=1`, `Studio=2`, `CoreScriptRaw=3`.

### Enum.CompletionAcceptanceBehavior

`Insert=0`, `Replace=1`, `ReplaceOnEnterInsertOnTab=2`, `InsertOnEnterReplaceOnTab=3`.

### Enum.CompletionItemKind

`Text=1`, `Method=2`, `Function=3`, `Constructor=4`, `Field=5`, `Variable=6`, `Class=7`, `Interface=8`, `Module=9`, `Property=10`, `Unit=11`, `Value=12`, `Enum=13`, `Keyword=14`, `Snippet=15`, `Color=16`, `File=17`, `Reference=18`, `Folder=19`, `EnumMember=20`, `Constant=21`, `Struct=22`, `Event=23`, `Operator=24`, `TypeParameter=25`.

### Enum.CompletionItemTag

`Deprecated=1`, `IncorrectIndexType=2`, `PluginPermissions=3`, `CommandLinePermissions=4`, `RobloxPermissions=5`, `AddParens=6`, `PutCursorInParens=7`, `TypeCorrect=8`, `ClientServerBoundaryViolation=9`, `Invalidated=10`, `PutCursorBeforeEnd=11`.

### Enum.CompletionTriggerKind

`Invoked=1`, `TriggerCharacter=2`, `TriggerForIncompleteCompletions=3`.

### Enum.CompositeValueCurveType

`ColorRGB=0`, `ColorHSV=1`, `NumberRange=2`, `Rect=3`, `UDim=4`, `UDim2=5`, `Vector2=6`, `Vector3=7`.

### Enum.CompressionAlgorithm

`Zstd=0`.

### Enum.ComputerCameraMovementMode

`Default=0`, `Classic=1`, `Follow=2`, `Orbital=3`, `CameraToggle=4`.

### Enum.ComputerMovementMode

`Default=0`, `KeyboardMouse=1`, `ClickToMove=2`.

### Enum.ConfigSnapshotErrorState

`None=0`, `LoadFailed=1`.

### Enum.ConnectionError

`OK=0`, `Unknown=1`, `ConnectErrors=2`, `AlreadyConnected=3`, `NoFreeIncomingConnections=4`, `ConnectionBanned=5`, `InvalidPassword=6`, `IncompatibleProtocolVersion=7`, `IPRecentlyConnected=8`, `OurSystemRequiresSecurity=9`, `SecurityKeyMismatch=10`, `DisconnectErrors=256`, `DisconnectBadhash=257`, `DisconnectSecurityKeyMismatch=258`, `DisconnectProtocolMismatch=259`, `DisconnectReceivePacketError=260`, `DisconnectReceivePacketStreamError=261`, `DisconnectSendPacketError=262`, `DisconnectIllegalTeleport=263`, `DisconnectDuplicatePlayer=264`, `DisconnectDuplicateTicket=265`, `DisconnectTimeout=266`, `DisconnectLuaKick=267`, `DisconnectOnRemoteSysStats=268`, `DisconnectHashTimeout=269`, `DisconnectCloudEditKick=270`, `DisconnectPlayerless=271`, `DisconnectNewSecurityKeyMismatch=272`, `DisconnectEvicted=273`, `DisconnectDevMaintenance=274`, `DisconnectRobloxMaintenance=275`, `DisconnectRejoin=276`, `DisconnectConnectionLost=277`, `DisconnectIdle=278`, `DisconnectRaknetErrors=279`, `DisconnectWrongVersion=280`, `DisconnectBySecurityPolicy=281`, `DisconnectBlockedIP=282`, `DisconnectClientFailure=284`, `DisconnectClientRequest=285`, `DisconnectPrivateServerKickout=286`, `DisconnectModeratedGame=287`, `ServerShutdown=288`, `ReplicatorTimeout=290`, `PlayerRemoved=291`, `DisconnectOutOfMemoryKeepPlayingLeave=292`, `DisconnectRomarkEndOfTest=293`, `DisconnectCollaboratorPermissionRevoked=294`, `DisconnectCollaboratorUnderage=295`, `NetworkInternal=296`, `NetworkSend=297`, `NetworkTimeout=298`, `NetworkMisbehavior=299`, `NetworkSecurity=300`, `ReplacementReady=301`, `ServerEmpty=302`, `PhantomFreeze=303`, `AndroidAnticheatKick=304`, `AndroidEmulatorKick=305`, `AndroidRootedKick=306`, `ScreentimeLockoutKick=307`, `DisconnectionNotification=308`, `DisconnectVerboselyModeratedGame=309`, `DisconnectCollaboratorNotAgeVerified=310`, `DisconnectCollaboratorTrustedConnectionsRequired=311`, `DisconnectCollaboratorOwnerActionRequired=312`, `DisconnectCollaboratorTooManyCollaborators=313`, `DisconnectCollaboratorUnknownError=314`, `DisconnectCollaboratorRequestedEviction=315`, `DisconnectCollaboratorTrustedConnectionsRequiredPC=316`, `DisconnectRemoteAttestationUnsupported=317`, `DisconnectRemoteAttestationGeneralFailure=318`, `DisconnectRemoteAttestationTimeout=319`, `DisconnectRemoteAttestationOSOutOfDate=320`, `DisconnectRemoteAttestationBootValidationFailure=321`, `PlacelaunchErrors=512`, `PlacelaunchDisabled=515`, `PlacelaunchError=516`, `PlacelaunchGameEnded=517`, `PlacelaunchGameFull=518`, `PlacelaunchUserLeft=522`, `PlacelaunchRestricted=523`, `PlacelaunchUnauthorized=524`, `PlacelaunchFlooded=525`, `PlacelaunchHashExpired=526`, `PlacelaunchHashException=527`, `PlacelaunchPartyCannotFit=528`, `PlacelaunchHttpError=529`, `PlacelaunchUserPrivacyUnauthorized=533`, `PlacelaunchVipOwnerNotPresent=541`, `PlacelaunchAgeVerificationRequired=542`, `PlacelaunchParentalApprovalRequired=543`, `PlacelaunchCoreGated=544`, `PlacelaunchCollaborationCoreGated=545`, `PlacelaunchCreatorBan=600`, `PlacelaunchDeviceBlock=601`, `PlacelaunchCustomMessage=610`, `PlacelaunchOtherError=611`, `TeleportErrors=768`, `TeleportFailure=769`, `TeleportGameNotFound=770`, `TeleportGameEnded=771`, `TeleportGameFull=772`, `TeleportUnauthorized=773`, `TeleportFlooded=774`, `TeleportIsTeleporting=775`.

### Enum.ConnectionState

`Connected=0`, `Disconnected=1`.

### Enum.ContentSourceType

`None=0`, `Uri=1`, `Object=2`, `Opaque=3`.

### Enum.ContextActionPriority

`Low=1000`, `Medium=2000`, `High=3000`.

### Enum.ContextActionResult

`Sink=0`, `Pass=1`.

### Enum.ControlMode

`Classic=0`, `MouseLockSwitch=1`.

### Enum.CoreGuiType

`PlayerList=0`, `Health=1`, `Backpack=2`, `Chat=3`, `All=4`, `EmotesMenu=5`, `SelfView=6`, `Captures=7`, `AvatarSwitcher=8`, `ExperienceShop=9`.

### Enum.CreateAssetResult

`Success=1`, `PermissionDenied=2`, `UploadFailed=3`, `Unknown=4`.

### Enum.CreateContentResult

`Success=1`, `PermissionDenied=2`, `UploadFailed=3`, `StorageLimitExceeded=4`, `Unknown=5`.

### Enum.CreateOutfitFailure

`InvalidName=1`, `OutfitLimitReached=2`, `Other=3`.

### Enum.CreatorType

`User=0`, `Group=1`.

### Enum.CreatorTypeFilter

`User=0`, `Group=1`, `All=2`.

### Enum.CurrencyType

`Default=0`, `Robux=1`, `Tix=2`.

### Enum.CustomCameraMode

`Default=0`, `Classic=1`, `Follow=2`.

### Enum.DataModelChangeType

`Add=0`, `Remove=1`, `Modify=2`, `AddPackage=3`.

### Enum.DataModelExtractorFileType

`PlaceFile=0`, `FirstSlice=1`, `NonFirstSlice=2`.

### Enum.DataStoreRequestType

`GetAsync=0`, `SetIncrementAsync=1`, `UpdateAsync=2`, `GetSortedAsync=3`, `SetIncrementSortedAsync=4`, `OnUpdate=5`, `ListAsync=6`, `GetVersionAsync=7`, `RemoveVersionAsync=8`, `StandardRead=9`, `StandardWrite=10`, `StandardList=11`, `StandardRemove=12`, `OrderedRead=13`, `OrderedWrite=14`, `OrderedList=15`, `OrderedRemove=16`.

### Enum.DebugBreakModeType

`Never=0`, `Always=1`, `Unhandled=2`.

### Enum.DebuggerEndReason

`ClientRequest=0`, `Timeout=1`, `InvalidHost=2`, `Disconnected=3`, `ServerShutdown=4`, `ServerProtocolMismatch=5`, `ConfigurationFailed=6`, `RpcError=7`.

### Enum.DebuggerExceptionBreakMode

`Never=0`, `Always=1`, `Unhandled=2`.

### Enum.DebuggerFrameType

`C=0`, `Lua=1`.

### Enum.DebuggerPauseReason

`Unknown=0`, `Requested=1`, `Breakpoint=2`, `Exception=3`, `SingleStep=4`, `Entrypoint=5`.

### Enum.DebuggerResumeType

`StepInto=0`, `StepOut=1`, `StepOver=2`, `Resume=3`.

### Enum.DebuggerStatus

`Success=0`, `Timeout=1`, `ConnectionLost=2`, `InvalidResponse=3`, `InternalError=4`, `InvalidState=5`, `RpcError=6`, `InvalidArgument=7`, `ConnectionClosed=8`.

### Enum.DefaultScriptSyncFileType

`Lua=0`, `Luau=1`.

### Enum.DevCameraOcclusionMode

`Zoom=0`, `Invisicam=1`.

### Enum.DevComputerCameraMovementMode

`UserChoice=0`, `Classic=1`, `Follow=2`, `Orbital=3`, `CameraToggle=4`.

### Enum.DevComputerMovementMode

`UserChoice=0`, `KeyboardMouse=1`, `ClickToMove=2`, `Scriptable=3`.

### Enum.DevTouchCameraMovementMode

`UserChoice=0`, `Classic=1`, `Follow=2`, `Orbital=3`.

### Enum.DevTouchMovementMode

`UserChoice=0`, `Thumbstick=1`, `DPad=2`, `Thumbpad=3`, `ClickToMove=4`, `Scriptable=5`, `DynamicThumbstick=6`.

### Enum.DeveloperMemoryTag

`Internal=0`, `HttpCache=1`, `Instances=2`, `Signals=3`, `LuaHeap=4`, `Script=5`, `PhysicsCollision=6`, `BaseParts=7`, `GraphicsSolidModels=8`, `GraphicsMeshParts=10`, `GraphicsParticles=11`, `GraphicsParts=12`, `GraphicsSpatialHash=13`, `GraphicsTerrain=14`, `GraphicsTexture=15`, `GraphicsTextureCharacter=16`, `Sounds=17`, `StreamingSounds=18`, `TerrainVoxels=19`, `Gui=21`, `Animation=22`, `Navigation=23`, `GeometryCSG=24`, `GraphicsSlimModels=25`.

### Enum.DeviceFeatureType

`DeviceCapture=0`, `InExperienceFAE=1`.

### Enum.DeviceForm

`Console=0`, `Phone=1`, `Tablet=2`, `Desktop=3`, `VR=4`.

### Enum.DeviceLevel

`Low=0`, `Medium=1`, `High=2`.

### Enum.DeviceSimulatorScalingMode

`ScaleToPhysicalSize=0`, `ActualResolution=1`, `FitToWindow=2`.

### Enum.DeviceType

`Unknown=0`, `Desktop=1`, `Tablet=2`, `Phone=3`, `TV=4`.

### Enum.DialogBehaviorType

`SinglePlayer=0`, `MultiplePlayers=1`.

### Enum.DialogPurpose

`Quest=0`, `Help=1`, `Shop=2`.

### Enum.DialogTone

`Neutral=0`, `Friendly=1`, `Enemy=2`.

### Enum.DigitsRigDescriptionSide

`None=0`, `Left=1`, `Right=2`.

### Enum.DiscountType

`Uncategorized=0`.

### Enum.DisplayScalingMode

`Default=0`, `Legacy=1`, `Responsive=2`.

### Enum.DisplaySize

`Small=0`, `Medium=1`, `Large=2`.

### Enum.DistanceAttenuationMode

`Custom=0`, `InverseTapered=1`, `Linear=2`, `LinearSquared=3`, `Inverse=4`.

### Enum.DomainType

`EXPERIENCE=1`, `OAUTH=3`.

### Enum.DominantAxis

`Width=0`, `Height=1`.

### Enum.DraftStatusCode

`OK=0`, `DraftOutdated=1`, `ScriptRemoved=2`, `DraftCommitted=3`.

### Enum.DragDetectorDragStyle

`TranslateLine=0`, `TranslatePlane=1`, `TranslatePlaneOrLine=2`, `TranslateLineOrPlane=3`, `TranslateViewPlane=4`, `RotateAxis=5`, `RotateTrackball=6`, `Scriptable=7`, `BestForDevice=8`.

### Enum.DragDetectorPermissionPolicy

`Nobody=0`, `Everybody=1`, `Scriptable=2`.

### Enum.DragDetectorResponseStyle

`Geometric=0`, `Physical=1`, `Custom=2`.

### Enum.DraggerCoordinateSpace

`Object=0`, `World=1`.

### Enum.DraggerMovementMode

`Geometric=0`, `Physical=1`.

### Enum.DraggingScrollBar

`None=0`, `Horizontal=1`, `Vertical=2`.

### Enum.EasingDirection

`In=0`, `Out=1`, `InOut=2`.

### Enum.EasingStyle

`Linear=0`, `Sine=1`, `Back=2`, `Quad=3`, `Quart=4`, `Quint=5`, `Bounce=6`, `Elastic=7`, `Exponential=8`, `Circular=9`, `Cubic=10`.

### Enum.EditableStatus

`Unknown=0`, `Allowed=1`, `Disallowed=2`.

### Enum.ElasticBehavior

`WhenScrollable=0`, `Always=1`, `Never=2`.

### Enum.EmitterPositionType

`Parent=0`, `Instance=1`.

### Enum.EngagementLevel

`Unknown=0`, `Inactive=1`, `Low=2`, `Medium=3`, `High=4`.

### Enum.EngineFolder

`Screenshots=0`, `Videos=1`, `Logs=2`.

### Enum.EnviromentalPhysicsThrottle

`DefaultAuto=0`, `Disabled=1`, `Always=2`, `Skip2=3`, `Skip4=4`, `Skip8=5`, `Skip16=6`.

### Enum.ExperienceActivationStatus

`Unknown=0`, `New=1`, `Active=2`, `Lapsed=3`, `Reactivated=4`.

### Enum.ExperienceAuthScope

`DefaultScope=0`, `CreatorAssetsCreate=1`.

### Enum.ExperienceEventStatus

`Active=0`, `Cancelled=1`, `Moderated=2`, `Unpublished=3`, `Unknown=4`.

### Enum.ExperienceStateCaptureSelectionMode

`Default=0`, `SafetyHighlightMode=1`.

### Enum.ExperienceStateRecordingLoadMode

`NewReplay=0`, `ContiguousSlice=1`, `NoncontiguousSlice=2`.

### Enum.ExperienceStateRecordingLoadSourceType

`S3Url=0`, `File=1`.

### Enum.ExperienceStateRecordingPlaybackMode

`Undefined=0`, `Stopped=1`, `Playing=2`, `Rewinding=3`.

### Enum.ExplosionType

`NoCraters=0`, `Craters=1`.

### Enum.ExternalEditorMode

`SystemDefault=0`, `UserSelectedEditor=1`.

### Enum.FACSDataLod

`LOD0=0`, `LOD1=1`, `LODCount=2`.

### Enum.FacialAgeEstimationResultType

`Complete=0`, `Cancel=1`, `Error=2`.

### Enum.FacialAnimationStreamingState

`None=0`, `Audio=1`, `Video=2`, `Place=4`, `Server=8`.

### Enum.FacsActionUnit

`ChinRaiserUpperLip=0`, `ChinRaiser=1`, `FlatPucker=2`, `Funneler=3`, `LowerLipSuck=4`, `LipPresser=5`, `LipsTogether=6`, `MouthLeft=7`, `MouthRight=8`, `Pucker=9`, `UpperLipSuck=10`, `LeftCheekPuff=11`, `LeftDimpler=12`, `LeftLipCornerDown=13`, `LeftLowerLipDepressor=14`, `LeftLipCornerPuller=15`, `LeftLipStretcher=16`, `LeftUpperLipRaiser=17`, `RightCheekPuff=18`, `RightDimpler=19`, `RightLipCornerDown=20`, `RightLowerLipDepressor=21`, `RightLipCornerPuller=22`, `RightLipStretcher=23`, `RightUpperLipRaiser=24`, `JawDrop=25`, `JawLeft=26`, `JawRight=27`, `Corrugator=28`, `LeftBrowLowerer=29`, `LeftOuterBrowRaiser=30`, `LeftNoseWrinkler=31`, `LeftInnerBrowRaiser=32`, `RightBrowLowerer=33`, `RightOuterBrowRaiser=34`, `RightInnerBrowRaiser=35`, `RightNoseWrinkler=36`, `EyesLookDown=37`, `EyesLookLeft=38`, `EyesLookUp=39`, `EyesLookRight=40`, `LeftCheekRaiser=41`, `LeftEyeUpperLidRaiser=42`, `LeftEyeClosed=43`, `RightCheekRaiser=44`, `RightEyeUpperLidRaiser=45`, `RightEyeClosed=46`, `TongueDown=47`, `TongueOut=48`, `TongueUp=49`.

### Enum.FeatureRestrictionAbuseVector

`ExperienceChat=0`, `Communication=1`.

### Enum.FeedbackType

`Feedback=0`, `PlayerSupport=1`.

### Enum.FieldOfViewMode

`Vertical=0`, `Diagonal=1`, `MaxAxis=2`.

### Enum.FillDirection

`Horizontal=0`, `Vertical=1`.

### Enum.FilterErrorType

`BackslashNotEscapingAnything=0`, `BadBespokeFilter=1`, `BadName=2`, `IncompleteOr=3`, `IncompleteParenthesis=4`, `InvalidDoubleStar=5`, `InvalidTilde=6`, `PropertyBadOperator=7`, `PropertyDoesNotExist=8`, `PropertyInvalidField=9`, `PropertyInvalidValue=10`, `PropertyUnsupportedFields=11`, `PropertyUnsupportedProperty=12`, `UnexpectedNameIndex=13`, `UnexpectedToken=14`, `UnfinishedBinaryOperator=15`, `UnfinishedQuote=16`, `UnknownBespokeFilter=17`, `WildcardInProperty=18`.

### Enum.FilterResult

`Accepted=0`, `Rejected=1`.

### Enum.FilterType

`Exclude=0`, `Include=1`.

### Enum.FinishRecordingOperation

`Cancel=0`, `Commit=1`, `Append=2`.

### Enum.FluidFidelity

`Automatic=0`, `UseCollisionGeometry=1`, `UsePreciseGeometry=2`.

### Enum.FluidForces

`Default=0`, `Experimental=1`.

### Enum.Font

`Legacy=0`, `Arial=1`, `ArialBold=2`, `SourceSans=3`, `SourceSansBold=4`, `SourceSansLight=5`, `SourceSansItalic=6`, `Bodoni=7`, `Garamond=8`, `Cartoon=9`, `Code=10`, `Highway=11`, `SciFi=12`, `Arcade=13`, `Fantasy=14`, `Antique=15`, `SourceSansSemibold=16`, `Gotham=17`, `GothamMedium=18`, `GothamBold=19`, `GothamBlack=20`, `AmaticSC=21`, `Bangers=22`, `Creepster=23`, `DenkOne=24`, `Fondamento=25`, `FredokaOne=26`, `GrenzeGotisch=27`, `IndieFlower=28`, `JosefinSans=29`, `Jura=30`, `Kalam=31`, `LuckiestGuy=32`, `Merriweather=33`, `Michroma=34`, `Nunito=35`, `Oswald=36`, `PatrickHand=37`, `PermanentMarker=38`, `Roboto=39`, `RobotoCondensed=40`, `RobotoMono=41`, `Sarpanch=42`, `SpecialElite=43`, `TitilliumWeb=44`, `Ubuntu=45`, `BuilderSans=46`, `BuilderSansMedium=47`, `BuilderSansBold=48`, `BuilderSansExtraBold=49`, `Arimo=50`, `ArimoBold=51`, `Unknown=100`.

### Enum.FontSize

`Size8=0`, `Size9=1`, `Size10=2`, `Size11=3`, `Size12=4`, `Size14=5`, `Size18=6`, `Size24=7`, `Size36=8`, `Size48=9`, `Size28=10`, `Size32=11`, `Size42=12`, `Size60=13`, `Size96=14`.

### Enum.FontStyle

`Normal=0`, `Italic=1`.

### Enum.FontWeight

`Thin=100`, `ExtraLight=200`, `Light=300`, `Regular=400`, `Medium=500`, `SemiBold=600`, `Bold=700`, `ExtraBold=800`, `Heavy=900`.

### Enum.ForceLimitMode

`Magnitude=0`, `PerAxis=1`.

### Enum.FormFactor

`Symmetric=0`, `Brick=1`, `Plate=2`, `Custom=3`.

### Enum.FrameStyle

`Custom=0`, `ChatBlue=1`, `RobloxSquare=2`, `RobloxRound=3`, `ChatGreen=4`, `ChatRed=5`, `DropShadow=6`.

### Enum.FramerateManagerMode

`Automatic=0`, `On=1`, `Off=2`.

### Enum.FriendRequestEvent

`Issue=0`, `Revoke=1`, `Accept=2`, `Deny=3`.

### Enum.FriendStatus

`Unknown=0`, `NotFriend=1`, `Friend=2`, `FriendRequestSent=3`, `FriendRequestReceived=4`.

### Enum.FrustumStreamingMode

`Default=0`, `Enabled=1`, `Disabled=2`, `Automatic=3`.

### Enum.FunctionalTestResult

`Passed=0`, `Warning=1`, `Error=2`.

### Enum.GameAvatarType

`R6=0`, `R15=1`, `PlayerChoice=2`.

### Enum.GamepadType

`Unknown=0`, `PS4=1`, `PS5=2`, `XboxOne=3`.

### Enum.GearGenreSetting

`AllGenres=0`, `MatchingGenreOnly=1`.

### Enum.GearType

`MeleeWeapons=0`, `RangedWeapons=1`, `Explosives=2`, `PowerUps=3`, `NavigationEnhancers=4`, `MusicalInstruments=5`, `SocialItems=6`, `BuildingTools=7`, `Transport=8`.

### Enum.GenerateMomentTextResult

`Success=0`, `Pending=1`, `Failed=2`.

### Enum.Genre

`All=0`, `TownAndCity=1`, `Fantasy=2`, `SciFi=3`, `Ninja=4`, `Scary=5`, `Pirate=6`, `Adventure=7`, `Sports=8`, `Funny=9`, `WildWest=10`, `War=11`, `SkatePark=12`, `Tutorial=13`.

### Enum.GradientTileMode

`Clamp=0`, `Repeat=1`, `Mirror=2`.

### Enum.GradientType

`Linear=0`, `Radial=1`, `Conical=2`.

### Enum.GraphicsMode

`Automatic=1`, `Direct3D11=2`, `OpenGL=4`, `Metal=5`, `Vulkan=6`, `NoGraphics=9`.

### Enum.GraphicsOptimizationMode

`Performance=0`, `Balanced=1`, `Quality=2`.

### Enum.GroupMembershipStatus

`None=0`, `Joined=1`, `JoinRequestPending=2`, `AlreadyMember=3`.

### Enum.GuiState

`Idle=0`, `Hover=1`, `Press=2`, `NonInteractable=3`.

### Enum.GuiType

`Core=0`, `Custom=1`, `PlayerNameplates=2`, `CustomBillboards=3`, `CoreBillboards=4`.

### Enum.HandlesStyle

`Resize=0`, `Movement=1`.

### Enum.HapticEffectType

`Custom=0`, `UIHover=1`, `UIClick=2`, `UINotification=3`, `GameplayExplosion=4`, `GameplayCollision=5`.

### Enum.HashAlgorithm

`Blake2b=0`, `Blake3=1`, `Md5=2`, `Sha1=3`, `Sha256=4`.

### Enum.HighlightDepthMode

`AlwaysOnTop=0`, `Occluded=1`.

### Enum.HorizontalAlignment

`Center=0`, `Left=1`, `Right=2`.

### Enum.HoverAnimateSpeed

`VerySlow=0`, `Slow=1`, `Medium=2`, `Fast=3`, `VeryFast=4`.

### Enum.HttpCachePolicy

`None=0`, `Full=1`, `DataOnly=2`, `Default=3`, `InternalRedirectRefresh=4`.

### Enum.HttpCompression

`None=0`, `Gzip=1`.

### Enum.HttpContentType

`ApplicationJson=0`, `ApplicationXml=1`, `ApplicationUrlEncoded=2`, `TextPlain=3`, `TextXml=4`.

### Enum.HttpError

`OK=0`, `InvalidUrl=1`, `DnsResolve=2`, `ConnectFail=3`, `OutOfMemory=4`, `TimedOut=5`, `TooManyRedirects=6`, `InvalidRedirect=7`, `NetFail=8`, `Aborted=9`, `SslConnectFail=10`, `SslVerificationFail=11`, `Unknown=12`, `ConnectionClosed=13`, `ServerProtocolError=14`, `CreatorEnvironmentsNotSupportedByService=15`, `InactivityTimeout=16`, `TooManyOutstandingRequests=17`, `InvalidRangeResponse=18`.

### Enum.HttpRequestType

`Default=0`, `MarketplaceService=2`, `Players=7`, `Chat=15`, `Avatar=16`, `Analytics=23`, `Localization=25`.

### Enum.HumanoidCollisionType

`OuterBox=0`, `InnerBox=1`.

### Enum.HumanoidDisplayDistanceType

`Viewer=0`, `Subject=1`, `None=2`.

### Enum.HumanoidHealthDisplayType

`DisplayWhenDamaged=0`, `AlwaysOn=1`, `AlwaysOff=2`.

### Enum.HumanoidRigType

`R6=0`, `R15=1`.

### Enum.HumanoidStateType

`FallingDown=0`, `Ragdoll=1`, `GettingUp=2`, `Jumping=3`, `Swimming=4`, `Freefall=5`, `Flying=6`, `Landed=7`, `Running=8`, `RunningNoPhysics=10`, `StrafingNoPhysics=11`, `Climbing=12`, `Seated=13`, `PlatformStanding=14`, `Dead=15`, `Physics=16`, `None=18`.

### Enum.IKCollisionsMode

`NoCollisions=0`, `OtherMechanismsAnchored=1`, `IncludeContactedMechanisms=2`.

### Enum.IKControlConstraintSupport

`Default=0`, `Disabled=1`, `Enabled=2`.

### Enum.IKControlType

`Transform=0`, `Position=1`, `Rotation=2`, `LookAt=3`.

### Enum.IXPLoadingStatus

`None=0`, `Pending=1`, `Initialized=2`, `ErrorInvalidUser=3`, `ErrorConnection=4`, `ErrorJsonParse=5`, `ErrorTimedOut=6`.

### Enum.ImageAlphaType

`Default=1`, `LockCanvasAlpha=2`, `LockCanvasColor=3`.

### Enum.ImageCombineType

`BlendSourceOver=1`, `Overwrite=2`, `Add=3`, `Multiply=4`, `AlphaBlend=5`, `NormalMapBlend=6`, `Subtract=7`.

### Enum.InOut

`Edge=0`, `Inset=1`, `Center=2`.

### Enum.InfoType

`Asset=0`, `Product=1`, `GamePass=2`, `Subscription=3`, `Bundle=4`.

### Enum.InitialDockState

`Top=0`, `Bottom=1`, `Left=2`, `Right=3`, `Float=4`.

### Enum.InputActionType

`Bool=0`, `Direction1D=1`, `Direction2D=2`, `Direction3D=3`, `ViewportPosition=4`.

### Enum.InputBindingType

`Automatic=0`, `Scriptable=1`.

### Enum.InputSink

`None=0`, `Activate=1`, `All=100`.

### Enum.InputType

`NoInput=0`, `Constant=12`, `Sin=13`.

### Enum.InstanceFileSyncStatus

`NotSynced=0`, `Errored=1`, `SyncedAsRoot=2`, `SyncedAsDescendant=3`, `AncestorErrored=4`.

### Enum.IntermediateMeshGenerationResult

`HighQualityMesh=0`.

### Enum.InternalVideoUsage

`Default=0`, `WatchPage=1`, `HomeCarousel=2`, `FeatureTileAd=3`.

### Enum.InterpolationThrottlingMode

`Default=0`, `Disabled=1`, `Enabled=2`.

### Enum.InviteState

`Placed=0`, `Accepted=1`, `Declined=2`, `Missed=3`.

### Enum.ItemLineAlignment

`Automatic=0`, `Start=1`, `Center=2`, `End=3`, `Stretch=4`.

### Enum.JoinSource

`CreatedItemAttribution=1`.

### Enum.JointCreationMode

`All=0`, `Surface=1`, `None=2`.

### Enum.KeyCode

`None=0`, `Backspace=8`, `Tab=9`, `Clear=12`, `Return=13`, `Pause=19`, `Escape=27`, `Space=32`, `QuotedDouble=34`, `Hash=35`, `Dollar=36`, `Percent=37`, `Ampersand=38`, `Quote=39`, `LeftParenthesis=40`, `RightParenthesis=41`, `Asterisk=42`, `Plus=43`, `Comma=44`, `Minus=45`, `Period=46`, `Slash=47`, `Zero=48`, `One=49`, `Two=50`, `Three=51`, `Four=52`, `Five=53`, `Six=54`, `Seven=55`, `Eight=56`, `Nine=57`, `Colon=58`, `Semicolon=59`, `LessThan=60`, `Equals=61`, `GreaterThan=62`, `Question=63`, `At=64`, `LeftBracket=91`, `BackSlash=92`, `RightBracket=93`, `Caret=94`, `Underscore=95`, `Backquote=96`, `A=97`, `B=98`, `C=99`, `D=100`, `E=101`, `F=102`, `G=103`, `H=104`, `I=105`, `J=106`, `K=107`, `L=108`, `M=109`, `N=110`, `O=111`, `P=112`, `Q=113`, `R=114`, `S=115`, `T=116`, `U=117`, `V=118`, `W=119`, `X=120`, `Y=121`, `Z=122`, `LeftCurly=123`, `Pipe=124`, `RightCurly=125`, `Tilde=126`, `Delete=127`, `World0=160`, `World1=161`, `World2=162`, `World3=163`, `World4=164`, `World5=165`, `World6=166`, `World7=167`, `World8=168`, `World9=169`, `World10=170`, `World11=171`, `World12=172`, `World13=173`, `World14=174`, `World15=175`, `World16=176`, `World17=177`, `World18=178`, `World19=179`, `World20=180`, `World21=181`, `World22=182`, `World23=183`, `World24=184`, `World25=185`, `World26=186`, `World27=187`, `World28=188`, `World29=189`, `World30=190`, `World31=191`, `World32=192`, `World33=193`, `World34=194`, `World35=195`, `World36=196`, `World37=197`, `World38=198`, `World39=199`, `World40=200`, `World41=201`, `World42=202`, `World43=203`, `World44=204`, `World45=205`, `World46=206`, `World47=207`, `World48=208`, `World49=209`, `World50=210`, `World51=211`, `World52=212`, `World53=213`, `World54=214`, `World55=215`, `World56=216`, `World57=217`, `World58=218`, `World59=219`, `World60=220`, `World61=221`, `World62=222`, `World63=223`, `World64=224`, `World65=225`, `World66=226`, `World67=227`, `World68=228`, `World69=229`, `World70=230`, `World71=231`, `World72=232`, `World73=233`, `World74=234`, `World75=235`, `World76=236`, `World77=237`, `World78=238`, `World79=239`, `World80=240`, `World81=241`, `World82=242`, `World83=243`, `World84=244`, `World85=245`, `World86=246`, `World87=247`, `World88=248`, `World89=249`, `World90=250`, `World91=251`, `World92=252`, `World93=253`, `World94=254`, `World95=255`, `KeypadZero=256`, `KeypadOne=257`, `KeypadTwo=258`, `KeypadThree=259`, `KeypadFour=260`, `KeypadFive=261`, `KeypadSix=262`, `KeypadSeven=263`, `KeypadEight=264`, `KeypadNine=265`, `KeypadPeriod=266`, `KeypadDivide=267`, `KeypadMultiply=268`, `KeypadMinus=269`, `KeypadPlus=270`, `KeypadEnter=271`, `KeypadEquals=272`, `Up=273`, `Down=274`, `Right=275`, `Left=276`, `Insert=277`, `Home=278`, `End=279`, `PageUp=280`, `PageDown=281`, `F1=282`, `F2=283`, `F3=284`, `F4=285`, `F5=286`, `F6=287`, `F7=288`, `F8=289`, `F9=290`, `F10=291`, `F11=292`, `F12=293`, `F13=294`, `F14=295`, `F15=296`, `NumLock=300`, `CapsLock=301`, `ScrollLock=302`, `RightShift=303`, `LeftShift=304`, `RightControl=305`, `LeftControl=306`, `RightAlt=307`, `LeftAlt=308`, `RightMeta=309`, `LeftMeta=310`, `LeftSuper=311`, `RightSuper=312`, `Mode=313`, `Compose=314`, `Help=315`, `Print=316`, `SysReq=317`, `Break=318`, `Menu=319`, `Power=320`, `Euro=321`, `Undo=322`, `ButtonX=1000`, `ButtonY=1001`, `ButtonA=1002`, `ButtonB=1003`, `ButtonR1=1004`, `ButtonL1=1005`, `ButtonR2=1006`, `ButtonL2=1007`, `ButtonR3=1008`, `ButtonL3=1009`, `ButtonStart=1010`, `ButtonSelect=1011`, `DPadLeft=1012`, `DPadRight=1013`, `DPadUp=1014`, `DPadDown=1015`, `Thumbstick1=1016`, `Thumbstick2=1017`, `Thumbstick1Up=1018`, `Thumbstick1Down=1019`, `Thumbstick1Left=1020`, `Thumbstick1Right=1021`, `Thumbstick2Up=1022`, `Thumbstick2Down=1023`, `Thumbstick2Left=1024`, `Thumbstick2Right=1025`, `MouseLeftButton=1026`, `MouseRightButton=1027`, `MouseMiddleButton=1028`, `MouseBackButton=1029`, `MouseNoButton=1030`, `MouseX=1031`, `MouseY=1032`, `MousePosition=1033`, `TouchPosition=1034`, `MouseWheel=1035`, `TrackpadPan=1040`, `TrackpadPinch=1045`, `MouseDelta=1048`, `TouchDelta=1049`, `TouchPinch=1050`, `ButtonCenter=1051`, `ButtonBack=1052`, `ButtonUp=1053`, `ButtonDown=1054`, `ButtonLeft=1055`, `ButtonRight=1056`.

### Enum.KeyCodeStringFormat

`Default=0`, `Abbreviated=1`.

### Enum.KeyInterpolationMode

`Constant=0`, `Linear=1`, `Cubic=2`.

### Enum.KeywordFilterType

`Include=0`, `Exclude=1`.

### Enum.KnownWindow

`Main=0`.

### Enum.Language

`Default=0`.

### Enum.LeftRight

`Left=0`, `Center=1`, `Right=2`.

### Enum.LexemeType

`Eof=0`, `Name=1`, `QuotedString=2`, `Number=3`, `And=4`, `Or=5`, `Equal=6`, `TildeEqual=7`, `GreaterThan=8`, `GreaterThanEqual=9`, `LessThan=10`, `LessThanEqual=11`, `Colon=12`, `Dot=13`, `LeftParenthesis=14`, `RightParenthesis=15`, `Star=16`, `DoubleStar=17`, `ReservedSpecial=18`.

### Enum.LightingStyle

`Realistic=0`, `Soft=1`.

### Enum.Limb

`Head=0`, `Torso=1`, `LeftArm=2`, `RightArm=3`, `LeftLeg=4`, `RightLeg=5`, `Unknown=6`.

### Enum.LineJoinMode

`Round=0`, `Bevel=1`, `Miter=2`.

### Enum.ListDisplayMode

`Horizontal=0`, `Vertical=1`.

### Enum.ListenerLocation

`Default=0`, `None=1`, `Character=2`, `Camera=3`.

### Enum.ListenerPositionType

`Parent=0`, `Instance=1`.

### Enum.ListenerType

`Camera=0`, `CFrame=1`, `ObjectPosition=2`, `ObjectCFrame=3`.

### Enum.LiveEditingAtomicUpdateResponse

`Success=0`, `FailureGuidNotFound=1`, `FailureHashMismatch=2`, `FailureOperationIllegal=3`.

### Enum.LiveEditingBroadcastMessageType

`Normal=0`, `Warning=1`, `Error=2`.

### Enum.LoadCharacterLayeredClothing

`Default=0`, `Disabled=1`, `Enabled=2`.

### Enum.LoadDynamicHeads

`Default=0`, `Disabled=1`, `Enabled=2`.

### Enum.LocationType

`Character=0`, `Camera=1`, `ObjectPosition=2`.

### Enum.LuauTypeCheckMode

`Default=0`, `NoCheck=1`, `Nonstrict=2`, `Strict=3`.

### Enum.MakeupType

`Face=0`, `Lip=1`, `Eye=2`.

### Enum.MarketplaceBulkPurchasePromptStatus

`Completed=1`, `Aborted=2`, `Error=3`.

### Enum.MarketplaceItemPurchaseStatus

`Success=1`, `SystemError=2`, `AlreadyOwned=3`, `InsufficientRobux=4`, `QuantityLimitExceeded=5`, `QuotaExceeded=6`, `NotForSale=7`, `NotAvailableForPurchaser=8`, `PriceMismatch=9`, `SoldOut=10`, `PurchaserIsSeller=11`, `InsufficientMembership=12`, `PlaceInvalid=13`.

### Enum.MarketplaceProductType

`AvatarAsset=1`, `AvatarBundle=2`.

### Enum.MarkupKind

`PlainText=0`, `Markdown=1`.

### Enum.MatchmakingType

`Default=1`, `XboxOnly=2`, `PlayStationOnly=3`.

### Enum.Material

`Plastic=256`, `SmoothPlastic=272`, `Neon=288`, `Wood=512`, `WoodPlanks=528`, `Marble=784`, `Basalt=788`, `Slate=800`, `CrackedLava=804`, `Concrete=816`, `Limestone=820`, `Granite=832`, `Pavement=836`, `Brick=848`, `Pebble=864`, `Cobblestone=880`, `Rock=896`, `Sandstone=912`, `CorrodedMetal=1040`, `DiamondPlate=1056`, `Foil=1072`, `Metal=1088`, `Grass=1280`, `LeafyGrass=1284`, `Sand=1296`, `Fabric=1312`, `Snow=1328`, `Mud=1344`, `Ground=1360`, `Asphalt=1376`, `Salt=1392`, `Ice=1536`, `Glacier=1552`, `Glass=1568`, `ForceField=1584`, `Air=1792`, `Water=2048`, `Cardboard=2304`, `Carpet=2305`, `CeramicTiles=2306`, `ClayRoofTiles=2307`, `RoofShingles=2308`, `Leather=2309`, `Plaster=2310`, `Rubber=2311`.

### Enum.MaterialPattern

`Regular=0`, `Organic=1`.

### Enum.MembershipType

`None=0`, `BuildersClub=1`, `TurboBuildersClub=2`, `OutrageousBuildersClub=3`, `Premium=4`.

### Enum.MeshAttribute

`Vertex=0`, `Normal=1`, `Color=2`, `UV=3`, `Face=4`.

### Enum.MeshPartDetailLevel

`DistanceBased=0`, `Level00=1`, `Level01=2`, `Level02=3`, `Level03=4`, `Level04=5`, `Level05=6`, `Level06=7`, `Level07=8`, `Level08=9`, `Level09=10`.

### Enum.MeshPartHeadsAndAccessories

`Default=0`, `Disabled=1`, `Enabled=2`.

### Enum.MeshScaleUnit

`Stud=0`, `Meter=1`, `CM=2`, `MM=3`, `Foot=4`, `Inch=5`.

### Enum.MeshType

`Head=0`, `Torso=1`, `Wedge=2`, `Sphere=3`, `Cylinder=4`, `FileMesh=5`, `Brick=6`, `Prism=7`, `Pyramid=8`, `ParallelRamp=9`, `RightAngleRamp=10`, `CornerWedge=11`.

### Enum.MessageType

`MessageOutput=0`, `MessageInfo=1`, `MessageWarning=2`, `MessageError=3`.

### Enum.ModelLevelOfDetail

`Automatic=0`, `StreamingMesh=1`, `Disabled=2`, `SLIM=4`.

### Enum.ModelStreamingBehavior

`Default=0`, `Legacy=1`, `Improved=2`.

### Enum.ModelStreamingMode

`Default=0`, `Atomic=1`, `Persistent=2`, `PersistentPerPlayer=3`, `Nonatomic=4`.

### Enum.ModerationResultCategory

`ViolationDetected=0`, `Borderline=1`, `NoViolationDetected=2`.

### Enum.ModerationResultLabel

`ChildExploitation=0`, `SuicideSelfInjuryAndHarmfulBehavior=1`, `ThreatsBullyingAndHarassment=2`, `TerrorismAndViolentExtremism=3`, `DiscriminationSlursAndHateSpeech=4`, `RealWorldSensitiveEvents=5`, `ViolentContentAndGore=6`, `RomanticAndSexualContent=7`, `IllegalAndRegulatedGoodsAndActivities=8`, `Profanity=9`, `Other=100`.

### Enum.ModerationStatus

`ReviewedApproved=1`, `ReviewedRejected=2`, `NotReviewed=3`, `NotApplicable=4`, `Invalid=5`.

### Enum.ModifierKey

`Shift=0`, `Ctrl=1`, `Alt=2`, `Meta=3`.

### Enum.MouseBehavior

`Default=0`, `LockCenter=1`, `LockCurrentPosition=2`.

### Enum.MoveState

`Stopped=0`, `Coasting=1`, `Pushing=2`, `Stopping=3`, `AirFree=4`.

### Enum.MuteState

`Unmuted=0`, `Muted=1`.

### Enum.NameOcclusion

`NoOcclusion=0`, `EnemyOcclusion=1`, `OccludeAll=2`.

### Enum.NegateOperationHiddenHistory

`None=0`, `NegatedUnion=1`, `NegatedIntersection=2`.

### Enum.NetworkOwnership

`Automatic=0`, `Manual=1`, `OnContact=2`.

### Enum.NetworkStatus

`Unknown=0`, `Connected=1`, `Disconnected=2`.

### Enum.NoiseType

`SimplexGabor=0`.

### Enum.NormalId

`Right=0`, `Top=1`, `Back=2`, `Left=3`, `Bottom=4`, `Front=5`.

### Enum.NotificationButtonType

`Primary=0`, `Secondary=1`.

### Enum.OperationType

`Null=0`, `Union=1`, `Subtraction=2`, `Intersection=3`, `Primitive=4`.

### Enum.OrientationAlignmentMode

`OneAttachment=0`, `TwoAttachment=1`.

### Enum.OutfitSource

`All=1`, `Created=2`, `Purchased=3`.

### Enum.OutfitType

`All=1`, `Avatar=2`, `DynamicHead=3`, `Shoes=4`, `Makeup=5`.

### Enum.OutputLayoutMode

`Horizontal=0`, `Vertical=1`.

### Enum.OverrideMouseIconBehavior

`None=0`, `ForceShow=1`, `ForceHide=2`.

### Enum.PackagePermission

`None=0`, `NoAccess=1`, `Revoked=2`, `UseView=3`, `Edit=4`, `Own=5`.

### Enum.PageMilestoneType

`Interactive=0`, `SurfaceMounted=1`, `FunctionallyReady=2`, `SurfaceReady=3`.

### Enum.PageType

`AvatarEditor=0`, `Party=1`, `ExperienceDetail=2`, `AvatarMarketplace=3`.

### Enum.PartType

`Ball=0`, `Block=1`, `Cylinder=2`, `Wedge=3`, `CornerWedge=4`.

### Enum.ParticleEmitterShape

`Box=0`, `Sphere=1`, `Cylinder=2`, `Disc=3`.

### Enum.ParticleEmitterShapeInOut

`Outward=0`, `Inward=1`, `InAndOut=2`.

### Enum.ParticleEmitterShapeStyle

`Volume=0`, `Surface=1`.

### Enum.ParticleFlipbookLayout

`None=0`, `Grid2x2=1`, `Grid4x4=2`, `Grid8x8=3`, `Custom=4`.

### Enum.ParticleFlipbookMode

`Loop=0`, `OneShot=1`, `PingPong=2`, `Random=3`.

### Enum.ParticleFlipbookTextureCompatible

`NotCompatible=0`, `Compatible=1`, `Unknown=2`.

### Enum.ParticleOrientation

`FacingCamera=0`, `FacingCameraWorldUp=1`, `VelocityParallel=2`, `VelocityPerpendicular=3`.

### Enum.PathStatus

`Success=0`, `ClosestNoPath=1`, `ClosestOutOfRange=2`, `FailStartNotEmpty=3`, `FailFinishNotEmpty=4`, `NoPath=5`.

### Enum.PathWaypointAction

`Walk=0`, `Jump=1`, `Custom=2`.

### Enum.PathfindingUseImprovedSearch

`Default=0`, `Disabled=1`, `Enabled=2`.

### Enum.PeoplePageLayout

`Card=0`, `List=1`.

### Enum.PerformanceOverlayMode

`Overdraw=0`, `Transparent=1`, `Decals=2`, `Lights=3`.

### Enum.PermissionLevelShown

`Game=0`, `RobloxGame=1`, `RobloxScript=2`, `Studio=3`, `Roblox=4`.

### Enum.PhysicalConstraintType

`AnimationConstraint=0`, `Motor6D=1`.

### Enum.PhysicsSimulationRate

`Fixed240Hz=0`, `Fixed120Hz=1`, `Fixed60Hz=2`.

### Enum.PhysicsSteppingMethod

`Default=0`, `Fixed=1`, `Adaptive=2`.

### Enum.PioneerSource

`Roblox=0`, `DaveyBazooka=1`, `Oof=2`.

### Enum.PlaceContentPreference

`None=0`, `All=1`, `MentionsAndReplies=2`, `Unknown=3`.

### Enum.PlacePublishType

`None=0`, `Publish=1`, `Save=2`.

### Enum.Platform

`Windows=0`, `OSX=1`, `IOS=2`, `Android=3`, `XBoxOne=4`, `PS4=5`, `PS3=6`, `XBox360=7`, `WiiU=8`, `NX=9`, `Ouya=10`, `AndroidTV=11`, `Chromecast=12`, `Linux=13`, `SteamOS=14`, `WebOS=15`, `DOS=16`, `BeOS=17`, `UWP=18`, `PS5=19`, `MetaOS=20`, `Web=21`, `None=22`.

### Enum.PlaybackState

`Begin=0`, `Delayed=1`, `Playing=2`, `Paused=3`, `Completed=4`, `Cancelled=5`.

### Enum.PlayerActions

`CharacterForward=0`, `CharacterBackward=1`, `CharacterLeft=2`, `CharacterRight=3`, `CharacterJump=4`.

### Enum.PlayerCharacterDestroyBehavior

`Default=0`, `Disabled=1`, `Enabled=2`.

### Enum.PlayerChatType

`All=0`, `Team=1`, `Whisper=2`.

### Enum.PlayerDataErrorState

`LoadFailed=0`, `FlushFailed=1`, `ReleaseFailed=2`, `None=3`.

### Enum.PlayerDataLoadFailureBehavior

`Failure=0`, `FallbackToDefault=1`, `Kick=2`.

### Enum.PlayerExitReason

`Unknown=0`, `PlatformKick=1`, `CreatorKick=2`.

### Enum.PlayerPlatformActivationStatus

`Unknown=0`, `New=1`, `Active=2`, `Lapsed=3`, `Reactivated=4`.

### Enum.PlayerPlatformSpenderStatus

`Unknown=0`, `Active=1`, `OtherPayer=2`.

### Enum.PluginConnectionTargetType

`Edit=0`, `Test=1`.

### Enum.PoseEasingDirection

`In=0`, `Out=1`, `InOut=2`.

### Enum.PoseEasingStyle

`Linear=0`, `Constant=1`, `Elastic=2`, `Cubic=3`, `Bounce=4`, `CubicV2=5`.

### Enum.PositionAlignmentMode

`OneAttachment=0`, `TwoAttachment=1`.

### Enum.PredictionMode

`Automatic=0`, `On=1`, `Off=2`.

### Enum.PredictionStatus

`Authoritative=0`, `Predicted=1`, `None=2`.

### Enum.PredictiveStreamingMode

`Default=0`, `Enabled=1`, `Disabled=2`.

### Enum.PreferredInput

`KeyboardAndMouse=0`, `Gamepad=1`, `Touch=2`, `MicroGamepad=3`.

### Enum.PreferredTextSize

`Medium=1`, `Large=2`, `Larger=3`, `Largest=4`.

### Enum.PrefetchDownloadStatus

`NotStarted=0`, `InProgress=1`, `Completed=2`, `Failed=3`.

### Enum.PrimalPhysicsSolver

`Default=0`, `Experimental=1`, `Disabled=2`.

### Enum.PrimitiveType

`Null=0`, `Ball=1`, `Cylinder=2`, `Block=3`, `Wedge=4`, `CornerWedge=5`.

### Enum.PrivilegeType

`Banned=0`, `Visitor=10`, `Member=128`, `Admin=240`, `Owner=255`.

### Enum.ProductLocationRestriction

`AvatarShop=0`, `AllowedGames=1`, `AllGames=2`.

### Enum.ProductPurchaseChannel

`InExperience=1`, `ExperienceDetailsPage=2`, `AdReward=3`, `CommerceProduct=4`.

### Enum.ProductPurchaseDecision

`NotProcessedYet=0`, `PurchaseGranted=1`.

### Enum.PromptCreateAssetResult

`Success=1`, `PermissionDenied=2`, `Timeout=3`, `UploadFailed=4`, `NoUserInput=5`, `UnknownFailure=6`, `UGCValidationFailed=7`, `ModeratedName=8`, `PurchaseFailure=9`, `TokenInvalid=10`.

### Enum.PromptCreateAvatarResult

`Success=1`, `PermissionDenied=2`, `Timeout=3`, `UploadFailed=4`, `NoUserInput=5`, `InvalidHumanoidDescription=6`, `UGCValidationFailed=7`, `ModeratedName=8`, `MaxOutfits=9`, `PurchaseFailure=10`, `UnknownFailure=11`, `TokenInvalid=12`.

### Enum.PromptCreateOutfitResult

`Success=1`, `PartialSuccess=2`, `CreationFailure=3`, `PermissionDenied=4`, `Timeout=5`, `NoUserInput=6`, `UnknownFailure=7`.

### Enum.PromptExperienceDetailsResult

`PromptClosed=0`, `TeleportAttempted=1`.

### Enum.PromptLinkSharingResult

`Success=1`, `PlayerLeft=2`, `InvalidLaunchData=3`.

### Enum.PromptPublishAssetResult

`Success=1`, `PermissionDenied=2`, `Timeout=3`, `UploadFailed=4`, `NoUserInput=5`, `UnknownFailure=6`.

### Enum.PropertyStatus

`Ok=0`, `Warning=1`, `Error=2`.

### Enum.ProximityPromptExclusivity

`OnePerButton=0`, `OneGlobally=1`, `AlwaysShow=2`.

### Enum.ProximityPromptInputType

`Keyboard=0`, `Gamepad=1`, `Touch=2`.

### Enum.ProximityPromptStyle

`Default=0`, `Custom=1`.

### Enum.PurchaseOption

`TimedOption=1`, `Permanent=2`.

### Enum.QualityLevel

`Automatic=0`, `Level01=1`, `Level02=2`, `Level03=3`, `Level04=4`, `Level05=5`, `Level06=6`, `Level07=7`, `Level08=8`, `Level09=9`, `Level10=10`, `Level11=11`, `Level12=12`, `Level13=13`, `Level14=14`, `Level15=15`, `Level16=16`, `Level17=17`, `Level18=18`, `Level19=19`, `Level20=20`, `Level21=21`.

### Enum.R15CollisionType

`OuterBox=0`, `InnerBox=1`.

### Enum.RaycastFilterType

`Exclude=0`, `Include=1`.

### Enum.ReadCapturesFromGalleryResult

`Success=0`, `NeedPermission=1`.

### Enum.ReceiptDecision

`NotProcessedYet=0`, `Processed=1`.

### Enum.ReceiptType

`DeveloperProduct=0`, `RobuxTransferSender=1`, `RobuxTransferReceiver=2`.

### Enum.RecommendationActionType

`AddReaction=0`, `RemoveReaction=1`, `Share=2`, `Report=3`, `Comment=4`, `Play=5`, `Purchase=6`.

### Enum.RecommendationDepartureIntent

`Neutral=0`, `Positive=1`, `Negative=2`.

### Enum.RecommendationImpressionType

`View=0`, `NotViewable=1`.

### Enum.RecommendationItemContentType

`Static=0`, `Dynamic=1`, `Interactive=2`.

### Enum.RecommendationItemVisibility

`Private=0`, `Public=1`.

### Enum.RecommendationPreferenceTargetType

`User=0`, `Universe=1`, `CustomTag=2`.

### Enum.RecommendationPreferenceType

`AddFollow=0`, `RemoveFollow=1`, `AddMute=2`, `RemoveMute=3`.

### Enum.RejectCharacterDeletions

`Default=0`, `Disabled=1`, `Enabled=2`.

### Enum.RenderFidelity

`Automatic=0`, `Precise=1`, `Performance=2`.

### Enum.RenderPriority

`First=0`, `Input=100`, `Camera=200`, `Character=300`, `Last=2000`.

### Enum.RenderingCacheOptimizationMode

`Default=0`, `Disabled=1`, `Enabled=2`.

### Enum.RenderingTestComparisonMethod

`psnr=0`, `diff=1`.

### Enum.ReplicateInstanceDestroySetting

`Default=0`, `Disabled=1`, `Enabled=2`.

### Enum.ResamplerMode

`Default=0`, `Pixelated=1`.

### Enum.ReservedHighlightId

`Standard=0`, `Active=131072`, `Hover=262144`, `Selection=524288`, `NegatedPart=1048576`.

### Enum.RestPose

`Default=0`, `RotationsReset=1`, `Custom=2`.

### Enum.RestPoseModel

`FromRigInACE=0`, `FromRigInFile=1`, `FromRigInFileZeroedRotations=2`, `FromCustomClip=3`.

### Enum.ReturnKeyType

`Default=0`, `Done=1`, `Go=2`, `Next=3`, `Search=4`, `Send=5`.

### Enum.ReverbType

`NoReverb=0`, `GenericReverb=1`, `PaddedCell=2`, `Room=3`, `Bathroom=4`, `LivingRoom=5`, `StoneRoom=6`, `Auditorium=7`, `ConcertHall=8`, `Cave=9`, `Arena=10`, `Hangar=11`, `CarpettedHallway=12`, `Hallway=13`, `StoneCorridor=14`, `Alley=15`, `Forest=16`, `City=17`, `Mountains=18`, `Quarry=19`, `Plain=20`, `ParkingLot=21`, `SewerPipe=22`, `UnderWater=23`.

### Enum.ReviewableContentState

`Pending=0`, `Completed=1`, `Failed=2`.

### Enum.RibbonTool

`Select=0`, `Scale=1`, `Rotate=2`, `Move=3`, `Transform=4`, `ColorPicker=5`, `MaterialPicker=6`, `Group=7`, `Ungroup=8`, `None=9`, `PivotEditor=10`.

### Enum.RigLabel

`Invalid=0`, `Root=2`, `LeftHip=3`, `LeftKnee=4`, `LeftAnkle=5`, `RightHip=7`, `RightKnee=8`, `RightAnkle=9`, `Waist=11`, `LeftShoulder=12`, `LeftElbow=13`, `LeftWrist=14`, `RightShoulder=16`, `RightElbow=17`, `RightWrist=18`, `Neck=20`, `Spine=23`, `Chest=24`, `HeadBase=25`, `LeftClavicle=26`, `RightClavicle=27`, `LeftToeBase=28`, `RightToeBase=29`, `Thumb1=30`, `Thumb2=31`, `Thumb3=32`, `Index1=33`, `Index2=34`, `Index3=35`, `Middle1=36`, `Middle2=37`, `Middle3=38`, `Ring1=39`, `Ring2=40`, `Ring3=41`, `Pinky1=42`, `Pinky2=43`, `Pinky3=44`.

### Enum.RigScale

`Default=0`, `Rthro=1`, `RthroNarrow=2`.

### Enum.RigType

`R15=0`, `CustomHumanoid=1`, `Custom=2`, `None=3`.

### Enum.RollOffMode

`Inverse=0`, `Linear=1`, `LinearSquare=2`, `InverseTapered=3`.

### Enum.RolloutState

`Default=0`, `Disabled=1`, `Enabled=2`.

### Enum.RotationOrder

`XYZ=0`, `XZY=1`, `YZX=2`, `YXZ=3`, `ZXY=4`, `ZYX=5`.

### Enum.RotationType

`MovementRelative=0`, `CameraRelative=1`.

### Enum.RsvpStatus

`None=0`, `Going=1`, `NotGoing=2`.

### Enum.RtlTextSupport

`Default=0`, `Disabled=1`, `Enabled=2`.

### Enum.RunContext

`Legacy=0`, `Server=1`, `Client=2`, `Plugin=3`.

### Enum.RunState

`Stopped=0`, `Running=1`, `Paused=2`.

### Enum.RuntimeUndoBehavior

`Aggregate=0`, `Snapshot=1`, `Hybrid=2`.

### Enum.SafeAreaCompatibility

`None=0`, `FullscreenExtension=1`.

### Enum.SalesTypeFilter

`All=1`, `Collectibles=2`, `Premium=3`, `TimedOptions=4`.

### Enum.SandboxedInstanceMode

`Default=0`, `Experimental=1`.

### Enum.SaveAvatarThumbnailCustomizationFailure

`BadThumbnailType=1`, `BadYRotDeg=2`, `BadFieldOfViewDeg=3`, `BadDistanceScale=4`, `Other=5`, `Throttled=6`.

### Enum.SaveFilter

`SaveWorld=0`, `SaveGame=1`, `SaveAll=2`.

### Enum.SavedQualitySetting

`Automatic=0`, `QualityLevel1=1`, `QualityLevel2=2`, `QualityLevel3=3`, `QualityLevel4=4`, `QualityLevel5=5`, `QualityLevel6=6`, `QualityLevel7=7`, `QualityLevel8=8`, `QualityLevel9=9`, `QualityLevel10=10`.

### Enum.ScaleType

`Stretch=0`, `Slice=1`, `Tile=2`, `Fit=3`, `Crop=4`.

### Enum.ScopeCheckResult

`ConsentAccepted=0`, `InvalidScopes=1`, `Timeout=2`, `NoUserInput=3`, `BackendError=4`, `UnexpectedError=5`, `InvalidArgument=6`, `ConsentDenied=7`.

### Enum.ScreenInsets

`None=0`, `DeviceSafeInsets=1`, `CoreUISafeInsets=2`, `TopbarSafeInsets=3`.

### Enum.ScreenOrientation

`LandscapeLeft=0`, `LandscapeRight=1`, `LandscapeSensor=2`, `Portrait=3`, `Sensor=4`.

### Enum.ScreenshotCaptureResult

`Success=0`, `OtherError=1`, `NoDeviceSupport=2`, `NoSpaceOnDevice=3`.

### Enum.ScriptScannerUpdateType

`Init=0`, `Added=1`, `Removed=2`.

### Enum.ScriptStoppedReason

`Breakpoint=0`, `Exception=1`, `Pause=2`, `Step=3`, `Entry=4`.

### Enum.ScriptVariableScope

`Local=0`, `Upvalue=1`, `Global=2`.

### Enum.ScrollBarInset

`None=0`, `ScrollBar=1`, `Always=2`.

### Enum.ScrollingDirection

`X=1`, `Y=2`, `XY=4`.

### Enum.SecurityCapability

`RunClientScript=0`, `RunServerScript=1`, `AccessOutsideWrite=2`, `AssetRequire=3`, `LoadString=4`, `ScriptGlobals=5`, `CreateInstances=6`, `Basic=7`, `Audio=8`, `DataStore=9`, `Network=10`, `Physics=11`, `UI=12`, `CSG=13`, `Chat=14`, `Animation=15`, `Avatar=16`, `Input=17`, `Environment=18`, `RemoteEvent=19`, `LegacySound=20`, `Players=21`, `CapabilityControl=22`, `Plugin=23`, `LocalUser=24`, `WritePlayer=25`, `RobloxScript=26`, `RobloxEngine=27`, `Unassigned=28`, `InternalTest=29`, `PluginOrOpenCloud=30`, `Assistant=31`, `RemoteCommand=32`, `AssetRead=33`, `AssetManagement=34`, `DynamicGeneration=35`, `PlatformAvatarEditing=36`, `AssetCreateUpdate=37`, `Capture=38`, `SensitiveInput=39`, `Monetization=40`, `LoadOwnedAsset=41`, `Social=42`, `ServerCommunication=43`, `Logging=44`, `PromptExternalPurchase=45`, `Groups=46`, `Teleport=47`, `Consequences=48`, `Material=49`, `AvatarBehavior=50`, `AvatarAppearance=51`, `LoadUnownedAsset=52`.

### Enum.SelectionBehavior

`Escape=0`, `Stop=1`.

### Enum.SelectionRenderMode

`Outlines=0`, `BoundingBoxes=1`, `Both=2`.

### Enum.SelfViewPosition

`LastPosition=0`, `TopLeft=1`, `TopRight=2`, `BottomLeft=3`, `BottomRight=4`.

### Enum.SensorMode

`Floor=0`, `Ladder=1`, `ClassicFloor=2`, `ClassicLadder=3`.

### Enum.SensorUpdateType

`OnRead=0`, `Manual=1`.

### Enum.ServerLiveEditingMode

`Uninitialized=0`, `Enabled=1`, `Disabled=2`.

### Enum.ServiceVisibility

`Always=0`, `Off=1`, `WithChildren=2`.

### Enum.Severity

`Error=1`, `Warning=2`, `Information=3`, `Hint=4`.

### Enum.ShowAdResult

`ShowCompleted=1`, `AdNotReady=2`, `AdAlreadyShowing=3`, `InternalError=4`, `ShowInterrupted=5`, `InsufficientMemory=6`.

### Enum.SignalBehavior

`Default=0`, `Immediate=1`, `Deferred=2`, `AncestryDeferred=3`.

### Enum.SimulationMode

`Default=0`, `Enabled=1`, `Disabled=2`.

### Enum.SizeConstraint

`RelativeXY=0`, `RelativeXX=1`, `RelativeYY=2`.

### Enum.SlimTintMode

`None=0`, `LOD=1`, `Meshes=2`, `MeshResourcePtr=3`, `ContentId=4`, `Zone=5`, `TranscoderStatus=6`.

### Enum.SlimTranscoderStatus

`Unknown=0`, `NoHash=1`, `NotUploaded=2`, `Uploaded=3`, `InProgress=4`, `Succeeded=5`, `Failed=6`.

### Enum.SlimViewContext

`Player=0`, `Editor=1`, `ImGui=2`.

### Enum.SolidPrimitiveType

`Capsule=5`, `Cone=6`, `RoundedBox=7`.

### Enum.SolverConvergenceMetricType

`IterationBased=0`, `AlgorithmAgnostic=1`.

### Enum.SolverConvergenceVisualizationMode

`Disabled=0`, `PerIsland=1`, `PerEdge=2`.

### Enum.SortDirection

`Ascending=0`, `Descending=1`.

### Enum.SortOrder

`Name=0`, `Custom=1`, `LayoutOrder=2`.

### Enum.SpecialKey

`Insert=0`, `Home=1`, `End=2`, `PageUp=3`, `PageDown=4`, `ChatHotkey=5`.

### Enum.StartCorner

`TopLeft=0`, `TopRight=1`, `BottomLeft=2`, `BottomRight=3`.

### Enum.StateObjectFieldType

`Boolean=0`, `CFrame=1`, `Color3=2`, `Float=3`, `Instance=4`, `Random=5`, `Vector2=6`, `Vector3=7`, `INVALID=8`.

### Enum.StateReferenceFrame

`CurrentState=0`, `PreviousState=1`, `LastObservedState=2`.

### Enum.Status

`Poison=0`, `Confusion=1`.

### Enum.StepFrequency

`Hz60=0`, `Hz30=1`, `Hz15=2`, `Hz10=3`, `Hz5=4`, `Hz1=5`.

### Enum.StreamOutBehavior

`Default=0`, `LowMemory=1`, `Opportunistic=2`.

### Enum.StreamingIntegrityMode

`Default=0`, `Disabled=1`, `MinimumRadiusPause=2`, `PauseOutsideLoadedArea=3`.

### Enum.StreamingPauseMode

`Default=0`, `Disabled=1`, `ClientPhysicsPause=2`.

### Enum.StrokeSizingMode

`FixedSize=0`, `ScaledSize=1`.

### Enum.StudioAction

`Undo=0`, `Redo=1`, `SelectAll=2`, `DeleteSelected=3`, `DuplicateSelection=4`, `ClearSelection=5`, `ZoomExtents=6`, `Copy=61`, `Cut=62`, `Paste=63`.

### Enum.StudioCaptureBufferStatus

`NotStarted=0`, `Pending=1`, `Ready=2`, `Error=3`.

### Enum.StudioCaptureScreenshotFormat

`RGBA8=0`, `PNG=1`.

### Enum.StudioCloseMode

`None=0`, `CloseStudio=1`, `CloseDoc=2`, `LogOut=3`.

### Enum.StudioDataModelType

`Edit=0`, `PlayClient=1`, `PlayServer=2`, `Standalone=3`, `None=4`.

### Enum.StudioPlaceUpdateFailureReason

`Other=0`, `TeamCreateConflict=1`.

### Enum.StudioScriptEditorColorCategories

`Default=0`, `Operator=1`, `Number=2`, `String=3`, `Comment=4`, `Keyword=5`, `Builtin=6`, `Method=7`, `Property=8`, `Nil=9`, `Bool=10`, `Function=11`, `Local=12`, `Self=13`, `LuauKeyword=14`, `FunctionName=15`, `TODO=16`, `Background=17`, `SelectionText=18`, `SelectionBackground=19`, `FindSelectionBackground=20`, `MatchingWordBackground=21`, `Warning=22`, `Error=23`, `Info=24`, `Hint=25`, `Whitespace=26`, `ActiveLine=27`, `DebuggerCurrentLine=28`, `DebuggerErrorLine=29`, `Ruler=30`, `Bracket=31`, `Type=32`, `MenuPrimaryText=33`, `MenuSecondaryText=34`, `MenuSelectedText=35`, `MenuBackground=36`, `MenuSelectedBackground=37`, `MenuScrollbarBackground=38`, `MenuScrollbarHandle=39`, `MenuBorder=40`, `DocViewCodeBackground=41`, `AICOOverlayText=42`, `AICOOverlayButtonBackground=43`, `AICOOverlayButtonBackgroundHover=44`, `AICOOverlayButtonBackgroundPressed=45`, `IndentationRuler=46`.

### Enum.StudioScriptEditorColorPresets

`RobloxDefault=0`, `Extra1=1`, `Extra2=2`, `Custom=3`.

### Enum.StudioStyleGuideColor

`MainBackground=0`, `Titlebar=1`, `Dropdown=2`, `Tooltip=3`, `Notification=4`, `ScrollBar=5`, `ScrollBarBackground=6`, `TabBar=7`, `Tab=8`, `FilterButtonDefault=9`, `FilterButtonHover=10`, `FilterButtonChecked=11`, `FilterButtonAccent=12`, `FilterButtonBorder=13`, `FilterButtonBorderAlt=14`, `RibbonTab=15`, `RibbonTabTopBar=16`, `Button=17`, `MainButton=18`, `RibbonButton=19`, `ViewPortBackground=20`, `InputFieldBackground=21`, `Item=22`, `TableItem=23`, `CategoryItem=24`, `GameSettingsTableItem=25`, `GameSettingsTooltip=26`, `EmulatorBar=27`, `EmulatorDropDown=28`, `ColorPickerFrame=29`, `CurrentMarker=30`, `Border=31`, `DropShadow=32`, `Shadow=33`, `Light=34`, `Dark=35`, `Mid=36`, `MainText=37`, `SubText=38`, `TitlebarText=39`, `BrightText=40`, `DimmedText=41`, `LinkText=42`, `WarningText=43`, `ErrorText=44`, `InfoText=45`, `SensitiveText=46`, `ScriptSideWidget=47`, `ScriptBackground=48`, `ScriptText=49`, `ScriptSelectionText=50`, `ScriptSelectionBackground=51`, `ScriptFindSelectionBackground=52`, `ScriptMatchingWordSelectionBackground=53`, `ScriptOperator=54`, `ScriptNumber=55`, `ScriptString=56`, `ScriptComment=57`, `ScriptKeyword=58`, `ScriptBuiltInFunction=59`, `ScriptWarning=60`, `ScriptError=61`, `ScriptInformation=62`, `ScriptHint=63`, `ScriptWhitespace=64`, `ScriptRuler=65`, `DocViewCodeBackground=66`, `DebuggerCurrentLine=67`, `DebuggerErrorLine=68`, `DiffFilePathText=69`, `DiffTextHunkInfo=70`, `DiffTextNoChange=71`, `DiffTextAddition=72`, `DiffTextDeletion=73`, `DiffTextSeparatorBackground=74`, `DiffTextNoChangeBackground=75`, `DiffTextAdditionBackground=76`, `DiffTextDeletionBackground=77`, `DiffLineNum=78`, `DiffLineNumSeparatorBackground=79`, `DiffLineNumNoChangeBackground=80`, `DiffLineNumAdditionBackground=81`, `DiffLineNumDeletionBackground=82`, `DiffFilePathBackground=83`, `DiffFilePathBorder=84`, `ChatIncomingBgColor=85`, `ChatIncomingTextColor=86`, `ChatOutgoingBgColor=87`, `ChatOutgoingTextColor=88`, `ChatModeratedMessageColor=89`, `Separator=90`, `ButtonBorder=91`, `ButtonText=92`, `InputFieldBorder=93`, `CheckedFieldBackground=94`, `CheckedFieldBorder=95`, `CheckedFieldIndicator=96`, `HeaderSection=97`, `Midlight=98`, `StatusBar=99`, `DialogButton=100`, `DialogButtonText=101`, `DialogButtonBorder=102`, `DialogMainButton=103`, `DialogMainButtonText=104`, `InfoBarWarningBackground=105`, `InfoBarWarningText=106`, `ScriptEditorCurrentLine=107`, `ScriptMethod=108`, `ScriptProperty=109`, `ScriptNil=110`, `ScriptBool=111`, `ScriptFunction=112`, `ScriptLocal=113`, `ScriptSelf=114`, `ScriptLuauKeyword=115`, `ScriptFunctionName=116`, `ScriptTodo=117`, `ScriptBracket=118`, `AttributeCog=119`, `AICOOverlayText=128`, `AICOOverlayButtonBackground=129`, `AICOOverlayButtonBackgroundHover=130`, `AICOOverlayButtonBackgroundPressed=131`, `OnboardingCover=132`, `OnboardingHighlight=133`, `OnboardingShadow=134`, `BreakpointMarker=136`, `DiffLineNumHover=137`, `DiffLineNumSeparatorBackgroundHover=138`.

### Enum.StudioStyleGuideModifier

`Default=0`, `Selected=1`, `Pressed=2`, `Disabled=3`, `Hover=4`.

### Enum.Style

`AlternatingSupports=0`, `BridgeStyleSupports=1`, `NoSupports=2`.

### Enum.SubscriptionExpirationReason

`ProductInactive=0`, `ProductDeleted=1`, `SubscriberCancelled=2`, `SubscriberRefunded=3`, `Lapsed=4`.

### Enum.SubscriptionPaymentStatus

`Paid=0`, `Refunded=1`.

### Enum.SubscriptionPeriod

`Month=0`.

### Enum.SubscriptionState

`NeverSubscribed=0`, `SubscribedWillRenew=1`, `SubscribedWillNotRenew=2`, `SubscribedRenewalPaymentPending=3`, `Expired=4`.

### Enum.SurfaceConstraint

`None=0`, `Hinge=1`, `SteppingMotor=2`, `Motor=3`.

### Enum.SurfaceGuiShape

`Flat=0`, `CurvedHorizontally=1`.

### Enum.SurfaceGuiSizingMode

`FixedSize=0`, `PixelsPerStud=1`.

### Enum.SurfaceType

`Smooth=0`, `Glue=1`, `Weld=2`, `Studs=3`, `Inlet=4`, `Universal=5`, `Hinge=6`, `Motor=7`, `SteppingMotor=8`, `SmoothNoOutlines=10`.

### Enum.SwipeDirection

`Right=0`, `Left=1`, `Up=2`, `Down=3`, `None=4`.

### Enum.SystemThemeValue

`error=0`, `light=1`, `dark=2`, `systemLight=3`, `systemDark=4`.

### Enum.TableMajorAxis

`RowMajor=0`, `ColumnMajor=1`.

### Enum.TeamCreateErrorState

`PlaceSizeTooLarge=0`, `PlaceSizeApproachingLimit=1`, `PlaceUploadFailing=2`, `NoError=3`.

### Enum.Technology

`Legacy=0`, `Voxel=1`, `Compatibility=2`, `ShadowMap=3`, `Future=4`, `Unified=5`.

### Enum.TelemetryBackend

`UNSPECIFIED=0`, `EventIngest=1`, `Points=2`, `Teletune=3`, `EphemeralCounter=4`, `EphemeralStat=5`, `Counter=6`, `Stat=7`.

### Enum.TelemetryStandardizedField

`AddDatacenterId=0`, `AddPlaceId=1`, `AddUniverseId=2`, `AddPlaceInstanceId=3`, `AddPlaySessionId=4`, `AddCurrentContextName=5`, `AddOsInfo=6`, `AddArchitectureInfo=7`, `AddCpuInfo=8`, `AddMemoryInfo=9`, `AddSessionInfo=10`.

### Enum.TeleportMethod

`TeleportToSpawnByName=0`, `TeleportToPlaceInstance=1`, `TeleportToPrivateServer=2`, `TeleportPartyAsync=3`, `TeleportToVIPServer=4`, `TeleportToInstanceBack=5`, `TeleportUnknown=6`.

### Enum.TeleportResult

`Success=0`, `Failure=1`, `GameNotFound=2`, `GameEnded=3`, `GameFull=4`, `Unauthorized=5`, `Flooded=6`, `IsTeleporting=7`.

### Enum.TeleportState

`RequestedFromServer=0`, `Started=1`, `WaitingForServer=2`, `Failed=3`, `InProgress=4`.

### Enum.TeleportType

`ToPlace=0`, `ToInstance=1`, `ToReservedServer=2`, `ToVIPServer=3`, `ToInstanceBack=4`.

### Enum.TerrainAcquisitionMethod

`None=0`, `Legacy=1`, `Template=2`, `Generate=3`, `Import=4`, `Convert=5`, `EditAddTool=6`, `EditSeaLevelTool=7`, `EditReplaceTool=8`, `RegionFillTool=9`, `RegionPasteTool=10`, `Other=11`.

### Enum.TerrainFace

`Top=0`, `Side=1`, `Bottom=2`.

### Enum.TerrainLiquidMergeOperation

`None=0`, `Source=1`, `Union=2`, `Difference=3`, `Intersect=4`.

### Enum.TerrainSolidMergeOperation

`None=0`, `Paint=1`, `Source=2`, `Union=3`, `Dig=4`, `Difference=5`, `Intersect=6`, `Cut=7`, `Place=8`.

### Enum.TextChatMessageStatus

`Unknown=1`, `Success=2`, `Sending=3`, `TextFilterFailed=4`, `Floodchecked=5`, `InvalidPrivacySettings=6`, `InvalidTextChannelPermissions=7`, `MessageTooLong=8`, `ModerationTimeout=9`.

### Enum.TextDirection

`Auto=0`, `LeftToRight=1`, `RightToLeft=2`.

### Enum.TextFilterContext

`PublicChat=1`, `PrivateChat=2`.

### Enum.TextInputType

`Default=0`, `NoSuggestions=1`, `Number=2`, `Email=3`, `Phone=4`, `Password=5`, `PasswordShown=6`, `Username=7`, `OneTimePassword=8`, `NewPassword=9`, `NewPasswordShown=10`.

### Enum.TextTruncate

`None=0`, `AtEnd=1`, `SplitWord=2`.

### Enum.TextXAlignment

`Left=0`, `Right=1`, `Center=2`.

### Enum.TextYAlignment

`Top=0`, `Center=1`, `Bottom=2`.

### Enum.TextureMode

`Stretch=0`, `Wrap=1`, `Static=2`.

### Enum.TextureQueryType

`NonHumanoid=0`, `NonHumanoidOrphaned=1`, `Humanoid=2`, `HumanoidOrphaned=3`.

### Enum.ThreadPoolConfig

`Auto=0`, `Threads1=1`, `Threads2=2`, `Threads3=3`, `Threads4=4`, `Threads8=8`, `Threads16=16`, `PerCore1=101`, `PerCore2=102`, `PerCore3=103`, `PerCore4=104`.

### Enum.ThrottlingPriority

`Default=0`, `ElevatedOnServer=1`, `Extreme=2`.

### Enum.ThumbnailSize

`Size48x48=0`, `Size180x180=1`, `Size420x420=2`, `Size60x60=3`, `Size100x100=4`, `Size150x150=5`, `Size352x352=6`.

### Enum.ThumbnailType

`HeadShot=0`, `AvatarBust=1`, `AvatarThumbnail=2`.

### Enum.TickCountSampleMethod

`Fast=0`, `Benchmark=1`, `Precise=2`.

### Enum.TitleBarControlsPosition

`Unknown=0`, `Left=1`, `Right=2`.

### Enum.TitleBarMode

`Native=0`, `Custom=1`.

### Enum.TonemapperPreset

`Default=0`, `Retro=1`.

### Enum.TopBottom

`Top=0`, `Center=1`, `Bottom=2`.

### Enum.TouchCameraMovementMode

`Default=0`, `Classic=1`, `Follow=2`, `Orbital=3`.

### Enum.TouchMovementMode

`Default=0`, `Thumbstick=1`, `DPad=2`, `Thumbpad=3`, `ClickToMove=4`, `DynamicThumbstick=5`.

### Enum.TrackerError

`Ok=0`, `NoService=1`, `InitFailed=2`, `NoVideo=3`, `VideoError=4`, `VideoNoPermission=5`, `VideoUnsupported=6`, `NoAudio=7`, `AudioError=8`, `AudioNoPermission=9`, `UnsupportedDevice=10`.

### Enum.TrackerExtrapolationFlagMode

`ForceDisabled=0`, `ExtrapolateFacsAndPose=1`, `ExtrapolateFacsOnly=2`, `Auto=3`.

### Enum.TrackerFaceTrackingStatus

`FaceTrackingSuccess=0`, `FaceTrackingNoFaceFound=1`, `FaceTrackingUnknown=2`, `FaceTrackingLost=3`, `FaceTrackingHasTrackingError=4`, `FaceTrackingIsOccluded=5`, `FaceTrackingUninitialized=6`.

### Enum.TrackerLodFlagMode

`ForceFalse=0`, `ForceTrue=1`, `Auto=2`.

### Enum.TrackerLodValueMode

`Force0=0`, `Force1=1`, `Auto=2`.

### Enum.TrackerMode

`None=0`, `Audio=1`, `Video=2`, `AudioVideo=3`.

### Enum.TrackerPromptEvent

`LODCameraRecommendDisable=0`.

### Enum.TrackerType

`None=0`, `Face=1`, `UpperBody=2`.

### Enum.TriStateBoolean

`Unknown=0`, `True=1`, `False=2`.

### Enum.TweenStatus

`Canceled=0`, `Completed=1`.

### Enum.UICaptureMode

`All=0`, `None=1`.

### Enum.UIDragDetectorBoundingBehavior

`Automatic=0`, `EntireObject=1`, `HitPoint=2`.

### Enum.UIDragDetectorDragRelativity

`Absolute=0`, `Relative=1`.

### Enum.UIDragDetectorDragSpace

`Parent=0`, `LayerCollector=1`, `Reference=2`.

### Enum.UIDragDetectorDragStyle

`TranslatePlane=0`, `TranslateLine=1`, `Rotate=2`, `Scriptable=3`.

### Enum.UIDragDetectorResponseStyle

`Offset=0`, `Scale=1`, `CustomOffset=2`, `CustomScale=3`.

### Enum.UIDragSpeedAxisMapping

`XY=0`, `XX=1`, `YY=2`.

### Enum.UIFlexAlignment

`None=0`, `Fill=1`, `SpaceAround=2`, `SpaceBetween=3`, `SpaceEvenly=4`.

### Enum.UIFlexMode

`None=0`, `Grow=1`, `Shrink=2`, `Fill=3`, `Custom=4`.

### Enum.UITheme

`Light=0`, `Dark=1`.

### Enum.UiMessageType

`UiMessageError=0`, `UiMessageInfo=1`.

### Enum.UpdateState

`UpdateNotAvailable=0`, `UpdateAvailable=1`, `UpdateInProgress=2`, `UpdateReady=3`, `UpdateFailed=4`.

### Enum.UploadCaptureResult

`Success=0`, `NeedPermission=1`, `CaptureModerated=2`, `CaptureNotInGallery=3`, `IneligibleCapture=4`, `UploadQuotaReached=5`, `UploadPending=6`, `UploadFailed=7`.

### Enum.UsageContext

`Default=0`, `Preview=1`.

### Enum.UserAcquisitionSource

`Unknown=0`, `PendingAttribution=1`, `HomeRecommendation=2`, `ContinueToPlay=3`, `Curation=4`, `Friends=5`, `Search=6`, `Teleport=7`, `Ads=8`, `HomeOther=9`, `Other=10`.

### Enum.UserCFrame

`Head=0`, `LeftHand=1`, `RightHand=2`, `Floor=3`.

### Enum.UserIdMode

`Invalid=0`, `Global=1`, `Domain=2`.

### Enum.UserInputState

`Begin=0`, `Change=1`, `End=2`, `Cancel=3`, `None=4`.

### Enum.UserInputType

`MouseButton1=0`, `MouseButton2=1`, `MouseButton3=2`, `MouseWheel=3`, `MouseMovement=4`, `Touch=7`, `Keyboard=8`, `Focus=9`, `Accelerometer=10`, `Gyro=11`, `Gamepad1=12`, `Gamepad2=13`, `Gamepad3=14`, `Gamepad4=15`, `Gamepad5=16`, `Gamepad6=17`, `Gamepad7=18`, `Gamepad8=19`, `TextInput=20`, `InputMethod=21`, `None=22`.

### Enum.UserNewReturningStatus

`Unknown=0`, `New=1`, `Returning=2`.

### Enum.UserReturnStatus

`Unknown=0`, `New=1`, `Returning=2`.

### Enum.VRComfortSetting

`Comfort=0`, `Normal=1`, `Expert=2`, `Custom=3`.

### Enum.VRControllerModelMode

`Disabled=0`, `Transparent=1`.

### Enum.VRDeviceType

`Unknown=0`, `OculusRift=1`, `HTCVive=2`, `ValveIndex=3`, `OculusQuest=4`.

### Enum.VRLaserPointerMode

`Disabled=0`, `Pointer=1`, `DualPointer=2`.

### Enum.VRSafetyBubbleMode

`NoOne=0`, `OnlyFriends=1`, `Anyone=2`.

### Enum.VRScaling

`World=0`, `Off=1`.

### Enum.VRSessionState

`Undefined=0`, `Idle=1`, `Visible=2`, `Focused=3`, `Stopping=4`.

### Enum.VRTouchpad

`Left=0`, `Right=1`.

### Enum.VRTouchpadMode

`Touch=0`, `VirtualThumbstick=1`, `ABXY=2`.

### Enum.VelocityConstraintMode

`Line=0`, `Plane=1`, `Vector=2`.

### Enum.VerifiedLevel

`Low=0`, `High=1`.

### Enum.VerticalAlignment

`Center=0`, `Top=1`, `Bottom=2`.

### Enum.VerticalScrollBarPosition

`Right=0`, `Left=1`.

### Enum.VibrationMotor

`Large=0`, `Small=1`, `LeftTrigger=2`, `RightTrigger=3`, `LeftHand=4`, `RightHand=5`.

### Enum.VideoCaptureResult

`Success=0`, `OtherError=1`, `ScreenSizeChanged=2`, `TimeLimitReached=3`.

### Enum.VideoCaptureStartedResult

`Success=0`, `OtherError=1`, `CapturingAlready=2`, `NoDeviceSupport=3`, `NoSpaceOnDevice=4`.

### Enum.VideoDeviceCaptureQuality

`Default=0`, `Low=1`, `Medium=2`, `High=3`.

### Enum.VideoError

`Ok=0`, `Eof=1`, `EAgain=2`, `BadParameter=3`, `AllocFailed=4`, `CodecInitFailed=5`, `CodecCloseFailed=6`, `DecodeFailed=7`, `ParsingFailed=8`, `Unsupported=9`, `Generic=10`, `DownloadFailed=11`, `StreamNotFound=12`, `EncodeFailed=13`, `CreateFailed=14`, `NoPermission=15`, `NoService=16`, `ReleaseFailed=17`, `Unknown=18`.

### Enum.VideoSampleSize

`Small=0`, `Medium=1`, `Large=2`, `Full=3`.

### Enum.ViewMode

`None=0`, `GeometryComplexity=1`, `Transparent=2`, `Decal=3`.

### Enum.VirtualCursorMode

`Default=0`, `Disabled=1`, `Enabled=2`.

### Enum.VirtualInputMode

`None=0`, `Recording=1`, `Playing=2`.

### Enum.VoiceChatDistanceAttenuationType

`Inverse=0`, `Legacy=1`.

### Enum.VoiceChatState

`Idle=0`, `Joining=1`, `JoiningRetry=2`, `Joined=3`, `Leaving=4`, `Ended=5`, `Failed=6`.

### Enum.VoiceClientLeaveReasons

`Unknown=0`, `ClientNetworkDisconnected=1`, `PlayerLeft=2`, `ClientShutdown=3`, `PublishFailed=4`, `RejoinReceived=5`, `VoiceReboot=6`, `ImguiDebugLeave=7`, `LuaInitiated=8`.

### Enum.VoiceControlPath

`Publish=0`, `Subscribe=1`, `Join=2`.

### Enum.VoiceRccReconnectReason

`Unknown=0`, `Migration=1`, `CloseRoom=2`, `FAEUpdate=3`, `BlockListChanged=4`.

### Enum.VolumetricAudio

`Disabled=0`, `Automatic=1`, `Enabled=2`.

### Enum.WaterDirection

`NegX=0`, `X=1`, `NegY=2`, `Y=3`, `NegZ=4`, `Z=5`.

### Enum.WaterForce

`None=0`, `Small=1`, `Medium=2`, `Strong=3`, `Max=4`.

### Enum.WebSocketState

`Connecting=0`, `Open=1`, `Closing=2`, `Closed=3`.

### Enum.WebStreamClientState

`Connecting=0`, `Open=1`, `Error=2`, `Closed=3`.

### Enum.WebStreamClientType

`SSE=0`, `RawStream=1`, `WebSocket=2`.

### Enum.WeldConstraintPreserve

`All=0`, `None=1`, `Touching=2`.

### Enum.WhenUserFirstPlayed

`Unknown=0`, `Days0To30=1`, `Days31To90=2`, `Days91To180=3`, `Days181To365=4`, `Days366Plus=5`.

### Enum.WhisperChatPrivacyMode

`AllUsers=0`, `NoOne=1`.

### Enum.WindSoundProfile

`Turbulence=0`, `Whistle=1`, `Foliage=2`.

### Enum.WindowState

`Normal=0`, `Minimized=1`, `Maximized=2`.

### Enum.WrapLayerAutoSkin

`Disabled=0`, `EnabledPreserve=1`, `EnabledOverride=2`.

### Enum.WrapLayerDebugMode

`None=0`, `BoundCage=1`, `LayerCage=2`, `BoundCageAndLinks=3`, `Reference=4`, `Rbf=5`, `OuterCage=6`, `ReferenceMeshAfterMorph=7`, `HSROuterDetail=8`, `HSROuter=9`, `HSRInner=10`, `HSRInnerReverse=11`, `LayerCageFittedToBase=12`, `LayerCageFittedToPrev=13`, `PreWrapDeformerOuterCage=14`, `SkinningTransfer=15`.

### Enum.WrapTargetDebugMode

`None=0`, `TargetCageOriginal=1`, `TargetCageCompressed=2`, `TargetCageInterface=3`, `TargetLayerCageOriginal=4`, `TargetLayerCageCompressed=5`, `TargetLayerInterface=6`, `Rbf=7`, `OuterCageDetail=8`, `PreWrapDeformerCage=9`.

### Enum.ZIndexBehavior

`Global=0`, `Sibling=1`.

