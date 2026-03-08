# QWEN.md - NeoNexusOne: Echo-Location

## Project Overview

**NeoNexusOne** is an Unreal Engine 5.6 project implementing **Project: Echo-Location**, a minimalist horror-puzzle game where "sound is your only sight, but also your greatest danger."

### Core Concept
The player controls a cube in total darkness. Physical impacts generate "Vision Ripples" that briefly reveal the environment via emissive material effects. However, sound also attracts enemy "Corrupted Cubes," creating a risk-reward loop between visibility and safety.

### Key Mechanics
| State | Trigger | Sound | Visual |
|-------|---------|-------|--------|
| **Idle** | No input | Silent | Total darkness |
| **Glide** | Movement input | Silent | Hover +20 units, 0% visibility |
| **Drop** | Release input | Medium "Clunk" | Mid-range ripple (~800 units) |
| **Slam Jump** | Active input | Loud "Boom" | Room-wide ripple (~2000 units) |

### Main Technologies
- **Engine:** Unreal Engine 5.6
- **Renderer:** DX12, SM6, Lumen GI, Virtual Shadow Maps, ray tracing enabled
- **Input:** UE5 Enhanced Input System
- **Visuals:** Material Parameter Collections (MPC) + SphereMask ripple shaders
- **AI:** AIPerception/PawnSensing reacting to `ReportNoiseEvent`
- **Audio:** 48kHz sample rate, 3D spatial audio

---

## Project Structure

```
NeoNexusOne/
├── Config/                    # Engine/Game configuration (.ini files)
├── Content/                   # Unreal assets (Blueprints, Materials, Maps)
├── Source/
│   ├── NeoNexusOne.Target.cs       # Game target (shipping/standalone)
│   ├── NeoNexusOneEditor.Target.cs # Editor target (development)
│   └── NeoNexusOne/                # Main module
│       ├── NeoNexusOne.Build.cs    # Module dependencies
│       ├── NeoNexusOne.h/.cpp      # Module registration
│       ├── Core/
│       │   ├── EchoTypes.h         # Enums, structs, constants
│       │   ├── EchoGameMode.h/.cpp # GameMode with RippleManager
│       │   └── EchoPlayerController.h/.cpp # Input mapping context setup
│       ├── Sound/
│       │   └── EchoRippleManager.h/.cpp # MPC-driven ripple animation
│       ├── Player/
│       │   ├── EchoPawn.h/.cpp           # Player pawn with components
│       │   └── EchoMovementComponent.h/.cpp # Glide/Drop/SlamJump physics
│       └── Feedback/
│           └── EchoFeedbackComponent.h/.cpp # Camera shake + haptics
├── reviews/
│   └── Code-Review.md          # Code review findings (READ-ONLY)
├── Project_EchoLocation.md     # Game design document
├── CLAUDE.md                   # AI assistant context (build/run instructions)
├── GEMINI.md                   # AI assistant context (project overview)
└── NeoNexusOne.uproject        # UE5 project descriptor
```

---

## Building and Running

### Prerequisites
- **Unreal Engine 5.6** (set in `NeoNexusOne.uproject`)
- **Visual Studio 2022** or **JetBrains Rider 2025.3+**

### Build Commands
```bash
# Open in Editor (primary workflow)
"<UE5_INSTALL>/Engine/Binaries/Win64/UnrealEditor-Cmd.exe" NeoNexusOne.uproject

# Or use RunUAT for automated builds
"<UE5_INSTALL>/Engine/Build/BatchFiles/RunUAT.bat" BuildCookRun -project=NeoNexusOne.uproject

# Generate Visual Studio solution
<UE5_INSTALL>/Engine/Build/BatchFiles/GenerateProjectFiles.bat NeoNexusOne.uproject
```

### IDE Workflow
1. Open `NeoNexusOne.sln` in Visual Studio or Rider
2. Build `NeoNexusOneEditor` target (Development configuration)
3. Open `NeoNexusOne.uproject` in the Editor
4. Use **Play-In-Editor (PIE)** for testing

