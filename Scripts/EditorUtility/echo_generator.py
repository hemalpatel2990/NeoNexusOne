"""
echo_generator.py — Config-driven asset generation for EchoLocation.

Wraps the logic from scripts 01–09, reading all tunable values from an
EchoConfig instance instead of hardcoded constants.  Each sub-generator
is idempotent — it checks asset existence before creating.

Usage (from UE5 Python console):
    from echo_config import EchoConfig
    from echo_generator import generate_all
    cfg = EchoConfig.load()       # or EchoConfig() for defaults
    generate_all(cfg)
"""

import os
import importlib

import unreal

from echo_config import EchoConfig
from helpers import (
    Paths, CppClasses, MPCParams,
    asset_exists, ensure_directory, save_asset,
    log_created, log_exists, log_manual,
)


# ======================================================================
# Public entry point
# ======================================================================

def generate_all(config: EchoConfig | None = None):
    """Run every sub-generator in dependency order with *config* values."""
    if config is None:
        config = EchoConfig.load()

    unreal.log("=" * 60)
    unreal.log("[EchoGenerator] Starting config-driven asset generation...")
    unreal.log("=" * 60)

    steps = [
        ("MPC_GlobalSound",       lambda: generate_mpc(config)),
        ("Curves",                lambda: generate_curves(config)),
        ("Input Actions",         lambda: generate_input_actions(config)),
        ("Input Mapping Context", lambda: generate_input_mapping(config)),
        ("Feedback",              lambda: generate_feedback(config)),
        ("Material",              lambda: generate_material(config)),
        ("Blueprints",            lambda: generate_blueprints(config)),
        ("Level",                 lambda: generate_level(config)),
        ("Engine Config",         lambda: generate_engine_config(config)),
    ]

    success = 0
    fail = 0
    for label, func in steps:
        unreal.log(f"\n--- {label} ---")
        try:
            func()
            success += 1
        except Exception as e:
            unreal.log_error(f"[EchoGenerator] FAILED: {label} — {e}")
            import traceback
            unreal.log_error(traceback.format_exc())
            fail += 1

    unreal.log("\n" + "=" * 60)
    unreal.log(f"[EchoGenerator] Done! {success} succeeded, {fail} failed.")
    unreal.log("=" * 60)


# ======================================================================
# 01 — MPC
# ======================================================================

def generate_mpc(config: EchoConfig):
    """Create MPC_GlobalSound. No config-tunable values (parameters are fixed)."""
    path = Paths.MPC_GLOBAL_SOUND
    if asset_exists(path):
        log_exists("MPC_GlobalSound", path)
        return

    ensure_directory(path)

    factory = unreal.MaterialParameterCollectionFactoryNew()
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    directory, name = path.rsplit("/", 1)

    mpc = asset_tools.create_asset(name, directory, unreal.MaterialParameterCollection, factory)
    if mpc is None:
        raise RuntimeError("create_asset returned None for MPC_GlobalSound")

    vec_param = unreal.CollectionVectorParameter()
    vec_param.set_editor_property("parameter_name", MPCParams.LAST_IMPACT_LOCATION)
    vec_param.set_editor_property("default_value", unreal.LinearColor(0, 0, 0, 0))
    mpc.get_editor_property("vector_parameters").append(vec_param)

    for pname in (MPCParams.CURRENT_RIPPLE_RADIUS, MPCParams.RIPPLE_INTENSITY):
        sp = unreal.CollectionScalarParameter()
        sp.set_editor_property("parameter_name", pname)
        sp.set_editor_property("default_value", 0.0)
        mpc.get_editor_property("scalar_parameters").append(sp)

    save_asset(path)
    log_created("MPC_GlobalSound", path)


# ======================================================================
# 02 — Curves
# ======================================================================

