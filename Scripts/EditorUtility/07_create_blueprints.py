"""
07_create_blueprints.py — Create Blueprint assets for core gameplay classes.

Depends on: all prior scripts (01-06)

Creates:
  BP_EchoGameMode       (parent: AEchoGameMode)
  BP_EchoPlayerController (parent: AEchoPlayerController)
  BP_EchoPawn           (parent: AEchoPawn)

Wires CDO properties to reference the assets created by earlier scripts.
"""

import unreal
from helpers import (
    Paths, CppClasses, asset_exists, ensure_directory,
    save_asset, log_created, log_exists, log_manual
)


def run():
    _create_game_mode_bp()
    _create_player_controller_bp()
    _create_pawn_bp()


def _create_blueprint(path: str, asset_name: str, parent_class_path: str):
    """
    Create a Blueprint asset with the given C++ parent class.
    Returns the Blueprint asset or None.
    """
    if asset_exists(path):
        log_exists(asset_name, path)
        return unreal.load_asset(path)

    ensure_directory(path)

    # Load the C++ parent class
    parent_class = unreal.load_object(None, parent_class_path)
    if parent_class is None:
        unreal.log_error(f"[EchoSetup] Could not load parent class: {parent_class_path}")
        return None

    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    directory = path.rsplit("/", 1)[0]
    name = path.rsplit("/", 1)[1]

    factory = unreal.BlueprintFactory()
    factory.set_editor_property("parent_class", parent_class)

    bp = asset_tools.create_asset(name, directory, unreal.Blueprint, factory)

    if bp is None:
        unreal.log_error(f"[EchoSetup] Failed to create Blueprint {asset_name}")
        return None

    log_created(asset_name, path)
    return bp


def _get_cdo(bp):
    """Get the Class Default Object from a Blueprint."""
    if bp is None:
        return None
    try:
        gen_class = bp.generated_class()
        if gen_class is not None:
            return unreal.get_default_object(gen_class)
    except Exception:
        pass
    return None


def _create_game_mode_bp():
    """Create BP_EchoGameMode and wire default pawn/controller classes."""
    bp = _create_blueprint(
        Paths.GAME_MODE_BP,
        "BP_EchoGameMode",
        CppClasses.ECHO_GAME_MODE
    )

    cdo = _get_cdo(bp)
    if cdo is None:
        log_manual("Open BP_EchoGameMode and set DefaultPawnClass, PlayerControllerClass manually")
        save_asset(Paths.GAME_MODE_BP)
        return

    try:
        # Set default pawn class to BP_EchoPawn
        pawn_bp = unreal.load_asset(Paths.PAWN_BP)
        if pawn_bp is not None:
            pawn_class = pawn_bp.generated_class()
            if pawn_class:
                cdo.set_editor_property("default_pawn_class", pawn_class)
        else:
            log_manual("Set BP_EchoGameMode.DefaultPawnClass → BP_EchoPawn")

        # Set player controller class to BP_EchoPlayerController
        pc_bp = unreal.load_asset(Paths.PLAYER_CONTROLLER_BP)
        if pc_bp is not None:
            pc_class = pc_bp.generated_class()
            if pc_class:
                cdo.set_editor_property("player_controller_class", pc_class)
        else:
            log_manual("Set BP_EchoGameMode.PlayerControllerClass → BP_EchoPlayerController")

        # Wire the RippleManager component's MPC and curves
        # RippleManager is a C++ component on the GameMode — access it via CDO
        ripple_mgr = cdo.get_editor_property("RippleManager")
        if ripple_mgr is not None:
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
            log_manual(
                "Open BP_EchoGameMode → RippleManager component and set:\n"
                "  EchoMPC → MPC_GlobalSound\n"
                "  RippleRadiusCurve → C_RippleRadius\n"
                "  RippleIntensityCurve → C_RippleIntensity"
            )

    except Exception as e:
        unreal.log_warning(f"[EchoSetup] Error wiring BP_EchoGameMode CDO: {e}")
        log_manual(
            "Open BP_EchoGameMode and set:\n"
            "  DefaultPawnClass → BP_EchoPawn\n"
            "  PlayerControllerClass → BP_EchoPlayerController\n"
            "  RippleManager.EchoMPC → MPC_GlobalSound\n"
            "  RippleManager.RippleRadiusCurve → C_RippleRadius\n"
            "  RippleManager.RippleIntensityCurve → C_RippleIntensity"
        )

    save_asset(Paths.GAME_MODE_BP)


