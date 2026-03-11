import unreal
import os
import sys

def run():
    asset_path = "/Game/EchoLocation/Materials/M_EchoMaster_Final"
    mpc_path = "/Game/EchoLocation/Materials/MPC_GlobalSound"
    
    eal = unreal.EditorAssetLibrary
    mel = unreal.MaterialEditingLibrary
    
    if eal.does_asset_exist(asset_path):
        eal.delete_asset(asset_path)
    
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    material = asset_tools.create_asset("M_EchoMaster_Final", "/Game/EchoLocation/Materials", unreal.Material, unreal.MaterialFactoryNew())
    material.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
    
    mpc = unreal.load_asset(mpc_path)

    # =====================================================================
    # 1. RIPPLE MASKS (The Sharp Ring & Decay)
    # =====================================================================
    unreal.log("Building Digital Scan Masks...")
    loc_node = mel.create_material_expression(material, unreal.MaterialExpressionCollectionParameter, -1500, -200)
    loc_node.set_editor_property("collection", mpc); loc_node.set_editor_property("parameter_name", unreal.Name("LastImpactLocation"))
    
    mask_rgb = mel.create_material_expression(material, unreal.MaterialExpressionComponentMask, -1300, -200)
    mask_rgb.set_editor_property("r", True); mask_rgb.set_editor_property("g", True); mask_rgb.set_editor_property("b", True); mask_rgb.set_editor_property("a", False)
    mel.connect_material_expressions(loc_node, "", mask_rgb, "")
    
    wp_node = mel.create_material_expression(material, unreal.MaterialExpressionWorldPosition, -1500, -300)
    dist_node = mel.create_material_expression(material, unreal.MaterialExpressionDistance, -1100, -250)
    mel.connect_material_expressions(wp_node, "", dist_node, "A"); mel.connect_material_expressions(mask_rgb, "", dist_node, "B")
    
    rad_node = mel.create_material_expression(material, unreal.MaterialExpressionCollectionParameter, -1300, -100)
    rad_node.set_editor_property("collection", mpc); rad_node.set_editor_property("parameter_name", unreal.Name("CurrentRippleRadius"))
    
    # Normalized Distance (0 at center, 1 at edge of wave)
    norm_dist = mel.create_material_expression(material, unreal.MaterialExpressionDivide, -950, -200)
    mel.connect_material_expressions(dist_node, "", norm_dist, "A"); mel.connect_material_expressions(rad_node, "", norm_dist, "B")
    
    norm_sat = mel.create_material_expression(material, unreal.MaterialExpressionSaturate, -850, -200)
    mel.connect_material_expressions(norm_dist, "", norm_sat, "")
    
    # Inside Mask: Prevents anything from glowing before the wave hits it
    inside_step = mel.create_material_expression(material, unreal.MaterialExpressionStep, -850, -300)
    inside_thresh = mel.create_material_expression(material, unreal.MaterialExpressionConstant, -950, -300); inside_thresh.set_editor_property("r", 1.0)
    mel.connect_material_expressions(norm_dist, "", inside_step, "X"); mel.connect_material_expressions(inside_thresh, "", inside_step, "Y")
    inside_inv = mel.create_material_expression(material, unreal.MaterialExpressionOneMinus, -750, -300)
    mel.connect_material_expressions(inside_step, "", inside_inv, "")
    
    # Decay Mask: Fades out smoothly from the ring to the center
    decay_pow = mel.create_material_expression(material, unreal.MaterialExpressionPower, -650, -200)
    decay_param = mel.create_material_expression(material, unreal.MaterialExpressionScalarParameter, -800, -100)
    decay_param.set_editor_property("parameter_name", unreal.Name("ScanDecay")); decay_param.set_editor_property("default_value", 4.0)
    mel.connect_material_expressions(norm_sat, "", decay_pow, "Base"); mel.connect_material_expressions(decay_param, "", decay_pow, "Exp")
    
    decay_mask = mel.create_material_expression(material, unreal.MaterialExpressionMultiply, -500, -250)
    mel.connect_material_expressions(decay_pow, "", decay_mask, "A"); mel.connect_material_expressions(inside_inv, "", decay_mask, "B")
    
    # Sharp Laser Ring: A razor thin 2% line at the leading edge
    ring_ss = mel.create_material_expression(material, unreal.MaterialExpressionSmoothStep, -650, 0)
    ring_min = mel.create_material_expression(material, unreal.MaterialExpressionConstant, -800, 0); ring_min.set_editor_property("r", 0.98)
    ring_max = mel.create_material_expression(material, unreal.MaterialExpressionConstant, -800, 50); ring_max.set_editor_property("r", 1.0)
    mel.connect_material_expressions(ring_min, "", ring_ss, "Min"); mel.connect_material_expressions(ring_max, "", ring_ss, "Max"); mel.connect_material_expressions(norm_sat, "", ring_ss, "Value")
    
    sharp_ring = mel.create_material_expression(material, unreal.MaterialExpressionMultiply, -500, -50)
    mel.connect_material_expressions(ring_ss, "", sharp_ring, "A"); mel.connect_material_expressions(inside_inv, "", sharp_ring, "B")
    
    # Apply Global Intensity
    int_node = mel.create_material_expression(material, unreal.MaterialExpressionCollectionParameter, -500, -150)
    int_node.set_editor_property("collection", mpc); int_node.set_editor_property("parameter_name", unreal.Name("RippleIntensity"))
    
    final_decay = mel.create_material_expression(material, unreal.MaterialExpressionMultiply, -350, -200)
    mel.connect_material_expressions(decay_mask, "", final_decay, "A"); mel.connect_material_expressions(int_node, "", final_decay, "B")
    
    final_ring = mel.create_material_expression(material, unreal.MaterialExpressionMultiply, -350, -50)
    mel.connect_material_expressions(sharp_ring, "", final_ring, "A"); mel.connect_material_expressions(int_node, "", final_ring, "B")

    # =====================================================================
    # 2. UV WIREFRAME
    # =====================================================================
    unreal.log("Building UV Wireframe...")
    uv_node = mel.create_material_expression(material, unreal.MaterialExpressionTextureCoordinate, -1200, 300)
    uv_sub = mel.create_material_expression(material, unreal.MaterialExpressionSubtract, -1000, 300)
    uv_const = mel.create_material_expression(material, unreal.MaterialExpressionConstant, -1100, 350); uv_const.set_editor_property("r", 0.5)
    mel.connect_material_expressions(uv_node, "", uv_sub, "A"); mel.connect_material_expressions(uv_const, "", uv_sub, "B")
    
    uv_abs = mel.create_material_expression(material, unreal.MaterialExpressionAbs, -850, 300)
    mel.connect_material_expressions(uv_sub, "", uv_abs, "")
    
    mask_r = mel.create_material_expression(material, unreal.MaterialExpressionComponentMask, -700, 250); mask_r.set_editor_property("r", True); mask_r.set_editor_property("g", False)
    mask_g = mel.create_material_expression(material, unreal.MaterialExpressionComponentMask, -700, 350); mask_g.set_editor_property("r", False); mask_g.set_editor_property("g", True)
    mel.connect_material_expressions(uv_abs, "", mask_r, ""); mel.connect_material_expressions(uv_abs, "", mask_g, "")
    
    uv_max = mel.create_material_expression(material, unreal.MaterialExpressionMax, -500, 300)
    mel.connect_material_expressions(mask_r, "", uv_max, "A"); mel.connect_material_expressions(mask_g, "", uv_max, "B")
    
    uv_step = mel.create_material_expression(material, unreal.MaterialExpressionStep, -350, 300)
    uv_thresh = mel.create_material_expression(material, unreal.MaterialExpressionScalarParameter, -500, 400); uv_thresh.set_editor_property("parameter_name", unreal.Name("EdgeThickness")); uv_thresh.set_editor_property("default_value", 0.495)
    mel.connect_material_expressions(uv_max, "", uv_step, "X"); mel.connect_material_expressions(uv_thresh, "", uv_step, "Y")

    # =====================================================================
    # 3. WORLD GRID & CONTACT
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
    
    grid_inv = mel.create_material_expression(material, unreal.MaterialExpressionOneMinus, -550, 600)
    mel.connect_material_expressions(grid_step_node, "", grid_inv, "")
    
    g_mask_r = mel.create_material_expression(material, unreal.MaterialExpressionComponentMask, -400, 550); g_mask_r.set_editor_property("r", True); g_mask_r.set_editor_property("g", False); g_mask_r.set_editor_property("b", False); mel.connect_material_expressions(grid_inv, "", g_mask_r, "")
    g_mask_g = mel.create_material_expression(material, unreal.MaterialExpressionComponentMask, -400, 600); g_mask_g.set_editor_property("r", False); g_mask_g.set_editor_property("g", True); g_mask_g.set_editor_property("b", False); mel.connect_material_expressions(grid_inv, "", g_mask_g, "")
    g_mask_b = mel.create_material_expression(material, unreal.MaterialExpressionComponentMask, -400, 650); g_mask_b.set_editor_property("r", False); g_mask_b.set_editor_property("g", False); g_mask_b.set_editor_property("b", True); mel.connect_material_expressions(grid_inv, "", g_mask_b, "")
    
    g_add1 = mel.create_material_expression(material, unreal.MaterialExpressionAdd, -200, 600); mel.connect_material_expressions(g_mask_r, "", g_add1, "A"); mel.connect_material_expressions(g_mask_g, "", g_add1, "B")
    g_add2 = mel.create_material_expression(material, unreal.MaterialExpressionAdd, -50, 600); mel.connect_material_expressions(g_add1, "", g_add2, "A"); mel.connect_material_expressions(g_mask_b, "", g_add2, "B")

    cont_dist = mel.create_material_expression(material, unreal.MaterialExpressionDistanceToNearestSurface, -900, 900)
    cont_div = mel.create_material_expression(material, unreal.MaterialExpressionDivide, -700, 900)
    cont_thick = mel.create_material_expression(material, unreal.MaterialExpressionScalarParameter, -900, 1000); cont_thick.set_editor_property("parameter_name", unreal.Name("ContactThickness")); cont_thick.set_editor_property("default_value", 25.0)
    mel.connect_material_expressions(cont_dist, "", cont_div, "A"); mel.connect_material_expressions(cont_thick, "", cont_div, "B")
    cont_sat = mel.create_material_expression(material, unreal.MaterialExpressionSaturate, -550, 900); mel.connect_material_expressions(cont_div, "", cont_sat, "")
    cont_one_minus = mel.create_material_expression(material, unreal.MaterialExpressionOneMinus, -400, 900); mel.connect_material_expressions(cont_sat, "", cont_one_minus, "")

    # =====================================================================
    # 4. FINAL COMBINE (Digital Scan Decay)
    # =====================================================================
    unreal.log("Wiring Final Combine...")
    color_param = mel.create_material_expression(material, unreal.MaterialExpressionVectorParameter, 600, 800)
    color_param.set_editor_property("parameter_name", unreal.Name("BlueprintColor")); color_param.set_editor_property("default_value", unreal.LinearColor(0.0, 1.0, 1.0, 1.0))
    
    # Base Detail = Grid + Contact + Wireframe
    world_extra = mel.create_material_expression(material, unreal.MaterialExpressionAdd, 100, 600)
    mel.connect_material_expressions(g_add2, "", world_extra, "A"); mel.connect_material_expressions(cont_one_minus, "", world_extra, "B")
    world_lines = mel.create_material_expression(material, unreal.MaterialExpressionAdd, 250, 600)
    mel.connect_material_expressions(uv_step, "", world_lines, "A"); mel.connect_material_expressions(world_extra, "", world_lines, "B")
    
    # Path A: PLAYER (Always On Wireframe)
    path_player = mel.create_material_expression(material, unreal.MaterialExpressionMultiply, 800, 300)
    mel.connect_material_expressions(uv_step, "", path_player, "A"); mel.connect_material_expressions(color_param, "", path_player, "B")
    
    # Path B: ENEMY (Decaying Wireframe ONLY)
    enemy_masked = mel.create_material_expression(material, unreal.MaterialExpressionMultiply, 400, 450)
    mel.connect_material_expressions(uv_step, "", enemy_masked, "A"); mel.connect_material_expressions(final_decay, "", enemy_masked, "B")
    path_enemy = mel.create_material_expression(material, unreal.MaterialExpressionMultiply, 800, 450)
    mel.connect_material_expressions(enemy_masked, "", path_enemy, "A"); mel.connect_material_expressions(color_param, "", path_enemy, "B")
    
    # Path C: WORLD (Decaying Detail + Sharp Laser Ring)
    world_masked = mel.create_material_expression(material, unreal.MaterialExpressionMultiply, 400, 600)
    mel.connect_material_expressions(world_lines, "", world_masked, "A"); mel.connect_material_expressions(final_decay, "", world_masked, "B")
    
    # Add Laser Ring to the fading grid
    world_final = mel.create_material_expression(material, unreal.MaterialExpressionMax, 600, 600)
    mel.connect_material_expressions(world_masked, "", world_final, "A"); mel.connect_material_expressions(final_ring, "", world_final, "B")
    path_world = mel.create_material_expression(material, unreal.MaterialExpressionMultiply, 800, 600)
    mel.connect_material_expressions(world_final, "", path_world, "A"); mel.connect_material_expressions(color_param, "", path_world, "B")
    
    # Switches
    sw_enemy = mel.create_material_expression(material, unreal.MaterialExpressionStaticSwitchParameter, 1000, 500)
    sw_enemy.set_editor_property("parameter_name", unreal.Name("IsEnemy")); mel.connect_material_expressions(path_enemy, "", sw_enemy, "True"); mel.connect_material_expressions(path_world, "", sw_enemy, "False")
    
    sw_player = mel.create_material_expression(material, unreal.MaterialExpressionStaticSwitchParameter, 1200, 400)
    sw_player.set_editor_property("parameter_name", unreal.Name("IsPlayer")); mel.connect_material_expressions(path_player, "", sw_player, "True"); mel.connect_material_expressions(sw_enemy, "", sw_player, "False")
    
    mel.connect_material_property(sw_player, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    
    mel.recompile_material(material)
    unreal.EditorAssetLibrary.save_asset(asset_path)
    unreal.log("SUCCESS: Digital Scan Decay Sonar Built!")

if __name__ == "__main__":
    run()