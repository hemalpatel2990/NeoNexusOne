"""
13_build_blueprint_sonar_material.py — Ink & Sonar Material Rebuild.

Builds M_EchoMaster with two visual modes:
  - Blueprint Sonar (UseFluxLook=False): Grid + geometric edges
  - Ink & Sonar (UseFluxLook=True): Cel-bands + halftone dots + ink outlines + afterglow + proximity
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

import helpers
import importlib
importlib.reload(helpers)
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

    # EchoColor — per-instance HDR color
    echo_color = mel.create_material_expression(material, unreal.MaterialExpressionVectorParameter, 0, 800)
    echo_color.set_editor_property("parameter_name", "EchoColor")
    echo_color.set_editor_property("default_value", unreal.LinearColor(0.0, 500.0, 500.0, 1.0))

    # Tunable scalar parameters for reveal systems (shared)
    sonar_decay_param = mel.create_material_expression(material, unreal.MaterialExpressionScalarParameter, -1200, 1600)
    sonar_decay_param.set_editor_property("parameter_name", "SonarDecaySeconds")
    sonar_decay_param.set_editor_property("default_value", 5.0)

    proximity_radius_param = mel.create_material_expression(material, unreal.MaterialExpressionScalarParameter, -1200, 1700)
    proximity_radius_param.set_editor_property("parameter_name", "ProximityRadius")
    proximity_radius_param.set_editor_property("default_value", 400.0)

    # Tunable scalar parameters for Ink & Sonar mode
    num_bands_param = mel.create_material_expression(material, unreal.MaterialExpressionScalarParameter, -1200, 1800)
    num_bands_param.set_editor_property("parameter_name", "NumBands")
    num_bands_param.set_editor_property("default_value", 3.0)


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

    # 4b. Bold Outlines HLSL (UV-edge + normal discontinuity + Fresnel silhouette)
    # Cubes have UVs 0→1 per face, so proximity to UV edge = face border
    edge_code = """
float3 N = normalize(Parameters.WorldNormal);
float3 CameraPos = LWCToFloat(ResolvedView.WorldCameraOrigin);
float3 WorldPos = LWCToFloat(GetWorldPosition(Parameters));
float CamDist = length(WorldPos - CameraPos);

// 1. UV-based edge: distance from UV border (works on standard cube UVs)
float2 edgeDist = min(UV, 1.0 - UV);
float uvEdge = 1.0 - smoothstep(0.0, BorderWidth, min(edgeDist.x, edgeDist.y));

// 2. Normal discontinuity: catches hard edges on any geometry
float GeomEdge = length(fwidth(N));
float GeomMask = saturate(GeomEdge * (Sensitivity / (CamDist * 0.001 + 1.0)));

// 3. Fresnel silhouette: thin rim where surface grazes the camera
float3 ViewDir = normalize(CameraPos - WorldPos);
float NdotV = abs(dot(N, ViewDir));
float SilEdge = 1.0 - smoothstep(0.02, 0.12, NdotV);