def _create_player_controller_bp():
    """Create BP_EchoPlayerController and wire DefaultMappingContext."""
    bp = _create_blueprint(
        Paths.PLAYER_CONTROLLER_BP,
        "BP_EchoPlayerController",
        CppClasses.ECHO_PLAYER_CONTROLLER
    )

    cdo = _get_cdo(bp)
    if cdo is None:
        log_manual("Open BP_EchoPlayerController and set DefaultMappingContext → IMC_EchoDefault")
        save_asset(Paths.PLAYER_CONTROLLER_BP)
        return

    try:
        imc = unreal.load_asset(Paths.IMC_ECHO_DEFAULT)
        if imc:
            cdo.set_editor_property("DefaultMappingContext", imc)
        else:
            log_manual("Set BP_EchoPlayerController.DefaultMappingContext → IMC_EchoDefault")
    except Exception as e:
        unreal.log_warning(f"[EchoSetup] Error wiring BP_EchoPlayerController CDO: {e}")
        log_manual("Set BP_EchoPlayerController.DefaultMappingContext → IMC_EchoDefault")

    save_asset(Paths.PLAYER_CONTROLLER_BP)


def _create_pawn_bp():
    """Create BP_EchoPawn and wire input actions + feedback assets."""
    bp = _create_blueprint(
        Paths.PAWN_BP,
        "BP_EchoPawn",
        CppClasses.ECHO_PAWN
    )

    cdo = _get_cdo(bp)
    if cdo is None:
        log_manual(
            "Open BP_EchoPawn and set:\n"
            "  IA_Move, IA_Look, IA_Slam input action references\n"
            "  FeedbackComponent: DropShake, SlamShake, DropForceFeedback, SlamForceFeedback"
        )
        save_asset(Paths.PAWN_BP)
        return

    try:
        # Wire input actions
        ia_move = unreal.load_asset(Paths.IA_MOVE)
        if ia_move:
            cdo.set_editor_property("IA_Move", ia_move)

        ia_look = unreal.load_asset(Paths.IA_LOOK)
        if ia_look:
            cdo.set_editor_property("IA_Look", ia_look)

        ia_slam = unreal.load_asset(Paths.IA_SLAM)
        if ia_slam:
            cdo.set_editor_property("IA_Slam", ia_slam)

        # Wire feedback component assets
        feedback = cdo.get_editor_property("FeedbackComponent")
        if feedback is not None:
            # Camera shakes are TSubclassOf — need to load the BP class
            drop_shake_bp = unreal.load_asset(Paths.CS_DROP_SHAKE)
            if drop_shake_bp:
                feedback.set_editor_property("DropShake", drop_shake_bp.generated_class())

            slam_shake_bp = unreal.load_asset(Paths.CS_SLAM_SHAKE)
            if slam_shake_bp:
                feedback.set_editor_property("SlamShake", slam_shake_bp.generated_class())

            # Force feedback effects are UObject references
            drop_ffe = unreal.load_asset(Paths.FFE_DROP_FEEDBACK)
            if drop_ffe:
                feedback.set_editor_property("DropForceFeedback", drop_ffe)

            slam_ffe = unreal.load_asset(Paths.FFE_SLAM_FEEDBACK)
            if slam_ffe:
                feedback.set_editor_property("SlamForceFeedback", slam_ffe)
        else:
            log_manual(
                "Open BP_EchoPawn → FeedbackComponent and set:\n"
                "  DropShake → CS_DropShake\n"
                "  SlamShake → CS_SlamShake\n"
                "  DropForceFeedback → FFE_DropFeedback\n"
                "  SlamForceFeedback → FFE_SlamFeedback"
            )

        # Set the cube mesh to engine default cube
        try:
            mesh_comp = cdo.get_editor_property("CubeMesh")
            if mesh_comp:
                cube_mesh = unreal.load_asset("/Engine/BasicShapes/Cube")
                if cube_mesh:
                    mesh_comp.set_editor_property("static_mesh", cube_mesh)
        except Exception:
            log_manual("Set BP_EchoPawn.CubeMesh StaticMesh to /Engine/BasicShapes/Cube")

    except Exception as e:
        unreal.log_warning(f"[EchoSetup] Error wiring BP_EchoPawn CDO: {e}")
        log_manual(
            "Open BP_EchoPawn and set:\n"
            "  IA_Move, IA_Look, IA_Slam → corresponding input action assets\n"
            "  FeedbackComponent → CS_DropShake, CS_SlamShake, FFE_DropFeedback, FFE_SlamFeedback\n"
            "  CubeMesh → /Engine/BasicShapes/Cube"
        )

    save_asset(Paths.PAWN_BP)


if __name__ == "__main__":
    run()
