# Status: NeoNexusOne — Echo-Location

## Current Milestone
**Milestone 2: "The Technical Foundation" — **COMPLETE**
*Goal: Rebuild the technical foundation using an Unlit, shader-driven blueprint aesthetic.*

---

## Roadmap

### Milestone 1: "The Technical Pivot" — **COMPLETE**
*   [x] Re-evaluated and pivoted to **Shader-First, Unlit Pipeline**.
*   [x] Locked global exposure (EV100 = 1.0) and disabled standard engine lighting/Lumen.
*   [x] Rebuilt `M_EchoMaster` as an Unlit, procedural 3D grid shader.
*   [x] Implemented automatic 3D wireframe edges via UV logic (Cube-optimized).
*   [x] Implemented "Energy Wave" ring with Digital Scan Decay.
*   [x] Verified "Sound-Vision" loop with the new "Cinematic Sonar" aesthetic.

### Milestone 2: "Universal Visuals & HUD" — **IN PROGRESS**
*   [ ] **Post-Process Edge Detection**: Build a Screen-Space shader to support complex models (monsters, rubble).
*   [ ] `WBP_EchoHUD`: Minimalist "Hacker's View" UI for signal strength and mapping progress.
*   [ ] `AEchoPlayerController`: C++ logic for signal decay and proximity interference.
*   [ ] Modular Level Kit: Create 3-4 simple "Blueprint" props for level building.

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
*   **Visual Strategy:** 100% Unlit, Procedural Sonar (Math-driven visuals).
*   **Build Status:** Clean. Foundation is robust and cinematic.
*   **Next Priority:** Implementing Post-Process Edge Detection for complex models.