def generate_curves(config: EchoConfig):
    """Create ripple radius and intensity curves (shape is fixed, duration is C++)."""
    _create_curve(
        Paths.CURVE_RIPPLE_RADIUS, "C_RippleRadius",
        [(0.0, 0.0), (1.0, 1.0)],
    )
    _create_curve(
        Paths.CURVE_RIPPLE_INTENSITY, "C_RippleIntensity",
        [(0.0, 1.0), (1.0, 0.0)],
    )


def _create_curve(path, asset_name, keys):
    if asset_exists(path):
        log_exists(asset_name, path)
        return

    ensure_directory(path)
    factory = unreal.CurveFloatFactory()
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    directory, name = path.rsplit("/", 1)

    curve = asset_tools.create_asset(name, directory, unreal.CurveFloat, factory)
    if curve is None:
        raise RuntimeError(f"create_asset returned None for {asset_name}")

    try:
        rich_curve = curve.float_curve
        for t, v in keys:
            rich_curve.add_key(t, v)
    except Exception as e:
        unreal.log_warning(f"[EchoGenerator] Could not add keyframes for {asset_name}: {e}")
        log_manual(f"Open {asset_name} and add keys manually: {keys}")

    save_asset(path)
    log_created(asset_name, path)


# ======================================================================
# 03 — Input Actions
# ======================================================================

def generate_input_actions(config: EchoConfig):
    """Create IA_Move, IA_Look, IA_Slam (no config-tunable values)."""
    _create_input_action(Paths.IA_MOVE, "IA_Move", unreal.InputActionValueType.AXIS2D)
    _create_input_action(Paths.IA_LOOK, "IA_Look", unreal.InputActionValueType.AXIS2D)
    _create_input_action(Paths.IA_SLAM, "IA_Slam", unreal.InputActionValueType.BOOLEAN)


def _create_input_action(path, asset_name, value_type):
    if asset_exists(path):
        log_exists(asset_name, path)
        return

    ensure_directory(path)
    factory = unreal.InputAction_Factory()
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    directory, name = path.rsplit("/", 1)

    action = asset_tools.create_asset(name, directory, None, factory)
    if action is None:
        raise RuntimeError(f"create_asset returned None for {asset_name}")

    action.set_editor_property("value_type", value_type)
    save_asset(path)
    log_created(asset_name, path)


# ======================================================================
# 04 — Input Mapping Context
# ======================================================================

def generate_input_mapping(config: EchoConfig):
    """Create IMC_EchoDefault with WASD/mouse/gamepad bindings."""
    path = Paths.IMC_ECHO_DEFAULT
    if asset_exists(path):
        log_exists("IMC_EchoDefault", path)
        return

    ensure_directory(path)
    factory = unreal.InputMappingContext_Factory()
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    directory, name = path.rsplit("/", 1)

    imc = asset_tools.create_asset(name, directory, None, factory)
    if imc is None:
        raise RuntimeError("create_asset returned None for IMC_EchoDefault")

    ia_move = unreal.load_asset(Paths.IA_MOVE)
    ia_look = unreal.load_asset(Paths.IA_LOOK)
    ia_slam = unreal.load_asset(Paths.IA_SLAM)

    if not all([ia_move, ia_look, ia_slam]):
        raise RuntimeError("Input actions not found. Run generate_input_actions first.")

    try:
        # IA_Move
        w = imc.map_key(ia_move, unreal.Key("W"))
        w.add_modifier(unreal.InputModifierSwizzleAxis())

        s = imc.map_key(ia_move, unreal.Key("S"))
        s.add_modifier(unreal.InputModifierSwizzleAxis())
        s.add_modifier(unreal.InputModifierNegate())

        imc.map_key(ia_move, unreal.Key("D"))

        a = imc.map_key(ia_move, unreal.Key("A"))
        a.add_modifier(unreal.InputModifierNegate())

        imc.map_key(ia_move, unreal.Key("Gamepad_Left2D"))

        # IA_Look
        imc.map_key(ia_look, unreal.Key("Mouse2D"))
        imc.map_key(ia_look, unreal.Key("Gamepad_Right2D"))

        # IA_Slam
        imc.map_key(ia_slam, unreal.Key("SpaceBar"))
        imc.map_key(ia_slam, unreal.Key("Gamepad_FaceButton_Bottom"))

    except Exception as e:
        unreal.log_warning(f"[EchoGenerator] IMC binding failed: {e}")
        log_manual(
            "Open IMC_EchoDefault and add key mappings manually:\n"
            "  IA_Move: W (Swizzle), S (Swizzle+Negate), D, A (Negate), Left Stick\n"
            "  IA_Look: Mouse2D, Right Stick\n"
            "  IA_Slam: SpaceBar, Gamepad Face Bottom"
        )

    save_asset(path)
    log_created("IMC_EchoDefault", path)