### Testing
- No automated test framework configured
- All testing done through PIE (Play-In-Editor)
- Logs located in `./Saved/Logs/`

---

## Architecture

### Module Dependencies
```csharp
Public:  Core, CoreUObject, Engine, InputCore, EnhancedInput
Private: AIModule, GameplayTasks, NavigationSystem
```

### Core Classes

| Class | Type | Purpose |
|-------|------|---------|
| `EEchoMovementState` | Enum | Idle/Glide/Drop/SlamJump states |
| `FEchoRippleEvent` | Struct | Ripple payload (Location, Radius, Intensity, NoiseVolume) |
| `EchoDefaults` | Namespace | Tunable constants (hover height, radii, intensities) |
| `EchoMPCParams` | Namespace | Inline FName constants for MPC parameters |
| `UEchoRippleManager` | UActorComponent | MPC-driven ripple animation authority |
| `AEchoGameMode` | AGameModeBase | Owns RippleManager, sets default pawn/controller |
| `AEchoPlayerController` | APlayerController | Adds Enhanced Input mapping context |
| `AEchoPawn` | APawn | Player cube with all components attached |
| `UEchoMovementComponent` | UPawnMovementComponent | Glide physics, gravity, impact detection |
| `UEchoFeedbackComponent` | UActorComponent | Camera shake + force feedback playback |

### Sound-Vision Technical Flow
```
1. Player pawn detects impact (Drop/Slam)
2. MovementComponent broadcasts OnEchoImpact delegate
3. EchoPawn builds FEchoRippleEvent with location + parameters
4. Calls UEchoRippleManager::TriggerRipple() via GameMode
5. FTimeline animates normalized 0→1 alpha over RippleDuration
6. OnRippleTimelineUpdate() samples curves, computes Radius/Intensity
7. UpdateMPC() writes to MPC_GlobalSound via UKismetMaterialLibrary
8. M_EchoMaster material reads MPC, applies SphereMask ring to Emissive
9. All cubes with M_EchoMaster reveal edges as ripple passes
```

### MPC Parameters (MPC_GlobalSound)
| Parameter | Type | Purpose |
|-----------|------|---------|
| `LastImpactLocation` | Vector (packed as FLinearColor) | Ripple center in world space |
| `CurrentRippleRadius` | Scalar | Expanding ring radius |
| `RippleIntensity` | Scalar | Emissive brightness multiplier |

---

## Development Conventions

### Code Style
- **Naming:** UE5 conventions (`U` prefix for classes, `F` for structs, `A` for actors)
- **Headers:** `#pragma once`, GENERATED_BODY(), UPROPERTY/UFUNCTION macros
- **Constants:** Use `inline const` for header constants (EchoMPCParams namespace)
- **Logging:** `UE_LOG(LogTemp, Level, TEXT("..."))`

### Sound-Vision Implementation Rules
1. All interactive objects must use `M_EchoMaster` material
2. Material must read from `MPC_GlobalSound` (never hardcode ripple logic)
3. Use `SphereMask(Distance(WorldPos, ImpactLoc), RippleRadius)` for ring effect
4. Connect mask output to Emissive Color

### Movement/Physics Rules
- Glide: Apply XY movement + `VInterpTo` hover (+20Z)
- Drop/Slam: Trigger `UEchoRippleManager::TriggerRipple()` + `MakeNoise()`
- Use `CheckGroundContact()` line trace for impact detection

### AI Behavior Rules
- Use `AIPerception` component with hearing sense
- Active Slam: High priority → move to `LastImpactLocation`
- Passive Drop: Low priority → chase if within short radius

### Aesthetic Standards ("The Juice")
- **Camera Shake:** Subtle on Drop, violent on Slam
- **Haptics:** `PlayDynamicForceFeedback()` scaled by ripple intensity
- **Audio-Visual Sync:** Ripple speed matches reverb tail decay

---

## Current Implementation Status

