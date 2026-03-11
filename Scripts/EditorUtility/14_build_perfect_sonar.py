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
    # 1. RIPPLE MASKS
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
    
    # Broad Mask (For hiding enemies in the dark)
    broad_min = mel.create_material_expression(material, unreal.MaterialExpressionConstant, -800, -300); broad_min.set_editor_property("r", 0.7)
    broad_max = mel.create_material_expression(material, unreal.MaterialExpressionConstant, -800, -250); broad_max.set_editor_property("r", 1.0)
    broad_ss = mel.create_material_expression(material, unreal.MaterialExpressionSmoothStep, -650, -250)
    mel.connect_material_expressions(broad_min, "", broad_ss, "Min"); mel.connect_material_expressions(broad_max, "", broad_ss, "Max"); mel.connect_material_expressions(div_node, "", broad_ss, "Value")
    broad_mask = mel.create_material_expression(material, unreal.MaterialExpressionOneMinus, -500, -250)
    mel.connect_material_expressions(broad_ss, "", broad_mask, "")
    
    # Sharp Wave (For the environment scanning ring)
    w_min1 = mel.create_material_expression(material, unreal.MaterialExpressionConstant, -800, -150); w_min1.set_editor_property("r", 0.8)
    w_max1 = mel.create_material_expression(material, unreal.MaterialExpressionConstant, -800, -100); w_max1.set_editor_property("r", 0.95)
    w_ss1 = mel.create_material_expression(material, unreal.MaterialExpressionSmoothStep, -650, -150)
    mel.connect_material_expressions(w_min1, "", w_ss1, "Min"); mel.connect_material_expressions(w_max1, "", w_ss1, "Max"); mel.connect_material_expressions(div_node, "", w_ss1, "Value")
    
    w_min2 = mel.create_material_expression(material, unreal.MaterialExpressionConstant, -800, 0); w_min2.set_editor_property("r", 0.95)
    w_max2 = mel.create_material_expression(material, unreal.MaterialExpressionConstant, -800, 50); w_max2.set_editor_property("r", 1.0)
    w_ss2 = mel.create_material_expression(material, unreal.MaterialExpressionSmoothStep, -650, 0)
    mel.connect_material_expressions(w_min2, "", w_ss2, "Min"); mel.connect_material_expressions(w_max2, "", w_ss2, "Max"); mel.connect_material_expressions(div_node, "", w_ss2, "Value")
    w_inv2 = mel.create_material_expression(material, unreal.MaterialExpressionOneMinus, -500, 0)
    mel.connect_material_expressions(w_ss2, "", w_inv2, "")
    
    sharp_wave = mel.create_material_expression(material, unreal.MaterialExpressionMultiply, -350, -100)
    mel.connect_material_expressions(w_ss1, "", sharp_wave, "A"); mel.connect_material_expressions(w_inv2, "", sharp_wave, "B")
    
    # Apply Intensity
    int_node = mel.create_material_expression(material, unreal.MaterialExpressionCollectionParameter, -500, -150)
    int_node.set_editor_property("collection", mpc); int_node.set_editor_property("parameter_name", unreal.Name("RippleIntensity"))
    
    final_broad = mel.create_material_expression(material, unreal.MaterialExpressionMultiply, -200, -200)
    mel.connect_material_expressions(broad_mask, "", final_broad, "A"); mel.connect_material_expressions(int_node, "", final_broad, "B")
    
    final_wave = mel.create_material_expression(material, unreal.MaterialExpressionMultiply, -200, -50)
    mel.connect_material_expressions(sharp_wave, "", final_wave, "A"); mel.connect_material_expressions(int_node, "", final_wave, "B")

    # =====================================================================
    # 2. UV WIREFRAME (For Player and Enemies)
    # =====================================================================
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
    # 3. WORLD GRID
    # =====================================================================
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
    
    g_mask_r = mel.create_material_expression(material, unreal.MaterialExpressionComponentMask, -400, 550); g_mask_r.set_editor_property("r", True); g_mask_r.set_editor_property("g", False); g_mask_r.set_editor_property("b", False)
    g_mask_g = mel.create_material_expression(material, unreal.MaterialExpressionComponentMask, -400, 600); g_mask_g.set_editor_property("r", False); g_mask_g.set_editor_property("g", True); g_mask_g.set_editor_property("b", False)
    g_mask_b = mel.create_material_expression(material, unreal.MaterialExpressionComponentMask, -400, 650); g_mask_b.set_editor_property("r", False); g_mask_b.set_editor_property("g", False); g_mask_b.set_editor_property("b", True)
    mel.connect_material_expressions(grid_inv, "", g_mask_r, ""); mel.connect_material_expressions(grid_inv, "", g_mask_g, ""); mel.connect_material_expressions(grid_inv, "", g_mask_b, "")
    
    g_add1 = mel.create_material_expression(material, unreal.MaterialExpressionAdd, -200, 600)
    mel.connect_material_expressions(g_mask_r, "", g_add1, "A"); mel.connect_material_expressions(g_mask_g, "", g_add1, "B")
    g_add2 = mel.create_material_expression(material, unreal.MaterialExpressionAdd, -50, 600)
    mel.connect_material_expressions(g_add1, "", g_add2, "A"); mel.connect_material_expressions(g_mask_b, "", g_add2, "B")

    # =====================================================================
    # 4. THREE-WAY SWITCH LOGIC
    # =====================================================================
    color_param = mel.create_material_expression(material, unreal.MaterialExpressionVectorParameter, 400, 800)
    color_param.set_editor_property("parameter_name", unreal.Name("BlueprintColor")); color_param.set_editor_property("default_value", unreal.LinearColor(0.0, 1.0, 1.0, 1.0))
    
    # --- PATH A: PLAYER (Always On Wireframe) ---
    path_player = mel.create_material_expression(material, unreal.MaterialExpressionMultiply, 100, 300)
    mel.connect_material_expressions(uv_step, "", path_player, "A"); mel.connect_material_expressions(color_param, "", path_player, "B")
    
    # --- PATH B: ENEMY (Masked Wireframe) ---
    enemy_mask = mel.create_material_expression(material, unreal.MaterialExpressionMultiply, 100, 450)
    mel.connect_material_expressions(uv_step, "", enemy_mask, "A"); mel.connect_material_expressions(final_broad, "", enemy_mask, "B")
    path_enemy = mel.create_material_expression(material, unreal.MaterialExpressionMultiply, 250, 450)
    mel.connect_material_expressions(enemy_mask, "", path_enemy, "A"); mel.connect_material_expressions(color_param, "", path_enemy, "B")
    
    # --- PATH C: ENVIRONMENT (Masked Grid + Solid Wave) ---
    env_grid = mel.create_material_expression(material, unreal.MaterialExpressionMultiply, 100, 600)
    mel.connect_material_expressions(g_add2, "", env_grid, "A"); mel.connect_material_expressions(final_broad, "", env_grid, "B")
    env_combine = mel.create_material_expression(material, unreal.MaterialExpressionMax, 250, 600)
    mel.connect_material_expressions(env_grid, "", env_combine, "A"); mel.connect_material_expressions(final_wave, "", env_combine, "B")
    path_env = mel.create_material_expression(material, unreal.MaterialExpressionMultiply, 400, 600)
    mel.connect_material_expressions(env_combine, "", path_env, "A"); mel.connect_material_expressions(color_param, "", path_env, "B")
    
    # --- SWITCHES ---
    sw_enemy = mel.create_material_expression(material, unreal.MaterialExpressionStaticSwitchParameter, 600, 500)
    sw_enemy.set_editor_property("parameter_name", unreal.Name("IsEnemy")); sw_enemy.set_editor_property("default_value", False)
    mel.connect_material_expressions(path_enemy, "", sw_enemy, "True"); mel.connect_material_expressions(path_env, "", sw_enemy, "False")
    
    sw_player = mel.create_material_expression(material, unreal.MaterialExpressionStaticSwitchParameter, 800, 400)
    sw_player.set_editor_property("parameter_name", unreal.Name("IsPlayer")); sw_player.set_editor_property("default_value", False)
    mel.connect_material_expressions(path_player, "", sw_player, "True"); mel.connect_material_expressions(sw_enemy, "", sw_player, "False")
    
    mel.connect_material_property(sw_player, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    
    mel.recompile_material(material)
    unreal.EditorAssetLibrary.save_asset(asset_path)
    unreal.log("SUCCESS: M_EchoMaster_Final built!")

if __name__ == "__main__":
    run()