# ======================================================================
# 05 — Feedback (Camera Shakes + Force Feedback)
# ======================================================================

def generate_feedback(config: EchoConfig):
    """Create camera shake and force feedback assets from config values."""
    # Camera shakes
    _create_camera_shake(
        Paths.CS_DROP_SHAKE, "CS_DropShake",
        duration=config.drop_shake_duration,
        loc_amp=config.drop_shake_loc_amplitude,
        rot_amp=config.drop_shake_rot_amplitude,
    )
    _create_camera_shake(
        Paths.CS_SLAM_SHAKE, "CS_SlamShake",
        duration=config.slam_shake_duration,
        loc_amp=config.slam_shake_loc_amplitude,
        rot_amp=config.slam_shake_rot_amplitude,
    )

    # Force feedback
    _create_force_feedback(
        Paths.FFE_DROP_FEEDBACK, "FFE_DropFeedback",
        large_amp=config.drop_ffe_large_amplitude,
        small_amp=config.drop_ffe_small_amplitude,
        duration=config.drop_ffe_duration,
    )
    _create_force_feedback(
        Paths.FFE_SLAM_FEEDBACK, "FFE_SlamFeedback",
        large_amp=config.slam_ffe_large_amplitude,
        small_amp=config.slam_ffe_small_amplitude,
        duration=config.slam_ffe_duration,
    )


def _create_camera_shake(path, asset_name, duration, loc_amp, rot_amp):
    if asset_exists(path):
        log_exists(asset_name, path)
        return

    ensure_directory(path)
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    directory, name = path.rsplit("/", 1)

    try:
        factory = unreal.BlueprintFactory()
        parent_class = getattr(unreal, "LegacyCameraShake", None)
        if parent_class is None:
            parent_class = getattr(unreal, "MatineeCameraShake", None)
        if parent_class is None:
            raise RuntimeError("Neither LegacyCameraShake nor MatineeCameraShake found")

        factory.set_editor_property("parent_class", parent_class)
        bp = asset_tools.create_asset(name, directory, unreal.Blueprint, factory)
        if bp is None:
            raise RuntimeError("create_asset returned None")

        cdo = unreal.get_default_object(bp.generated_class())
        if cdo is not None:
            cdo.set_editor_property("oscillation_duration", duration)

            try:
                loc_osc = cdo.get_editor_property("loc_oscillation")
                if loc_osc:
                    loc_x = loc_osc.get_editor_property("x")
                    if loc_x:
                        loc_x.set_editor_property("amplitude", loc_amp)
                        loc_x.set_editor_property("frequency", 15.0)
                    loc_z = loc_osc.get_editor_property("z")
                    if loc_z:
                        loc_z.set_editor_property("amplitude", loc_amp * 0.5)
                        loc_z.set_editor_property("frequency", 12.0)
            except Exception as e:
                unreal.log_warning(f"[EchoGenerator] loc_oscillation for {asset_name}: {e}")

            try:
                rot_osc = cdo.get_editor_property("rot_oscillation")
                if rot_osc:
                    pitch = rot_osc.get_editor_property("pitch")
                    if pitch:
                        pitch.set_editor_property("amplitude", rot_amp)
                        pitch.set_editor_property("frequency", 12.0)
                    roll = rot_osc.get_editor_property("roll")
                    if roll:
                        roll.set_editor_property("amplitude", rot_amp * 0.3)
                        roll.set_editor_property("frequency", 10.0)
            except Exception as e:
                unreal.log_warning(f"[EchoGenerator] rot_oscillation for {asset_name}: {e}")

        save_asset(path)
        log_created(asset_name, path)

    except Exception as e:
        unreal.log_warning(f"[EchoGenerator] Camera shake failed for {asset_name}: {e}")
        try:
            factory = unreal.BlueprintFactory()
            factory.set_editor_property("parent_class", unreal.CameraShakeBase)
            bp = asset_tools.create_asset(name, directory, unreal.Blueprint, factory)
            if bp:
                save_asset(path)
                log_created(f"{asset_name} (empty)", path)
        except Exception:
            pass
        log_manual(
            f"Open {asset_name} and set: Duration={duration}s, "
            f"LocAmp={loc_amp}, RotAmp={rot_amp}"
        )