return saturate(max(uvEdge, max(GeomMask, SilEdge)));
"""
    edge_node = mel.create_material_expression(material, unreal.MaterialExpressionCustom, -1000, 1000)
    edge_node.set_editor_property("code", edge_code)
    edge_node.set_editor_property("output_type", unreal.CustomMaterialOutputType.CMOT_FLOAT1)
    input_sens = unreal.CustomInput()
    input_sens.set_editor_property("input_name", "Sensitivity")
    input_bw = unreal.CustomInput()
    input_bw.set_editor_property("input_name", "BorderWidth")
    input_uv = unreal.CustomInput()
    input_uv.set_editor_property("input_name", "UV")
    edge_node.set_editor_property("inputs", [input_sens, input_bw, input_uv])

    edge_sns = mel.create_material_expression(material, unreal.MaterialExpressionScalarParameter, -1200, 1050)
    edge_sns.set_editor_property("parameter_name", "EdgeSensitivity")
    edge_sns.set_editor_property("default_value", 200.0)
    mel.connect_material_expressions(edge_sns, "", edge_node, "Sensitivity")

    border_width_param = mel.create_material_expression(material, unreal.MaterialExpressionScalarParameter, -1200, 1150)
    border_width_param.set_editor_property("parameter_name", "BorderWidth")
    border_width_param.set_editor_property("default_value", 0.06)
    mel.connect_material_expressions(border_width_param, "", edge_node, "BorderWidth")

    texcoord_node = mel.create_material_expression(material, unreal.MaterialExpressionTextureCoordinate, -1200, 1250)
    mel.connect_material_expressions(texcoord_node, "", edge_node, "UV")

    # Blueprint path combine: max(grid, edges)
    blueprint_path = mel.create_material_expression(material, unreal.MaterialExpressionMax, -600, 800)
    mel.connect_material_expressions(grid_node, "", blueprint_path, "A")
    mel.connect_material_expressions(edge_node, "", blueprint_path, "B")

    # =========================================================================
    # 5. INK & SONAR PATH: Cel-Bands + Halftone + Ink + Afterglow + Proximity
    # =========================================================================

    # 5-pre. Player position from MPC (needed by proximity and cel-bands)
    player_pos = mel.create_material_expression(material, unreal.MaterialExpressionCollectionParameter, -1500, 2000)
    player_pos.set_editor_property("collection", mpc)
    player_pos.set_editor_property("parameter_name", unreal.Name(MPCParams.PLAYER_WORLD_POSITION))

    player_pos_rgb = mel.create_material_expression(material, unreal.MaterialExpressionComponentMask, -1300, 2000)
    player_pos_rgb.set_editor_property("r", True)
    player_pos_rgb.set_editor_property("g", True)
    player_pos_rgb.set_editor_property("b", True)
    mel.connect_material_expressions(player_pos, "", player_pos_rgb, "")

    # 5a-pre. MPC and params needed by both cel-bands and afterglow
    ripple_start = mel.create_material_expression(material, unreal.MaterialExpressionCollectionParameter, -1500, 1800)
    ripple_start.set_editor_property("collection", mpc)
    ripple_start.set_editor_property("parameter_name", unreal.Name(MPCParams.RIPPLE_START_TIME))

    max_radius_param = mel.create_material_expression(material, unreal.MaterialExpressionScalarParameter, -1200, 2300)
    max_radius_param.set_editor_property("parameter_name", "MaxRippleRadius")
    max_radius_param.set_editor_property("default_value", 2000.0)

    ripple_duration_param = mel.create_material_expression(material, unreal.MaterialExpressionScalarParameter, -1200, 2400)
    ripple_duration_param.set_editor_property("parameter_name", "RippleDuration")
    ripple_duration_param.set_editor_property("default_value", 1.5)

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

    # 5b. Sonar Afterglow Decay HLSL (temporal noise dissolve behind ring)

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

// Smooth fade: starts bright, dims gradually with a slight ease-out curve
float Fade = 1.0 - DecayProgress;
return Fade * Fade;
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

    # 5d. Sonar Ring Edge — bright expanding wavefront from MPC CurrentRippleRadius
    ring_edge_code = """
float3 WorldPos = LWCToFloat(GetWorldPosition(Parameters));
float DistToImpact = length(WorldPos - ImpactLoc);
// Ring is a thin band at the current radius edge
float RingWidth = 80.0;
float Inner = CurRadius - RingWidth;
float RingMask = smoothstep(Inner, Inner + RingWidth * 0.3, DistToImpact)
              * (1.0 - smoothstep(CurRadius - RingWidth * 0.3, CurRadius, DistToImpact));
return RingMask * Intensity;
"""
    ring_edge_node = mel.create_material_expression(material, unreal.MaterialExpressionCustom, -1000, 2350)
    ring_edge_node.set_editor_property("code", ring_edge_code)
    ring_edge_node.set_editor_property("output_type", unreal.CustomMaterialOutputType.CMOT_FLOAT1)
    input_re_il = unreal.CustomInput()
    input_re_il.set_editor_property("input_name", "ImpactLoc")
    input_re_cr = unreal.CustomInput()
    input_re_cr.set_editor_property("input_name", "CurRadius")
    input_re_in = unreal.CustomInput()
    input_re_in.set_editor_property("input_name", "Intensity")
    ring_edge_node.set_editor_property("inputs", [input_re_il, input_re_cr, input_re_in])
    mel.connect_material_expressions(mask_rgb, "", ring_edge_node, "ImpactLoc")
    mel.connect_material_expressions(rad, "", ring_edge_node, "CurRadius")
    mel.connect_material_expressions(inten, "", ring_edge_node, "Intensity")

    # 5d-ii. Halftone Dots — small dots, denser further from impact
    # Near sonar = clean/sparse, far = dense shading dots
    halftone_code = """
