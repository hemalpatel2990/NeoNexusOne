# Post-Process Edge Detection (Digital Scan) Design

## Overview
This design replaces the model-specific UV wireframe logic with a global **Post-Process "Digital Scan"** effect. This ensures a consistent "Blueprint" aesthetic across all geometry (cubes, monsters, rubble) while providing visual feedback for player actions.

## Architecture & Data Flow

### 1. The Sound-Vision Loop (`MPC_GlobalSound`)
The visual intensity is directly driven by the game's audio events.
*   **`DigitalJitterIntensity`**: A new parameter spiked by `UEchoRippleManager` on impact (Slam/Drop) and decayed over time.
*   **`RippleRadius` / `MemoryRadius`**: Existing parameters used to mask the active "Pulse" vs. the latent "Memory".

### 2. Post-Process Material (`M_EchoPostProcess`)
A screen-space shader that performs real-time edge detection and digital fragmentation.
*   **Sobel Edge Detection**: Samples a 3x3 grid of Scene Depth and World Normals to find geometric outlines.
*   **Jittered UV Sampling**: Offsets the sampling UVs using a high-frequency Blue Noise texture, scaled by `MPC.DigitalJitterIntensity`.
*   **Perceptual Clamp**: Limits the maximum jitter offset (e.g., 2-4 pixels) and scales it by camera velocity to prevent motion sickness.

### 3. Active-to-Latent Transition
To provide persistence without constant noise, the effect follows a two-stage decay:
1.  **Active Pulse (`Distance < RippleRadius`)**: High-contrast, jittering "Digital Scan" edges. Maximum brightness and noise.
2.  **Latent Memory (`RippleRadius < Distance < MemoryRadius`)**: Faded, stable "Ghost" edges. Jitter is zeroed out for readability and comfort, providing long-term navigation context.

## Technical Implementation

### Sobel Filter Logic
```hlsl
// Conceptual HLSL for Edge Detection
float DepthEdge = Sobel(SceneDepthTexture, ScreenUV);
float NormalEdge = Sobel(WorldNormalTexture, ScreenUV);
float FinalEdge = max(DepthEdge, NormalEdge);
```

### Jitter Logic
```hlsl
// Conceptual HLSL for Digital Jitter
float2 Noise = Texture2DSample(BlueNoise, ScreenUV * NoiseScale + Time * NoiseSpeed).rg;
float2 JitterOffset = (Noise - 0.5) * MPC.DigitalJitterIntensity * PerceptualClamp;
float2 SampledUV = ScreenUV + JitterOffset;
```

## Performance & UX
*   **Optimization**: 3x3 Sobel kernel implemented in a single custom HLSL node to minimize texture lookups.
*   **UX**: Jitter is disabled in the "Latent Memory" zone to allow for clear, static navigation after the initial pulse.
