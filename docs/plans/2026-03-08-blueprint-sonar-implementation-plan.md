# Blueprint Sonar Implementation Plan

> **For Gemini:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement the "Blueprint Sonar" technical foundation, including an Unlit master material, MPC integration, and a fixed exposure setup.

**Architecture:** We will rebuild the `M_EchoMaster` material to be **Unlit** and procedural, using `WorldPosition` to draw a 3D grid and wireframes. We will use a `PostProcessVolume` to lock the camera's auto-exposure at a constant value, ensuring 100% predictable visuals.

**Tech Stack:** Unreal Engine 5.6 (Materials, Post-Process, C++ for Ripple Manager).

---

### Task 1: Lock Global Exposure & Disable Lights

**Files:**
- Modify: `L_EchoPrototype` (Editor Level)
- Modify: `Config/DefaultEngine.ini`

**Step 1: Configure PostProcessVolume**
- Open `L_EchoPrototype`.
- Find or add a `PostProcessVolume`.
- Set **Infinite Extent (Unbound)** to true.
- Under **Lens > Exposure**, set **Min EV100** and **Max EV100** to **1.0**.
- Under **Lens > Local Exposure**, set **Highlight Contrast Scale** and **Shadow Contrast Scale** to **1.0**.
- Under **Rendering Features > Global Illumination**, set **Method** to **None**.

**Step 2: Disable Default Engine Lighting**
- Open `Config/DefaultEngine.ini`.
- Ensure `r.DefaultFeature.AutoExposure.ExtendDefaultLuminanceRange` is true.
- Set `r.DynamicGlobalIlluminationMethod=0`.

**Step 3: Verify in PIE**
- Run PIE.
- Expected: The entire world should be solid pitch-black, and the camera should not "hunt" for light when looking around.

**Step 4: Commit**
```bash
git add Config/DefaultEngine.ini
git commit -m "feat: lock global exposure and disable standard lighting"
```

---

### Task 2: Build Unlit Blueprint Master Material

**Files:**
- Modify: `Content/EchoLocation/Materials/M_EchoMaster.uasset`

**Step 1: Set Material to Unlit**
- Open `M_EchoMaster`.
- Set **Shading Model** to **Unlit**.

**Step 2: Create Procedural Grid Logic**
- Add a **`WorldPosition`** node.
- Component-Mask to **RG (XY)** and **RB (XZ)**.
- Divide by a new Scalar Parameter `GridSize` (Default: 100).
- Add a **`Frac`** node to the result.
- Use **`Step`** (or `SmoothStep`) to create thin lines.

**Step 3: Create Wireframe Edge Logic**
- Add a **`BoxMask-3D`** node.
- Use it to detect the edges of the mesh based on its bounds.

**Step 4: Combine with Vision Ripple**
- Add the Grid and Wireframe logic together.
- Multiply the result by a Vector Parameter `BlueprintColor` (Default: Cyan).
- Multiply the entire result by the existing `MPC_GlobalSound` ripple logic (SphereMask).
- Plug the final result into the **Emissive Color** pin.

**Step 5: Verify in PIE**
- Run PIE and trigger a "Slam."
- Expected: A crisp, neon-blue grid/wireframe "blueprint" expands and fades correctly in total darkness.

**Step 6: Commit**
```bash
git add Content/EchoLocation/Materials/M_EchoMaster.uasset
git commit -m "feat: implement unlit procedural blueprint material"
```

---

### Task 3: Implement Blueprint Sonar Visual Polish

**Files:**
- Create: `Content/EchoLocation/Materials/MI_EchoGrid.uasset` (Material Instance)
- Modify: `Content/EchoLocation/Maps/L_EchoPrototype.umap`

**Step 1: Refine Colors and Grid Scale**
- Open `MI_EchoGrid` (Instance of `M_EchoMaster`).
- Set `GridSize` to `100.0`.
- Set `BlueprintColor` to Cyan `(0, 1, 1)`.

**Step 2: Update All Modular Blocks**
- Apply `MI_EchoGrid` to all cubes, corridors, and hazards in the level.

**Step 3: Add Bloom Boost**
- Open the `PostProcessVolume`.
- Under **Rendering Features > Bloom**, set **Intensity** to **1.5** and **Threshold** to **0.0**.

**Step 4: Final Verification**
- Run PIE.
- Expected: The world is sharp, glowing, and feels like a professional "Blueprint" scan. No more visibility issues.

**Step 5: Commit**
```bash
git add Content/EchoLocation/
git commit -m "feat: apply blueprint sonar polish and post-processing"
```
