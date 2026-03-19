# Echo-Location

A minimalist horror-puzzle game built in **Unreal Engine 5.6**. Navigate total darkness as a cube, using physics-based impacts to generate sonar pulses that briefly reveal the environment. Sound attracts enemies — every pulse is a gamble between seeing and being found.

## The Concept

You control a cube in pitch-black space. Your only way to see is to **make noise**:

- **Glide** silently across surfaces — invisible, safe, blind
- **Drop** from a hover to emit a mid-range sonar ping — reveals nearby geometry
- **Slam Jump** to unleash a room-wide sonar pulse — reveals everything, alerts everything

Each impact sends out a cyan "Vision Ripple" that draws the environment as a glowing wireframe grid, then fades back to black. Enemies hear your noise and hunt you down.

## Visual Style

**"Blueprint Sonar"** — a 100% Unlit, shader-driven aesthetic. No engine lighting, no Lumen, no SkyLight. Everything is procedural:

- Cyan-on-black 3D wireframe grid revealed by sonar pulses
- Energy wave ring expanding from impact points
- Digital Scan Decay as the ripple fades
- All visuals driven by a Material Parameter Collection updated in C++

## Tech Stack

- **Engine:** Unreal Engine 5.6 (C++)
- **Rendering:** 100% Unlit pipeline, DX12/SM6
- **Input:** UE5 Enhanced Input System
- **AI:** AIPerception hearing-based state machine (Idle/Investigating/Returning)
- **Architecture:** Single C++ module, APawn-based player, FTimeline-driven MPC ripple system

## Project Structure

```
Source/NeoNexusOne/
    Public/  & Private/
        Core/       EchoTypes, EchoGameMode, EchoPlayerController
        Player/     EchoPawn, EchoMovementComponent
        Sound/      EchoRippleManager
        Feedback/   EchoFeedbackComponent
        AI/         EchoAIController, EchoEnemyPawn

Content/EchoLocation/
    Core/       BP_EchoGameMode, BP_EchoPlayerController
    Player/     BP_EchoPawn
    Materials/  MPC_GlobalSound, M_EchoMaster, MI_EchoMaster
    Input/      IA_Move, IA_Look, IA_Slam, IMC_EchoDefault
    Curves/     C_RippleRadius, C_RippleIntensity
    Feedback/   CS_DropShake, CS_SlamShake, FFE_DropFeedback, FFE_SlamFeedback
    Maps/       L_EchoPrototype
```

## Building

1. Install **Unreal Engine 5.6** via the Epic Games Launcher
2. Open `NeoNexusOne.uproject` — the engine will prompt to build
3. Alternatively, open `NeoNexusOne.sln` in Visual Studio 2022 or JetBrains Rider and build the `NeoNexusOneEditor` target

## Roadmap

| Milestone | Status |
|-----------|--------|
| 1. "The Technical Pivot" — Unlit pipeline, procedural sonar shader | Complete |
| 2. "Universal Visuals & HUD" — Post-process edge detection, HUD, level kit | In Progress |
| 3. "The Mapping Puzzle" — Zone mapping, directional pings, objectives | Planned |
| 4. "Atmosphere & Polish" — Spatial audio, glitch effects, enemy proximity | Planned |

## License

All rights reserved.
