# Ink & Sonar Cel-Shading Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the Living Contour Map visual mode in M_EchoMaster with an "Ink & Sonar" comic-book aesthetic featuring dark ink outlines, cel-shading bands, and halftone dots.

**Architecture:** All changes are in two Python editor scripts — `13_build_blueprint_sonar_material.py` (material graph rebuild) and `06_create_material.py` (material instance colors). No C++ changes. The material is rebuilt from scratch each run (delete + recreate pattern). The Blueprint Sonar path (`UseFluxLook=False`) is unchanged.

**Tech Stack:** UE5 Material Editor via Python (`unreal.MaterialEditingLibrary`), Custom HLSL nodes, MPC parameters, Static Switch parameters.

**Spec:** `docs/superpowers/specs/2026-03-17-ink-and-paint-cel-shading-design.md`

---

## File Map

| File | Action | Responsibility |
|---|---|---|
| `Scripts/EditorUtility/helpers.py` | Modify | Add `MI_ECHO_OBSTACLE` path constant |
| `Scripts/EditorUtility/13_build_blueprint_sonar_material.py` | Rewrite section 5 + 6 | Replace contour map path with Ink & Sonar path |
| `Scripts/EditorUtility/06_create_material.py` | Modify | Update colors, add MI_EchoObstacle |

---

### Task 1: Add MI_EchoObstacle path to helpers.py

**Files:**
- Modify: `Scripts/EditorUtility/helpers.py:14` (add new path after MI_ECHO_ENEMY)

- [ ] **Step 1: Add the path constant**

```python
# In class Paths, after MI_ECHO_ENEMY line:
MI_ECHO_OBSTACLE     = f"{BASE}/Materials/MI_EchoObstacle"
```

- [ ] **Step 2: Commit**

```bash
git add Scripts/EditorUtility/helpers.py
git commit -m "feat: add MI_EchoObstacle path constant to helpers"
```

---

### Task 2: Rebuild M_EchoMaster — Parameters & Ink Outlines

Replaces section 1 (parameters) and section 5 of `13_build_blueprint_sonar_material.py`. This task handles the docstring, parameters, and edge detection tuning. Sections 1–4 (parameters, coordinates, sonar reveal, Blueprint path) are mostly unchanged except for swapping contour params with cel-shading params.

**Files:**
- Modify: `Scripts/EditorUtility/13_build_blueprint_sonar_material.py`

- [ ] **Step 1: Update docstring**

Replace the module docstring (lines 1-7) with:

```python
"""
13_build_blueprint_sonar_material.py — Ink & Sonar Material Rebuild.

Builds M_EchoMaster with two visual modes:
  - Blueprint Sonar (UseFluxLook=False): Grid + geometric edges
  - Ink & Sonar (UseFluxLook=True): Cel-bands + halftone dots + ink outlines + afterglow + proximity
"""
```

- [ ] **Step 2: Replace contour parameters with cel-shading parameters**

Remove the `ContourScale` and `ContourFlowSpeed` parameter creation (lines 60-66). Replace with:

```python
    # Tunable scalar parameters for Ink & Sonar mode
    num_bands_param = mel.create_material_expression(material, unreal.MaterialExpressionScalarParameter, -1200, 1800)
    num_bands_param.set_editor_property("parameter_name", "NumBands")
    num_bands_param.set_editor_property("default_value", 3.0)

    dot_scale_param = mel.create_material_expression(material, unreal.MaterialExpressionScalarParameter, -1200, 1900)
    dot_scale_param.set_editor_property("parameter_name", "DotScale")
    dot_scale_param.set_editor_property("default_value", 0.15)

    dot_contrast_param = mel.create_material_expression(material, unreal.MaterialExpressionScalarParameter, -1200, 2000)
    dot_contrast_param.set_editor_property("parameter_name", "DotContrast")
    dot_contrast_param.set_editor_property("default_value", 0.3)

    dot_min_param = mel.create_material_expression(material, unreal.MaterialExpressionScalarParameter, -1200, 2100)
    dot_min_param.set_editor_property("parameter_name", "DotMinSize")
    dot_min_param.set_editor_property("default_value", 0.15)

    dot_max_param = mel.create_material_expression(material, unreal.MaterialExpressionScalarParameter, -1200, 2200)
    dot_max_param.set_editor_property("parameter_name", "DotMaxSize")
    dot_max_param.set_editor_property("default_value", 0.4)
```

