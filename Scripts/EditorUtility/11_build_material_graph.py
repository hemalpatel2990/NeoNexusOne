"""
11_build_material_graph.py — Build the M_EchoMaster SphereMask ring shader node graph.

Depends on: 06_create_material.py (M_EchoMaster must exist), 01_create_mpc.py (MPC_GlobalSound)

Constructs the material node graph programmatically:
  - Reads MPC_GlobalSound parameters (LastImpactLocation, CurrentRippleRadius, RippleIntensity)
  - SphereMask node: pixel WorldPosition vs LastImpactLocation, radius from MPC
  - SmoothStep inner/outer ring mask
  - Emissive = white * ring mask * RippleIntensity * emissive multiplier
  - Base Color = near-black constant

Uses MaterialEditingLibrary to create expressions and connect them.
"""

import sys
import os
import unreal

try:
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    SCRIPT_DIR = os.path.join(unreal.Paths.project_dir(), "Scripts", "EditorUtility").replace("\\", "/")

if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from helpers import Paths, MPCParams, asset_exists, save_asset, log_created, log_manual


def run():
    _build_material_graph()


def _build_material_graph():
    """Wire the SphereMask ring shader into M_EchoMaster."""
    path = Paths.M_ECHO_MASTER
    if not asset_exists(path):
        unreal.log_error("[EchoSetup] M_EchoMaster not found. Run 06_create_material first.")
        return

    material = unreal.load_asset(path)
    if material is None:
        unreal.log_error("[EchoSetup] Failed to load M_EchoMaster")
        return

    mel = unreal.MaterialEditingLibrary

    # Check if material already has expressions (avoid double-wiring)
    existing = mel.get_used_textures(material)  # lightweight check
    # More reliable: check expression count via the material's expressions
    try:
        expressions = material.get_editor_property("expressions")
        if expressions is not None and len(expressions) > 0:
            unreal.log("[EchoSetup] M_EchoMaster already has expressions, skipping graph build")
            return
    except Exception:
        pass  # Proceed if we can't check

    mpc = unreal.load_asset(Paths.MPC_GLOBAL_SOUND)
    if mpc is None:
        unreal.log_error("[EchoSetup] MPC_GlobalSound not found. Run 01_create_mpc first.")
        return

    # =====================================================================
    # Create expression nodes
    # =====================================================================

    # --- MPC parameters ---
    # LastImpactLocation (Vector)
    mpc_location = mel.create_material_expression(
        material, unreal.MaterialExpressionCollectionParameter, -1200, -200
    )
    mpc_location.set_editor_property("collection", mpc)
    mpc_location.set_editor_property("parameter_name", unreal.Name(MPCParams.LAST_IMPACT_LOCATION))

    # CurrentRippleRadius (Scalar)
    mpc_radius = mel.create_material_expression(
        material, unreal.MaterialExpressionCollectionParameter, -1200, 0
    )
    mpc_radius.set_editor_property("collection", mpc)
    mpc_radius.set_editor_property("parameter_name", unreal.Name(MPCParams.CURRENT_RIPPLE_RADIUS))

    # RippleIntensity (Scalar)
    mpc_intensity = mel.create_material_expression(
        material, unreal.MaterialExpressionCollectionParameter, -1200, 200
    )
    mpc_intensity.set_editor_property("collection", mpc)
    mpc_intensity.set_editor_property("parameter_name", unreal.Name(MPCParams.RIPPLE_INTENSITY))

    # --- World Position ---
    world_pos = mel.create_material_expression(
        material, unreal.MaterialExpressionWorldPosition, -1200, -400
    )

    # --- Mask MPC vector to RGB (float4 → float3) to match WorldPosition LWCVector3 ---
    mask_node = mel.create_material_expression(
        material, unreal.MaterialExpressionComponentMask, -1000, -200
    )
    mask_node.set_editor_property("r", True)
    mask_node.set_editor_property("g", True)
    mask_node.set_editor_property("b", True)
    mask_node.set_editor_property("a", False)
    mel.connect_material_expressions(mpc_location, "", mask_node, "")

    # --- Distance from impact ---
    # Distance(WorldPosition, LastImpactLocation.RGB)
    distance_node = mel.create_material_expression(
        material, unreal.MaterialExpressionDistance, -800, -200
    )
    mel.connect_material_expressions(world_pos, "", distance_node, "A")
    mel.connect_material_expressions(mask_node, "", distance_node, "B")

    # --- Divide distance by radius to get normalized distance (0=center, 1=edge) ---
    divide_node = mel.create_material_expression(
        material, unreal.MaterialExpressionDivide, -700, -200
    )
    mel.connect_material_expressions(distance_node, "", divide_node, "A")
    mel.connect_material_expressions(mpc_radius, "", divide_node, "B")

    # --- Ring mask using SmoothStep ---
    # Inner edge of ring: SmoothStep(0.7, 0.85, normalizedDist) — ramps up
    # Outer edge of ring: 1 - SmoothStep(0.9, 1.0, normalizedDist) — ramps down
    # Ring = inner * outer

    # Inner ring edge constants
    inner_low = mel.create_material_expression(
        material, unreal.MaterialExpressionConstant, -600, -400
    )
    inner_low.set_editor_property("r", 0.7)

    inner_high = mel.create_material_expression(
        material, unreal.MaterialExpressionConstant, -600, -350
    )
    inner_high.set_editor_property("r", 0.85)

    # SmoothStep for inner edge
    inner_smooth = mel.create_material_expression(
        material, unreal.MaterialExpressionSmoothStep, -400, -350
    )
    mel.connect_material_expressions(inner_low, "", inner_smooth, "Min")
    mel.connect_material_expressions(inner_high, "", inner_smooth, "Max")
    mel.connect_material_expressions(divide_node, "", inner_smooth, "Value")

    # Outer ring edge constants
    outer_low = mel.create_material_expression(
        material, unreal.MaterialExpressionConstant, -600, -200
    )
    outer_low.set_editor_property("r", 0.9)

    outer_high = mel.create_material_expression(
        material, unreal.MaterialExpressionConstant, -600, -150
    )
    outer_high.set_editor_property("r", 1.0)

    # SmoothStep for outer edge
    outer_smooth = mel.create_material_expression(
        material, unreal.MaterialExpressionSmoothStep, -400, -150
    )
    mel.connect_material_expressions(outer_low, "", outer_smooth, "Min")
    mel.connect_material_expressions(outer_high, "", outer_smooth, "Max")
    mel.connect_material_expressions(divide_node, "", outer_smooth, "Value")

    # OneMinus the outer smooth to invert it (1 inside, 0 outside)
    one_minus = mel.create_material_expression(
        material, unreal.MaterialExpressionOneMinus, -200, -150
    )
    mel.connect_material_expressions(outer_smooth, "", one_minus, "")

    # Multiply inner * (1 - outer) = ring mask
    ring_mask = mel.create_material_expression(
        material, unreal.MaterialExpressionMultiply, -50, -250
    )
    mel.connect_material_expressions(inner_smooth, "", ring_mask, "A")
    mel.connect_material_expressions(one_minus, "", ring_mask, "B")

    # --- Multiply ring mask by RippleIntensity ---
    intensity_multiply = mel.create_material_expression(
        material, unreal.MaterialExpressionMultiply, 150, -200
    )
    mel.connect_material_expressions(ring_mask, "", intensity_multiply, "A")
    mel.connect_material_expressions(mpc_intensity, "", intensity_multiply, "B")

    # --- Emissive multiplier ---
    emissive_mult_const = mel.create_material_expression(
        material, unreal.MaterialExpressionConstant, 150, -50
    )
    emissive_mult_const.set_editor_property("r", 5.0)

    emissive_final = mel.create_material_expression(
        material, unreal.MaterialExpressionMultiply, 350, -200
    )
    mel.connect_material_expressions(intensity_multiply, "", emissive_final, "A")
    mel.connect_material_expressions(emissive_mult_const, "", emissive_final, "B")

    # --- Base Color: near-black ---
    base_color = mel.create_material_expression(
        material, unreal.MaterialExpressionConstant3Vector, 350, 100
    )
    base_color.set_editor_property("constant", unreal.LinearColor(0.02, 0.02, 0.02, 1.0))

    # =====================================================================
    # Connect to material outputs
    # =====================================================================
    mel.connect_material_property(emissive_final, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    mel.connect_material_property(base_color, "", unreal.MaterialProperty.MP_BASE_COLOR)

    # --- Roughness = 1 (fully rough, no reflections needed) ---
    roughness_const = mel.create_material_expression(
        material, unreal.MaterialExpressionConstant, 350, 250
    )
    roughness_const.set_editor_property("r", 1.0)
    mel.connect_material_property(roughness_const, "", unreal.MaterialProperty.MP_ROUGHNESS)

    # =====================================================================
    # Recompile and save
    # =====================================================================
    mel.recompile_material(material)
    save_asset(path)
    log_created("M_EchoMaster node graph", path)

    unreal.log("[EchoSetup] M_EchoMaster ring shader built successfully:")
    unreal.log("  WorldPos + MPC distance -> normalized -> SmoothStep ring -> emissive")
    unreal.log("  Tune ring shape by adjusting SmoothStep constants (0.7/0.85 inner, 0.9/1.0 outer)")


if __name__ == "__main__":
    run()
