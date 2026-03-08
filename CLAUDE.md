# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**NeoNexusOne** is the repository for **Project: Echo-Location**, a minimalist horror-puzzle game built in **Unreal Engine 5.6**. The player controls a cube in total darkness, using physics-based impacts to generate "Vision Ripples" that briefly reveal the environment. Sound also attracts enemy "Corrupted Cubes", creating a risk-reward loop between visibility and safety.

## Build & Run

- **Engine:** Unreal Engine 5.6 (set in `NeoNexusOne.uproject`)
- **IDE:** Visual Studio 2022 (solution: `NeoNexusOne.sln`) or JetBrains Rider
- **Build from CLI:** Use Unreal Build Tool via `UnrealBuildTool` or `RunUAT.bat` from the engine installation
- **Build from IDE:** Open `.sln` in VS/Rider, build the `NeoNexusOneEditor` target for development
- **Run/Test:** Open `NeoNexusOne.uproject` in the Editor, use Play-In-Editor (PIE)
- **No custom test framework or linter is configured** — testing is done through PIE

## Architecture

Single module project (`NeoNexusOne`, Runtime, Default loading phase).

**Module dependencies** (from `Build.cs`):
- **Public:** Core, CoreUObject, Engine, InputCore, EnhancedInput
- **Private:** AIModule, GameplayTasks, NavigationSystem

**Include path:** `PublicIncludePaths` includes `ModuleDirectory`, so headers can be included with subfolder-relative paths (e.g., `#include "Core/EchoTypes.h"`) from anywhere in the module.

### Source Layout

```
Source/NeoNexusOne/
    Core/
        EchoTypes.h                    # Shared enums, structs, constants (no .cpp)
        EchoGameMode.h/.cpp            # AEchoGameMode — owns UEchoRippleManager, sets default pawn/controller
        EchoPlayerController.h/.cpp    # AEchoPlayerController — adds Enhanced Input mapping context on BeginPlay
    Player/
        EchoPawn.h/.cpp                # AEchoPawn : APawn — cube mesh, box collision, camera, input, impact→ripple flow
        EchoMovementComponent.h/.cpp   # UEchoMovementComponent : UPawnMovementComponent — glide/hover/drop/slam state machine
    Sound/
        EchoRippleManager.h/.cpp       # UEchoRippleManager : UActorComponent — FTimeline-driven MPC updates
    Feedback/
        EchoFeedbackComponent.h/.cpp   # UEchoFeedbackComponent : UActorComponent — camera shake + haptics
```

### Core Data Flow

1. **Input** → `AEchoPawn` receives Enhanced Input actions (Move, Look, Slam)
2. **Movement** → `UEchoMovementComponent` processes state machine (Glide/Drop/SlamJump), fires `OnEchoImpact` delegate on landing
3. **Ripple** → `AEchoPawn::OnImpact()` builds `FEchoRippleEvent`, calls `UEchoRippleManager::TriggerRipple()` on the GameMode's manager
4. **MPC Update** → `UEchoRippleManager` animates `MPC_GlobalSound` parameters via `FTimeline` + `UKismetMaterialLibrary` — all materials using the MPC see changes instantly
5. **AI Noise** → `AEchoPawn` calls `MakeNoise()` on impact, enemies use `AIPerception`/`PawnSensing` to detect it
6. **Feedback** → `UEchoFeedbackComponent::PlayFeedback()` triggers camera shake + force feedback based on movement state

### Key Types (EchoTypes.h)

- `EEchoMovementState` — Idle, Glide, Drop, SlamJump
- `FEchoRippleEvent` — ImpactLocation, MaxRadius, Intensity, NoiseVolume
- `EchoDefaults` namespace — GlideHoverHeight (20), DropRippleRadius (800), SlamRippleRadius (2000), etc.
- `EchoMPCParams` namespace — FName constants for MPC parameter keys (LastImpactLocation, CurrentRippleRadius, RippleIntensity)

## Key Technical Decisions