def _create_force_feedback(path, asset_name, large_amp, small_amp, duration):
    if asset_exists(path):
        log_exists(asset_name, path)
        return

    ensure_directory(path)
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    directory, name = path.rsplit("/", 1)

    try:
        factory = unreal.ForceFeedbackEffectFactory()
        ffe = asset_tools.create_asset(name, directory, unreal.ForceFeedbackEffect, factory)
        if ffe is None:
            raise RuntimeError(f"create_asset returned None for {asset_name}")

        channel_details = ffe.get_editor_property("channel_details")

        entry_large = unreal.ForceFeedbackChannelDetails()
        entry_large.set_editor_property("affects_left_large", True)
        entry_large.set_editor_property("affects_right_large", True)
        entry_large.set_editor_property("affects_left_small", False)
        entry_large.set_editor_property("affects_right_small", False)
        channel_details.append(entry_large)

        entry_small = unreal.ForceFeedbackChannelDetails()
        entry_small.set_editor_property("affects_left_large", False)
        entry_small.set_editor_property("affects_right_large", False)
        entry_small.set_editor_property("affects_left_small", True)
        entry_small.set_editor_property("affects_right_small", True)
        channel_details.append(entry_small)

        ffe.set_editor_property("duration", duration)

        save_asset(path)
        log_created(asset_name, path)

    except Exception as e:
        unreal.log_warning(f"[EchoGenerator] Force feedback failed for {asset_name}: {e}")
        log_manual(
            f"Create {asset_name}: LargeAmp={large_amp}, SmallAmp={small_amp}, "
            f"Duration={duration}s"
        )


# ======================================================================
# 06 — Material
# ======================================================================

def generate_material(config: EchoConfig):
    """Create M_EchoMaster and MI_EchoMaster."""
    _create_master_material(config)
    _create_material_instance(config)


def _create_master_material(config: EchoConfig):
    path = Paths.M_ECHO_MASTER
    if asset_exists(path):
        log_exists("M_EchoMaster", path)
        return

    ensure_directory(path)
    factory = unreal.MaterialFactoryNew()
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    directory, name = path.rsplit("/", 1)

    material = asset_tools.create_asset(name, directory, unreal.Material, factory)
    if material is None:
        raise RuntimeError("create_asset returned None for M_EchoMaster")

    try:
        material.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_DEFAULT_LIT)
        material.set_editor_property("blend_mode", unreal.BlendMode.BLEND_OPAQUE)
        material.set_editor_property("two_sided", False)
    except Exception as e:
        unreal.log_warning(f"[EchoGenerator] Material properties: {e}")

    save_asset(path)
    log_created("M_EchoMaster", path)

    bc = config.base_color
    log_manual(
        "Build M_EchoMaster node graph:\n"
        f"  1. MPC_GlobalSound collection parameter nodes\n"
        f"  2. SphereMask: Radius=CurrentRippleRadius, Hardness={config.sphere_mask_hardness}\n"
        f"  3. Multiply SphereMask x RippleIntensity x {config.emissive_multiplier}\n"
        f"  4. Emissive Color: white x mask\n"
        f"  5. Base Color: ({bc[0]}, {bc[1]}, {bc[2]})\n"
        f"  6. SmoothStep ring-shaped reveal"
    )


