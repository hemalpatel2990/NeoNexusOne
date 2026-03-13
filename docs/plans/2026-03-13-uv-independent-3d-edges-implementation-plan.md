# UV-Independent 3D Edge Implementation Plan

> **For Gemini:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement robust, object-space edge detection in the Master Material to restore the "Perfect Cube" look while supporting complex meshes without UVs.

**Architecture:** 
1.  **Preparation**: Remove Post-Process approach from level and scripts.
2.  **Geometric Detection**: Use `fwidth(WorldNormal)` in `M_EchoMaster` to find edges.
3.  **Refinement**: Implement View-Distance normalization for consistent line thickness.
4.  **Local Jitter**: Localize the digital shimmer to the 3D edges using `DigitalJitterIntensity`.

**Tech Stack:** Unreal Engine 5.6 (Material Editor, HLSL, Python).

---

### Task 1: Cleanup Post-Process approach

**Files:**
- Modify: `Scripts/EditorUtility/12_polish_level.py`
- Modify: `Scripts/EditorUtility/helpers.py`

**Step 1: Remove Post-Process assignment logic**
Update `12_polish_level.py` to stop adding `M_EchoPostProcess` to the volume.

**Step 2: Commit**
```bash
git add Scripts/EditorUtility/12_polish_level.py
git commit -m "refactor: remove post-process material assignment from level setup"
```

---

### Task 2: Implement Geometric Edges in Master Material

**Files:**
- Modify: `Scripts/EditorUtility/13_build_blueprint_sonar_material.py`

**Step 1: Add Geometric Edge Detection Logic**
Inject a new block into the script that uses a Custom HLSL node for `fwidth(WorldNormal)`.

```hlsl
// HLSL for Geometric Edges
float3 N = normalize(WorldNormal);
float Edge = length(fwidth(N));
return saturate(Edge * EdgeSensitivity);
```

**Step 2: Connect to Final Visuals**
Update the `final_visual` calculation to include `GeometricEdges`.

**Step 3: Run script and verify in Editor**
Run: `py "D:/Users/hemal/Documents/Unreal Projects/NeoNexusOne/Scripts/EditorUtility/13_build_blueprint_sonar_material.py"`

**Step 4: Commit**
```bash
git add Scripts/EditorUtility/13_build_blueprint_sonar_material.py
git commit -m "feat: implement geometric derivative edges in master material"
```

---

### Task 3: View-Distance Normalization

**Files:**
- Modify: `Scripts/EditorUtility/13_build_blueprint_sonar_material.py`

**Step 1: Implement Distance Scaling**
Add logic to scale the edge threshold based on `Distance(CameraPosition, WorldPosition)`.

**Step 2: Run script and verify stability**
Ensure lines don't disappear or get too thick as you move.

**Step 3: Commit**
```bash
git add Scripts/EditorUtility/13_build_blueprint_sonar_material.py
git commit -m "feat: add view-distance normalization to edge width"
```

---

### Task 4: Localized 3D Jitter

**Files:**
- Modify: `Scripts/EditorUtility/13_build_blueprint_sonar_material.py`

**Step 1: Add 3D Jitter to Edges**
Multiply the Geometric Edge intensity by a 3D noise texture/math, driven by `DigitalJitterIntensity`.

**Step 2: Run script and PIE test**
Verify that only the edges "crackle" when the ripple hits them.

**Step 3: Commit**
```bash
git add Scripts/EditorUtility/13_build_blueprint_sonar_material.py
git commit -m "feat: localize digital jitter to 3D geometric edges"
```

---

### Task 5: Final Polish & Level Refresh

**Step 1: Run Polish Level**
Run: `py "D:/Users/hemal/Documents/Unreal Projects/NeoNexusOne/Scripts/EditorUtility/12_polish_level.py"`

**Step 2: Final PIE Verification**
Perform Slams and Drops. Ensure the "Perfect Cube" look is restored and monsters/complex meshes are outlined.

**Step 3: Cleanup**
Delete `Scripts/EditorUtility/17_create_post_process_material.py` and remove it from `helpers.py`.

**Step 4: Commit**
```bash
git rm Scripts/EditorUtility/17_create_post_process_material.py
git commit -m "cleanup: remove obsolete post-process material script"
```