- [ ] **Step 3: Increase EdgeSensitivity default**

Change line 170 from `20.0` to `40.0`:

```python
    edge_sns.set_editor_property("default_value", 40.0)
```

- [ ] **Step 4: Commit**

```bash
git add Scripts/EditorUtility/13_build_blueprint_sonar_material.py
git commit -m "feat: replace contour params with cel-shading and halftone params, boost edge sensitivity"
```

---

### Task 3: Rebuild M_EchoMaster — Cel-Shading Bands (replaces contour lines)

Replaces section 5a (contour lines) with the cel-shading bands node and adds the proximity cel-bands node.

**Files:**
- Modify: `Scripts/EditorUtility/13_build_blueprint_sonar_material.py` — section 5a

- [ ] **Step 1: Replace contour lines with sonar cel-bands node**

Remove the entire contour lines section (contour_code, contour_node, contour_path — approximately lines 193-221). Replace with:

```python
    # 5a. Cel-Shading Bands HLSL (distance-to-impact quantized into discrete brightness steps)
    cel_bands_code = """
float3 WorldPos = LWCToFloat(GetWorldPosition(Parameters));
float DistToImpact = length(WorldPos - ImpactLoc);
if (StartTime <= 0.0) return 0.5;
float NB = max(NumBands, 1.0);
float DistRatio = saturate(DistToImpact / max(MaxRadius, 1.0));
float BandIndex = min(floor(DistRatio * NB), NB - 1.0);
return 1.0 - BandIndex / NB;
"""
    cel_bands_node = mel.create_material_expression(material, unreal.MaterialExpressionCustom, -1000, 1500)
    cel_bands_node.set_editor_property("code", cel_bands_code)
    cel_bands_node.set_editor_property("output_type", unreal.CustomMaterialOutputType.CMOT_FLOAT1)
    input_cb_il = unreal.CustomInput()
    input_cb_il.set_editor_property("input_name", "ImpactLoc")
    input_cb_mr = unreal.CustomInput()
    input_cb_mr.set_editor_property("input_name", "MaxRadius")
    input_cb_nb = unreal.CustomInput()
    input_cb_nb.set_editor_property("input_name", "NumBands")
    input_cb_st = unreal.CustomInput()
    input_cb_st.set_editor_property("input_name", "StartTime")
    cel_bands_node.set_editor_property("inputs", [input_cb_il, input_cb_mr, input_cb_nb, input_cb_st])
    mel.connect_material_expressions(mask_rgb, "", cel_bands_node, "ImpactLoc")
    mel.connect_material_expressions(max_radius_param, "", cel_bands_node, "MaxRadius")
    mel.connect_material_expressions(num_bands_param, "", cel_bands_node, "NumBands")
    mel.connect_material_expressions(ripple_start, "", cel_bands_node, "StartTime")
```

- [ ] **Step 2: Add proximity cel-bands node**

Add after the proximity_node section (after line ~297), before the ring_edge section:

```python
    # 5c-ii. Proximity Cel-Bands (player-distance banding for proximity zone)
    prox_bands_code = """
float3 WorldPos = LWCToFloat(GetWorldPosition(Parameters));
float DistToPlayer = length(WorldPos - PlayerPos);
float NB = max(NumBands, 1.0);
float ProxRatio = saturate(DistToPlayer / max(Radius, 1.0));
float BandIdx = min(floor(ProxRatio * NB), NB - 1.0);
return 1.0 - BandIdx / NB;
"""
    prox_bands_node = mel.create_material_expression(material, unreal.MaterialExpressionCustom, -1000, 2150)
    prox_bands_node.set_editor_property("code", prox_bands_code)
    prox_bands_node.set_editor_property("output_type", unreal.CustomMaterialOutputType.CMOT_FLOAT1)
    input_pb_pp = unreal.CustomInput()
    input_pb_pp.set_editor_property("input_name", "PlayerPos")
    input_pb_r = unreal.CustomInput()
    input_pb_r.set_editor_property("input_name", "Radius")
    input_pb_nb = unreal.CustomInput()
    input_pb_nb.set_editor_property("input_name", "NumBands")
    prox_bands_node.set_editor_property("inputs", [input_pb_pp, input_pb_r, input_pb_nb])
    mel.connect_material_expressions(player_pos_rgb, "", prox_bands_node, "PlayerPos")
    mel.connect_material_expressions(proximity_radius_param, "", prox_bands_node, "Radius")
    mel.connect_material_expressions(num_bands_param, "", prox_bands_node, "NumBands")
```