def _create_material_instance(config: EchoConfig):
    path = Paths.MI_ECHO_MASTER
    if asset_exists(path):
        log_exists("MI_EchoMaster", path)
        return

    parent = unreal.load_asset(Paths.M_ECHO_MASTER)
    if parent is None:
        unreal.log_error("[EchoGenerator] M_EchoMaster not found")
        return

    ensure_directory(path)
    factory = unreal.MaterialInstanceConstantFactoryNew()
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    directory, name = path.rsplit("/", 1)

    mi = asset_tools.create_asset(name, directory, unreal.MaterialInstanceConstant, factory)
    if mi is None:
        raise RuntimeError("create_asset returned None for MI_EchoMaster")

    mi.set_editor_property("parent", parent)
    save_asset(path)
    log_created("MI_EchoMaster", path)


# ======================================================================
# 07 — Blueprints
# ======================================================================

def generate_blueprints(config: EchoConfig):
    """Create BP_EchoGameMode, BP_EchoPlayerController, BP_EchoPawn and wire CDOs."""
    _create_game_mode_bp(config)
    _create_player_controller_bp(config)
    _create_pawn_bp(config)


def _bp_create(path, asset_name, parent_class_path):
    """Shared Blueprint creation helper. Returns the Blueprint or None."""
    if asset_exists(path):
        log_exists(asset_name, path)
        return unreal.load_asset(path)

    ensure_directory(path)
    parent_class = unreal.load_object(None, parent_class_path)
    if parent_class is None:
        unreal.log_error(f"[EchoGenerator] Parent class not found: {parent_class_path}")
        return None

    factory = unreal.BlueprintFactory()
    factory.set_editor_property("parent_class", parent_class)
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    directory, name = path.rsplit("/", 1)

    bp = asset_tools.create_asset(name, directory, unreal.Blueprint, factory)
    if bp is None:
        unreal.log_error(f"[EchoGenerator] Failed to create {asset_name}")
        return None

    log_created(asset_name, path)
    return bp


def _get_cdo(bp):
    if bp is None:
        return None
    try:
        gen_class = bp.generated_class()
        if gen_class is not None:
            return unreal.get_default_object(gen_class)
    except Exception:
        pass
    return None


def _create_game_mode_bp(config: EchoConfig):
    bp = _bp_create(Paths.GAME_MODE_BP, "BP_EchoGameMode", CppClasses.ECHO_GAME_MODE)
    cdo = _get_cdo(bp)

    if cdo is None:
        log_manual("Open BP_EchoGameMode and set DefaultPawnClass, PlayerControllerClass manually")
        save_asset(Paths.GAME_MODE_BP)
        return

    try:
        pawn_bp = unreal.load_asset(Paths.PAWN_BP)
        if pawn_bp:
            cdo.set_editor_property("default_pawn_class", pawn_bp.generated_class())

        pc_bp = unreal.load_asset(Paths.PLAYER_CONTROLLER_BP)
        if pc_bp:
            cdo.set_editor_property("player_controller_class", pc_bp.generated_class())

        ripple_mgr = cdo.get_editor_property("RippleManager")
        if ripple_mgr:
            mpc = unreal.load_asset(Paths.MPC_GLOBAL_SOUND)
            if mpc:
                ripple_mgr.set_editor_property("EchoMPC", mpc)
            radius_curve = unreal.load_asset(Paths.CURVE_RIPPLE_RADIUS)
            if radius_curve:
                ripple_mgr.set_editor_property("RippleRadiusCurve", radius_curve)
            intensity_curve = unreal.load_asset(Paths.CURVE_RIPPLE_INTENSITY)
            if intensity_curve:
                ripple_mgr.set_editor_property("RippleIntensityCurve", intensity_curve)
        else:
            log_manual("Wire RippleManager: EchoMPC, RippleRadiusCurve, RippleIntensityCurve")

    except Exception as e:
        unreal.log_warning(f"[EchoGenerator] Error wiring BP_EchoGameMode: {e}")
        log_manual("Wire BP_EchoGameMode CDO manually (see 07_create_blueprints.py)")

    save_asset(Paths.GAME_MODE_BP)


