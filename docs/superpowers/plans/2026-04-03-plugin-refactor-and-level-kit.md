# Plugin Refactor & Modular Level Kit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extract all Echo gameplay C++ into an `EchoLocation` plugin, then build a 5-piece modular level kit as a content-only `EchoLevelKit` plugin with per-instance color tinting.

**Architecture:** Two-phase sequential work. Phase 1 creates the `EchoLocation` plugin, moves all existing C++ source files into it, updates API macros, adds Core Redirects in `DefaultEngine.ini` for Blueprint class path remapping, and strips the main `NeoNexusOne` module to a minimal stub. Phase 2 creates a content-only `EchoLevelKit` plugin with 5 Blueprint Actor props (wall, rock, tree, crate, ramp) that use Dynamic Material Instances from `MI_EchoMaster` for per-instance color tinting.

**Tech Stack:** Unreal Engine 5.6 C++, UMG, Material Parameter Collections, Blueprint Actors.

**Spec Reference:** `docs/superpowers/specs/2026-04-03-modular-level-kit-design.md`

**Rollback:** All changes are committed incrementally. If a build fails at any point, use `git log --oneline -5` to find the last good commit and `git checkout <hash> -- <files>` to restore specific files. The full original source is recoverable via git history.

---

## File Map

| File | Action | Responsibility |
|---|---|---|
| `Plugins/EchoLocation/EchoLocation.uplugin` | Create | Plugin descriptor |
| `Plugins/EchoLocation/Source/EchoLocation/EchoLocation.Build.cs` | Create | Module build rules (all dependencies) |
| `Plugins/EchoLocation/Source/EchoLocation/EchoLocationModule.h` | Create | Module interface header |
| `Plugins/EchoLocation/Source/EchoLocation/EchoLocationModule.cpp` | Create | Module registration |
| `Plugins/EchoLocation/Source/EchoLocation/Public/**` | Create (move) | All Echo gameplay headers |
| `Plugins/EchoLocation/Source/EchoLocation/Private/**` | Create (move) | All Echo gameplay implementations |
| `Source/NeoNexusOne/NeoNexusOne.Build.cs` | Modify | Strip to minimal deps |
| `Source/NeoNexusOne/Public/NeoNexusOne.h` | Keep | Minimal module header |
| `Source/NeoNexusOne/Private/NeoNexusOne.cpp` | Keep | Module registration stub |
| `Config/DefaultEngine.ini` | Modify | Add Core Redirects for class path remapping |
| `NeoNexusOne.uproject` | Modify | Add plugin entries (EchoLocation first, EchoLevelKit later) |
| `Plugins/EchoLevelKit/EchoLevelKit.uplugin` | Create | Content-only plugin descriptor |
| `Content/EchoLocation/Materials/M_EchoMaster.uasset` | Modify (Manual) | Add `BaseColor` vector parameter |

---

## Phase 1: EchoLocation Plugin Refactor

### Task 1: Create Plugin Scaffold

**Files:**
- Create: `Plugins/EchoLocation/EchoLocation.uplugin`
- Create: `Plugins/EchoLocation/Source/EchoLocation/EchoLocation.Build.cs`
- Create: `Plugins/EchoLocation/Source/EchoLocation/EchoLocationModule.h`
- Create: `Plugins/EchoLocation/Source/EchoLocation/EchoLocationModule.cpp`

- [ ] **Step 1: Create plugin directory structure**
```bash
mkdir -p "Plugins/EchoLocation/Source/EchoLocation/Public/Core"
mkdir -p "Plugins/EchoLocation/Source/EchoLocation/Public/Player"
mkdir -p "Plugins/EchoLocation/Source/EchoLocation/Public/Sound"
mkdir -p "Plugins/EchoLocation/Source/EchoLocation/Public/Feedback"
mkdir -p "Plugins/EchoLocation/Source/EchoLocation/Public/AI"
mkdir -p "Plugins/EchoLocation/Source/EchoLocation/Public/UI"
mkdir -p "Plugins/EchoLocation/Source/EchoLocation/Private/Core"
mkdir -p "Plugins/EchoLocation/Source/EchoLocation/Private/Player"
mkdir -p "Plugins/EchoLocation/Source/EchoLocation/Private/Sound"
mkdir -p "Plugins/EchoLocation/Source/EchoLocation/Private/Feedback"
mkdir -p "Plugins/EchoLocation/Source/EchoLocation/Private/AI"
mkdir -p "Plugins/EchoLocation/Source/EchoLocation/Private/UI"
```

