# UV-Independent 3D Edge Detection Design

## Overview
This design replaces the screen-space Post-Process Edge Detection with a robust, **Object-Space "Geometry Scanner"** integrated directly into the Master Material. This ensures a "mathematically perfect" blueprint look that respects 3D depth, handles any mesh geometry without UV requirements, and eliminates depth-buffer artifacts.

## Architecture & Data Flow

### 1. Geometric Derivative Edge Detection
Instead of sampling the screen depth buffer, the material calculates edges based on the rate of change of the surface normals in world space.
*   **Method**: Uses `fwidth(WorldNormal)` to identify sharp transitions in geometry.
*   **Benefits**: Perfectly traces the edges of cubes, steps, and complex monster geometry. It is inherently occlusion-aware and depth-correct.

### 2. View-Distance Normalization
To maintain a consistent "Technical Drawing" aesthetic, line widths are normalized based on the camera distance.
*   **Logic**: `LineScale = PixelSize * DistanceToCamera`. 
*   **Visual**: A 2-pixel outline remains exactly 2 pixels wide regardless of how far the object is from the player.

### 3. Integrated Digital Shimmer
Digital "instability" is applied as a localized jitter to the **emissive mask** rather than the screen UVs.
*   **Behavior**: When the Sonar Ripple (`MPC.RippleRadius`) passes over an edge, a high-frequency 3D noise (based on `WorldPosition`) causes the line to "crackle" or "fragment" briefly.
*   **Stability**: The base geometry remains rock-solid; only the "visual readout" of the edge flickers, preventing motion sickness and "bad glitch" artifacts.

### 4. Hybrid Rendering Layering
The material combines three distinct 3D layers:
1.  **Geometric Outlines**: Sharp edges found via normal gradients (The "Skeleton").
2.  **World Grid**: Proportional grid lines based on absolute World Position (The "Scale").
3.  **Contact Shadows**: Thickened lines where surfaces meet (The "Depth").

## Technical Implementation

### Normal Gradient HLSL
```hlsl
// Conceptual logic for Object-Space Edges
float3 Normal = GetWorldNormal();
float EdgeMask = length(fwidth(Normal));
EdgeMask = smoothstep(Threshold - Width, Threshold + Threshold, EdgeMask);
```

### 3D Jitter Logic
```hlsl
// Jitter applied to the mask intensity, not the UVs
float JitterNoise = PseudoRandom(WorldPosition + Time);
float FinalEdge = EdgeMask * (1.0 - (JitterNoise * MPC.DigitalJitterIntensity));
```

## Transition Plan
1.  **Disable Post-Process Volume**: Remove `M_EchoPostProcess` from the level.
2.  **Update `M_EchoMaster`**: Inject the new Geometric Scanner block into the generation script.
3.  **Unified Control**: Drive both the Grid and the Geometric Outlines using the same `RippleRadius` and `MemoryRadius` logic.