- [ ] **Step 3: Commit**

```bash
git add Scripts/EditorUtility/13_build_blueprint_sonar_material.py
git commit -m "feat: add cel-shading bands and proximity cel-bands nodes"
```

---

### Task 4: Rebuild M_EchoMaster — Halftone Dots

Adds the triplanar halftone dot pattern node.

**Files:**
- Modify: `Scripts/EditorUtility/13_build_blueprint_sonar_material.py` — new section after cel-bands

- [ ] **Step 1: Add halftone dots HLSL node**

Add after the proximity cel-bands node from Task 3, before the ring edge section:

```python
    # 5c-iii. Halftone Dots HLSL (triplanar screentone pattern)
    halftone_code = """
float3 N = abs(normalize(Parameters.WorldNormal));
N = N / (N.x + N.y + N.z + 0.001);
float2 uvXY = Position.xy * DotScale;
float2 uvXZ = Position.xz * DotScale;
float2 uvYZ = Position.yz * DotScale;
float dotXY = length(frac(uvXY) - 0.5);
float dotXZ = length(frac(uvXZ) - 0.5);
float dotYZ = length(frac(uvYZ) - 0.5);
float dot = dotXY * N.z + dotXZ * N.y + dotYZ * N.x;
float threshold = lerp(DotMinSize, DotMaxSize, CelBandValue);
float halftone = smoothstep(threshold - 0.02, threshold + 0.02, dot);
return lerp(1.0, 1.0 - DotContrast, halftone);
"""
    halftone_node = mel.create_material_expression(material, unreal.MaterialExpressionCustom, -1000, 2250)
    halftone_node.set_editor_property("code", halftone_code)
    halftone_node.set_editor_property("output_type", unreal.CustomMaterialOutputType.CMOT_FLOAT1)
    input_ht_pos = unreal.CustomInput()
    input_ht_pos.set_editor_property("input_name", "Position")
    input_ht_ds = unreal.CustomInput()
    input_ht_ds.set_editor_property("input_name", "DotScale")
    input_ht_cb = unreal.CustomInput()
    input_ht_cb.set_editor_property("input_name", "CelBandValue")
    input_ht_dc = unreal.CustomInput()
    input_ht_dc.set_editor_property("input_name", "DotContrast")
    input_ht_min = unreal.CustomInput()
    input_ht_min.set_editor_property("input_name", "DotMinSize")
    input_ht_max = unreal.CustomInput()
    input_ht_max.set_editor_property("input_name", "DotMaxSize")
    halftone_node.set_editor_property("inputs", [input_ht_pos, input_ht_ds, input_ht_cb, input_ht_dc, input_ht_min, input_ht_max])
    mel.connect_material_expressions(grid_coords_sw, "", halftone_node, "Position")
    mel.connect_material_expressions(dot_scale_param, "", halftone_node, "DotScale")
    # CelBandValue will be connected in Task 5 after the final cel_bands_combined is built
    mel.connect_material_expressions(dot_contrast_param, "", halftone_node, "DotContrast")
    mel.connect_material_expressions(dot_min_param, "", halftone_node, "DotMinSize")
    mel.connect_material_expressions(dot_max_param, "", halftone_node, "DotMaxSize")
```

- [ ] **Step 2: Commit**

