# Inked HUD Design Spec

**Date:** 2026-03-19
**Status:** Draft
**Project:** NeoNexusOne: Echo-Location

## 1. Overview
The "Inked HUD" is a minimalist, comic-book style user interface that provides the player with critical data (Signal Intensity, Mapping Progress) while maintaining visual harmony with the game's "Ink & Sonar" cel-shaded aesthetic.

## 2. Visual Language
The HUD avoids pixel-perfect digital precision in favor of a "Hand-Drawn Marker" look.

- **Bold Outlines:** All UI elements (bars, boxes, text backgrounds) use thick, slightly irregular black ink outlines (simulating `fwidth` object edges).
- **Asymmetric Rotations:** Containers are tilted at slight angles (-2° to 2°) to feel sketched.
- **Halftone Fills:** Progress bars are filled with a distance-scaled halftone dot pattern (radial gradient dots) rather than flat colors.
- **Color Palette:** 
    - **Cyan (#00FFFF):** Signal/Intensity (Harmony with Sonar Ring).
    - **Magenta (#FF00FF):** Mapping/Objectives (Harmony with Obstacles).
    - **White (#FFFFFF):** Primary Labels/Data.
- **Dynamic Distortion:** The HUD "jitters" and bleeds color (chromatic aberration) as enemies approach, driven by proximity data.

## 3. Core Components

### 3.1. WBP_InkedHUD (UserWidget)
- **SignalBar:** A custom progress bar using a Material (M_HUD_InkedBar) for the halftone fill and hand-drawn edge.
- **MappingCounter:** A magenta-bordered box containing a large, high-contrast percentage text.
- **Annotation Text:** Small, "scribbled" notes (e.g., `// IMPACT_DETECTED`) that appear briefly near UI elements during events.

### 3.2. AEchoPlayerController (C++)
- **Variables:**
    - `float CurrentSignal`: 0.0 to 1.0 (decays linearly over time).
    - `float MappingProgress`: 0.0 to 100.0 (incremented by exploration triggers).
    - `float ProximityDist`: Normalized distance to nearest enemy (0.0 = far, 1.0 = adjacent).
    - `float MaxSensingRadius`: 1500.0 (distance at which proximity interference begins).
- **Logic:**
    - **Signal Decay:** Decays `CurrentSignal` every tick based on a `SignalDecayRate` (default: 0.2/sec).
    - **Signal Reset:** Resets `CurrentSignal` to 1.0 when an `OnEchoImpact` event is received (e.g., from `AEchoPawn` slam or drop).
    - **Proximity Calculation:** Every tick, the controller searches for the nearest `AEchoEnemyPawn` within `MaxSensingRadius`. `ProximityDist` is calculated as `1.0 - (ActualDist / MaxSensingRadius)`, clamped from 0 to 1.
    - **MPC Update:** Updates `MPC_GlobalSound` with `ProximityDist` and `CurrentSignal` parameters to drive both world shader effects and HUD jitter.

## 4. Technical Integration
- **MPC_GlobalSound:** Add `ProximityInterference` (Scalar) and `SignalIntensity` (Scalar) parameters.
- **M_HUD_InkedBar:** A UI material that uses a `SphereMask` or custom noise to create "rough" edges and a `frac` coordinate system for the halftone dots.
- **Exploration Triggers:** Simple collision volumes in the level that notify the PlayerController when entered, incrementing `MappingProgress`.

## 5. Success Criteria
- HUD elements feel like they were drawn on the screen with a marker.
- Signal bar decay perfectly matches the visual sonar ring fade in the world.
- HUD jitter clearly indicates enemy proximity without being unreadable.
- 0% Mapping Progress is shown at start; 100% is achievable by visiting all level zones.
