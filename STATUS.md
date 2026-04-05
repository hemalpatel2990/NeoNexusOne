# Status: NeoNexusOne — Echo-Location

## Current Milestone
**Milestone 2: "Universal Visuals & HUD"** — **COMPLETE**
*Goal: Supporting complex models without UVs, vibrant "Ink & Sonar" comic-book aesthetic, Inked HUD, and modular level kit.*

---

## Roadmap

### Milestone 1: "The Technical Pivot" — **COMPLETE**
*   [x] Re-evaluated and pivoted to **Shader-First, Unlit Pipeline**.
*   [x] Locked global exposure (EV100 = 1.0) and disabled standard engine lighting/Lumen.
*   [x] Rebuilt `M_EchoMaster` as an Unlit, procedural 3D grid shader.
*   [x] Implemented "Energy Wave" ring with Digital Scan Decay.
*   [x] Verified "Sound-Vision" loop with the new "Cinematic Sonar" aesthetic.

### Milestone 2: "Universal Visuals & HUD" — **COMPLETE**
*   [x] **UV-Independent 3D Edge Detection**: Pivoted from 2D Post-Process to superior object-space `fwidth` edges. Supports all meshes (monsters, rubble) with no UV requirements.
*   [x] **"Ink & Sonar" Cel Shading**: Bold comic-book aesthetic with three visual layers:
    *   UV-edge + Fresnel + fwidth **bold outlines** on all geometry
    *   **Cel-shading bands** (3 discrete brightness steps by sonar distance)
    *   **Distance-scaled halftone dots** (sparse near impact, dense far)
    *   Smooth quadratic **afterglow fade** (replaces pixel noise dissolve)
    *   Vibrant **per-instance colors**: blue walls, purple obstacles, red enemies, green player
    *   New `MI_EchoObstacle` material instance for obstacle differentiation
*   [x] **Sonar Reveal Bug Fixes**: Fixed afterglow decay (preserved MPC params after ring finishes), added explicit sonar ring edge node, fixed contour distance calculation.
*   [x] **Source Reorganization**: Moved all C++ files into standard `Public/` and `Private/` directories.
*   [x] **Inked HUD**: "Hand-Drawn" UI with bold outlines and halftone fills for signal strength and mapping progress. C++ widget base, PlayerController signal decay/proximity, WBP_InkedHUD widget BP, M_EchoInterference post-process scanlines.
*   [x] **EchoLocation Plugin Refactor**: Extracted all gameplay C++ into `EchoLocation` plugin. Main `NeoNexusOne` module is a minimal stub. Core Redirects in `DefaultEngine.ini` for seamless Blueprint class remapping.
*   [x] **Modular Level Kit**: 5 stylized geometric Blueprint Actor props (Wall, Rock, Tree, Crate, Ramp) in separate `EchoLevelKit` content-only plugin. Per-instance color tinting via `BaseColor` vector parameter on `M_EchoMaster` + Dynamic Material Instances. Supports indoor corridors, mountainous terrain, and forest environments.

### Milestone 3: "The Mapping Puzzle" — **PLANNED**
*   [ ] Zone-based mapping triggers (exploring the dark increases percentage).
*   [ ] Directional sonar "pings" for tactical scanning.
*   [ ] Data Key / Exit Port objective loop.

### Milestone 4: "Atmosphere & Polish" — **PLANNED**
*   [ ] 3D spatial audio reverb matching the "grid" size.
*   [ ] Post-process glitch effects tied to enemy proximity.

---

## Technical Health
*   **Engine:** Unreal Engine 5.6
*   **Source Structure:** Two-plugin architecture — `EchoLocation` (all gameplay C++) and `EchoLevelKit` (content-only level props). Main module is a minimal stub.
*   **Visual Strategy:** 100% Unlit, "Ink & Sonar" cel-shaded comic-book aesthetic. Per-instance color via `BaseColor` parameter on `M_EchoMaster`.
*   **Stability:** High. Custom HLSL nodes for cel-bands, halftone, outlines, afterglow.
*   **Optimization:** RippleManager MPC writes reduced to 1×/frame via dirty flag pattern. Debug logs demoted to Verbose. Hardcoded constants extracted to `EchoDefaults`.
*   **Next Priority:** Milestone 3 — "The Mapping Puzzle".
