"""
13_build_blueprint_sonar_material.py — Living Contour Map Material Rebuild.

Builds M_EchoMaster with two visual modes:
  - Blueprint Sonar (UseFluxLook=False): Grid + geometric edges
  - Living Contour Map (UseFluxLook=True): Contour lines + edges + afterglow decay + proximity glow
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

    material = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
        "M_EchoMaster", "/Game/EchoLocation/Materials",
        unreal.Material, factory=unreal.MaterialFactoryNew())
    material.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
    mpc = unreal.load_asset(mpc_path)

    # =========================================================================
    # 1. PARAMETERS
    # =========================================================================

    # EchoColor — per-instance HDR color (replaces hardcoded cyan)
    echo_color = mel.create_material_expression(material, unreal.MaterialExpressionVectorParameter, 0, 800)
    echo_color.set_editor_property("parameter_name", "EchoColor")
    echo_color.set_editor_property("default_value", unreal.LinearColor(0.0, 500.0, 500.0, 1.0))

    # Tunable scalar parameters for contour map mode
    sonar_decay_param = mel.create_material_expression(material, unreal.MaterialExpressionScalarParameter, -1200, 1600)
    sonar_decay_param.set_editor_property("parameter_name", "SonarDecaySeconds")
    sonar_decay_param.set_editor_property("default_value", 5.0)

    proximity_radius_param = mel.create_material_expression(material, unreal.MaterialExpressionScalarParameter, -1200, 1700)
    proximity_radius_param.set_editor_property("parameter_name", "ProximityRadius")
    proximity_radius_param.set_editor_property("default_value", 400.0)

    contour_scale_param = mel.create_material_expression(material, unreal.MaterialExpressionScalarParameter, -1200, 1800)
    contour_scale_param.set_editor_property("parameter_name", "ContourScale")
    contour_scale_param.set_editor_property("default_value", 0.05)

    contour_speed_param = mel.create_material_expression(material, unreal.MaterialExpressionScalarParameter, -1200, 1900)
    contour_speed_param.set_editor_property("parameter_name", "ContourFlowSpeed")
    contour_speed_param.set_editor_property("default_value", 0.5)

    # =========================================================================
    # 2. COORDINATES (LocalPosition for Actors, WorldPosition for World)
    # =========================================================================

    wp = mel.create_material_expression(material, unreal.MaterialExpressionWorldPosition, -1600, 400)
    lp = mel.create_material_expression(material, unreal.MaterialExpressionLocalPosition, -1600, 500)

    grid_coords_sw = mel.create_material_expression(material, unreal.MaterialExpressionStaticSwitchParameter, -1200, 400)
    grid_coords_sw.set_editor_property("parameter_name", "IsActor")
    mel.connect_material_expressions(lp, "", grid_coords_sw, "True")
    mel.connect_material_expressions(wp, "", grid_coords_sw, "False")

    # =========================================================================
    # 3. SONAR REVEAL (existing ring mask — unchanged)
    # =========================================================================

    loc = mel.create_material_expression(material, unreal.MaterialExpressionCollectionParameter, -1500, -200)
    loc.set_editor_property("collection", mpc)
    loc.set_editor_property("parameter_name", unreal.Name(MPCParams.LAST_IMPACT_LOCATION))

    mask_rgb = mel.create_material_expression(material, unreal.MaterialExpressionComponentMask, -1300, -200)
    mask_rgb.set_editor_property("r", True)
    mask_rgb.set_editor_property("g", True)
    mask_rgb.set_editor_property("b", True)
    mel.connect_material_expressions(loc, "", mask_rgb, "")

    dist = mel.create_material_expression(material, unreal.MaterialExpressionDistance, -1100, -100)
    mel.connect_material_expressions(wp, "", dist, "A")
    mel.connect_material_expressions(mask_rgb, "", dist, "B")

    rad = mel.create_material_expression(material, unreal.MaterialExpressionCollectionParameter, -1300, 0)
    rad.set_editor_property("collection", mpc)
    rad.set_editor_property("parameter_name", unreal.Name(MPCParams.CURRENT_RIPPLE_RADIUS))

    inten = mel.create_material_expression(material, unreal.MaterialExpressionCollectionParameter, -600, 0)
    inten.set_editor_property("collection", mpc)
    inten.set_editor_property("parameter_name", unreal.Name(MPCParams.RIPPLE_INTENSITY))

    # Simple sonar mask: saturate(radius - distance) * intensity
    reveal_sub = mel.create_material_expression(material, unreal.MaterialExpressionSubtract, -900, 0)
    mel.connect_material_expressions(rad, "", reveal_sub, "A")
    mel.connect_material_expressions(dist, "", reveal_sub, "B")

    reveal_mask = mel.create_material_expression(material, unreal.MaterialExpressionSaturate, -750, 0)
    mel.connect_material_expressions(reveal_sub, "", reveal_mask, "")

    final_sonar = mel.create_material_expression(material, unreal.MaterialExpressionMultiply, -400, 0)
    mel.connect_material_expressions(reveal_mask, "", final_sonar, "A")
    mel.connect_material_expressions(inten, "", final_sonar, "B")

    # =========================================================================
    # 4. BLUEPRINT PATH: Grid + Edges (existing, proven)
    # =========================================================================

    # 4a. Grid HLSL
    grid_code = """
