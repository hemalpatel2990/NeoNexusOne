# Player Silhouette Design

## Overview
Currently, the game is in total darkness between Vision Ripples, making it difficult for the player to track the position of their own cube. This design introduces a faint emissive rim light to the player's material to ensure they are always visible, without illuminating the floor or revealing enemies.

## Architecture & Material Setup
We will modify the existing master material (`M_EchoMaster`) and create a new instance for the player.

1. **Master Material Update (`M_EchoMaster`)**: 
   - Add a `Fresnel` node to isolate the edges of the mesh based on camera angle.
   - Add a Scalar Parameter `RimLightIntensity` (Default: 0).
   - Add a Vector Parameter `RimLightColor` (Default: White).
   - Multiply the Fresnel output by these parameters and add it to the final Emissive output (alongside the existing Vision Ripple logic).

2. **Player Material Instance (`MI_EchoPlayer`)**: 
   - Create a new Material Instance specifically for `BP_EchoPawn`.
   - Enable `RimLightIntensity` (e.g., 0.5) and set a subtle `RimLightColor`. 
   - The player cube will now always have a faint glowing edge, completely independent of the Vision Ripples.

3. **World & Enemy Materials**: 
   - The default `MI_EchoMaster` (used for the environment) and the future `MI_EchoEnemy` will leave `RimLightIntensity` at `0`.
   - This guarantees that enemies and walls remain in 100% total darkness until illuminated by a sound ripple.

## Performance & Data Flow
- **Performance:** Adding a Fresnel calculation is extremely cheap and requires no ticking or CPU overhead. It happens entirely on the GPU.
- **Data Flow:** No C++ or Blueprint changes are required for the movement logic or the `EchoRippleManager`. This is purely a visual enhancement on the material layer.