```bash
git add Scripts/EditorUtility/13_build_blueprint_sonar_material.py
git commit -m "feat: add triplanar halftone dot pattern node"
```

---

### Task 5: Rebuild M_EchoMaster — Final Compositing (Section 5e + 6)

Rewires the reveal mask combine and the final output chain to use the new Ink & Sonar compositing: `cel_bands * halftone * (1 - ink) * reveal_mask * EchoColor`.

**Files:**
- Modify: `Scripts/EditorUtility/13_build_blueprint_sonar_material.py` — sections 5e and 6

- [ ] **Step 1: Replace section 5e combine and section 6 final output**

Remove everything from the current `# 5e. Combine` through to `mel.recompile_material`. Replace with:

```python
    # =========================================================================
    # 5e. INK & SONAR COMPOSITING
    # =========================================================================

    # Combined cel-bands: max(sonar_bands, proximity_bands)
    cel_bands_combined = mel.create_material_expression(material, unreal.MaterialExpressionMax, -600, 1600)
    mel.connect_material_expressions(cel_bands_node, "", cel_bands_combined, "A")
    mel.connect_material_expressions(prox_bands_node, "", cel_bands_combined, "B")

    # Connect CelBandValue input on halftone node (deferred from Task 4)
    mel.connect_material_expressions(cel_bands_combined, "", halftone_node, "CelBandValue")

    # Halftone for player path: feed 1.0 (full brightness) to get minimal dot coverage
    player_cel_const = mel.create_material_expression(material, unreal.MaterialExpressionConstant, -1000, 2400)
    player_cel_const.set_editor_property("r", 1.0)

    halftone_player_node = mel.create_material_expression(material, unreal.MaterialExpressionCustom, -800, 2400)
    halftone_player_node.set_editor_property("code", halftone_code)
    halftone_player_node.set_editor_property("output_type", unreal.CustomMaterialOutputType.CMOT_FLOAT1)
    # Reuse same input definitions
    input_hp_pos = unreal.CustomInput()
    input_hp_pos.set_editor_property("input_name", "Position")
    input_hp_ds = unreal.CustomInput()
    input_hp_ds.set_editor_property("input_name", "DotScale")
    input_hp_cb = unreal.CustomInput()
    input_hp_cb.set_editor_property("input_name", "CelBandValue")
    input_hp_dc = unreal.CustomInput()
    input_hp_dc.set_editor_property("input_name", "DotContrast")
    input_hp_min = unreal.CustomInput()
    input_hp_min.set_editor_property("input_name", "DotMinSize")
    input_hp_max = unreal.CustomInput()
    input_hp_max.set_editor_property("input_name", "DotMaxSize")
    halftone_player_node.set_editor_property("inputs", [input_hp_pos, input_hp_ds, input_hp_cb, input_hp_dc, input_hp_min, input_hp_max])
    mel.connect_material_expressions(grid_coords_sw, "", halftone_player_node, "Position")
    mel.connect_material_expressions(dot_scale_param, "", halftone_player_node, "DotScale")
    mel.connect_material_expressions(player_cel_const, "", halftone_player_node, "CelBandValue")
    mel.connect_material_expressions(dot_contrast_param, "", halftone_player_node, "DotContrast")
    mel.connect_material_expressions(dot_min_param, "", halftone_player_node, "DotMinSize")
    mel.connect_material_expressions(dot_max_param, "", halftone_player_node, "DotMaxSize")

    # Ink mask inversion: (1.0 - edge_node)
    one_const = mel.create_material_expression(material, unreal.MaterialExpressionConstant, -600, 1000)
    one_const.set_editor_property("r", 1.0)
    ink_invert = mel.create_material_expression(material, unreal.MaterialExpressionSubtract, -400, 1000)
    mel.connect_material_expressions(one_const, "", ink_invert, "A")
    mel.connect_material_expressions(edge_node, "", ink_invert, "B")

    # --- World Ink & Sonar path: cel_bands * halftone * (1 - ink) * reveal_mask ---

    # cel_bands * halftone
    world_cel_ht = mel.create_material_expression(material, unreal.MaterialExpressionMultiply, -400, 1600)
    mel.connect_material_expressions(cel_bands_combined, "", world_cel_ht, "A")
    mel.connect_material_expressions(halftone_node, "", world_cel_ht, "B")

    # * (1 - ink)
    world_cel_ht_ink = mel.create_material_expression(material, unreal.MaterialExpressionMultiply, -200, 1600)
    mel.connect_material_expressions(world_cel_ht, "", world_cel_ht_ink, "A")
    mel.connect_material_expressions(ink_invert, "", world_cel_ht_ink, "B")

    # * reveal_mask
    ink_sonar_masked = mel.create_material_expression(material, unreal.MaterialExpressionMultiply, 0, 1600)
    mel.connect_material_expressions(world_cel_ht_ink, "", ink_sonar_masked, "A")
    mel.connect_material_expressions(contour_reveal, "", ink_sonar_masked, "B")

    # --- Player Ink & Sonar path: 1.0 * halftone_player * (1 - ink) ---

    player_ht_ink = mel.create_material_expression(material, unreal.MaterialExpressionMultiply, -200, 2400)
    mel.connect_material_expressions(halftone_player_node, "", player_ht_ink, "A")
    mel.connect_material_expressions(ink_invert, "", player_ht_ink, "B")

    # =========================================================================
    # 6. FINAL COMBINE (UseFluxLook switch + IsPlayer bypass + EchoColor)
    # =========================================================================

    # --- World geometry path (IsPlayer=False): visual * reveal mask ---

    # Blueprint mode world: grid+edges * sonar ring mask (unchanged)
    world_masked_bp = mel.create_material_expression(material, unreal.MaterialExpressionMultiply, -400, 800)
    mel.connect_material_expressions(blueprint_path, "", world_masked_bp, "A")
    mel.connect_material_expressions(final_sonar, "", world_masked_bp, "B")

    # UseFluxLook switch for world geometry (non-player)
    world_mode_sw = mel.create_material_expression(material, unreal.MaterialExpressionStaticSwitchParameter, -200, 800)
    world_mode_sw.set_editor_property("parameter_name", "UseFluxLook")
    world_mode_sw.set_editor_property("default_value", False)
    mel.connect_material_expressions(ink_sonar_masked, "", world_mode_sw, "True")
    mel.connect_material_expressions(world_masked_bp, "", world_mode_sw, "False")

    # --- Player path (IsPlayer=True) ---

    # UseFluxLook switch for player visual
    player_visual_sw = mel.create_material_expression(material, unreal.MaterialExpressionStaticSwitchParameter, -200, 500)
    player_visual_sw.set_editor_property("parameter_name", "UseFluxLook")
    mel.connect_material_expressions(player_ht_ink, "", player_visual_sw, "True")
    mel.connect_material_expressions(blueprint_path, "", player_visual_sw, "False")

    # IsPlayer bypass: True = player visual, False = world masked visual
    visible_sw = mel.create_material_expression(material, unreal.MaterialExpressionStaticSwitchParameter, 0, 600)
    visible_sw.set_editor_property("parameter_name", "IsPlayer")
    mel.connect_material_expressions(player_visual_sw, "", visible_sw, "True")
    mel.connect_material_expressions(world_mode_sw, "", visible_sw, "False")

    # Final: visible * EchoColor
    emissive_final = mel.create_material_expression(material, unreal.MaterialExpressionMultiply, 200, 600)
    mel.connect_material_expressions(visible_sw, "", emissive_final, "A")
    mel.connect_material_expressions(echo_color, "", emissive_final, "B")

    mel.connect_material_property(emissive_final, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)

    mel.recompile_material(material)
    eal.save_asset(asset_path)
    unreal.log("SUCCESS: Rebuilt M_EchoMaster with Ink & Sonar mode.")
```

