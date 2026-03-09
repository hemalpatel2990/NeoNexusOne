# GEMINI.md - NeoNexusOne: Echo-Location

## Project Overview
**NeoNexusOne** is a minimalist, high-tension horror-puzzle game developed in **Unreal Engine 5.6**. The player controls a cube in total darkness and must create physical impacts (sound) to generate "Vision Ripples" that briefly reveal the environment. However, sound also attracts "Corrupted Cubes" (enemies), creating a risk-reward loop between visibility and safety.

### Main Technologies
*   **Engine:** Unreal Engine 5.6
*   **Visuals:** Custom "Echo" Shaders using Material Parameter Collections (MPC) and SphereMasks.
*   **Input:** UE5 Enhanced Input system.
*   **AI:** AI Perception / Pawn Sensing reacting to `MakeNoise()` events.
*   **Audio:** 3D Spatial Audio and Audio Synesthesia (visuals matched to audio decay).

---

## Superpowers: Skills & Commands

This project leverages the **Gemini Superpowers** extension to enhance reasoning, planning, and execution. Skills are battle-tested approaches that prevent common mistakes.

### Core Mandates
1. **Mandatory Activation:** If a skill might apply (even 1% chance), you MUST activate it using `activate_skill`.
2. **Prioritize Process:** Process skills (`brainstorming`, `systematic-debugging`) MUST be used before implementation skills.
3. **Verification First:** Use `verification-before-completion` before any success claims or commit requests.

### Primary Skills
*   **`brainstorming`**: Use before ANY creative work (features, components, behavior modification).
*   **`writing-plans` / `executing-plans`**: Use for all multi-step implementations.
*   **`test-driven-development`**: Use for all code changes.
*   **`systematic-debugging`**: Use for all bugs, test failures, or unexpected behaviors.
*   **`verification-before-completion`**: Use before claiming a task is complete.

### Available Commands
*   `/code-review`: Triggers a comprehensive review (see Tool Specific Workflows).
*   `/icon`, `/pattern`, `/diagram`, `/story`: **Nano Banana** image generation tools for assets and diagrams.

---

## Building and Running
*   **Engine:** Unreal Engine 5.6 (set in `NeoNexusOne.uproject`)
*   **IDE:** Visual Studio 2022 (solution: `NeoNexusOne.sln`) or JetBrains Rider
*   **Build:** Use Unreal Build Tool (UBT) or compile directly from within the Editor / Visual Studio.
*   **Test:** Use "Play In Editor" (PIE) mode for functional testing of mechanics and AI.
*   **Logs:** Check `./Saved/Logs/` and read the last 100 lines before diagnosing crashes.

---

## Architecture

Single module project (`NeoNexusOne`). Public include paths are configured so headers can be included with subfolder-relative paths (e.g., `#include "Core/EchoTypes.h"`).

### Source Layout
```
Source/NeoNexusOne/
    Core/          # Shared types, GameMode, PlayerController
    Player/        # Pawn and MovementComponent (Glide/Drop/Slam state machine)
    Sound/         # RippleManager (Timeline-driven MPC updates)
    Feedback/      # FeedbackComponent (Camera shake + haptics)
    AI/            # Enemy Pawn and AI Controller (Perception-driven)
```

### Core Data Flow
1. **Input** → `AEchoPawn` receives Enhanced Input (Move, Look, Slam).
2. **Movement** → `UEchoMovementComponent` handles states, fires `OnEchoImpact` on landing.
3. **Ripple** → `AEchoPawn` calls `UEchoRippleManager::TriggerRipple()` via the GameMode.
4. **MPC Update** → `UEchoRippleManager` animates `MPC_GlobalSound` via `FTimeline` + `UCurveFloat`.
5. **AI Noise** → `AEchoPawn` calls `MakeNoise()`; enemies detect via `AIPerception`.
6. **Feedback** → `UEchoFeedbackComponent` triggers camera shake + haptics.

---

## Development Conventions

### 1. Sound-Vision Loop
- Interactive objects must use the "Echo" Shader with `MPC_GlobalSound`.
- Materials implement `SphereMask` emissive reveal driven by `LastImpactLocation`, `CurrentRippleRadius`, and `RippleIntensity`.

### 2. Movement & Physics
- **Glide:** Silent movement (no vision).
- **Drop:** Medium sound, mid-range ripple (Radius: 800).
- **Slam Jump:** Loud sound, wide sonar pulse (Radius: 2000).
- Floating logic uses `VInterpTo` to raise cube; impacts trigger ripples and `MakeNoise()`.

### 3. AI Behavior
- Enemies use hearing perception to investigate noise.
- **Active Slam:** High priority, move to impact location.
- **Passive Drop:** Low priority, investigate if close.
- **Kill:** Overlap with player triggers Game Over (restarts level).

### 4. Aesthetic Standards
- Minimalist "Greybox" aesthetic.
- Focus on "The Juice": synced camera shakes, haptics, and audio-visual decay.

---

## Tool Specific Workflows

### 1. Code Review (`/code-review`)
*   Review output MUST be written to `reviews/Code-Review.md`.
*   Maintain `reviews/Code-Review.md` as a persistent record of the last review.
*   Consult this file before modifying code that has been reviewed.
*   Use `requesting-code-review` when completion or major feature steps are reached.
*   Use `receiving-code-review` for systematic implementation of review feedback.

### 2. Planning & Brainstorming
*   All design or implementation plans MUST be written to the `docs/plans/` directory.
*   Plan files MUST be prefixed with the current date (e.g., `YYYY-MM-DD-plan-name.md`).

---

## Milestones

1. **"The Greybox"** — Cube movement + basic Drop vision *(COMPLETE)*
2. **"The Threat"** — AI cubes reacting to Slam *(IN PROGRESS)*
3. **"The Puzzle"** — Blind Gliding through obstacle levels
4. **"Atmosphere"** — 3D spatial audio and post-processing