def _create_player_controller_bp(config: EchoConfig):
    bp = _bp_create(
        Paths.PLAYER_CONTROLLER_BP, "BP_EchoPlayerController",
        CppClasses.ECHO_PLAYER_CONTROLLER,
    )
    cdo = _get_cdo(bp)

    if cdo is None:
        log_manual("Set BP_EchoPlayerController.DefaultMappingContext manually")
        save_asset(Paths.PLAYER_CONTROLLER_BP)
        return

    try:
        imc = unreal.load_asset(Paths.IMC_ECHO_DEFAULT)
        if imc:
            cdo.set_editor_property("DefaultMappingContext", imc)
    except Exception as e:
        unreal.log_warning(f"[EchoGenerator] Error wiring BP_EchoPlayerController: {e}")

    save_asset(Paths.PLAYER_CONTROLLER_BP)


def _create_pawn_bp(config: EchoConfig):
    bp = _bp_create(Paths.PAWN_BP, "BP_EchoPawn", CppClasses.ECHO_PAWN)
    cdo = _get_cdo(bp)

    if cdo is None:
        log_manual("Wire BP_EchoPawn input actions and feedback assets manually")
        save_asset(Paths.PAWN_BP)
        return

    try:
        # Input actions
        for prop, path in [("IA_Move", Paths.IA_MOVE), ("IA_Look", Paths.IA_LOOK), ("IA_Slam", Paths.IA_SLAM)]:
            asset = unreal.load_asset(path)
            if asset:
                cdo.set_editor_property(prop, asset)

        # Feedback component
        feedback = cdo.get_editor_property("FeedbackComponent")
        if feedback:
            drop_shake_bp = unreal.load_asset(Paths.CS_DROP_SHAKE)
            if drop_shake_bp:
                feedback.set_editor_property("DropShake", drop_shake_bp.generated_class())

            slam_shake_bp = unreal.load_asset(Paths.CS_SLAM_SHAKE)
            if slam_shake_bp:
                feedback.set_editor_property("SlamShake", slam_shake_bp.generated_class())

            drop_ffe = unreal.load_asset(Paths.FFE_DROP_FEEDBACK)
            if drop_ffe:
                feedback.set_editor_property("DropForceFeedback", drop_ffe)

            slam_ffe = unreal.load_asset(Paths.FFE_SLAM_FEEDBACK)
            if slam_ffe:
                feedback.set_editor_property("SlamForceFeedback", slam_ffe)
        else:
            log_manual("Wire FeedbackComponent shakes + force feedback manually")

        # Cube mesh
        try:
            mesh_comp = cdo.get_editor_property("CubeMesh")
            if mesh_comp:
                cube_mesh = unreal.load_asset("/Engine/BasicShapes/Cube")
                if cube_mesh:
                    mesh_comp.set_editor_property("static_mesh", cube_mesh)
        except Exception:
            log_manual("Set BP_EchoPawn.CubeMesh → /Engine/BasicShapes/Cube")

    except Exception as e:
        unreal.log_warning(f"[EchoGenerator] Error wiring BP_EchoPawn: {e}")

    save_asset(Paths.PAWN_BP)


