"""
13_build_blueprint_sonar_material.py — Robust Coordinate Stability Rewrite.

Fixes: Grid rotation using internal LocalPosition node and HDR Overdrive.
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
    
    if eal.does_asset_exist(asset_path):
        eal.delete_asset(asset_path)
    
    material = unreal.AssetToolsHelpers.get_asset_tools().create_asset("M_EchoMaster", "/Game/EchoLocation/Materials", unreal.Material, factory=unreal.MaterialFactoryNew())
    material.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
    mpc = unreal.load_asset(mpc_path)

    # 1. PARAMETERS
    is_actor_sw = mel.create_material_expression(material, unreal.MaterialExpressionStaticSwitchParameter, -1000, 0)
    is_actor_sw.set_editor_property("parameter_name", "IsActor")

    # 2. COORDINATES (LocalPosition for Actors, WorldPosition for World)
    wp = mel.create_material_expression(material, unreal.MaterialExpressionWorldPosition, -1600, 400)
    lp = mel.create_material_expression(material, unreal.MaterialExpressionLocalPosition, -1600, 500)
    
    grid_coords_sw = mel.create_material_expression(material, unreal.MaterialExpressionStaticSwitchParameter, -1200, 400)
    grid_coords_sw.set_editor_property("parameter_name", "IsActor")
    mel.connect_material_expressions(lp, "", grid_coords_sw, "True")
    mel.connect_material_expressions(wp, "", grid_coords_sw, "False")

    # 3. SONAR REVEAL
    loc = mel.create_material_expression(material, unreal.MaterialExpressionCollectionParameter, -1500, -200)
    loc.set_editor_property("collection", mpc); loc.set_editor_property("parameter_name", unreal.Name(MPCParams.LAST_IMPACT_LOCATION))
    mask_rgb = mel.create_material_expression(material, unreal.MaterialExpressionComponentMask, -1300, -200)
    mask_rgb.set_editor_property("r", True); mask_rgb.set_editor_property("g", True); mask_rgb.set_editor_property("b", True)
    mel.connect_material_expressions(loc, "", mask_rgb, "")
    
    dist = mel.create_material_expression(material, unreal.MaterialExpressionDistance, -1100, -100)
    mel.connect_material_expressions(wp, "", dist, "A"); mel.connect_material_expressions(mask_rgb, "", dist, "B")
    
    rad = mel.create_material_expression(material, unreal.MaterialExpressionCollectionParameter, -1300, 0)
    rad.set_editor_property("collection", mpc); rad.set_editor_property("parameter_name", unreal.Name(MPCParams.CURRENT_RIPPLE_RADIUS))
    
    reveal_sub = mel.create_material_expression(material, unreal.MaterialExpressionSubtract, -900, 0)
    mel.connect_material_expressions(rad, "", reveal_sub, "A"); mel.connect_material_expressions(dist, "", reveal_sub, "B")
    reveal_mask = mel.create_material_expression(material, unreal.MaterialExpressionSaturate, -750, 0)
    mel.connect_material_expressions(reveal_sub, "", reveal_mask, "")
    
    inten = mel.create_material_expression(material, unreal.MaterialExpressionCollectionParameter, -600, 0)
    inten.set_editor_property("collection", mpc); inten.set_editor_property("parameter_name", unreal.Name(MPCParams.RIPPLE_INTENSITY))
    
    final_sonar = mel.create_material_expression(material, unreal.MaterialExpressionMultiply, -400, 0)
    mel.connect_material_expressions(reveal_mask, "", final_sonar, "A"); mel.connect_material_expressions(inten, "", final_sonar, "B")

    # 4. CUSTOM HLSL GRID
    grid_code = """
float3 p = Position / GridSize;
float3 grid = abs(frac(p - 0.5) - 0.5) / fwidth(p);
float val = min(grid.x, min(grid.y, grid.z));
return 1.0 - saturate(val / Thickness);
"""
    grid_node = mel.create_material_expression(material, unreal.MaterialExpressionCustom, -1000, 600)
    grid_node.set_editor_property("code", grid_code); grid_node.set_editor_property("output_type", unreal.CustomMaterialOutputType.CMOT_FLOAT1)
    
    input_p = unreal.CustomInput(); input_p.set_editor_property("input_name", "Position")
    input_s = unreal.CustomInput(); input_s.set_editor_property("input_name", "GridSize")
    input_t = unreal.CustomInput(); input_t.set_editor_property("input_name", "Thickness")
    grid_node.set_editor_property("inputs", [input_p, input_s, input_t])
    
    grid_sz = mel.create_material_expression(material, unreal.MaterialExpressionScalarParameter, -1200, 700); grid_sz.set_editor_property("parameter_name", "GridSize"); grid_sz.set_editor_property("default_value", 100.0)
    grid_th = mel.create_material_expression(material, unreal.MaterialExpressionScalarParameter, -1200, 800); grid_th.set_editor_property("parameter_name", "GridThickness"); grid_th.set_editor_property("default_value", 1.5)
    
    mel.connect_material_expressions(grid_coords_sw, "", grid_node, "Position")
    mel.connect_material_expressions(grid_sz, "", grid_node, "GridSize")
    mel.connect_material_expressions(grid_th, "", grid_node, "Thickness")

    # 4b. DATA RAIN HLSL (FLUX LOOK)
    data_rain_code = """