float3 N = abs(normalize(Parameters.WorldNormal));
N = N / (N.x + N.y + N.z + 0.001);
float2 uvXY = Position.xy * DotScale;
float2 uvXZ = Position.xz * DotScale;
float2 uvYZ = Position.yz * DotScale;
float dotXY = length(frac(uvXY) - 0.5);
float dotXZ = length(frac(uvXZ) - 0.5);
float dotYZ = length(frac(uvYZ) - 0.5);
float dotBlend = dotXY * N.z + dotXZ * N.y + dotYZ * N.x;
// Invert CelBandValue: bright band (near) = high threshold = few dots, dark band (far) = low threshold = many dots
float threshold = lerp(0.1, 0.4, CelBandValue);
float halftone = smoothstep(threshold - 0.02, threshold + 0.02, dotBlend);
return lerp(1.0, 1.0 - DotStrength, 1.0 - halftone);
"""
    halftone_node = mel.create_material_expression(material, unreal.MaterialExpressionCustom, -1000, 2450)
    halftone_node.set_editor_property("code", halftone_code)
    halftone_node.set_editor_property("output_type", unreal.CustomMaterialOutputType.CMOT_FLOAT1)
    input_ht_pos = unreal.CustomInput()
    input_ht_pos.set_editor_property("input_name", "Position")
    input_ht_ds = unreal.CustomInput()
    input_ht_ds.set_editor_property("input_name", "DotScale")
    input_ht_cb = unreal.CustomInput()
    input_ht_cb.set_editor_property("input_name", "CelBandValue")
    input_ht_str = unreal.CustomInput()
    input_ht_str.set_editor_property("input_name", "DotStrength")
    halftone_node.set_editor_property("inputs", [input_ht_pos, input_ht_ds, input_ht_cb, input_ht_str])

    dot_scale_param = mel.create_material_expression(material, unreal.MaterialExpressionScalarParameter, -1200, 2450)
    dot_scale_param.set_editor_property("parameter_name", "DotScale")
    dot_scale_param.set_editor_property("default_value", 0.05)

    dot_strength_param = mel.create_material_expression(material, unreal.MaterialExpressionScalarParameter, -1200, 2550)
    dot_strength_param.set_editor_property("parameter_name", "DotStrength")
    dot_strength_param.set_editor_property("default_value", 0.25)

    mel.connect_material_expressions(grid_coords_sw, "", halftone_node, "Position")
    mel.connect_material_expressions(dot_scale_param, "", halftone_node, "DotScale")
    mel.connect_material_expressions(dot_strength_param, "", halftone_node, "DotStrength")
    # CelBandValue connected below after cel_bands_combined

    # =========================================================================
    # 5e. INK & SONAR COMPOSITING
    # =========================================================================

    # reveal_mask = max(ring_edge, afterglow, proximity)
    ring_or_afterglow = mel.create_material_expression(material, unreal.MaterialExpressionMax, -400, 2100)
    mel.connect_material_expressions(ring_edge_node, "", ring_or_afterglow, "A")
    mel.connect_material_expressions(afterglow_node, "", ring_or_afterglow, "B")

    contour_reveal = mel.create_material_expression(material, unreal.MaterialExpressionMax, -400, 1900)
    mel.connect_material_expressions(ring_or_afterglow, "", contour_reveal, "A")
    mel.connect_material_expressions(proximity_node, "", contour_reveal, "B")

    # Combined cel-bands: max(sonar_bands, proximity_bands)
    cel_bands_combined = mel.create_material_expression(material, unreal.MaterialExpressionMax, -600, 1600)
    mel.connect_material_expressions(cel_bands_node, "", cel_bands_combined, "A")
    mel.connect_material_expressions(prox_bands_node, "", cel_bands_combined, "B")

    # Connect CelBandValue to halftone (deferred from above)
    mel.connect_material_expressions(cel_bands_combined, "", halftone_node, "CelBandValue")

    # Ink mask inversion: (1.0 - edge_node) — dark outlines where edges are detected
    one_const = mel.create_material_expression(material, unreal.MaterialExpressionConstant, -600, 1000)
    one_const.set_editor_property("r", 1.0)
    ink_invert = mel.create_material_expression(material, unreal.MaterialExpressionSubtract, -400, 1000)
    mel.connect_material_expressions(one_const, "", ink_invert, "A")
    mel.connect_material_expressions(edge_node, "", ink_invert, "B")

    # --- World Ink & Sonar path: cel_bands * halftone * (1 - ink) * reveal_mask ---

    # cel_bands * halftone
    world_cel_ht = mel.create_material_expression(material, unreal.MaterialExpressionMultiply, -300, 1600)
    mel.connect_material_expressions(cel_bands_combined, "", world_cel_ht, "A")
    mel.connect_material_expressions(halftone_node, "", world_cel_ht, "B")

    # * (1 - ink)
    world_cel_ink = mel.create_material_expression(material, unreal.MaterialExpressionMultiply, -200, 1600)
    mel.connect_material_expressions(world_cel_ht, "", world_cel_ink, "A")
    mel.connect_material_expressions(ink_invert, "", world_cel_ink, "B")

    # * reveal_mask
    ink_sonar_masked = mel.create_material_expression(material, unreal.MaterialExpressionMultiply, 0, 1600)
    mel.connect_material_expressions(world_cel_ink, "", ink_sonar_masked, "A")
    mel.connect_material_expressions(contour_reveal, "", ink_sonar_masked, "B")

    # --- Player Ink & Sonar path: 1.0 * (1 - ink) — flat bright with outlines ---
    # Player uses UV edges for outlines, which work well on cube faces
    player_ink_path = mel.create_material_expression(material, unreal.MaterialExpressionMultiply, -200, 2500)
    mel.connect_material_expressions(one_const, "", player_ink_path, "A")
    mel.connect_material_expressions(ink_invert, "", player_ink_path, "B")

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
    mel.connect_material_expressions(player_ink_path, "", player_visual_sw, "True")
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


if __name__ == "__main__":
    run()