- [ ] **Step 2: Create EchoLocation.uplugin**
```json
{
    "FileVersion": 3,
    "Version": 1,
    "VersionName": "1.0",
    "FriendlyName": "Echo Location",
    "Description": "Core gameplay module for Project: Echo-Location — sonar-based horror-puzzle game.",
    "Category": "Gameplay",
    "CreatedBy": "NeoNexusOne",
    "CanContainContent": false,
    "IsBetaVersion": false,
    "IsExperimentalVersion": false,
    "Installed": false,
    "Modules": [
        {
            "Name": "EchoLocation",
            "Type": "Runtime",
            "LoadingPhase": "Default"
        }
    ]
}
```

- [ ] **Step 3: Create EchoLocation.Build.cs**
```csharp
// Copyright NeoNexusOne. All Rights Reserved.

using UnrealBuildTool;
using System.IO;

public class EchoLocation : ModuleRules
{
    public EchoLocation(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

        PublicIncludePaths.AddRange(new string[] {
            ModuleDirectory,
            Path.Combine(ModuleDirectory, "Public")
        });

        PrivateIncludePaths.AddRange(new string[] {
            Path.Combine(ModuleDirectory, "Private")
        });

        PublicDependencyModuleNames.AddRange(new string[] {
            "Core",
            "CoreUObject",
            "Engine",
            "InputCore",
            "EnhancedInput"
        });

        PrivateDependencyModuleNames.AddRange(new string[] {
            "AIModule",
            "GameplayTasks",
            "NavigationSystem",
            "Slate",
            "SlateCore",
            "UMG"
        });
    }
}
```

- [ ] **Step 4: Create EchoLocationModule.h**
```cpp
// Copyright NeoNexusOne. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FEchoLocationModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

- [ ] **Step 5: Create EchoLocationModule.cpp**
```cpp
// Copyright NeoNexusOne. All Rights Reserved.

#include "EchoLocationModule.h"

#define LOCTEXT_NAMESPACE "FEchoLocationModule"

void FEchoLocationModule::StartupModule()
{
}

void FEchoLocationModule::ShutdownModule()
{
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FEchoLocationModule, EchoLocation)
```

**Note on `ECHOLOCATION_API`:** UBT automatically generates the `ECHOLOCATION_API` DLL export/import macro based on the module name in `EchoLocation.Build.cs`. No manual header is needed — UBT creates the macro definition and makes it available to all compilation units in the module. The moved headers that use `ECHOLOCATION_API` will compile correctly as long as they are part of this module.

- [ ] **Step 6: Commit scaffold**
```bash
git add Plugins/EchoLocation/
git commit -m "feat(plugin): create EchoLocation plugin scaffold"
```

---

### Task 2: Move Source Files into Plugin

**Files:**
- Move: All `.h` files from `Source/NeoNexusOne/Public/` (except `NeoNexusOne.h`) → `Plugins/EchoLocation/Source/EchoLocation/Public/`
- Move: All `.cpp` files from `Source/NeoNexusOne/Private/` (except `NeoNexusOne.cpp`) → `Plugins/EchoLocation/Source/EchoLocation/Private/`

Using `git mv` to preserve file history.

- [ ] **Step 1: Move header files**
```bash
# Core
git mv "Source/NeoNexusOne/Public/Core/EchoTypes.h" "Plugins/EchoLocation/Source/EchoLocation/Public/Core/"
git mv "Source/NeoNexusOne/Public/Core/EchoGameMode.h" "Plugins/EchoLocation/Source/EchoLocation/Public/Core/"
git mv "Source/NeoNexusOne/Public/Core/EchoPlayerController.h" "Plugins/EchoLocation/Source/EchoLocation/Public/Core/"