float3 p = Position / GridSize;
float3 grid = abs(frac(p - 0.5) - 0.5) / fwidth(p);
float val = min(grid.x, min(grid.y, grid.z));
return 1.0 - saturate(val / Thickness);
"""
    grid_node = mel.create_material_expression(material, unreal.MaterialExpressionCustom, -1000, 600)
    grid_node.set_editor_property("code", grid_code)
    grid_node.set_editor_property("output_type", unreal.CustomMaterialOutputType.CMOT_FLOAT1)

    input_p = unreal.CustomInput()
    input_p.set_editor_property("input_name", "Position")
    input_s = unreal.CustomInput()
    input_s.set_editor_property("input_name", "GridSize")
    input_t = unreal.CustomInput()
    input_t.set_editor_property("input_name", "Thickness")
    grid_node.set_editor_property("inputs", [input_p, input_s, input_t])

    grid_sz = mel.create_material_expression(material, unreal.MaterialExpressionScalarParameter, -1200, 700)
    grid_sz.set_editor_property("parameter_name", "GridSize")
    grid_sz.set_editor_property("default_value", 100.0)

    grid_th = mel.create_material_expression(material, unreal.MaterialExpressionScalarParameter, -1200, 800)
    grid_th.set_editor_property("parameter_name", "GridThickness")
    grid_th.set_editor_property("default_value", 1.5)

    mel.connect_material_expressions(grid_coords_sw, "", grid_node, "Position")
    mel.connect_material_expressions(grid_sz, "", grid_node, "GridSize")
    mel.connect_material_expressions(grid_th, "", grid_node, "Thickness")

    # 4b. Geometric Edges HLSL (fwidth(Normal) with distance normalization)
    edge_code = """
float3 N = normalize(Parameters.WorldNormal);
float Edge = length(fwidth(N));
float3 CameraPos = LWCToFloat(ResolvedView.WorldCameraOrigin);
float3 WorldPos = LWCToFloat(GetWorldPosition(Parameters));
return saturate(Edge * (Sensitivity / (length(WorldPos - CameraPos) * 0.001 + 1.0)));
"""
    edge_node = mel.create_material_expression(material, unreal.MaterialExpressionCustom, -1000, 1000)
    edge_node.set_editor_property("code", edge_code)
    edge_node.set_editor_property("output_type", unreal.CustomMaterialOutputType.CMOT_FLOAT1)
    input_sens = unreal.CustomInput()
    input_sens.set_editor_property("input_name", "Sensitivity")
    edge_node.set_editor_property("inputs", [input_sens])

    edge_sns = mel.create_material_expression(material, unreal.MaterialExpressionScalarParameter, -1200, 1050)
    edge_sns.set_editor_property("parameter_name", "EdgeSensitivity")
    edge_sns.set_editor_property("default_value", 20.0)
    mel.connect_material_expressions(edge_sns, "", edge_node, "Sensitivity")

    # Blueprint path combine: max(grid, edges)
    blueprint_path = mel.create_material_expression(material, unreal.MaterialExpressionMax, -600, 800)
    mel.connect_material_expressions(grid_node, "", blueprint_path, "A")
    mel.connect_material_expressions(edge_node, "", blueprint_path, "B")

    # =========================================================================
    # 5. CONTOUR MAP PATH: Contour Lines + Edges + Afterglow + Proximity
    # =========================================================================

    # 5a. Animated Contour Lines HLSL
    contour_code = """