- [ ] **Step 2: Commit**

```bash
git add Scripts/EditorUtility/13_build_blueprint_sonar_material.py
git commit -m "feat: wire Ink & Sonar compositing — cel*halftone*(1-ink)*reveal*color"
```

---

### Task 6: Update Material Instances — Vibrant Colors + MI_EchoObstacle

**Files:**
- Modify: `Scripts/EditorUtility/06_create_material.py`

- [ ] **Step 1: Update colors and add MI_EchoObstacle**

Replace the entire `run()` function:

```python
def run():
    # World: WorldSpace, Masked by Sonar, Vibrant Blue
    _setup_instance(Paths.MI_ECHO_MASTER, "MI_EchoMaster",
                    is_actor=False, is_player=False, use_flux=True,
                    echo_color=unreal.LinearColor(0.0, 200.0, 800.0, 1.0))
    # Obstacle: WorldSpace, Masked by Sonar, Vivid Purple
    _setup_instance(Paths.MI_ECHO_OBSTACLE, "MI_EchoObstacle",
                    is_actor=False, is_player=False, use_flux=True,
                    echo_color=unreal.LinearColor(400.0, 0.0, 800.0, 1.0))
    # Enemy: LocalSpace, Masked by Sonar, Hot Red
    _setup_instance(Paths.MI_ECHO_ENEMY, "MI_EchoEnemy",
                    is_actor=True, is_player=False, use_flux=True,
                    echo_color=unreal.LinearColor(800.0, 50.0, 0.0, 1.0))
    # Player: LocalSpace, Always Visible, Bright Green
    _setup_instance(Paths.MI_ECHO_PLAYER, "MI_EchoPlayer",
                    is_actor=True, is_player=True, use_flux=True,
                    echo_color=unreal.LinearColor(0.0, 800.0, 100.0, 1.0))
```

