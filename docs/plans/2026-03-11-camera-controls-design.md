# Camera Controls Redesign: Free Mouse Look

## Problem
Camera currently requires right-click + drag to look around. This is non-standard for 3rd-person games and feels clunky. The root cause is the `IA_Look` input action in `IMC_EchoDefault` having a right-click modifier/condition on the Mouse XY binding.

## Solution
Standard free mouse look: mouse always controls camera, cursor hidden and locked, pitch clamped to prevent flipping, sensitivity tunable from Blueprint.

## Changes

### C++ — `AEchoPlayerController::BeginPlay()`
- Set input mode to Game Only (`FInputModeGameOnly`)
- Hide mouse cursor (`bShowMouseCursor = false`)
- Clamp pitch via `PlayerCameraManager->ViewPitchMin = -70.0f` and `ViewPitchMax = 20.0f`

### C++ — `AEchoPawn`
- Add `UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Echo|Input") float MouseSensitivity = 1.0f`
- Modify `HandleLook()` to multiply input by `MouseSensitivity`

### Editor — `IMC_EchoDefault`
- Remove right-click modifier from the `IA_Look` → Mouse XY mapping
- Result: Mouse XY fires `IA_Look` unconditionally

## Pitch Clamp Rationale
- **-70 degrees (down):** Player cube is on the ground, so looking down is common for spatial awareness
- **+20 degrees (up):** In a "total darkness" game there's nothing above to see; limited up-look keeps the camera grounded

## Resulting Controls
- **Mouse** → Camera rotation (always, no click required)
- **WASD** → Move relative to camera direction (already works this way)
- **Space** → Slam jump (unchanged)
- **Cursor** → Hidden and locked to center