float3 WorldPos = LWCToFloat(GetWorldPosition(Parameters));
float Time = ResolvedView.RealTime0;
float p = (WorldPos.z * 0.05) + (Time * Intensity * 5.0);
float lines = saturate(sin(p * 6.28) * 50.0);
float noise = frac(sin(dot(floor(WorldPos.xy * 0.1), float2(12.9898, 78.233))) * 43758.5453);
return lines * noise;
"""
    data_rain_node = mel.create_material_expression(material, unreal.MaterialExpressionCustom, -1000, 1200)
    data_rain_node.set_editor_property("code", data_rain_code); data_rain_node.set_editor_property("output_type", unreal.CustomMaterialOutputType.CMOT_FLOAT1)
    input_int = unreal.CustomInput(); input_int.set_editor_property("input_name", "Intensity")
    data_rain_node.set_editor_property("inputs", [input_int])
    mel.connect_material_expressions(inten, "", data_rain_node, "Intensity")

    # 5. CUSTOM HLSL EDGES
    edge_code = """
float3 N = normalize(Parameters.WorldNormal);
float Edge = length(fwidth(N));
float3 CameraPos = LWCToFloat(ResolvedView.WorldCameraOrigin);
float3 WorldPos = LWCToFloat(GetWorldPosition(Parameters));
return saturate(Edge * (Sensitivity / (length(WorldPos - CameraPos) * 0.001 + 1.0)));
"""
    edge_node = mel.create_material_expression(material, unreal.MaterialExpressionCustom, -1000, 1000)
    edge_node.set_editor_property("code", edge_code); edge_node.set_editor_property("output_type", unreal.CustomMaterialOutputType.CMOT_FLOAT1)
    input_sens = unreal.CustomInput(); input_sens.set_editor_property("input_name", "Sensitivity")
    edge_node.set_editor_property("inputs", [input_sens])
    edge_sns = mel.create_material_expression(material, unreal.MaterialExpressionScalarParameter, -1200, 1050); edge_sns.set_editor_property("parameter_name", "EdgeSensitivity"); edge_sns.set_editor_property("default_value", 20.0)
    mel.connect_material_expressions(edge_sns, "", edge_node, "Sensitivity")

    # 5b. FRACTURED EDGES HLSL
    fractured_edge_code = """
float3 N = normalize(Parameters.WorldNormal);
float Edge = length(fwidth(N));
float3 CameraPos = LWCToFloat(ResolvedView.WorldCameraOrigin);
float3 WorldPos = LWCToFloat(GetWorldPosition(Parameters));
float noise = frac(sin(dot(floor(WorldPos.xyz * 0.1), float2(12.9898, 78.233).xyx)) * 43758.5453);
float flicker = saturate(sin(ResolvedView.RealTime0 * 10.0 + noise * 6.28));
return saturate(Edge * (Sensitivity / (length(WorldPos - CameraPos) * 0.001 + 1.0))) * flicker;
"""
    fract_edge_node = mel.create_material_expression(material, unreal.MaterialExpressionCustom, -1000, 1400)
    fract_edge_node.set_editor_property("code", fractured_edge_code); fract_edge_node.set_editor_property("output_type", unreal.CustomMaterialOutputType.CMOT_FLOAT1)
    input_sens_f = unreal.CustomInput(); input_sens_f.set_editor_property("input_name", "Sensitivity")
    fract_edge_node.set_editor_property("inputs", [input_sens_f])
    mel.connect_material_expressions(edge_sns, "", fract_edge_node, "Sensitivity")

    # 6. FINAL COMBINE (Visibility Logic)
    # Combine Paths
    blueprint_path = mel.create_material_expression(material, unreal.MaterialExpressionMax, -600, 800)
    mel.connect_material_expressions(grid_node, "", blueprint_path, "A"); mel.connect_material_expressions(edge_node, "", blueprint_path, "B")
    
    flux_path = mel.create_material_expression(material, unreal.MaterialExpressionMax, -600, 1300)
    mel.connect_material_expressions(data_rain_node, "", flux_path, "A"); mel.connect_material_expressions(fract_edge_node, "", flux_path, "B")
    
    # UseFluxLook Switch
    total_mask = mel.create_material_expression(material, unreal.MaterialExpressionStaticSwitchParameter, -400, 1000)
    total_mask.set_editor_property("parameter_name", "UseFluxLook"); total_mask.set_editor_property("default_value", False)
    mel.connect_material_expressions(flux_path, "", total_mask, "True")
    mel.connect_material_expressions(blueprint_path, "", total_mask, "False")

    world_masked = mel.create_material_expression(material, unreal.MaterialExpressionMultiply, -400, 800)
    mel.connect_material_expressions(total_mask, "", world_masked, "A"); mel.connect_material_expressions(final_sonar, "", world_masked, "B")
    
    visible_sw = mel.create_material_expression(material, unreal.MaterialExpressionStaticSwitchParameter, -200, 600)
    visible_sw.set_editor_property("parameter_name", "IsPlayer")
    mel.connect_material_expressions(total_mask, "", visible_sw, "True")
    mel.connect_material_expressions(world_masked, "", visible_sw, "False")
    
    # OVERDRIVE HDR (500.0)
    cyan_rgb = mel.create_material_expression(material, unreal.MaterialExpressionConstant3Vector, 0, 800)
    cyan_rgb.set_editor_property("constant", unreal.LinearColor(0.0, 500.0, 500.0, 1.0))
    
    emissive_final = mel.create_material_expression(material, unreal.MaterialExpressionMultiply, 200, 600)
    mel.connect_material_expressions(visible_sw, "", emissive_final, "A"); mel.connect_material_expressions(cyan_rgb, "", emissive_final, "B")
    
    mel.connect_material_property(emissive_final, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    
    mel.recompile_material(material); eal.save_asset(asset_path)
    unreal.log("SUCCESS: Rebuilt Master Material with Digital Flux Mode and 500x Brightness.")

if __name__ == "__main__":
    run()