float3 WorldPos = LWCToFloat(GetWorldPosition(Parameters));
float Time = ResolvedView.RealTime;
float phase = frac((WorldPos.z * ContourScale) + (Time * FlowSpeed));
float band = smoothstep(0.42, 0.48, phase) - smoothstep(0.52, 0.58, phase);
return band;
"""
    contour_node = mel.create_material_expression(material, unreal.MaterialExpressionCustom, -1000, 1500)
    contour_node.set_editor_property("code", contour_code)
    contour_node.set_editor_property("output_type", unreal.CustomMaterialOutputType.CMOT_FLOAT1)
    input_cs = unreal.CustomInput()
    input_cs.set_editor_property("input_name", "ContourScale")
    input_cf = unreal.CustomInput()
    input_cf.set_editor_property("input_name", "FlowSpeed")
    contour_node.set_editor_property("inputs", [input_cs, input_cf])
    mel.connect_material_expressions(contour_scale_param, "", contour_node, "ContourScale")
    mel.connect_material_expressions(contour_speed_param, "", contour_node, "FlowSpeed")

    # Contour map visual: max(edges, contour_lines)
    contour_path = mel.create_material_expression(material, unreal.MaterialExpressionMax, -600, 1500)
    mel.connect_material_expressions(edge_node, "", contour_path, "A")
    mel.connect_material_expressions(contour_node, "", contour_path, "B")

    # 5b. Sonar Afterglow Decay HLSL (temporal noise dissolve behind ring)
    ripple_start = mel.create_material_expression(material, unreal.MaterialExpressionCollectionParameter, -1500, 1800)
    ripple_start.set_editor_property("collection", mpc)
    ripple_start.set_editor_property("parameter_name", unreal.Name(MPCParams.RIPPLE_START_TIME))

    max_radius_param = mel.create_material_expression(material, unreal.MaterialExpressionScalarParameter, -1200, 2000)
    max_radius_param.set_editor_property("parameter_name", "MaxRippleRadius")
    max_radius_param.set_editor_property("default_value", 2000.0)

    ripple_duration_param = mel.create_material_expression(material, unreal.MaterialExpressionScalarParameter, -1200, 2100)
    ripple_duration_param.set_editor_property("parameter_name", "RippleDuration")
    ripple_duration_param.set_editor_property("default_value", 1.5)

    afterglow_code = """
float3 WorldPos = LWCToFloat(GetWorldPosition(Parameters));
float Now = ResolvedView.RealTime;
float DistToImpact = length(WorldPos - ImpactLoc);

// Was there ever a ripple?
if (StartTime <= 0.0) return 0.0;

// Ring expands at constant speed: MaxRadius / Duration
float RingSpeed = MaxRadius / max(Duration, 0.001);
float TimeRingReached = StartTime + (DistToImpact / max(RingSpeed, 0.001));

// Has the ring reached this pixel yet?
if (Now < TimeRingReached) return 0.0;

// How long since the ring passed this pixel?
float TimeSinceRing = Now - TimeRingReached;
float DecayProgress = saturate(TimeSinceRing / max(DecaySeconds, 0.001));

// Noise dissolve: pixel goes dark when noise < decay progress
float Noise = frac(sin(dot(floor(WorldPos * 0.05), float3(12.9898, 78.233, 45.164))) * 43758.5453);
float AfterglowMask = step(DecayProgress, Noise);
return AfterglowMask;
"""
    afterglow_node = mel.create_material_expression(material, unreal.MaterialExpressionCustom, -1000, 1800)
    afterglow_node.set_editor_property("code", afterglow_code)
    afterglow_node.set_editor_property("output_type", unreal.CustomMaterialOutputType.CMOT_FLOAT1)
    input_il = unreal.CustomInput()
    input_il.set_editor_property("input_name", "ImpactLoc")
    input_mr = unreal.CustomInput()
    input_mr.set_editor_property("input_name", "MaxRadius")
    input_dur = unreal.CustomInput()
    input_dur.set_editor_property("input_name", "Duration")
    input_ds = unreal.CustomInput()
    input_ds.set_editor_property("input_name", "DecaySeconds")
    input_st = unreal.CustomInput()
    input_st.set_editor_property("input_name", "StartTime")
    afterglow_node.set_editor_property("inputs", [input_il, input_mr, input_dur, input_ds, input_st])
    mel.connect_material_expressions(mask_rgb, "", afterglow_node, "ImpactLoc")
    mel.connect_material_expressions(max_radius_param, "", afterglow_node, "MaxRadius")
    mel.connect_material_expressions(ripple_duration_param, "", afterglow_node, "Duration")
    mel.connect_material_expressions(sonar_decay_param, "", afterglow_node, "DecaySeconds")
    mel.connect_material_expressions(ripple_start, "", afterglow_node, "StartTime")

    # 5c. Proximity Awareness HLSL
    player_pos = mel.create_material_expression(material, unreal.MaterialExpressionCollectionParameter, -1500, 2000)
    player_pos.set_editor_property("collection", mpc)
    player_pos.set_editor_property("parameter_name", unreal.Name(MPCParams.PLAYER_WORLD_POSITION))

    player_pos_rgb = mel.create_material_expression(material, unreal.MaterialExpressionComponentMask, -1300, 2000)
    player_pos_rgb.set_editor_property("r", True)
    player_pos_rgb.set_editor_property("g", True)
    player_pos_rgb.set_editor_property("b", True)
    mel.connect_material_expressions(player_pos, "", player_pos_rgb, "")

    proximity_code = """
