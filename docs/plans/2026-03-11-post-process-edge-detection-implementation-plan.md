# Post-Process Edge Detection Implementation Plan

> **For Gemini:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement a global "Digital Scan" effect using Post-Process Edge Detection that reacts to sound impacts.

**Architecture:** 
1.  **Global Data**: Add `DigitalJitterIntensity` to `MPC_GlobalSound` and `EchoRippleManager`.
2.  **Edge Detection**: Create a Post-Process Material using Sobel filtering on Depth and Normals.
3.  **Digital Jitter**: Apply UV-jitter to the edge sampling driven by the new MPC parameter.
4.  **Active-to-Latent Transition**: Fade edges from "Jittered/Bright" to "Stable/Ghost" based on `RippleRadius` and `MemoryRadius`.

**Tech Stack:** Unreal Engine 5.6 (C++, HLSL, Material Editor).

---

### Task 1: Update Global Sound Parameters

**Files:**
- Modify: `Source/NeoNexusOne/Core/EchoTypes.h`
- Modify: `Source/NeoNexusOne/Sound/EchoRippleManager.h`
- Modify: `Source/NeoNexusOne/Sound/EchoRippleManager.cpp`

**Step 1: Add parameter name to `EchoMPCParams`**

```cpp
// Source/NeoNexusOne/Core/EchoTypes.h
namespace EchoMPCParams
{
    // ...
    inline const FName DigitalJitterIntensity = FName(TEXT("DigitalJitterIntensity"));
}
```

**Step 2: Update `EchoRippleManager` to drive jitter**

Modify `UpdateMPC` to include the new parameter:

```cpp
// Source/NeoNexusOne/Sound/EchoRippleManager.cpp
void UEchoRippleManager::UpdateMPC(const FVector& Location, float Radius, float Intensity)
{
    // ... existing code ...
    UKismetMaterialLibrary::SetScalarParameterValue(
        World, EchoMPC, EchoMPCParams::DigitalJitterIntensity, Intensity);
}
```

**Step 3: Commit**

```bash
git add Source/NeoNexusOne/Core/EchoTypes.h Source/NeoNexusOne/Sound/EchoRippleManager.*
git commit -m "feat: add DigitalJitterIntensity to MPC and RippleManager"
```

---

### Task 2: Create the Post-Process Material (Blueprint Script)

**Files:**
- Create: `Scripts/EditorUtility/17_create_post_process_material.py`

**Step 1: Write the generation script**
Create a script that generates `M_EchoPostProcess`. It should:
1.  Set Material Domain to **Post Process**.
2.  Implement **Sobel Edge Detection** (Custom HLSL node preferred).
3.  Implement **Jitter Logic** using `DigitalJitterIntensity`.
4.  Implement **Active-to-Latent Masking** using `RippleRadius` and `MemoryRadius`.

**Step 2: Run the script to generate the asset**

Run: `py "D:/Users/hemal/Documents/Unreal Projects/NeoNexusOne/Scripts/EditorUtility/17_create_post_process_material.py"`

**Step 3: Commit**

```bash
git add Scripts/EditorUtility/17_create_post_process_material.py
git commit -m "feat: add script to generate M_EchoPostProcess"
```

---

### Task 3: Implement Sobel & Jitter HLSL

**Files:**
- Modify: `Scripts/EditorUtility/17_create_post_process_material.py`

**Step 1: Add Custom HLSL for Edge Detection**
```hlsl
// Sobel Depth + Normal
float3 Offset = float3(1.0/ViewportSize.x, 1.0/ViewportSize.y, 0.0);
float D0 = SceneDepth(UV - Offset.xy); float D1 = SceneDepth(UV - Offset.zy); // ... etc
// Return Max(DepthGrad, NormalGrad)
```

**Step 2: Add Jitter logic**
Apply `(Noise - 0.5) * DigitalJitterIntensity` to the `UV` passed into the Sobel node.

**Step 3: Run script and verify in Editor**
Check if `M_EchoPostProcess` compiles and shows edges.

**Step 4: Commit**

```bash
git add Scripts/EditorUtility/17_create_post_process_material.py
git commit -m "feat: implement Sobel and Jitter HLSL in generation script"
```

---

### Task 4: Setup Post-Process Volume

**Files:**
- Modify: `Scripts/EditorUtility/12_polish_level.py` (or a new setup script)

**Step 1: Add Post-Process Volume to the level**
Create a script or update existing one to:
1.  Spawn an `APostProcessVolume`.
2.  Set `bUnbound = true`.
3.  Add `M_EchoPostProcess` to `Settings.WeightedBlendables`.

**Step 2: Run script**
Verify the level now has a global blueprint-style outline.

**Step 3: Commit**

```bash
git add Scripts/EditorUtility/12_polish_level.py
git commit -m "feat: add PostProcessVolume to level setup"
```

---

### Task 5: Final Validation & Integration

**Step 1: Play In Editor (PIE)**
Perform a **Slam** and verify:
1.  Edges jitter aggressively during the pulse.
2.  Edges stabilize and fade out as the memory decays.
3.  No "fighting" with existing UV wireframes (which should be removed or disabled in `M_EchoMaster`).

**Step 2: Update `M_EchoMaster`**
Run `13_build_blueprint_sonar_material.py` but modify it first to remove the UV Wireframe logic since the Post-Process now handles it.

**Step 3: Commit**

```bash
git add Content/EchoLocation/Materials/M_EchoMaster.uasset
git commit -m "refactor: remove UV wireframe from master material"
```
