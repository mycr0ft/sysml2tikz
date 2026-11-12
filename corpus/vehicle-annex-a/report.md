# Corpus run — vehicle-annex-a

* model: `SysML v2 Spec Annex A SimpleVehicleModel.sysml` (sha256 77d7ee54951e…)
* packages with elements: 29 · rendered: 22 · failed: 0 · skipped: 7
* routing clean: 19/22 rendered
* readable (≤4000 px wide, aspect ≤6:1): 18/22
* renders live in `private/corpus/vehicle-annex-a/` (gitignored — model content is EPL-2.0 and not redistributed here)

| package | nodes | edges | status | note |
|---|---|---|---|---|
| `PartDefinitions` | 34 | 0 | rendered |  |
| `PortDefinitions` | 27 | 0 | rendered |  |
| `ItemDefinitions` | 4 | 0 | rendered |  |
| `SignalDefinitions` | 12 | 0 | rendered |  |
| `InterfaceDefinitions` | 4 | 0 | rendered |  |
| `AllocationDefinitions` | 1 | 0 | skipped | fewer than 2 nodes |
| `ActionDefinitions` | 8 | 0 | rendered |  |
| `StateDefinitions` | 3 | 0 | rendered |  |
| `RequirementDefinitions` | 5 | 0 | rendered |  |
| `AttributeDefinitions` | 5 | 1 | rendered |  |
| `KeyWord_MetadataDefinitions` | 1 | 0 | skipped | fewer than 2 nodes |
| `GenericContext` | 1 | 0 | skipped | fewer than 2 nodes |
| `PartsTree` | 0 | 0 | skipped | fewer than 2 nodes |
| `VehicleLogicalToPhysicalAllocation` | 3 | 2 | rendered |  |
| `PartsTree` | 19 | 18 | rendered | unreadable strip (2957x467) — layout puts every sibling at one rank |
| `PartsTree` | 87 | 86 | skipped | 87 nodes exceeds --max-nodes 60 (a single rank becomes a strip) |
| `ActionTree` | 5 | 4 | rendered | unreadable strip (1695x271) — layout puts every sibling at one rank |
| `Sequence` | 9 | 8 | rendered | routing not clean |
| `Requirements` | 6 | 4 | rendered | unreadable strip (1934x275) — layout puts every sibling at one rank |
| `Engine4Cyl_Variant` | 8 | 6 | rendered |  |
| `WheelHubAssemblies` | 32 | 29 | rendered | unreadable strip (5657x737) — layout puts every sibling at one rank |
| `FuelEconomyAnalysisModel` | 8 | 0 | rendered |  |
| `VehicleTradeOffAnalysis` | 3 | 0 | rendered |  |
| `VerificationSystem` | 8 | 7 | rendered |  |
| `MissionContext` | 11 | 10 | rendered |  |
| `ContextDefinitions` | 5 | 0 | rendered |  |
| `VariationPointDefinitions` | 1 | 0 | skipped | fewer than 2 nodes |
| `VehiclePartsTree` | 12 | 11 | rendered | routing not clean |
| `ViewpointDefinitions` | 1 | 0 | skipped | fewer than 2 nodes |

Regenerate with:

```
python3 tools/build_corpus.py /home/jfox/proj/third_party/SysML-v2-Release/sysml/src/examples/Vehicle Example/SysML v2 Spec Annex A SimpleVehicleModel.sysml --label vehicle-annex-a
```