# Player
git mv "Source/NeoNexusOne/Public/Player/EchoPawn.h" "Plugins/EchoLocation/Source/EchoLocation/Public/Player/"
git mv "Source/NeoNexusOne/Public/Player/EchoMovementComponent.h" "Plugins/EchoLocation/Source/EchoLocation/Public/Player/"

# Sound
git mv "Source/NeoNexusOne/Public/Sound/EchoRippleManager.h" "Plugins/EchoLocation/Source/EchoLocation/Public/Sound/"

# Feedback
git mv "Source/NeoNexusOne/Public/Feedback/EchoFeedbackComponent.h" "Plugins/EchoLocation/Source/EchoLocation/Public/Feedback/"

# AI
git mv "Source/NeoNexusOne/Public/AI/EchoAIController.h" "Plugins/EchoLocation/Source/EchoLocation/Public/AI/"
git mv "Source/NeoNexusOne/Public/AI/EchoEnemyPawn.h" "Plugins/EchoLocation/Source/EchoLocation/Public/AI/"

# UI
git mv "Source/NeoNexusOne/Public/UI/EchoHUDWidget.h" "Plugins/EchoLocation/Source/EchoLocation/Public/UI/"
```

- [ ] **Step 2: Move implementation files**
```bash
# Core
git mv "Source/NeoNexusOne/Private/Core/EchoGameMode.cpp" "Plugins/EchoLocation/Source/EchoLocation/Private/Core/"
git mv "Source/NeoNexusOne/Private/Core/EchoPlayerController.cpp" "Plugins/EchoLocation/Source/EchoLocation/Private/Core/"

# Player
git mv "Source/NeoNexusOne/Private/Player/EchoPawn.cpp" "Plugins/EchoLocation/Source/EchoLocation/Private/Player/"
git mv "Source/NeoNexusOne/Private/Player/EchoMovementComponent.cpp" "Plugins/EchoLocation/Source/EchoLocation/Private/Player/"

# Sound
git mv "Source/NeoNexusOne/Private/Sound/EchoRippleManager.cpp" "Plugins/EchoLocation/Source/EchoLocation/Private/Sound/"

# Feedback
git mv "Source/NeoNexusOne/Private/Feedback/EchoFeedbackComponent.cpp" "Plugins/EchoLocation/Source/EchoLocation/Private/Feedback/"

# AI
git mv "Source/NeoNexusOne/Private/AI/EchoAIController.cpp" "Plugins/EchoLocation/Source/EchoLocation/Private/AI/"
git mv "Source/NeoNexusOne/Private/AI/EchoEnemyPawn.cpp" "Plugins/EchoLocation/Source/EchoLocation/Private/AI/"