- **Renderer:** DX12 with SM6, Lumen GI + reflections, Virtual Shadow Maps, ray tracing enabled, static lighting **disabled**
- **Input:** UE5 Enhanced Input system (not legacy input)
- **Audio:** 48kHz sample rate, 1024 buffer frame size
- **Player base class:** `APawn` (not `ACharacter`) — no skeletal mesh needed for a cube
- **Ripple animation:** `FTimeline` + `UCurveFloat` in C++ with manual `TickTimeline()` calls. Timeline uses normalized 0→1 range with `SetPlayRate(1/RippleDuration)` to decouple curve authoring from duration
- **Single active ripple** — new ripple overwrites current (acceptable for Milestone 1; future: MPC array or Niagara for multi-ripple)

## Development Conventions

### Sound-Vision Loop
- All interactive objects use the "Echo" Shader with `MPC_GlobalSound` (Material Parameter Collection) storing `LastImpactLocation`, `CurrentRippleRadius`, `RippleIntensity`
- Materials implement `SphereMask`/`SmoothStep` ring-shaped emissive reveal driven by these MPC parameters

### Movement States
- **Glide:** Silent hover movement, zero visibility
- **Drop:** Medium sound "clunk", mid-range Vision Ripple (radius 800)
- **Slam Jump:** Loud "boom", room-wide Sonar Pulse (radius 2000)
- Floating logic uses `VInterpTo` to raise cube on Z-axis; impacts trigger Timeline-driven ripple + `MakeNoise()`

### Enemy AI
- Uses `AIPerception`/`PawnSensing` to detect noise events
- Active Slam: high priority, AI moves to impact location
- Passive Drop: low priority, AI chases if within short radius

### Aesthetic
- Minimalist "Greybox" aesthetic initially
- "Juice" elements: camera shake (subtle on Drop, violent on Slam), haptic feedback, audio-visual sync (ripple speed matches reverb tail)

## Debugging Guidelines

- Logs: `./Saved/Logs/`
- Key error patterns: `LogWindows: Error`, `LogScript: Warning`
- Always read the last 100 lines of the project log before suggesting a fix for a runtime crash
- Rider build logs: `%LOCALAPPDATA%\JetBrains\Rider2025.3\log\SolutionBuilder`

## Code Review

- Review feedback is in `reviews/Code-Review.md` — always consult before modifying reviewed files.
- **READ-ONLY:** Do NOT write to or modify `reviews/Code-Review.md` — it is maintained by the review agent.

## Development Milestones

1. **"The Greybox"** — Cube movement + basic Drop vision *(COMPLETE)*
2. **"The Threat"** — AI cubes reacting to Slam
3. **"The Puzzle"** — Blind Gliding through obstacle levels
4. **"Atmosphere"** — 3D spatial audio and post-processing

### Milestone 1: Complete

C++ foundation and Editor assets are all in place. Code review issues have been resolved.

```
Content/EchoLocation/
    Core/          BP_EchoGameMode, BP_EchoPlayerController
    Player/        BP_EchoPawn
    Materials/     MPC_GlobalSound, M_EchoMaster, MI_EchoMaster
    Input/         IA_Move, IA_Look, IA_Slam, IMC_EchoDefault
    Curves/        C_RippleRadius, C_RippleIntensity
    Feedback/      CS_DropShake, CS_SlamShake, FFE_DropFeedback, FFE_SlamFeedback
    Maps/          L_EchoPrototype
```

**Remaining Editor steps** (run scripts 11–12 or via `00_run_all.py`):
- `11_build_material_graph.py` — Wires the M_EchoMaster SphereMask ring shader (Distance→SmoothStep ring→emissive)
- `12_polish_level.py` — Adds SkyLight, ExponentialHeightFog, PostProcessVolume, NavMeshBoundsVolume
- After running: Build Paths in editor for nav mesh, then PIE test

### Milestone 2: Next Up — "The Threat"

- AI "Corrupted Cube" enemy with `AIPerception` hearing-based detection
- Enemy pawn + AI controller + behavior tree
- Slam attracts enemies (high priority), Drop attracts within short radius (low priority)
- Game over / restart on player-enemy collision
