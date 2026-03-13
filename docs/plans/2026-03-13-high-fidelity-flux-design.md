# High-Fidelity "Digital Flux" (Daredevil) Design

## Overview
This design introduces an alternative visual mode inspired by Daredevil's "World on Fire," skinned with a "Data Flux" hacker aesthetic. It replaces static technical lines with living, shimmering vertical data streams that vibrate where sound is strongest. This system coexists with the original "Blueprint" look via a toggleable switch.

## Architecture & Data Flow

### 1. Dual-Mode Master Material (`M_EchoMaster`)
The material uses a **Static Switch Parameter** (`UseFluxLook`) to branch between two visual philosophies while sharing the same core sonar logic.
*   **Blueprint Mode (Default)**: Crisp world grids and solid geometric outlines.
*   **Flux Mode**: Fluid vertical data rain and shimmering, fractured edges.

### 2. The "Digital Flux" Components
When `UseFluxLook` is enabled, the surface rendering changes to:
*   **Vertical Data Streams**: A series of high-frequency vertical lines (panned `WorldPosition.Z`) that create a "falling data" effect.
*   **Fractured Edge Detection**: The standard `fwidth` edge logic is masked by a high-frequency noise texture, creating a "dashed" or "glitchy" outline that flickers based on `MPC.RippleIntensity`.
*   **Velocity-Based Blur**: (Optional) A slight procedural shimmer applied to edges when the camera moves quickly, mimicking sensory disorientation.

### 3. Sonic-Visual Synchronization
The flux behavior is directly linked to the audio environment via the Material Parameter Collection:
*   **`RippleIntensity`**: Drives the scrolling speed of the vertical streams and the "Heat" (emissive intensity) of the edges.
*   **`DigitalJitterIntensity`**: Drives the "Fracture" frequency, making edges more unstable as sound increases.

## Visual Highlights (Meaningful Identity)
Highlights are no longer just outlines; they are unique "Flux Signatures":
*   **World Geometry**: Calm, deep blueprint blue vertical crawl.
*   **Threats (Enemies)**: Fast-vibrating, "Red-Alert" fractured flux.
*   **Objectives**: Steady, high-intensity gold "Solid Stream."

## Technical Implementation

### Flux Stream HLSL (Conceptual)
```hlsl
// Vertical Data Rain
float Flux = sin(WorldPos.z * Frequency + Time * Speed * Intensity);
Flux = step(Threshold, Flux); // Creates sharp strips
```

### Fractured Edge HLSL (Conceptual)
```hlsl
float Edge = length(fwidth(Normal));
float Noise = PseudoRandom(WorldPos + Time);
float FracturedEdge = Edge * step(Noise, JitterThreshold);
```

## Transition & Safety
*   **Static Switch Optimization**: Objects using the Blueprint look incur zero GPU cost from the Flux logic.
*   **Motion Sickness**: Vertical flux speed is clamped to prevent "screen-swim" effects.