# ======================================================================
# 08 — Level
# ======================================================================

def generate_level(config: EchoConfig):
    """Create L_EchoPrototype with geometry driven by config values."""
    path = Paths.L_ECHO_PROTOTYPE
    if asset_exists(path):
        log_exists("L_EchoPrototype", path)
        return

    ensure_directory(path)

    try:
        editor_level_lib = unreal.EditorLevelLibrary
        level_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)

        if not level_subsystem.new_level(path):
            raise RuntimeError("new_level returned False")

        mi_echo = unreal.load_asset(Paths.MI_ECHO_MASTER)
        cube_mesh = unreal.load_asset("/Engine/BasicShapes/Cube")
        plane_mesh = unreal.load_asset("/Engine/BasicShapes/Plane")

        fs = config.floor_scale
        wh = config.wall_height

        # Derive wall position from floor scale (floor_scale * 100 / 2 = half-extent)
        half = fs * 50.0  # floor_scale=50 → 2500
        wall_z = wh * 0.5  # center walls at half height
        wall_h_scale = wh / 100.0  # wall_height=300 → scale 3

        # --- Floor ---
        floor = editor_level_lib.spawn_actor_from_class(
            unreal.StaticMeshActor, unreal.Vector(0, 0, 0)
        )
        if floor:
            floor.set_actor_label("Floor")
            mc = floor.static_mesh_component
            if plane_mesh:
                mc.set_static_mesh(plane_mesh)
            floor.set_actor_scale3d(unreal.Vector(fs, fs, 1))
            if mi_echo:
                mc.set_material(0, mi_echo)

        # --- Walls ---
        wall_configs = [
            ("Wall_North", unreal.Vector(0, half, wall_z),  unreal.Vector(fs, 1, wall_h_scale)),
            ("Wall_South", unreal.Vector(0, -half, wall_z), unreal.Vector(fs, 1, wall_h_scale)),
            ("Wall_East",  unreal.Vector(half, 0, wall_z),  unreal.Vector(1, fs, wall_h_scale)),
            ("Wall_West",  unreal.Vector(-half, 0, wall_z), unreal.Vector(1, fs, wall_h_scale)),
        ]
        for label, loc, scale in wall_configs:
            wall = editor_level_lib.spawn_actor_from_class(unreal.StaticMeshActor, loc)
            if wall:
                wall.set_actor_label(label)
                wmc = wall.static_mesh_component
                if cube_mesh:
                    wmc.set_static_mesh(cube_mesh)
                wall.set_actor_scale3d(scale)
                if mi_echo:
                    wmc.set_material(0, mi_echo)

        # --- Obstacles ---
        # Distribute obstacles in a rough grid within the arena
        num = config.num_obstacles
        obs_scale = config.obstacle_scale
        default_positions = [
            unreal.Vector(500, 300, 50),
            unreal.Vector(-400, -600, 50),
            unreal.Vector(800, -200, 50),
            unreal.Vector(-200, 700, 50),
        ]
        for i in range(num):
            pos = default_positions[i] if i < len(default_positions) else unreal.Vector(
                (i * 317) % int(half) - half / 2,
                (i * 541) % int(half) - half / 2,
                50,
            )
            obs = editor_level_lib.spawn_actor_from_class(unreal.StaticMeshActor, pos)
            if obs:
                obs.set_actor_label(f"Obstacle_{i}")
                omc = obs.static_mesh_component
                if cube_mesh:
                    omc.set_static_mesh(cube_mesh)
                obs.set_actor_scale3d(unreal.Vector(obs_scale, obs_scale, obs_scale))
                if mi_echo:
                    omc.set_material(0, mi_echo)

        # --- PlayerStart ---
        ps = editor_level_lib.spawn_actor_from_class(
            unreal.PlayerStart, unreal.Vector(0, 0, 100)
        )
        if ps:
            ps.set_actor_label("PlayerStart_Echo")

        # --- Directional Light ---
        lc = config.ambient_light_color
        dl = editor_level_lib.spawn_actor_from_class(
            unreal.DirectionalLight, unreal.Vector(0, 0, 500)
        )
        if dl:
            dl.set_actor_label("DimDirectionalLight")
            light_comp = dl.get_component_by_class(unreal.DirectionalLightComponent)
            if light_comp:
                light_comp.set_editor_property("intensity", config.ambient_light_intensity)
                light_comp.set_editor_property(
                    "light_color",
                    unreal.Color(int(lc[0]), int(lc[1]), int(lc[2]), 255),
                )

        unreal.EditorLevelLibrary.save_current_level()
        log_created("L_EchoPrototype", path)
        log_manual(
            "Level polish:\n"
            "  1. Add SkyLight (low intensity)\n"
            "  2. Add ExponentialHeightFog\n"
            "  3. Build nav mesh for AI\n"
            "  4. Add PostProcessVolume"
        )

    except Exception as e:
        unreal.log_error(f"[EchoGenerator] Level creation failed: {e}")
        log_manual("Create L_EchoPrototype manually (see 08_create_level.py)")


