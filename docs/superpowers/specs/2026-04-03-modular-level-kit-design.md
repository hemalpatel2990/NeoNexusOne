# Modular Level Kit & Plugin Refactor Design Spec

**Date:** 2026-04-03
**Status:** Draft
**Project:** NeoNexusOne: Echo-Location
**Milestone:** 2 — "Universal Visuals & HUD"

## 1. Overview

Two deliverables that complete Milestone 2, executed **sequentially** (refactor first, then level kit):

1. **EchoLocation Plugin Refactor** — Extract all existing C++ gameplay code from the `NeoNexusOne` module into a reusable `EchoLocation` gameplay plugin. User-requested architectural improvement for modularity.
2. **EchoLevelKit Plugin** — A separate content-only plugin containing 5 stylized geometric Blueprint Actor props for building varied level environments (indoor corridors, mountainous terrain, forests).

**Ordering:** The plugin refactor must complete and verify before the Level Kit is built. This avoids building assets during a class path migration.

## 2. Plugin Architecture

### 2.1 Directory Structure

```
Plugins/
    EchoLocation/
        EchoLocation.uplugin
        Source/EchoLocation/
            EchoLocation.Build.cs
            EchoLocationModule.h/.cpp
            Public/
                Core/EchoTypes.h
                Core/EchoGameMode.h
                Core/EchoPlayerController.h
                Player/EchoPawn.h
                Player/EchoMovementComponent.h
                Sound/EchoRippleManager.h
                Feedback/EchoFeedbackComponent.h
                AI/EchoAIController.h
                AI/EchoEnemyPawn.h
                UI/EchoHUDWidget.h
            Private/
                Core/EchoGameMode.cpp
                Core/EchoPlayerController.cpp
                Player/EchoPawn.cpp
                Player/EchoMovementComponent.cpp
                Sound/EchoRippleManager.cpp
                Feedback/EchoFeedbackComponent.cpp
                AI/EchoAIController.cpp
                AI/EchoEnemyPawn.cpp
                UI/EchoHUDWidget.cpp

    EchoLevelKit/                  ← Content-only plugin (no C++ source)
        EchoLevelKit.uplugin
        Content/
            LevelKit/
                BP_LevelWall.uasset
                BP_LevelRock.uasset
                BP_LevelTree.uasset
                BP_LevelCrate.uasset
                BP_LevelRamp.uasset

Source/NeoNexusOne/
    NeoNexusOne.Build.cs          (minimal — depends on EchoLocation)
    NeoNexusOneModule.h/.cpp      (empty module registration stub)
```

### 2.2 Dependencies

| Module | Depends On |
|--------|-----------|
| `EchoLocation` | Core, CoreUObject, Engine, InputCore, EnhancedInput, AIModule, GameplayTasks, NavigationSystem, Slate, SlateCore, UMG |
| `EchoLevelKit` | *(Content-only plugin — no module dependencies)* |
| `NeoNexusOne` | Core, CoreUObject, Engine |

`NeoNexusOne.uproject` lists both `EchoLocation` and `EchoLevelKit` as enabled plugins. The main module depends on `EchoLocation` as a plugin dependency (not a module dependency), so UBT loads it automatically.

### 2.3 API Macro

All `NEONEXUSONE_API` macros change to `ECHOLOCATION_API` in the moved source files.

### 2.4 Include Paths

Include paths remain the same subfolder-relative style (e.g., `#include "Core/EchoTypes.h"`). `EchoLocation.Build.cs` adds `ModuleDirectory` and `Public/` to `PublicIncludePaths`, mirroring the current setup.

### 2.5 Blueprint Assets

Existing Blueprint assets in `Content/EchoLocation/` (BP_EchoPawn, BP_EchoGameMode, etc.) stay in the project's Content folder. They reference C++ classes that moved from `/Script/NeoNexusOne` to `/Script/EchoLocation` — Core Redirects handle this transparently (see Section 3.3).

Level Kit Blueprint assets live inside the `EchoLevelKit` plugin's own Content folder (`Plugins/EchoLevelKit/Content/LevelKit/`).

## 3. EchoLocation Plugin Refactor

### 3.1 Scope

Move all files from `Source/NeoNexusOne/Public/` and `Source/NeoNexusOne/Private/` into `Plugins/EchoLocation/Source/EchoLocation/Public/` and `Private/` respectively, preserving the subfolder structure.

