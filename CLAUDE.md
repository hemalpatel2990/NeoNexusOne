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

- **Renderer:** DX12 with SM6, **100% Unlit pipeline** — Lumen, SkyLights, and all standard engine lights are **disabled**. Auto-exposure locked at EV100 = 1.0 via PostProcessVolume.
- **Visual Strategy:** Shader-First, Procedural Sonar. `M_EchoMaster` is an Unlit material with a procedural 3D cyan grid (`WorldPosition` + `Frac`), wireframe edges via UV logic, and an "Energy Wave" ring with Digital Scan Decay driven by MPC.
- **Input:** UE5 Enhanced Input system (not legacy input)
- **Audio:** 48kHz sample rate, 1024 buffer frame size
- **Player base class:** `APawn` (not `ACharacter`) — no skeletal mesh needed for a cube
- **Ripple animation:** `FTimeline` + `UCurveFloat` in C++ with manual `TickTimeline()` calls. Timeline uses normalized 0→1 range with `SetPlayRate(1/RippleDuration)` to decouple curve authoring from duration
- **Single active ripple** — new ripple overwrites current (future: MPC array or Niagara for multi-ripple)

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
- **"Blueprint Sonar"** — Cyan-on-black, procedural 3D grid with wireframe edges revealed by sonar pulses
- 100% Unlit, shader-driven: no engine lighting, no Lumen, no SkyLight
- "Juice" elements: camera shake (subtle on Drop, violent on Slam), haptic feedback, audio-visual sync (ripple speed matches reverb tail)

## Debugging Guidelines

- Logs: `./Saved/Logs/`
- Key error patterns: `LogWindows: Error`, `LogScript: Warning`
- Always read the last 100 lines of the project log before suggesting a fix for a runtime crash
- Rider build logs: `%LOCALAPPDATA%\JetBrains\Rider2025.3\log\SolutionBuilder`

## Code Review

- Review feedback is in `reviews/Code-Review.md` — always consult before modifying reviewed files.
- **READ-ONLY:** Do NOT write to or modify `reviews/Code-Review.md` — it is maintained by the review agent.

## Milestone Plans

- Design plans and feature proposals live in `docs/plans/` — **always check this directory for new or updated plans** before starting work on any milestone or feature.
- When creating a new implementation plan, write it as a dated markdown file in `docs/plans/` (e.g., `2026-03-09-ai-threat-system.md`).
- If a plan has changed since the last session, follow the updated plan — do not rely on stale context from previous conversations.

## Development Milestones

1. **"The Technical Pivot"** — Shader-first unlit pipeline, procedural 3D grid, energy wave sonar *(COMPLETE)*
2. **"Universal Visuals & HUD"** — Post-process edge detection, Hacker's View HUD, modular level kit *(IN PROGRESS)*
3. **"The Mapping Puzzle"** — Zone-based mapping, directional sonar pings, Data Key / Exit Port objectives
4. **"Atmosphere & Polish"** — 3D spatial audio reverb, post-process glitch effects tied to enemy proximity

### Earlier Work (Complete)

**C++ foundation:** Movement system (Glide/Drop/Slam state machine), ripple manager (FTimeline + MPC), feedback component (camera shake + haptics), player controller (Enhanced Input), game mode.

**AI foundation (C++ written, needs Editor setup):** `AEchoAIController` (hearing perception + Idle/Investigating/Returning state machine), `AEchoEnemyPawn` (box collision, cube mesh, kill overlap sphere, `UFloatingPawnMovement`), `TriggerGameOver()` on GameMode. Editor work still needed: BP_EchoEnemyPawn, NavMesh verification, enemy placement.

**Visual pivot (Milestone 1):** Rebuilt `M_EchoMaster` as Unlit procedural sonar shader with 3D wireframe edges, "Energy Wave" ring, and Digital Scan Decay. Disabled all engine lighting.

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

### Milestone 2: "Universal Visuals & HUD" — Current

- **Post-Process Edge Detection:** Screen-space shader to support complex models (monsters, rubble) beyond UV-based wireframes
- **WBP_EchoHUD:** Minimalist "Hacker's View" UI — signal strength bar, mapping progress counter, static interference overlays
- **AEchoPlayerController:** Signal decay and proximity interference logic
- **Modular Level Kit:** 3–4 simple "Blueprint" props for level building
