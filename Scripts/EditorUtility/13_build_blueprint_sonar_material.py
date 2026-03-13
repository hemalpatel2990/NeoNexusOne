"""
13_build_blueprint_sonar_material.py — Generates the perfect Blueprint Sonar Master Material.

This script creates the M_EchoMaster material that uses
procedurally generated Blueprint Sonar math (Unlit, World Grid, Contact Shadows, 
Geometric Derivative Edges with 3D Jitter, and the Ripple Mask combination logic). 
"""

import unreal
import os
import sys

try:
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    SCRIPT_DIR = os.path.join(unreal.Paths.project_dir(), "Scripts", "EditorUtility").replace("\\", "/")

if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from helpers import Paths, MPCParams

def run():
    asset_path = Paths.M_ECHO_MASTER
    mpc_path = Paths.MPC_GLOBAL_SOUND
    
    eal = unreal.EditorAssetLibrary
    mel = unreal.MaterialEditingLibrary
    
    # 1. Create the new material
    if eal.does_asset_exist(asset_path):
        eal.delete_asset(asset_path)
    
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    material_factory = unreal.MaterialFactoryNew()
    material = asset_tools.create_asset("M_EchoMaster", "/Game/EchoLocation/Materials", unreal.Material, material_factory)
    
    if not material:
        unreal.log_error("Failed to create M_EchoMaster")
        return
        
    # Set to Unlit
    material.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
    
    mpc = unreal.load_asset(mpc_path)

    # =====================================================================
    # BLOCK 1: RIPPLE MASK (The Energy Wave & Mask)
    # =====================================================================
    unreal.log("Building Ripple Mask...")
    
    loc_node = mel.create_material_expression(material, unreal.MaterialExpressionCollectionParameter, -1500, -200)
    loc_node.set_editor_property("collection", mpc)
    loc_node.set_editor_property("parameter_name", unreal.Name(MPCParams.LAST_IMPACT_LOCATION))
    
    mask_rgb = mel.create_material_expression(material, unreal.MaterialExpressionComponentMask, -1300, -200)
    mask_rgb.set_editor_property("r", True); mask_rgb.set_editor_property("g", True); mask_rgb.set_editor_property("b", True); mask_rgb.set_editor_property("a", False)
    mel.connect_material_expressions(loc_node, "", mask_rgb, "")
    
    world_pos_ripple = mel.create_material_expression(material, unreal.MaterialExpressionWorldPosition, -1500, -400)
    
    dist_node = mel.create_material_expression(material, unreal.MaterialExpressionDistance, -1100, -300)
    mel.connect_material_expressions(world_pos_ripple, "", dist_node, "A")
    mel.connect_material_expressions(mask_rgb, "", dist_node, "B")
    
    rad_node = mel.create_material_expression(material, unreal.MaterialExpressionCollectionParameter, -1300, -100)
    rad_node.set_editor_property("collection", mpc)
    rad_node.set_editor_property("parameter_name", unreal.Name(MPCParams.CURRENT_RIPPLE_RADIUS))
    
    div_ripple = mel.create_material_expression(material, unreal.MaterialExpressionDivide, -950, -250)
    mel.connect_material_expressions(dist_node, "", div_ripple, "A")
    mel.connect_material_expressions(rad_node, "", div_ripple, "B")
    
    # --- The Geometry Reveal Mask (Circle) ---
    geo_mask_node = mel.create_material_expression(material, unreal.MaterialExpressionOneMinus, -800, -350)
    geo_sat = mel.create_material_expression(material, unreal.MaterialExpressionSaturate, -900, -350)
    mel.connect_material_expressions(div_ripple, "", geo_sat, "")
    mel.connect_material_expressions(geo_sat, "", geo_mask_node, "")
    
    # --- The Energy Wave Ring ---
    ring_in = mel.create_material_expression(material, unreal.MaterialExpressionSmoothStep, -800, -150)
    rin_min = mel.create_material_expression(material, unreal.MaterialExpressionConstant, -950, -200); rin_min.set_editor_property("r", 0.8)
    rin_max = mel.create_material_expression(material, unreal.MaterialExpressionConstant, -950, -150); rin_max.set_editor_property("r", 0.95)
    mel.connect_material_expressions(rin_min, "", ring_in, "Min"); mel.connect_material_expressions(rin_max, "", ring_in, "Max"); mel.connect_material_expressions(div_ripple, "", ring_in, "Value")
    
    ring_out = mel.create_material_expression(material, unreal.MaterialExpressionSmoothStep, -800, 0)
    rout_min = mel.create_material_expression(material, unreal.MaterialExpressionConstant, -950, 0); rout_min.set_editor_property("r", 0.95)
    rout_max = mel.create_material_expression(material, unreal.MaterialExpressionConstant, -950, 50); rout_max.set_editor_property("r", 1.0)
    mel.connect_material_expressions(rout_min, "", ring_out, "Min"); mel.connect_material_expressions(rout_max, "", ring_out, "Max"); mel.connect_material_expressions(div_ripple, "", ring_out, "Value")
    
    ring_inv = mel.create_material_expression(material, unreal.MaterialExpressionOneMinus, -650, 0)
    mel.connect_material_expressions(ring_out, "", ring_inv, "")
    
    wave_ring = mel.create_material_expression(material, unreal.MaterialExpressionMultiply, -500, -100)
    mel.connect_material_expressions(ring_in, "", wave_ring, "A"); mel.connect_material_expressions(ring_inv, "", wave_ring, "B")
    
    # Global Intensity from MPC
    int_node = mel.create_material_expression(material, unreal.MaterialExpressionCollectionParameter, -650, -200)
    int_node.set_editor_property("collection", mpc)
    int_node.set_editor_property("parameter_name", unreal.Name(MPCParams.RIPPLE_INTENSITY))
    
    # Final Ripple Outputs
    final_geo_mask = mel.create_material_expression(material, unreal.MaterialExpressionMultiply, -350, -300)
    mel.connect_material_expressions(geo_mask_node, "", final_geo_mask, "A"); mel.connect_material_expressions(int_node, "", final_geo_mask, "B")
    
    final_wave_ring = mel.create_material_expression(material, unreal.MaterialExpressionMultiply, -350, -100)
    mel.connect_material_expressions(wave_ring, "", final_wave_ring, "A"); mel.connect_material_expressions(int_node, "", final_wave_ring, "B")

    # =====================================================================
    # BLOCK 2: GRID (World Position)
    # =====================================================================
    unreal.log("Building Grid...")
    grid_wp = mel.create_material_expression(material, unreal.MaterialExpressionWorldPosition, -1200, 600)
    grid_div = mel.create_material_expression(material, unreal.MaterialExpressionDivide, -1000, 600)
    grid_size = mel.create_material_expression(material, unreal.MaterialExpressionScalarParameter, -1200, 700); grid_size.set_editor_property("parameter_name", unreal.Name("GridSize")); grid_size.set_editor_property("default_value", 100.0)
    mel.connect_material_expressions(grid_wp, "", grid_div, "A"); mel.connect_material_expressions(grid_size, "", grid_div, "B")
    grid_frac = mel.create_material_expression(material, unreal.MaterialExpressionFrac, -850, 600)
    mel.connect_material_expressions(grid_div, "", grid_frac, "")
    grid_step_node = mel.create_material_expression(material, unreal.MaterialExpressionStep, -700, 600)
    grid_thick = mel.create_material_expression(material, unreal.MaterialExpressionScalarParameter, -850, 700); grid_thick.set_editor_property("parameter_name", unreal.Name("GridThickness")); grid_thick.set_editor_property("default_value", 0.02)
    mel.connect_material_expressions(grid_frac, "", grid_step_node, "X"); mel.connect_material_expressions(grid_thick, "", grid_step_node, "Y")
    
    # Invert grid step to get thin glowing lines
    grid_inv = mel.create_material_expression(material, unreal.MaterialExpressionOneMinus, -550, 600)
    mel.connect_material_expressions(grid_step_node, "", grid_inv, "")
    
    grid_mask_r = mel.create_material_expression(material, unreal.MaterialExpressionComponentMask, -400, 550); grid_mask_r.set_editor_property("r", True); grid_mask_r.set_editor_property("g", False); grid_mask_r.set_editor_property("b", False)
    grid_mask_g = mel.create_material_expression(material, unreal.MaterialExpressionComponentMask, -400, 600); grid_mask_g.set_editor_property("r", False); grid_mask_g.set_editor_property("g", True); grid_mask_g.set_editor_property("b", False)
    grid_mask_b = mel.create_material_expression(material, unreal.MaterialExpressionComponentMask, -400, 650); grid_mask_b.set_editor_property("r", False); grid_mask_g.set_editor_property("g", False); grid_mask_b.set_editor_property("b", True)
    mel.connect_material_expressions(grid_inv, "", grid_mask_r, ""); mel.connect_material_expressions(grid_inv, "", grid_mask_g, ""); mel.connect_material_expressions(grid_inv, "", grid_mask_b, "")
    
    grid_add1 = mel.create_material_expression(material, unreal.MaterialExpressionAdd, -200, 600); mel.connect_material_expressions(grid_mask_r, "", grid_add1, "A"); mel.connect_material_expressions(grid_mask_g, "", grid_add1, "B")
    grid_add2 = mel.create_material_expression(material, unreal.MaterialExpressionAdd, -50, 600); mel.connect_material_expressions(grid_add1, "", grid_add2, "A"); mel.connect_material_expressions(grid_mask_b, "", grid_add2, "B")
    
    # =====================================================================
    # BLOCK 3: CONTACT LINES
    # =====================================================================
    unreal.log("Building Contact Lines...")
    cont_dist = mel.create_material_expression(material, unreal.MaterialExpressionDistanceToNearestSurface, -900, 900)
    cont_div = mel.create_material_expression(material, unreal.MaterialExpressionDivide, -700, 900)
    cont_thick = mel.create_material_expression(material, unreal.MaterialExpressionScalarParameter, -900, 1000); cont_thick.set_editor_property("parameter_name", unreal.Name("ContactThickness")); cont_thick.set_editor_property("default_value", 25.0)
    mel.connect_material_expressions(cont_dist, "", cont_div, "A"); mel.connect_material_expressions(cont_thick, "", cont_div, "B")
    cont_sat = mel.create_material_expression(material, unreal.MaterialExpressionSaturate, -550, 900); mel.connect_material_expressions(cont_div, "", cont_sat, "")
    cont_one_minus = mel.create_material_expression(material, unreal.MaterialExpressionOneMinus, -400, 900); mel.connect_material_expressions(cont_sat, "", cont_one_minus, "")

    # =====================================================================
    # BLOCK 4: GEOMETRIC EDGES (fwidth Normal)
    # =====================================================================
    unreal.log("Building Geometric Edges...")
    edge_code = """
float3 N = normalize(Parameters.WorldNormal);
float Edge = length(fwidth(N));

// Normalize width by distance so edges stay crisp
float Dist = length(Parameters.WorldPosition - View.WorldCameraOrigin);
float NormalizedEdge = Edge * (EdgeSensitivity / (Dist * 0.001 + 1.0));

return saturate(NormalizedEdge);
"""
    edge_node = mel.create_material_expression(material, unreal.MaterialExpressionCustom, -900, 1200)
    edge_node.set_editor_property("code", edge_code)
    edge_node.set_editor_property("output_type", unreal.CustomMaterialOutputType.CMOT_FLOAT1)
    
    edge_sens = mel.create_material_expression(material, unreal.MaterialExpressionScalarParameter, -1100, 1300)
    edge_sens.set_editor_property("parameter_name", unreal.Name("EdgeSensitivity"))
    edge_sens.set_editor_property("default_value", 10.0)
    
    # Custom node inputs
    sens_input = unreal.CustomInput()
    sens_input.set_editor_property("input_name", "EdgeSensitivity")
    edge_node.set_editor_property("inputs", [sens_input])
    
    mel.connect_material_expressions(edge_sens, "", edge_node, "EdgeSensitivity")

    # Intensity-Gated 3D Jitter for Geometric Edges
    jitter_int = mel.create_material_expression(material, unreal.MaterialExpressionCollectionParameter, -1100, 1450)
    jitter_int.set_editor_property("collection", mpc)
    jitter_int.set_editor_property("parameter_name", unreal.Name(MPCParams.DIGITAL_JITTER_INTENSITY))
    
    # 3D Noise based on WorldPosition
    noise_wp = mel.create_material_expression(material, unreal.MaterialExpressionWorldPosition, -1300, 1500)
    time_node_noise = mel.create_material_expression(material, unreal.MaterialExpressionTime, -1300, 1600)
    
    noise_wp_add = mel.create_material_expression(material, unreal.MaterialExpressionAdd, -1100, 1550)
    mel.connect_material_expressions(noise_wp, "", noise_wp_add, "A")
    mel.connect_material_expressions(time_node_noise, "", noise_wp_add, "B")
    
    # Dot product for 3D noise (Pseudo-Random Hash)
    noise_dot_3d = mel.create_material_expression(material, unreal.MaterialExpressionDotProduct, -900, 1550)
    mel.connect_material_expressions(noise_wp_add, "", noise_dot_3d, "A")
    dot_const_3d = mel.create_material_expression(material, unreal.MaterialExpressionVectorParameter, -1000, 1650)
    dot_const_3d.set_editor_property("default_value", unreal.LinearColor(12.9898, 78.233, 45.164, 0))
    mel.connect_material_expressions(dot_const_3d, "", noise_dot_3d, "B")
    
    noise_sine_3d = mel.create_material_expression(material, unreal.MaterialExpressionSine, -750, 1550)
    mel.connect_material_expressions(noise_dot_3d, "", noise_sine_3d, "")
    
    noise_frac_3d = mel.create_material_expression(material, unreal.MaterialExpressionFrac, -600, 1550)
    mel.connect_material_expressions(noise_sine_3d, "", noise_frac_3d, "")
    
    # Jitter multiplier: 1.0 - (Frac * JitterIntensity)
    jitter_mul_3d = mel.create_material_expression(material, unreal.MaterialExpressionMultiply, -450, 1500)
    mel.connect_material_expressions(noise_frac_3d, "", jitter_mul_3d, "A")
    mel.connect_material_expressions(jitter_int, "", jitter_mul_3d, "B")
    
    jitter_inv_3d = mel.create_material_expression(material, unreal.MaterialExpressionOneMinus, -300, 1500)
    mel.connect_material_expressions(jitter_mul_3d, "", jitter_inv_3d, "")
    
    # Apply jitter to edge_node
    edge_jittered = mel.create_material_expression(material, unreal.MaterialExpressionMultiply, -150, 1200)
    mel.connect_material_expressions(edge_node, "", edge_jittered, "A")
    mel.connect_material_expressions(jitter_inv_3d, "", edge_jittered, "B")

    # =====================================================================
    # FINAL COMBINE
    # =====================================================================
    unreal.log("Wiring Final Combine...")
    
    # Blueprint Detail = Grid + Contact + GeometricEdges
    detail_sum = mel.create_material_expression(material, unreal.MaterialExpressionAdd, 150, 600)
    mel.connect_material_expressions(grid_add2, "", detail_sum, "A")
    mel.connect_material_expressions(cont_one_minus, "", detail_sum, "B")
    
    detail_total = mel.create_material_expression(material, unreal.MaterialExpressionAdd, 350, 600)
    mel.connect_material_expressions(detail_sum, "", detail_total, "A")
    mel.connect_material_expressions(edge_jittered, "", detail_total, "B")
    
    # Detail is only visible where the sonar has reached
    detail_masked = mel.create_material_expression(material, unreal.MaterialExpressionMultiply, 550, 500)
    mel.connect_material_expressions(detail_total, "", detail_masked, "A")
    mel.connect_material_expressions(final_geo_mask, "", detail_masked, "B")
    
    # Final Visual = Max(Masked Detail, Sharp Wave Ring)
    final_visual = mel.create_material_expression(material, unreal.MaterialExpressionMax, 750, 400)
    mel.connect_material_expressions(detail_masked, "", final_visual, "A")
    mel.connect_material_expressions(final_wave_ring, "", final_visual, "B")
    
    blueprint_color = mel.create_material_expression(material, unreal.MaterialExpressionVectorParameter, 750, 600)
    blueprint_color.set_editor_property("parameter_name", unreal.Name("BlueprintColor"))
    blueprint_color.set_editor_property("default_value", unreal.LinearColor(0.0, 1.0, 1.0, 1.0))
    
    world_out = mel.create_material_expression(material, unreal.MaterialExpressionMultiply, 950, 450)
    mel.connect_material_expressions(final_visual, "", world_out, "A")
    mel.connect_material_expressions(blueprint_color, "", world_out, "B")
    
    mel.connect_material_property(world_out, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    
    mel.recompile_material(material)
    unreal.EditorAssetLibrary.save_asset(asset_path)
    unreal.log("=========================================")
    unreal.log(f"SUCCESS: Created {asset_path}")
    unreal.log("=========================================")

if __name__ == "__main__":
    run()