### 3.2 Changes Required

1. Create `EchoLocation.uplugin` descriptor (Type: Runtime, Category: Gameplay), including Core Redirects (see 3.3).
2. Create `EchoLocation.Build.cs` with all current dependencies from `NeoNexusOne.Build.cs`.
3. Create `EchoLocationModule.h/.cpp` with `IModuleInterface` startup/shutdown stubs.
4. Move all `.h` and `.cpp` files, preserving directory structure.
5. Find-and-replace `NEONEXUSONE_API` → `ECHOLOCATION_API` in all moved headers.
6. Strip `NeoNexusOne.Build.cs` down to minimal dependencies (Core, CoreUObject, Engine).
7. Replace `NeoNexusOne` module source with an empty registration stub.
8. Update `NeoNexusOne.uproject` to enable both plugins.
9. Close Editor, rebuild solution, verify DLL timestamps, test in PIE.

### 3.3 Core Redirects

Add to `EchoLocation.uplugin` to remap all class paths from the old module to the new one. Every `UCLASS`, `USTRUCT`, and `UENUM` that moved needs an entry:

```json
"CoreRedirects": [
    { "OldName": "/Script/NeoNexusOne.EchoPawn",               "NewName": "/Script/EchoLocation.EchoPawn" },
    { "OldName": "/Script/NeoNexusOne.EchoMovementComponent",  "NewName": "/Script/EchoLocation.EchoMovementComponent" },
    { "OldName": "/Script/NeoNexusOne.EchoGameMode",           "NewName": "/Script/EchoLocation.EchoGameMode" },
    { "OldName": "/Script/NeoNexusOne.EchoPlayerController",   "NewName": "/Script/EchoLocation.EchoPlayerController" },
    { "OldName": "/Script/NeoNexusOne.EchoRippleManager",      "NewName": "/Script/EchoLocation.EchoRippleManager" },
    { "OldName": "/Script/NeoNexusOne.EchoFeedbackComponent",  "NewName": "/Script/EchoLocation.EchoFeedbackComponent" },
    { "OldName": "/Script/NeoNexusOne.EchoAIController",       "NewName": "/Script/EchoLocation.EchoAIController" },
    { "OldName": "/Script/NeoNexusOne.EchoEnemyPawn",          "NewName": "/Script/EchoLocation.EchoEnemyPawn" },
    { "OldName": "/Script/NeoNexusOne.EchoHUDWidget",          "NewName": "/Script/EchoLocation.EchoHUDWidget" },
    { "OldName": "/Script/NeoNexusOne.EEchoMovementState",     "NewName": "/Script/EchoLocation.EEchoMovementState" },
    { "OldName": "/Script/NeoNexusOne.EEchoAIState",           "NewName": "/Script/EchoLocation.EEchoAIState" },
    { "OldName": "/Script/NeoNexusOne.FEchoRippleEvent",       "NewName": "/Script/EchoLocation.FEchoRippleEvent" }
]
```

This ensures all existing Blueprint assets (BP_EchoPawn, BP_EchoGameMode, BP_EchoPlayerController, WBP_InkedHUD, BP_EchoEnemyPawn) resolve their C++ parent classes without manual re-parenting.

### 3.4 Verification

After the refactor, verify in PIE:
- Player spawns and moves (Glide/Drop/Slam)
- Sonar ripples fire on impact and reveal geometry
- HUD signal bar decays and resets on impact
- AI hearing perception triggers (if enemy is placed)
- No "missing class" warnings in the Output Log

## 4. Per-Instance Color System

### 4.1 Material Change

**M_EchoMaster** gets a new `BaseColor` Vector Parameter (default: Cyan `0, 1, 1, 1`). This parameter multiplies into the emissive output where per-instance color differentiation currently occurs.

Existing Material Instances continue to work — they override `BaseColor` statically:
- `MI_EchoMaster`: Cyan (default)
- `MI_EchoObstacle`: Purple
- `MI_EchoPlayer`: Green
- `MI_EchoEnemy`: Red

### 4.2 DMI Source

Level Kit props create their Dynamic Material Instance from **`MI_EchoMaster`** (the base material instance), not from `M_EchoMaster` directly. This ensures all static parameter overrides from the MI carry over — only `BaseColor` is changed dynamically.