# UI
git mv "Source/NeoNexusOne/Private/UI/EchoHUDWidget.cpp" "Plugins/EchoLocation/Source/EchoLocation/Private/UI/"
```

- [ ] **Step 3: Remove empty subdirectories**
```bash
rmdir "Source/NeoNexusOne/Public/Core" "Source/NeoNexusOne/Public/Player" "Source/NeoNexusOne/Public/Sound" "Source/NeoNexusOne/Public/Feedback" "Source/NeoNexusOne/Public/AI" "Source/NeoNexusOne/Public/UI"
rmdir "Source/NeoNexusOne/Private/Core" "Source/NeoNexusOne/Private/Player" "Source/NeoNexusOne/Private/Sound" "Source/NeoNexusOne/Private/Feedback" "Source/NeoNexusOne/Private/AI" "Source/NeoNexusOne/Private/UI"
```

- [ ] **Step 4: Commit file moves**
```bash
git add -A
git commit -m "refactor: move all Echo source files into EchoLocation plugin"
```

---

### Task 3: Update API Macros

**Files:**
- Modify: All 9 headers in `Plugins/EchoLocation/Source/EchoLocation/Public/`

- [ ] **Step 1: Replace NEONEXUSONE_API with ECHOLOCATION_API**
In each of these files, find `NEONEXUSONE_API` and replace with `ECHOLOCATION_API`:

| File | Line |
|------|------|
| `Public/Core/EchoGameMode.h` | `class ECHOLOCATION_API AEchoGameMode : public AGameModeBase` |
| `Public/Core/EchoPlayerController.h` | `class ECHOLOCATION_API AEchoPlayerController : public APlayerController` |
| `Public/Player/EchoPawn.h` | `class ECHOLOCATION_API AEchoPawn : public APawn` |
| `Public/Player/EchoMovementComponent.h` | `class ECHOLOCATION_API UEchoMovementComponent : public UPawnMovementComponent` |
| `Public/Sound/EchoRippleManager.h` | `class ECHOLOCATION_API UEchoRippleManager : public UActorComponent` |
| `Public/Feedback/EchoFeedbackComponent.h` | `class ECHOLOCATION_API UEchoFeedbackComponent : public UActorComponent` |
| `Public/AI/EchoAIController.h` | `class ECHOLOCATION_API AEchoAIController : public AAIController` |
| `Public/AI/EchoEnemyPawn.h` | `class ECHOLOCATION_API AEchoEnemyPawn : public APawn` |
| `Public/UI/EchoHUDWidget.h` | `class ECHOLOCATION_API UEchoHUDWidget : public UUserWidget` |

All paths relative to `Plugins/EchoLocation/Source/EchoLocation/`.

- [ ] **Step 2: Commit macro changes**
```bash
git add Plugins/EchoLocation/Source/EchoLocation/Public/
git commit -m "refactor: replace NEONEXUSONE_API with ECHOLOCATION_API in all plugin headers"
```

---

### Task 4: Add Core Redirects & Update Main Module

**Files:**
- Modify: `Config/DefaultEngine.ini`
- Modify: `Source/NeoNexusOne/NeoNexusOne.Build.cs`
- Modify: `NeoNexusOne.uproject`

- [ ] **Step 1: Add Core Redirects to DefaultEngine.ini**
Open (or create) `Config/DefaultEngine.ini` and append the following section. If the file already has content, add this at the end:
```ini
[CoreRedirects]
+ClassRedirects=(OldName="/Script/NeoNexusOne.EchoPawn", NewName="/Script/EchoLocation.EchoPawn")
+ClassRedirects=(OldName="/Script/NeoNexusOne.EchoMovementComponent", NewName="/Script/EchoLocation.EchoMovementComponent")
+ClassRedirects=(OldName="/Script/NeoNexusOne.EchoGameMode", NewName="/Script/EchoLocation.EchoGameMode")
+ClassRedirects=(OldName="/Script/NeoNexusOne.EchoPlayerController", NewName="/Script/EchoLocation.EchoPlayerController")
+ClassRedirects=(OldName="/Script/NeoNexusOne.EchoRippleManager", NewName="/Script/EchoLocation.EchoRippleManager")
+ClassRedirects=(OldName="/Script/NeoNexusOne.EchoFeedbackComponent", NewName="/Script/EchoLocation.EchoFeedbackComponent")
+ClassRedirects=(OldName="/Script/NeoNexusOne.EchoAIController", NewName="/Script/EchoLocation.EchoAIController")
+ClassRedirects=(OldName="/Script/NeoNexusOne.EchoEnemyPawn", NewName="/Script/EchoLocation.EchoEnemyPawn")
+ClassRedirects=(OldName="/Script/NeoNexusOne.EchoHUDWidget", NewName="/Script/EchoLocation.EchoHUDWidget")
+EnumRedirects=(OldName="/Script/NeoNexusOne.EEchoMovementState", NewName="/Script/EchoLocation.EEchoMovementState")
+EnumRedirects=(OldName="/Script/NeoNexusOne.EEchoAIState", NewName="/Script/EchoLocation.EEchoAIState")
+StructRedirects=(OldName="/Script/NeoNexusOne.EchoRippleEvent", NewName="/Script/EchoLocation.EchoRippleEvent")
```

These redirects ensure all existing Blueprint assets (BP_EchoPawn, BP_EchoGameMode, BP_EchoPlayerController, WBP_InkedHUD, etc.) find their C++ parent classes in the new module without manual re-parenting.

- [ ] **Step 2: Strip NeoNexusOne.Build.cs to minimal stub**
Replace the entire contents with:
```csharp
// Copyright NeoNexusOne. All Rights Reserved.

using UnrealBuildTool;

