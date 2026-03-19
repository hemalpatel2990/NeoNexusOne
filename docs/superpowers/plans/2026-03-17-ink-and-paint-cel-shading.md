# "Ink & Paint" Cel Shading Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement a bold, vibrant "Ink & Paint" comic-book aesthetic with thick dark outlines, vibrant fill colors, and world-space halftone shading.

**Architecture:** We use `fwidth`-based 3D edge detection for outlines and triplanar projection for halftone dots. Sonar intensity drives the halftone dot size to simulate shading without lights. All logic is encapsulated in a new material build script.

**Tech Stack:** Unreal Engine 5.6, HLSL, Python (Editor Scripting), C++

---

## Task 1: Foundation (C++ & Helpers)

**Files:**
- Modify: `Source/NeoNexusOne/Public/Core/EchoTypes.h`
- Modify: `Source/NeoNexusOne/Public/Player/EchoPawn.h`
- Modify: `Source/NeoNexusOne/Private/Player/EchoPawn.cpp`
- Modify: `Scripts/EditorUtility/helpers.py`

- [ ] **Step 1: Update C++ MPC Constants**

In `Source/NeoNexusOne/Public/Core/EchoTypes.h`, ensure the `EchoMPCParams` namespace has the correct constants:

```cpp
namespace EchoMPCParams
{
	inline const FName LastImpactLocation = FName(TEXT("LastImpactLocation"));
	inline const FName CurrentRippleRadius = FName(TEXT("CurrentRippleRadius"));
	inline const FName RippleIntensity = FName(TEXT("RippleIntensity"));
	inline const FName PlayerWorldPosition = FName(TEXT("PlayerWorldPosition"));
	inline const FName RippleStartTime = FName(TEXT("RippleStartTime"));
}
```

- [ ] **Step 2: Add Player Position Update to EchoPawn**

In `EchoPawn.h`, add:
```cpp
virtual void Tick(float DeltaTime) override;
UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Echo|Ripple")
TObjectPtr<UMaterialParameterCollection> EchoMPC;
```

In `EchoPawn.cpp`:
- Add `#include "Kismet/KismetMaterialLibrary.h"`
- Set `PrimaryActorTick.bCanEverTick = true;` in constructor.
- Implement `Tick` to write actor location to `EchoMPCParams::PlayerWorldPosition`.

- [ ] **Step 3: Update Python Helpers**

In `Scripts/EditorUtility/helpers.py`, update `MPCParams` class:

```python
class MPCParams:
    LAST_IMPACT_LOCATION     = "LastImpactLocation"
    CURRENT_RIPPLE_RADIUS    = "CurrentRippleRadius"
    RIPPLE_INTENSITY         = "RippleIntensity"
    PLAYER_WORLD_POSITION    = "PlayerWorldPosition"
    RIPPLE_START_TIME        = "RippleStartTime"
```

- [ ] **Step 4: Commit Foundation**

```bash
git add Source/NeoNexusOne/Public/Core/EchoTypes.h Source/NeoNexusOne/Public/Player/EchoPawn.h Source/NeoNexusOne/Private/Player/EchoPawn.cpp Scripts/EditorUtility/helpers.py
git commit -m "feat: foundation for Ink & Paint (MPC params and player position tracking)"
```

---

## Task 2: MPC & Infrastructure Script Updates

**Files:**
- Modify: `Scripts/EditorUtility/01_create_mpc.py`

- [ ] **Step 1: Update 01_create_mpc.py**

Ensure `PlayerWorldPosition` is a Vector parameter and `RippleStartTime` is a Scalar.

```python
    ensure_vector(MPCParams.LAST_IMPACT_LOCATION)
    ensure_vector(MPCParams.PLAYER_WORLD_POSITION)
    ensure_scalar(MPCParams.CURRENT_RIPPLE_RADIUS)
    ensure_scalar(MPCParams.RIPPLE_INTENSITY)
    ensure_scalar(MPCParams.RIPPLE_START_TIME)
```

- [ ] **Step 2: Commit**

```bash
git add Scripts/EditorUtility/01_create_mpc.py
git commit -m "feat: update MPC creation script for Ink & Paint"
```

---

## Task 3: Build Ink & Paint Material Script

**Files:**
- Create: `Scripts/EditorUtility/19_build_ink_and_paint_material.py`

- [ ] **Step 1: Implement Material Build Script**

Create the script to build `M_EchoMaster`. Key logic in `19_build_ink_and_paint_material.py`:
- **Ink Mask:** `fwidth(Normal)` based detection.
- **Local Sonar Intensity:** Combine `ActiveRing` (from distance) and `AfterglowDecay` (from noise/time) to get a 0-1 value per pixel.
- **Halftone HLSL:**
  ```hlsl
  float3 p = WorldPos * DotScale;
  float3 dot = abs(frac(p - 0.5) - 0.5);
  float val = length(dot);
  // Scale threshold by local intensity: low intensity = large dots (shadow)
  float threshold = lerp(DotMaxSize, DotMinSize, LocalIntensity);
  return step(val, threshold);
  ```
- **Final Combine:** `lerp(EchoColor, EchoColor * 0.2, HalftoneMask) * (1.0 - InkMask) * LocalIntensity`.

- [ ] **Step 2: Commit**

```bash
git add Scripts/EditorUtility/19_build_ink_and_paint_material.py
git commit -m "feat: add Ink & Paint material build script"
```

---

## Task 4: Update Material Instances & Status

**Files:**
- Modify: `Scripts/EditorUtility/06_create_material.py`
- Modify: `STATUS.md`

- [ ] **Step 1: Update Material Instances**

Update `06_create_material.py` to use `UseFluxLook=True` and set vibrant `EchoColor` values (Cyan for world, Red for enemies).

- [ ] **Step 2: Update STATUS.md**

Update Milestone 2 to reflect the pivot to "Ink & Paint" Cel Shading.

- [ ] **Step 3: Commit**

```bash
git add Scripts/EditorUtility/06_create_material.py STATUS.md
git commit -m "docs: update status and material instances for Ink & Paint"
```

---

## Task 5: Verification

- [ ] **Step 1: Compile C++ and run scripts in Editor**
- [ ] **Step 2: Verify "Ink & Paint" look in PIE**
- [ ] **Step 3: Verify Black Outlines and Vibrant Halftone dots**