### Completed (Milestone 1 Foundation)
- ✅ `EchoTypes.h` — Movement states, ripple event struct, constants
- ✅ `EchoRippleManager` — MPC-driven ripple animation with FTimeline
- ✅ `EchoGameMode` — GameMode owning RippleManager
- ✅ `EchoPlayerController` — Enhanced Input mapping context setup
- ✅ `EchoPawn` — Player pawn with all components
- ✅ `EchoMovementComponent` — Glide/Drop/SlamJump physics + impact detection
- ✅ `EchoFeedbackComponent` — Camera shake + force feedback

### Code Review Issues (Resolved in Current Implementation)
| Severity | Issue | Status |
|----------|-------|--------|
| LOW | AI modules should be private dependencies | ✅ Fixed |
| LOW | Use `inline` for header constants | ✅ Fixed in EchoTypes.h |
| MEDIUM | FTimeline should be UPROPERTY | ⚠️ Pending |
| HIGH | Component ticks when idle | ✅ Fixed (bStartWithTickEnabled=false) |
| HIGH | Inconsistent animation scaling | ✅ Fixed (normalized alpha approach) |
| MEDIUM | Missing EchoMPC validation | ✅ Fixed (BeginPlay error log) |

### Remaining Milestone 1 Tasks
- [ ] Editor: Create MPC_GlobalSound asset with 3 parameters
- [ ] Editor: Create M_EchoMaster material reading MPC params
- [ ] Editor: Create C_RippleRadius curve (0→1 ease-out, 1.5s)
- [ ] Editor: Create C_RippleIntensity curve (1→0 fade, 1.5s)
- [ ] Editor: Create BP_EchoGameMode subclass with EchoMPC reference
- [ ] Editor: Create BP_EchoPawn subclass with mesh + input actions
- [ ] Editor: Create Input Actions (IA_Move, IA_Look, IA_Slam)
- [ ] Editor: Create Input Mapping Context (IMC_EchoDefault)
- [ ] Editor: Create prototype map with test cubes

---

## Debugging Guidelines

### Log Locations
- Runtime logs: `./Saved/Logs/`
- Rider build logs: `%LOCALAPPDATA%\JetBrains\Rider2025.3\log\SolutionBuilder`

### Common Error Patterns
- `LogWindows: Error` — Runtime crash (check call stack)
- `LogScript: Warning` — Blueprint/Reflection issues
- `EchoRippleManager: EchoMPC is null` — MPC asset not assigned in Blueprint

### Debug Workflow
1. Check last 100 lines of `./Saved/Logs/NeoNexusOne.log`
2. Verify MPC_GlobalSound exists and is assigned to `EchoMPC` property
3. Verify RippleRadiusCurve is set in Blueprint
4. Confirm M_EchoMaster material uses correct MPC parameter names

---

## Development Milestones

| Milestone | Name | Goal |
|-----------|------|------|
| 1 | **The Greybox** | Cube movement + basic Drop/Slam vision ripple |
| 2 | **The Threat** | AI cubes react to Slam events |
| 3 | **The Puzzle** | Blind Gliding through obstacle courses |
| 4 | **Atmosphere** | 3D spatial audio + post-processing |

---

## Important Notes

### READ-ONLY Files
- `reviews/Code-Review.md` — Maintained by review agent, do not modify

### Editor Asset Dependencies
The C++ code expects these Editor-created assets:
1. `MPC_GlobalSound` — Material Parameter Collection with 3 parameters
2. `M_EchoMaster` — Master material reading MPC params
3. `C_RippleRadius` — Float curve (0→1 ease-out, 1.5s duration)
4. `C_RippleIntensity` — Float curve (1→0 fade, 1.5s duration)
5. `BP_EchoGameMode` — Blueprint subclass with EchoMPC reference assigned
6. `BP_EchoPawn` — Blueprint subclass with mesh + input actions assigned
7. `IA_Move`, `IA_Look`, `IA_Slam` — Input Actions
8. `IMC_EchoDefault` — Input Mapping Context

### Known Limitations
- **Single active ripple:** New ripples overwrite current (acceptable for Milestone 1)
- **Future enhancement:** MPC array parameters or Niagara for multi-ripple support