public class NeoNexusOne : ModuleRules
{
    public NeoNexusOne(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

        PublicDependencyModuleNames.AddRange(new string[] {
            "Core",
            "CoreUObject",
            "Engine"
        });
    }
}
```

- [ ] **Step 3: Update NeoNexusOne.uproject — add EchoLocation only**
Replace the entire contents with:
```json
{
    "FileVersion": 3,
    "EngineAssociation": "5.6",
    "Category": "",
    "Description": "",
    "Modules": [
        {
            "Name": "NeoNexusOne",
            "Type": "Runtime",
            "LoadingPhase": "Default"
        }
    ],
    "Plugins": [
        {
            "Name": "ModelingToolsEditorMode",
            "Enabled": true,
            "TargetAllowList": [
                "Editor"
            ]
        },
        {
            "Name": "PythonScriptPlugin",
            "Enabled": true
        },
        {
            "Name": "EditorScriptingUtilities",
            "Enabled": true
        },
        {
            "Name": "EchoLocation",
            "Enabled": true
        }
    ]
}
```

Note: `EchoLevelKit` is NOT added yet — it doesn't exist on disk until Task 6.

- [ ] **Step 4: Commit**
```bash
git add Config/DefaultEngine.ini Source/NeoNexusOne/NeoNexusOne.Build.cs NeoNexusOne.uproject
git commit -m "refactor: add Core Redirects, strip main module to stub, enable EchoLocation plugin"
```

---

### Task 5: Build & Verify Plugin Refactor

- [ ] **Step 1: Close Unreal Editor**
The Editor must be closed before rebuilding. Hot reload / Live Coding is unreliable for this project.

- [ ] **Step 2: Regenerate project files**
Right-click `NeoNexusOne.uproject` → "Generate Visual Studio project files" (or run `GenerateProjectFiles.bat` from the engine).

- [ ] **Step 3: Rebuild solution**
Open the `.sln` in VS/Rider and build the `NeoNexusOneEditor` target. Verify:
- Build succeeds with 0 errors
- DLL timestamp for `EchoLocation` is newer than source timestamps
- No linker errors about missing symbols

If build fails: check `ECHOLOCATION_API` — UBT should generate it automatically. If it doesn't, verify `EchoLocation.Build.cs` module name matches `.uplugin` module name exactly.

- [ ] **Step 4: Open Editor and test in PIE**
Open `NeoNexusOne.uproject` in the Editor. Verify in Output Log:
- No "missing class" or "unknown class" warnings
- `EchoLocation` module loads (check `LogModuleManager`)
- Core Redirects are working (no "failed to find class" errors)

Play in Editor and verify:
- Player spawns and moves (Glide/Drop/Slam)
- Sonar ripples fire on impact and reveal geometry
- HUD signal bar appears, decays on impact, resets
- No crashes or assertion failures

- [ ] **Step 5: Commit verification note**
```bash
git commit --allow-empty -m "chore: verified EchoLocation plugin refactor — PIE test passed"
```

---

## Phase 2: Modular Level Kit

### Task 6: Create EchoLevelKit Plugin Scaffold

**Files:**
- Create: `Plugins/EchoLevelKit/EchoLevelKit.uplugin`
- Modify: `NeoNexusOne.uproject`

- [ ] **Step 1: Create plugin directory**
```bash
mkdir -p "Plugins/EchoLevelKit/Content/LevelKit"
```

- [ ] **Step 2: Create EchoLevelKit.uplugin**
```json
{
    "FileVersion": 3,
    "Version": 1,
    "VersionName": "1.0",
    "FriendlyName": "Echo Level Kit",
    "Description": "Modular level building props for Project: Echo-Location — stylized geometric primitives with per-instance color.",
    "Category": "Gameplay",
    "CreatedBy": "NeoNexusOne",
    "CanContainContent": true,
    "IsBetaVersion": false,
    "IsExperimentalVersion": false,
    "Installed": false
}
```

Note: No `Modules` array — this is a content-only plugin.

- [ ] **Step 3: Add EchoLevelKit to NeoNexusOne.uproject**
Add the following entry to the `Plugins` array in `NeoNexusOne.uproject`, after the `EchoLocation` entry:
```json
        {
            "Name": "EchoLevelKit",
            "Enabled": true
        }