### 4.3 Blueprint Property

Each Level Kit Blueprint exposes:
- `PropColor` (`FLinearColor`, default Cyan, category "Echo|LevelKit", Instance Editable)

### 4.4 Construction Script Flow

```
1. Create Dynamic Material Instance from MI_EchoMaster
2. Set Vector Parameter "BaseColor" = PropColor
3. Apply DMI to all Static Mesh Components in the actor
```

### 4.5 Sonar Reveal Compatibility

M_EchoMaster's sonar reveal uses `WorldPosition` in the shader to compute distance from `LastImpactLocation` (MPC parameter). This is a world-space calculation — it works at any position and any scale. No shader changes are needed for the Level Kit props to reveal correctly under sonar pulses. Any mesh using M_EchoMaster (or a child MI/DMI) will automatically participate in the sonar reveal.

## 5. Level Kit Pieces

All pieces use UE5 engine basic shapes (`/Engine/BasicShapes/`). No external modeling.

**Collision:** All props use the **WorldStatic** object type with **BlockAll** collision preset. This ensures they interact correctly with the player's `LineTraceSingleByObjectType` floor detection (which queries WorldStatic + WorldDynamic) and block pawn movement.

### 5.1 BP_LevelWall
- **Mesh:** `/Engine/BasicShapes/Cube` scaled to (4.0, 0.5, 4.0) → 400×50×400 units
- **Collision:** Box (from mesh simple collision), WorldStatic/BlockAll
- **Default Color:** Cyan
- **Use:** Corridors, rooms, boundaries. Core structural piece.

### 5.2 BP_LevelRock
- **Mesh:** `/Engine/BasicShapes/Cone` scaled to (3.0, 3.0, 3.0) → R:150, H:300
- **Collision:** Convex (from mesh), WorldStatic/BlockAll
- **Default Color:** Cyan
- **Use:** Mountains, rocky outcrops. Scale up for peaks, cluster small ones for rocky terrain.

### 5.3 BP_LevelTree
- **Meshes:**
  - Trunk: `/Engine/BasicShapes/Cylinder` scaled to (0.5, 0.5, 4.0) → R:25, H:200
  - Canopy: `/Engine/BasicShapes/Sphere` scaled to (1.6, 1.6, 1.6) → R:80, offset Z+250
- **Collision:** Per-component simple collision, WorldStatic/BlockAll
- **Default Color:** Green
- **Use:** Forest areas. Compound shape — sonar sweeping over round canopies creates distinctive reveals.

### 5.4 BP_LevelCrate
- **Mesh:** `/Engine/BasicShapes/Cube` at default scale (1.0, 1.0, 1.0) → 100×100×100
- **Collision:** Box (from mesh), WorldStatic/BlockAll
- **Default Color:** Purple
- **Use:** Scattered obstacles, cover, stackable. Works in any environment.

### 5.5 BP_LevelRamp
- **Mesh:** `/Engine/BasicShapes/Cube` scaled to (2.0, 2.0, 1.5) → 200×200×150
- **Rotation:** Rotate the mesh component -30° on the Y axis to create the angled ramp surface
- **Collision:** Box collision component (manually sized to cover the visible mesh), WorldStatic/BlockAll
- **Default Color:** Cyan
- **Use:** Elevation changes, hillsides. Connects flat areas to raised platforms.
- **Note:** This is an approximation — a rotated box creates a slope but not a true triangular wedge. For a precise wedge, a simple 3-vertex static mesh can be imported later as an upgrade. The rotated cube is sufficient for prototyping.

## 6. Success Criteria

- All existing gameplay (movement, sonar, AI, HUD) works identically after plugin refactor.
- No Blueprint asset breakage — Core Redirects handle all class path remapping, verified by zero "missing class" log warnings.
- `NeoNexusOne` main module contains only a minimal stub.
- All 5 Level Kit props are placeable in the Editor with per-instance color tinting.
- Props reveal correctly under sonar pulses (sonar ring sweeps over them, grid/edges/cel-bands appear).
- Props block player movement and respond to floor trace (WorldStatic collision).
- A test level can be built mixing walls (indoor), rocks (mountain), and trees (forest) in one map.
