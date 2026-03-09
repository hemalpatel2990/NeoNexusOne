# Hacker's View HUD Design

## Overview
NeoNexusOne's UI is being rebuilt as a **Minimalist, Data-Focused HUD**. This design solves the "from-scratch" problem of giving the player spatial feedback in total darkness without using "standard" game UI. The HUD feels like a high-tech digital terminal.

## HUD Visuals (The "Digital Overlay")
The HUD will be a flat, 2D overlay on top of the sonar world.

1.  **Signal Strength (Top Left):** 
    - A sharp, glowing cyan progress bar. 
    - **Intensity:** 100% when a Slam occurs, decays to 0% over 5 seconds (sync'd to the Vision Ripple fading).
    - **Visual Ping:** A small, pulsing "Pulse" icon flashes when a sound impact happens.
2.  **Mapping Progress (Top Right):** 
    - A digital percentage counter (e.g., `MAPPING: 45.2%`). 
    - **Logic:** Increases as the player enters "Unexplored Zones" (spherical mapping triggers).
3.  **Static Interference (Overlays):** 
    - A very faint, flickering scanline effect across the whole screen. 
    - **Proximity Intensity:** As a Corrupted Cube gets closer, the scanlines vibrate and become more visible (synergy with the "Heartbeat" haptics).

## Technical Foundation (Widget & Controller)
The HUD will be driven by C++ for efficiency.

1.  **WBP_EchoHUD:** A minimalist Widget Blueprint using **`ProgressBar`** and **`Text`** nodes.
2.  **AEchoPlayerController:** 
    - Adds `CurrentSignal` and `MappingProgress` as blueprint-exposed variables.
    - Handles the `UpdateHUD` logic on Tick.
3.  **Proximity Mask:** A material parameter in the PostProcess material that drives the "Static Interference" intensity.

## The "Amazing" Factor
The sharp, glowing HUD creates a unified visual language with the sonar world, making the player feel like they are "remotely piloting" the cube through a digital construct.
