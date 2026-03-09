# Blueprint Sonar: Project "From Scratch" Design

## Overview
NeoNexusOne is being rebuilt from the ground up with a **Shader-First, Unlit Visual Pipeline**. This design solves the technical frustration of fighting Unreal Engine's standard lighting, auto-exposure, and fog in a "total darkness" game. The result is a high-contrast, "Blueprint" sonar aesthetic that is technically robust and coder-friendly.

## The Technical Foundation (Unlit Sonar)
The core visual engine is moving to a **100% Unlit / Shader-Driven Pipeline**.

1.  **Global Lighting:** Lumen, SkyLights, and all standard engine lights are **Disabled**.
2.  **Auto-Exposure:** Fixed at a constant value (Min/Max EV100 = 1.0) in a PostProcessVolume to prevent "exposure hunting" in the dark.
3.  **Master Material (`M_EchoMaster`)**: 
    - **Procedural Grid:** Draws a stable, 3D cyan grid using `WorldPosition` and `Frac`.
    - **Wireframe Edges:** Uses `CustomDepth` or screen-space math to draw sharp white edges on all geometry.
    - **Impact Pulse:** The Vision Ripple (via `MPC_GlobalSound`) multiplies the **Opacity** of the grid and wireframe, "drawing" the blueprint into existence for 5 seconds before it fades to black.

## Project Setup & Level Design
The project will be organized around a minimalist, modular "Echo" kit.

1.  **BP_EchoManager:** A single actor that owns the `UEchoRippleManager` and `MPC_GlobalSound`. No other atmospheric actors are allowed in the level.
2.  **L_EchoPrototype:** Rebuilt from scratch using a sharp, geometric modular kit (corridors, gaps, rooms). 
3.  **Spatial Reasoning Puzzles:** Levels are "Digital Zones" to be mapped. Players must memorize the grid after a pulse to navigate obstacles in total darkness.
4.  **Goals & Keys:** Exit Ports (white glowing wireframes) open when "Data Keys" (smaller glowing cubes) are pinged by a sound pulse.

## Visual Polish & Performance
- **The "Corrupted Cubes":** Red fluid-like masses that "glitch" out and vibrate when they detect noise.
- **Performance:** Being 100% Unlit and procedural makes the game extremely lightweight and scalable across different hardware.
- **The "Amazing" Factor:** The sharp, glowing cyan-on-black aesthetic looks like a high-budget sci-fi sonar scan, providing a strong, unified art direction with zero artistic labor.