# ======================================================================
# 09 — Engine Config
# ======================================================================

def generate_engine_config(config: EchoConfig):
    """Update DefaultEngine.ini with GameDefaultMap and GlobalDefaultGameMode."""
    project_dir = unreal.Paths.project_dir()
    config_path = os.path.join(project_dir, "Config", "DefaultEngine.ini")

    if not os.path.exists(config_path):
        unreal.log_error(f"[EchoGenerator] DefaultEngine.ini not found: {config_path}")
        return

    with open(config_path, "r", encoding="utf-8") as f:
        content = f.read()

    modified = False

    # --- GameDefaultMap ---
    new_map_line = f"GameDefaultMap={Paths.L_ECHO_PROTOTYPE}"
    old_map_line = "GameDefaultMap=/Engine/Maps/Templates/OpenWorld"

    if old_map_line in content:
        content = content.replace(old_map_line, new_map_line)
        modified = True
    elif new_map_line not in content:
        section = "[/Script/EngineSettings.GameMapsSettings]"
        if section in content:
            lines = content.split("\n")
            new_lines = []
            in_section = False
            map_set = False
            for line in lines:
                if line.strip() == section:
                    in_section = True
                    new_lines.append(line)
                    continue
                if in_section and line.startswith("GameDefaultMap="):
                    new_lines.append(new_map_line)
                    map_set = True
                    in_section = False
                    continue
                if in_section and line.startswith("["):
                    if not map_set:
                        new_lines.append(new_map_line)
                        map_set = True
                    in_section = False
                new_lines.append(line)
            content = "\n".join(new_lines)
            modified = True

    # --- GlobalDefaultGameMode ---
    gm_class_path = f"{Paths.GAME_MODE_BP}.BP_EchoGameMode_C"
    gm_line = f"GlobalDefaultGameMode={gm_class_path}"

    if gm_line not in content:
        lines = content.split("\n")
        new_lines = []
        gm_set = False
        for line in lines:
            if line.startswith("GlobalDefaultGameMode="):
                new_lines.append(gm_line)
                gm_set = True
                continue
            new_lines.append(line)

        if not gm_set:
            final = []
            for line in new_lines:
                final.append(line)
                if line.startswith("GameDefaultMap="):
                    final.append(gm_line)
            new_lines = final

        content = "\n".join(new_lines)
        modified = True

    if modified:
        with open(config_path, "w", encoding="utf-8") as f:
            f.write(content)
        log_created("DefaultEngine.ini updates", config_path)
    else:
        unreal.log("[EchoGenerator] DefaultEngine.ini already up to date")