Also update the import to include the new path:

```python
from helpers import Paths, BASE, asset_exists, ensure_directory, save_asset
```

(No change needed — `Paths.MI_ECHO_OBSTACLE` is already accessible via the helpers change in Task 1.)

- [ ] **Step 2: Commit**

```bash
git add Scripts/EditorUtility/06_create_material.py
git commit -m "feat: update material instance colors and add MI_EchoObstacle"
```

---

### Task 7: Run Scripts in Editor & Verify

This task is manual — run the scripts in the UE5 Editor Python console and verify visually.

- [ ] **Step 1: Open UE5 Editor with the project**

- [ ] **Step 2: Run material rebuild script**

In the Output Log Python console:

```python
exec(open("Scripts/EditorUtility/13_build_blueprint_sonar_material.py").read()); run()
```

Expected output: `SUCCESS: Rebuilt M_EchoMaster with Ink & Sonar mode.`

- [ ] **Step 3: Run material instance script**

```python
exec(open("Scripts/EditorUtility/06_create_material.py").read()); run()
```

Expected output: `Saved MI_EchoMaster ...`, `Saved MI_EchoObstacle ...`, `Saved MI_EchoEnemy ...`, `Saved MI_EchoPlayer ...`

- [ ] **Step 4: Assign MI_EchoObstacle to obstacle actors**

In the level `L_EchoPrototype`, select the 4 obstacle cubes (`Obstacle_0` through `Obstacle_3`). Set their material to `MI_EchoObstacle`.

- [ ] **Step 5: Re-apply MI_EchoMaster to floor and walls**

Select `Floor`, `Wall_North`, `Wall_South`, `Wall_East`, `Wall_West`. Verify or set material to `MI_EchoMaster`.

- [ ] **Step 6: PIE and verify**

Play In Editor. Verify:
- **Standing still:** Faint proximity glow nearby with cel-banding (3 brightness steps centered on player). Halftone dots visible on surfaces. Dark ink outlines on cube/wall edges.
- **Slam:** Bright expanding ring edge. Behind the ring, cel-shaded geometry with halftone dots and ink outlines. Geometry dissolves via noise as afterglow decays.
- **Color:** Walls/floor = vibrant blue, obstacles = vivid purple, player cube = bright green.
- **Player cube:** Always visible, bright green with dark ink edges and minimal dot pattern.
- **No pulsing/flashing** on flat surfaces.

- [ ] **Step 7: Final commit**

```bash
git add -A
git commit -m "feat: implement Ink & Sonar cel-shaded visual mode"
```
