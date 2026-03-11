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
    # 1. SMOOTH RIPPLE MASKS
    # =====================================================================
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
    
    div_node = mel.create_material_expression(material, unreal.MaterialExpressionDivide, -950, -200)
    mel.connect_material_expressions(dist_node, "", div_node, "A"); mel.connect_material_expressions(rad_node, "", div_node, "B")
    
    # Smooth Broad Mask (For hiding enemies in the dark)
    # We use a slight fade at the edge to prevent hard-pixel artifacts
    broad_min = mel.create_material_expression(material, unreal.MaterialExpressionConstant, -800, -300); broad_min.set_editor_property("r", 0.7)
    broad_max = mel.create_material_expression(material, unreal.MaterialExpressionConstant, -800, -250); broad_max.set_editor_property("r", 0.98)
    broad_ss = mel.create_material_expression(material, unreal.MaterialExpressionSmoothStep, -650, -250)
    mel.connect_material_expressions(broad_min, "", broad_ss, "Min"); mel.connect_material_expressions(broad_max, "", broad_ss, "Max"); mel.connect_material_expressions(div_node, "", broad_ss, "Value")
    broad_mask = mel.create_material_expression(material, unreal.MaterialExpressionOneMinus, -500, -250)
    mel.connect_material_expressions(broad_ss, "", broad_mask, "")
    
    # Smooth Energy Wave (The glowing ring)
    # We use two SmoothSteps to create a "Soft Tube" shape for the wave
    w_ring_in = mel.create_material_expression(material, unreal.MaterialExpressionSmoothStep, -800, -150)
    wi_min = mel.create_material_expression(material, unreal.MaterialExpressionConstant, -950, -200); wi_min.set_editor_property("r", 0.85)
    wi_max = mel.create_material_expression(material, unreal.MaterialExpressionConstant, -950, -150); wi_max.set_editor_property("r", 0.95)
    mel.connect_material_expressions(wi_min, "", w_ring_in, "Min"); mel.connect_material_expressions(wi_max, "", w_ring_in, "Max"); mel.connect_material_expressions(div_node, "", w_ring_in, "Value")
    
    w_ring_out = mel.create_material_expression(material, unreal.MaterialExpressionSmoothStep, -800, 0)
    wo_min = mel.create_material_expression(material, unreal.MaterialExpressionConstant, -950, 0); wo_min.set_editor_property("r", 0.95)
    wo_max = mel.create_material_expression(material, unreal.MaterialExpressionConstant, -950, 50); wo_max.set_editor_property("r", 1.0)
    mel.connect_material_expressions(wo_min, "", w_ring_out, "Min"); mel.connect_material_expressions(wo_max, "", w_ring_out, "Max"); mel.connect_material_expressions(div_node, "", w_ring_out, "Value")
    
    w_ring_inv = mel.create_material_expression(material, unreal.MaterialExpressionOneMinus, -650, 0)
    mel.connect_material_expressions(w_ring_out, "", w_ring_inv, "")
    
    wave_ring_soft = mel.create_material_expression(material, unreal.MaterialExpressionMultiply, -500, -100)
    mel.connect_material_expressions(w_ring_in, "", wave_ring_soft, "A"); mel.connect_material_expressions(w_ring_inv, "", wave_ring_soft, "B")
    
    # Intensity
    int_node = mel.create_material_expression(material, unreal.MaterialExpressionCollectionParameter, -500, -50)
    int_node.set_editor_property("collection", mpc); int_node.set_editor_property("parameter_name", unreal.Name("RippleIntensity"))
    
    geo_reveal_mask = mel.create_material_expression(material, unreal.MaterialExpressionMultiply, -350, -200)
    mel.connect_material_expressions(broad_mask, "", geo_reveal_mask, "A"); mel.connect_material_expressions(int_node, "", geo_reveal_mask, "B")
    
    wave_ring_final = mel.create_material_expression(material, unreal.MaterialExpressionMultiply, -350, -50)
    mel.connect_material_expressions(wave_ring_soft, "", wave_ring_final, "A"); mel.connect_material_expressions(int_node, "", wave_ring_final, "B")

    # =====================================================================
    # 2. UV WIREFRAME
    # =====================================================================
    uv_node = mel.create_material_expression(material, unreal.MaterialExpressionTextureCoordinate, -1200, 300)
    uv_sub = mel.create_material_expression(material, unreal.MaterialExpressionSubtract, -1000, 300)
    uv_const = mel.create_material_expression(material, unreal.MaterialExpressionConstant, -1100, 350); uv_const.set_editor_property("r", 0.5)
    mel.connect_material_expressions(uv_node, "", uv_sub, "A"); mel.connect_material_expressions(uv_const, "", uv_sub, "B")
    uv_abs = mel.create_material_expression(material, unreal.MaterialExpressionAbs, -850, 300); mel.connect_material_expressions(uv_sub, "", uv_abs, "")
    mask_r = mel.create_material_expression(material, unreal.MaterialExpressionComponentMask, -700, 250); mask_r.set_editor_property("r", True); mask_r.set_editor_property("g", False); mel.connect_material_expressions(uv_abs, "", mask_r, "")
    mask_g = mel.create_material_expression(material, unreal.MaterialExpressionComponentMask, -700, 350); mask_g.set_editor_property("r", False); mask_g.set_editor_property("g", True); mel.connect_material_expressions(uv_abs, "", mask_g, "")
    uv_max = mel.create_material_expression(material, unreal.MaterialExpressionMax, -500, 300); mel.connect_material_expressions(mask_r, "", uv_max, "A"); mel.connect_material_expressions(mask_g, "", uv_max, "B")
    uv_step = mel.create_material_expression(material, unreal.MaterialExpressionStep, -350, 300)
    uv_thresh = mel.create_material_expression(material, unreal.MaterialExpressionScalarParameter, -500, 400); uv_thresh.set_editor_property("parameter_name", unreal.Name("EdgeThickness")); uv_thresh.set_editor_property("default_value", 0.495)
    mel.connect_material_expressions(uv_max, "", uv_step, "X"); mel.connect_material_expressions(uv_thresh, "", uv_step, "Y")

    # =====================================================================
    # 3. WORLD GRID & CONTACT
    # =====================================================================
    grid_wp = mel.create_material_expression(material, unreal.MaterialExpressionWorldPosition, -1200, 600)
    grid_div = mel.create_material_expression(material, unreal.MaterialExpressionDivide, -1000, 600)
    grid_size = mel.create_material_expression(material, unreal.MaterialExpressionScalarParameter, -1200, 700); grid_size.set_editor_property("parameter_name", unreal.Name("GridSize")); grid_size.set_editor_property("default_value", 100.0)
    mel.connect_material_expressions(grid_wp, "", grid_div, "A"); mel.connect_material_expressions(grid_size, "", grid_div, "B")
    grid_frac = mel.create_material_expression(material, unreal.MaterialExpressionFrac, -850, 600); mel.connect_material_expressions(grid_div, "", grid_frac, "")
    grid_step_node = mel.create_material_expression(material, unreal.MaterialExpressionStep, -700, 600)
    grid_thick = mel.create_material_expression(material, unreal.MaterialExpressionScalarParameter, -850, 700); grid_thick.set_editor_property("parameter_name", unreal.Name("GridThickness")); grid_thick.set_editor_property("default_value", 0.02)
    mel.connect_material_expressions(grid_frac, "", grid_step_node, "X"); mel.connect_material_expressions(grid_thick, "", grid_step_node, "Y")
    grid_inv = mel.create_material_expression(material, unreal.MaterialExpressionOneMinus, -550, 600); mel.connect_material_expressions(grid_step_node, "", grid_inv, "")
    g_mask_r = mel.create_material_expression(material, unreal.MaterialExpressionComponentMask, -400, 550); g_mask_r.set_editor_property("r", True); g_mask_r.set_editor_property("g", False); g_mask_r.set_editor_property("b", False); mel.connect_material_expressions(grid_inv, "", g_mask_r, "")
    g_mask_g = mel.create_material_expression(material, unreal.MaterialExpressionComponentMask, -400, 600); g_mask_g.set_editor_property("r", False); g_mask_g.set_editor_property("g", True); g_mask_g.set_editor_property("b", False); mel.connect_material_expressions(grid_inv, "", g_mask_g, "")
    g_mask_b = mel.create_material_expression(material, unreal.MaterialExpressionComponentMask, -400, 650); g_mask_b.set_editor_property("r", False); g_mask_b.set_editor_property("g", False); g_mask_b.set_editor_property("b", True); mel.connect_material_expressions(grid_inv, "", g_mask_b, "")
    g_add1 = mel.create_material_expression(material, unreal.MaterialExpressionAdd, -200, 600); mel.connect_material_expressions(g_mask_r, "", g_add1, "A"); mel.connect_material_expressions(g_mask_g, "", g_add1, "B")
    g_add2 = mel.create_material_expression(material, unreal.MaterialExpressionAdd, -50, 600); mel.connect_material_expressions(g_add1, "", g_add2, "A"); mel.connect_material_expressions(g_mask_b, "", g_add2, "B")

    cont_dist = mel.create_material_expression(material, unreal.MaterialExpressionDistanceToNearestSurface, -900, 900)
    cont_div = mel.create_material_expression(material, unreal.MaterialExpressionDivide, -700, 900); cont_thick = mel.create_material_expression(material, unreal.MaterialExpressionScalarParameter, -900, 1000); cont_thick.set_editor_property("parameter_name", unreal.Name("ContactThickness")); cont_thick.set_editor_property("default_value", 25.0)
    mel.connect_material_expressions(cont_dist, "", cont_div, "A"); mel.connect_material_expressions(cont_thick, "", cont_div, "B")
    cont_sat = mel.create_material_expression(material, unreal.MaterialExpressionSaturate, -550, 900); mel.connect_material_expressions(cont_div, "", cont_sat, "")
    cont_inv = mel.create_material_expression(material, unreal.MaterialExpressionOneMinus, -400, 900); mel.connect_material_expressions(cont_sat, "", cont_inv, "")

    # =====================================================================
    # 4. FINAL COMBINE
    # =====================================================================
    color_param = mel.create_material_expression(material, unreal.MaterialExpressionVectorParameter, 600, 800)
    color_param.set_editor_property("parameter_name", unreal.Name("BlueprintColor")); color_param.set_editor_property("default_value", unreal.LinearColor(0.0, 1.0, 1.0, 1.0))
    
    # Path A: PLAYER (Always On Wireframe)
    path_player = mel.create_material_expression(material, unreal.MaterialExpressionMultiply, 800, 300)
    mel.connect_material_expressions(uv_step, "", path_player, "A"); mel.connect_material_expressions(color_param, "", path_player, "B")
    
    # Path B: ENEMY (Masked Wireframe ONLY)
    enemy_masked = mel.create_material_expression(material, unreal.MaterialExpressionMultiply, 400, 450)
    mel.connect_material_expressions(uv_step, "", enemy_masked, "A"); mel.connect_material_expressions(geo_reveal_mask, "", enemy_masked, "B")
    path_enemy = mel.create_material_expression(material, unreal.MaterialExpressionMultiply, 800, 450)
    mel.connect_material_expressions(enemy_masked, "", path_enemy, "A"); mel.connect_material_expressions(color_param, "", path_enemy, "B")
    
    # Path C: WORLD (Masked Geometry + Smooth Wave)
    world_extra = mel.create_material_expression(material, unreal.MaterialExpressionAdd, 100, 600); mel.connect_material_expressions(g_add2, "", world_extra, "A"); mel.connect_material_expressions(cont_inv, "", world_extra, "B")
    world_lines = mel.create_material_expression(material, unreal.MaterialExpressionAdd, 250, 600); mel.connect_material_expressions(uv_step, "", world_lines, "A"); mel.connect_material_expressions(world_extra, "", world_lines, "B")
    world_masked = mel.create_material_expression(material, unreal.MaterialExpressionMultiply, 400, 600); mel.connect_material_expressions(world_lines, "", world_masked, "A"); mel.connect_material_expressions(geo_reveal_mask, "", world_masked, "B")
    
    # Smooth Combine with Wave Ring
    world_combined = mel.create_material_expression(material, unreal.MaterialExpressionMax, 600, 600)
    mel.connect_material_expressions(world_masked, "", world_combined, "A"); mel.connect_material_expressions(wave_ring_final, "", world_combined, "B")
    path_world = mel.create_material_expression(material, unreal.MaterialExpressionMultiply, 800, 600)
    mel.connect_material_expressions(world_combined, "", path_world, "A"); mel.connect_material_expressions(color_param, "", path_world, "B")
    
    # Static Switches
    sw_enemy = mel.create_material_expression(material, unreal.MaterialExpressionStaticSwitchParameter, 1000, 500); sw_enemy.set_editor_property("parameter_name", unreal.Name("IsEnemy")); mel.connect_material_expressions(path_enemy, "", sw_enemy, "True"); mel.connect_material_expressions(path_world, "", sw_enemy, "False")
    sw_player = mel.create_material_expression(material, unreal.MaterialExpressionStaticSwitchParameter, 1200, 400); sw_player.set_editor_property("parameter_name", unreal.Name("IsPlayer")); mel.connect_material_expressions(path_player, "", sw_player, "True"); mel.connect_material_expressions(sw_enemy, "", sw_player, "False")
    
    mel.connect_material_property(sw_player, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    
    mel.recompile_material(material)
    unreal.EditorAssetLibrary.save_asset(asset_path)
    unreal.log("SUCCESS: Smooth High-Fidelity Sonar Built!")

if __name__ == "__main__":
    run()