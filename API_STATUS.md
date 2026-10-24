# API status against the official reference

Name presence indicates declarations only. Full behavior is not established.

Documentation: `0.744.0.7441077`; runtime: `0.735.19.7351131`.

| Datatype | Status | Observed constructors |
| --- | --- | --- |
| AdReward | missing |  |
| Axes | partial | new |
| BrickColor | partial | Black, Blue, DarkGray, Gray, Green, Red, White, Yellow, new, palette, random |
| CFrame | partial | Angles, fromEulerAnglesXYZ, fromMatrix, lookAt, new |
| CatalogSearchParams | missing |  |
| Collection | missing |  |
| Color3 | partial | fromHSV, fromRGB, new |
| ColorSequence | partial | new |
| ColorSequenceKeypoint | partial | new |
| Content | missing |  |
| DateTime | partial | fromIsoDate, fromLocalTime, fromUniversalTime, fromUnixTimestamp, fromUnixTimestampMillis, now |
| DockWidgetPluginGuiInfo | missing |  |
| Enum | partial |  |
| EnumItem | partial |  |
| Enums | partial |  |
| Faces | partial | new |
| FloatCurveKey | missing |  |
| Font | partial | fromEnum, fromId, fromName, new |
| Instance | partial | new |
| InstanceHandle | missing |  |
| NumberRange | partial | new |
| NumberSequence | partial | new |
| NumberSequenceKeypoint | partial | new |
| OverlapParams | partial | new |
| Path2DControlPoint | missing |  |
| PathWaypoint | partial | new |
| PhysicalProperties | partial | new |
| RBXScriptConnection | partial |  |
| RBXScriptSignal | partial |  |
| Random | partial | new |
| Ray | partial | new |
| RaycastParams | partial | new |
| RaycastResult | partial |  |
| Rect | partial | new |
| Region3 | missing |  |
| Region3int16 | missing |  |
| RotationCurveKey | missing |  |
| Secret | missing |  |
| SecurityCapabilities | missing |  |
| SharedTable | missing |  |
| TweenInfo | partial | new |
| UDim | partial | new |
| UDim2 | partial | fromOffset, fromScale, new |
| User | missing |  |
| ValueCurveKey | missing |  |
| Vector2 | partial | new |
| Vector2int16 | missing |  |
| Vector3 | partial | new |
| Vector3int16 | missing |  |

Missing global names: DebuggerManager, PluginManager, UserSettings, elapsedTime, loadstring, plugin, printidentity, settings, stats, version, ypcall.

Declared 234 of 4861 documented class-member names (4.81%).
This measures name declarations, not full compatibility or overall engine completion.

Detailed class/library gaps: `evidence/api_coverage.json`.
Signatures and sources: `evidence/api_reference.json`.