```

- [ ] **Step 4: Commit**
```bash
git add Plugins/EchoLevelKit/ NeoNexusOne.uproject
git commit -m "feat(levelkit): create EchoLevelKit content-only plugin scaffold"
```

---

### Task 7: Add BaseColor Parameter to M_EchoMaster (Manual Editor Steps)

**Files:**
- Modify: `Content/EchoLocation/Materials/M_EchoMaster.uasset`

- [ ] **Step 1: Open M_EchoMaster in the Material Editor**
1. Content Browser → `Content/EchoLocation/Materials/M_EchoMaster`
2. Double-click to open

- [ ] **Step 2: Add BaseColor Vector Parameter**
1. Right-click in the graph → create a `VectorParameter` node
2. Name it exactly `BaseColor`
3. Set default value to Cyan: R=0, G=1, B=1, A=1

- [ ] **Step 3: Multiply into emissive output**
1. Find the **last node connected to the Material Result node's Emissive Color input pin** — this is where all color calculations combine before final output
2. Disconnect that node from the Emissive Color pin
3. Add a `Multiply` node
4. Connect the previously-connected node to Multiply input A
5. Connect `BaseColor` (RGB) to Multiply input B
6. Connect the Multiply result to the Material Result's Emissive Color pin

This makes `BaseColor` act as a color tint. Since the default is Cyan (0,1,1) and existing colors are already cyan-based, the default appearance is unchanged. Material Instances (MI_EchoObstacle, MI_EchoPlayer, MI_EchoEnemy) can override `BaseColor` statically, and Level Kit props override it dynamically via DMI.

- [ ] **Step 4: Verify existing materials still work**
1. Save M_EchoMaster
2. Open PIE
3. Verify: Floor/walls still appear cyan under sonar, obstacles still purple, player still green
4. If any colors look wrong, check that the Multiply node is between the last color computation and the Emissive Color pin (should tint, not replace)

- [ ] **Step 5: Commit material change**
```bash
git add Content/EchoLocation/Materials/M_EchoMaster.uasset
git commit -m "feat(materials): add BaseColor vector parameter to M_EchoMaster for per-instance tinting"
```

---

### Task 8: Create BP_LevelWall (Manual Editor Steps)

**Files:**
- Create: `Plugins/EchoLevelKit/Content/LevelKit/BP_LevelWall.uasset`

- [ ] **Step 1: Create Blueprint Actor**
1. Content Browser → navigate to `Plugins/EchoLevelKit Content/LevelKit/`
   (Enable "Show Plugin Content" in Content Browser settings if not visible)
2. Right-click → Blueprint Class → Actor
3. Name it `BP_LevelWall`

- [ ] **Step 2: Add Static Mesh Component**
1. Open BP_LevelWall
2. Add Component → Static Mesh
3. Set Static Mesh to `/Engine/BasicShapes/Cube`
4. Set Scale to (4.0, 0.5, 4.0) → 400×50×400 units
5. Set Collision Preset to `BlockAll`
6. Set Collision Object Type to `WorldStatic`

- [ ] **Step 3: Add PropColor variable**
1. In the Variables panel, add a new variable `PropColor`
2. Type: `Linear Color`
3. Default value: (R=0, G=1, B=1, A=1) — Cyan
4. Check "Instance Editable" and "Expose on Spawn"
5. Category: "Echo|LevelKit"

- [ ] **Step 4: Construction Script — create DMI and apply color**
1. Open the Construction Script graph
2. Add a `Create Dynamic Material Instance` node
   - Source Material: `MI_EchoMaster` (from `Content/EchoLocation/Materials/`)
   - Element Index: 0
3. From the return value, add `Set Vector Parameter Value`
   - Parameter Name: `BaseColor`
   - Value: drag in the `PropColor` variable
4. Add `Set Material` on the StaticMesh component
   - Material: the DMI from step 2
   - Element Index: 0
5. Compile and Save

- [ ] **Step 5: Test**
1. Place `BP_LevelWall` in `L_EchoPrototype`
2. In Details panel, change `PropColor` to orange
3. PIE: Verify wall reveals under sonar with the orange tint
4. Verify wall blocks player movement

---

### Task 9: Create BP_LevelRock (Manual Editor Steps)

**Files:**
- Create: `Plugins/EchoLevelKit/Content/LevelKit/BP_LevelRock.uasset`

- [ ] **Step 1: Create Blueprint Actor**
1. Content Browser → `Plugins/EchoLevelKit Content/LevelKit/`
2. Right-click → Blueprint Class → Actor → `BP_LevelRock`

- [ ] **Step 2: Add Static Mesh Component**
1. Add Component → Static Mesh
2. Set Static Mesh to `/Engine/BasicShapes/Cone`
3. Set Scale to (3.0, 3.0, 3.0) → R:150, H:300
4. Collision Preset: `BlockAll`, Object Type: `WorldStatic`

- [ ] **Step 3: Add PropColor variable**
Same as BP_LevelWall Step 3. Default: Cyan (0, 1, 1, 1).

- [ ] **Step 4: Construction Script**
Same DMI pattern as BP_LevelWall Step 4. Source: `MI_EchoMaster`, parameter: `BaseColor`, value: `PropColor`.

- [ ] **Step 5: Test**
1. Place in level, scale up to (5, 5, 8) for a mountain peak
2. Place 3 small ones clustered for rocky terrain
3. PIE: Verify sonar reveals the cone geometry, color tinting works

---

### Task 10: Create BP_LevelTree (Manual Editor Steps)

**Files:**
- Create: `Plugins/EchoLevelKit/Content/LevelKit/BP_LevelTree.uasset`

- [ ] **Step 1: Create Blueprint Actor**
1. Content Browser → `Plugins/EchoLevelKit Content/LevelKit/`
2. Right-click → Blueprint Class → Actor → `BP_LevelTree`

- [ ] **Step 2: Add Trunk mesh component**
1. Add Component → Static Mesh (name it `Trunk`)
2. Set Static Mesh to `/Engine/BasicShapes/Cylinder`
3. Set Scale to (0.5, 0.5, 4.0) → R:25, H:200
4. Collision Preset: `BlockAll`, Object Type: `WorldStatic`

- [ ] **Step 3: Add Canopy mesh component**
1. Add Component → Static Mesh (name it `Canopy`), as child of `Trunk`
2. Set Static Mesh to `/Engine/BasicShapes/Sphere`
3. Set Scale to (1.6, 1.6, 1.6) → R:80
4. Set Relative Location to (0, 0, 250) to sit on top of the trunk
5. Collision Preset: `BlockAll`, Object Type: `WorldStatic`

- [ ] **Step 4: Add PropColor variable**
Same pattern. Default: Green (0, 0.8, 0.2, 1).

- [ ] **Step 5: Construction Script**
Same DMI pattern, but apply the material to **both** mesh components:
1. Create Dynamic Material Instance from `MI_EchoMaster`
2. Set Vector Parameter `BaseColor` = `PropColor`
3. Set Material on `Trunk` (Element Index 0)
4. Set Material on `Canopy` (Element Index 0) — reuse the same DMI

- [ ] **Step 6: Test**
1. Place 5-6 trees in a cluster to create a forest area
2. PIE: Verify sonar sweeps over the round canopies — should create distinctive circular reveals
3. Verify green tinting, verify player is blocked by trunk collision

---

### Task 11: Create BP_LevelCrate (Manual Editor Steps)

**Files:**
- Create: `Plugins/EchoLevelKit/Content/LevelKit/BP_LevelCrate.uasset`

- [ ] **Step 1: Create Blueprint Actor**
1. Content Browser → `Plugins/EchoLevelKit Content/LevelKit/`
2. Right-click → Blueprint Class → Actor → `BP_LevelCrate`

- [ ] **Step 2: Add Static Mesh Component**
1. Add Component → Static Mesh
2. Set Static Mesh to `/Engine/BasicShapes/Cube`
3. Keep Scale at (1.0, 1.0, 1.0) → 100×100×100
4. Collision Preset: `BlockAll`, Object Type: `WorldStatic`

- [ ] **Step 3: Add PropColor variable**
Same pattern. Default: Purple (0.5, 0, 1, 1).

- [ ] **Step 4: Construction Script**
Same DMI pattern as BP_LevelWall.

- [ ] **Step 5: Test**
1. Place several crates, stack some on top of each other
2. PIE: Verify sonar reveal, purple tinting, collision blocking

---

### Task 12: Create BP_LevelRamp (Manual Editor Steps)

**Files:**
- Create: `Plugins/EchoLevelKit/Content/LevelKit/BP_LevelRamp.uasset`

- [ ] **Step 1: Create Blueprint Actor**
1. Content Browser → `Plugins/EchoLevelKit Content/LevelKit/`
2. Right-click → Blueprint Class → Actor → `BP_LevelRamp`

- [ ] **Step 2: Add Static Mesh Component**
1. Add Component → Static Mesh
2. Set Static Mesh to `/Engine/BasicShapes/Cube`
3. Set Scale to (2.0, 2.0, 1.5) → 200×200×150
4. Set Rotation on the mesh component: Pitch (Y) = -30°
   (This tilts the cube to create a ramp-like slope)
5. Collision Preset: `BlockAll`, Object Type: `WorldStatic`

- [ ] **Step 3: Add Box Collision Component**
1. Add Component → Box Collision (as child of root, NOT the mesh)
2. Scale and position the box to cover the visible mesh area
3. This provides a walkable collision surface for the ramp
4. Set Collision Preset: `BlockAll`, Object Type: `WorldStatic`

- [ ] **Step 4: Add PropColor variable**
Same pattern. Default: Cyan (0, 1, 1, 1).

- [ ] **Step 5: Construction Script**
Same DMI pattern as BP_LevelWall.

- [ ] **Step 6: Test**
1. Place ramp connecting the floor to a raised crate stack
2. PIE: Verify sonar reveal, color tinting
3. Verify player can glide up the ramp surface
4. Note: This is an approximation — a rotated cube is not a true wedge. If the slope feels wrong, adjust the Pitch angle or replace with a custom wedge mesh later.

---

### Task 13: Build a Test Scene (Manual Editor Steps)

- [ ] **Step 1: Create a mixed-environment test area in L_EchoPrototype**
Using the 5 props, build a small test area that demonstrates all three environments:
1. **Indoor section:** 4 walls forming a room, a doorway opening made by leaving a gap between two walls
2. **Rocky outdoor section:** 3-4 rocks at various scales (small clusters + one large peak)
3. **Forest section:** 5-6 trees in a cluster
4. Scatter crates throughout as obstacles
5. Use a ramp to connect a raised platform to the floor

- [ ] **Step 2: Color-code the environments**
Using per-instance `PropColor`:
- Indoor walls: Cyan (default)
- Rocks: warm orange (1.0, 0.5, 0.1)
- Trees: green (default)
- Crates: purple (default)
- Ramp: cyan (default)

- [ ] **Step 3: PIE verification**
Verify in Play-In-Editor:
- All props reveal under sonar pulses with correct colors
- All props block player movement (WorldStatic collision)
- Player floor trace works on all surfaces (no falling through)
- Sonar ring sweeps create visually interesting reveals on varied geometry (cone peaks, sphere canopies, flat walls)
- HUD signal bar works normally

- [ ] **Step 4: Commit test scene and all Level Kit assets**
```bash
git add Content/EchoLocation/Maps/L_EchoPrototype.umap
git add Plugins/EchoLevelKit/Content/
git commit -m "feat(levelkit): add 5 modular level props and test scene with per-instance color"
```

---

### Task 14: Update STATUS.md

**Files:**
- Modify: `STATUS.md`

- [ ] **Step 1: Mark Modular Level Kit as complete**
Update the Milestone 2 section to check off the Modular Level Kit item and add a description of what was built.

- [ ] **Step 2: Update Technical Health section**
- Add note about two-plugin architecture (EchoLocation + EchoLevelKit)
- Update Next Priority to Milestone 3

- [ ] **Step 3: Commit**
```bash
git add STATUS.md
git commit -m "docs: update STATUS.md — Milestone 2 complete"
```
