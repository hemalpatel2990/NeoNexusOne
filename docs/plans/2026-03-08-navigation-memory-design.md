# Navigation Memory & UX Design

## Section 1: The "Lingering Static" After Image
*   **Architecture:** We will add a second visual layer to the `M_EchoMaster` material. Alongside the current fast-moving "Vision Ripple" ring, we will implement a "Memory Sphere."
*   **Data Flow:** The `UEchoRippleManager` will drive two new parameters in the `MPC_GlobalSound`: `MemoryRadius` and `MemoryOpacity`. When an impact occurs, the Memory Sphere expands rapidly to the max radius of the sound.
*   **Material Logic:** Unlike the ripple, the Memory Sphere is a filled volume. We will multiply this sphere mask by a world-aligned 3D noise texture to give it a grainy, static-like appearance. The `EchoRippleManager` will use a secondary, slow Timeline to fade `MemoryOpacity` to 0 over 5-10 seconds, leaving a ghostly imprint of the level geometry.

## Section 2: Audio Hazards & Visual Breadcrumbs
*   **Audio Hazards:** We will implement an base hazard actor (e.g., `BP_EchoHazard`). It will feature a `UAudioComponent` playing a low-frequency, looping ambient hum. With UE5's spatial audio attenuation configured, players using stereo headphones will be able to pinpoint the location of drops or spikes purely by sound.
*   **Visual Pings:** Key level objectives (exits, puzzle switches) will utilize a localized, independent material setup. They will pulse a very small, faint emissive ring (radius ~50) every 3-5 seconds. This acts as a lighthouse, orienting the player without lighting up the surrounding room.

## Section 3: The "Heartbeat" Tension Haptics
*   **Architecture:** We will add a proximity detection system, likely managed by the `UEchoFeedbackComponent` or the `EchoPlayerController`.
*   **Data Flow:** The system will periodically check the distance to the nearest `AEchoEnemyPawn`. If an enemy breaches a "tension threshold" (e.g., 1500 units), it triggers a looping Force Feedback Effect (controller rumble).
*   **Dynamic Feedback:** As the distance decreases, the frequency and intensity of the heartbeat rumble will scale up. This gives the player crucial survival information entirely through physical touch.
