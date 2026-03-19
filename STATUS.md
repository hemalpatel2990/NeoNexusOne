# Status: NeoNexusOne — Echo-Location

## Current Milestone
**Milestone 2: "Universal Visuals & HUD"** — **IN PROGRESS**
*Goal: Supporting complex models without UVs, high-fidelity "Flux" look, and Hacker's View HUD.*

---

## Roadmap

### Milestone 1: "The Technical Pivot" — **COMPLETE**
*   [x] Re-evaluated and pivoted to **Shader-First, Unlit Pipeline**.
*   [x] Locked global exposure (EV100 = 1.0) and disabled standard engine lighting/Lumen.
*   [x] Rebuilt `M_EchoMaster` as an Unlit, procedural 3D grid shader.
*   [x] Implemented "Energy Wave" ring with Digital Scan Decay.
*   [x] Verified "Sound-Vision" loop with the new "Cinematic Sonar" aesthetic.

### Milestone 2: "Universal Visuals & HUD" — **IN PROGRESS**
*   [x] **UV-Independent 3D Edge Detection**: Pivoted from 2D Post-Process to superior object-space `fwidth` edges. Supports all meshes (monsters, rubble) with no UV requirements.
*   [ ] **"Ink & Paint" Cel Shading**: Pivoted from Digital Flux to a bold comic-book aesthetic with vibrant colors, dark ink outlines, and world-space halftone dots.
*   [x] **Source Reorganization**: Moved all C++ files into standard `Public/` and `Private/` directories.
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
*   **Source Structure:** Standardized (Public/Private split complete).
*   **Visual Strategy:** 100% Unlit, Procedural 3D Sonar.
*   **Stability:** High. Custom HLSL nodes used for grid and edge stability.
*   **Next Priority:** `WBP_EchoHUD` implementation.