float3 WorldPos = LWCToFloat(GetWorldPosition(Parameters));
float Dist = length(WorldPos - PlayerPos);
float InRadius = step(Dist, Radius);
float Glow = saturate(1.0 - (Dist / max(Radius, 0.001)));
return lerp(0.2, 0.6, Glow) * InRadius;
"""
    proximity_node = mel.create_material_expression(material, unreal.MaterialExpressionCustom, -1000, 2100)
    proximity_node.set_editor_property("code", proximity_code)
    proximity_node.set_editor_property("output_type", unreal.CustomMaterialOutputType.CMOT_FLOAT1)
    input_pp = unreal.CustomInput()
    input_pp.set_editor_property("input_name", "PlayerPos")
    input_pr = unreal.CustomInput()
    input_pr.set_editor_property("input_name", "Radius")
    proximity_node.set_editor_property("inputs", [input_pp, input_pr])
    mel.connect_material_expressions(player_pos_rgb, "", proximity_node, "PlayerPos")
    mel.connect_material_expressions(proximity_radius_param, "", proximity_node, "Radius")

    # 5d. Combine: reveal_mask = max(afterglow, proximity)
    contour_reveal = mel.create_material_expression(material, unreal.MaterialExpressionMax, -400, 1900)
    mel.connect_material_expressions(afterglow_node, "", contour_reveal, "A")
    mel.connect_material_expressions(proximity_node, "", contour_reveal, "B")

    # Contour map masked: contour_visual * reveal_mask
    contour_masked = mel.create_material_expression(material, unreal.MaterialExpressionMultiply, -200, 1600)
    mel.connect_material_expressions(contour_path, "", contour_masked, "A")
    mel.connect_material_expressions(contour_reveal, "", contour_masked, "B")

    # =========================================================================
    # 6. FINAL COMBINE (UseFluxLook switch + IsPlayer bypass + EchoColor)
    # =========================================================================

    # --- World geometry path (IsPlayer=False): visual * reveal mask ---

    # Blueprint mode world: grid+edges * sonar ring mask
    world_masked_bp = mel.create_material_expression(material, unreal.MaterialExpressionMultiply, -400, 800)
    mel.connect_material_expressions(blueprint_path, "", world_masked_bp, "A")
    mel.connect_material_expressions(final_sonar, "", world_masked_bp, "B")

    # UseFluxLook switch for world geometry (non-player)
    world_mode_sw = mel.create_material_expression(material, unreal.MaterialExpressionStaticSwitchParameter, -200, 800)
    world_mode_sw.set_editor_property("parameter_name", "UseFluxLook")
    world_mode_sw.set_editor_property("default_value", False)
    mel.connect_material_expressions(contour_masked, "", world_mode_sw, "True")
    mel.connect_material_expressions(world_masked_bp, "", world_mode_sw, "False")

    # --- Player path (IsPlayer=True): unmasked visual pattern, always visible ---

    # UseFluxLook switch for player visual (no sonar/proximity masking)
    player_visual_sw = mel.create_material_expression(material, unreal.MaterialExpressionStaticSwitchParameter, -200, 500)
    player_visual_sw.set_editor_property("parameter_name", "UseFluxLook")
    mel.connect_material_expressions(contour_path, "", player_visual_sw, "True")
    mel.connect_material_expressions(blueprint_path, "", player_visual_sw, "False")

    # IsPlayer bypass: True = unmasked visual, False = world masked visual
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
    unreal.log("SUCCESS: Rebuilt M_EchoMaster with Living Contour Map mode.")


if __name__ == "__main__":
    run()
