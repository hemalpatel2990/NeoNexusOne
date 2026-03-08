"""
06_create_material.py — Create M_EchoMaster material and MI_EchoMaster instance.

Depends on: 01_create_mpc.py (MPC_GlobalSound must exist)

M_EchoMaster:
  - Domain: Surface
  - Blend Mode: Opaque
  - Shading Model: Default Lit (emissive-driven visibility)
  - Dark base color (near-black)
  - The SphereMask node graph must be built manually in the Material Editor

MI_EchoMaster:
  - Material Instance of M_EchoMaster
  - Used on level geometry
"""

import unreal
from helpers import Paths, asset_exists, ensure_directory, save_asset, log_created, log_exists, log_manual


def run():
    _create_master_material()
    _create_material_instance()


def _create_master_material():
    """Create M_EchoMaster — empty material with correct settings."""
    path = Paths.M_ECHO_MASTER

    if asset_exists(path):
        log_exists("M_EchoMaster", path)
        return

    ensure_directory(path)

    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    directory = path.rsplit("/", 1)[0]
    name = path.rsplit("/", 1)[1]

    factory = unreal.MaterialFactoryNew()
    material = asset_tools.create_asset(name, directory, unreal.Material, factory)

    if material is None:
        unreal.log_error("[EchoSetup] Failed to create M_EchoMaster")
        return

    # Set material properties
    try:
        material.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_DEFAULT_LIT)
        material.set_editor_property("blend_mode", unreal.BlendMode.BLEND_OPAQUE)
        # Two-sided off (default), fully rough for performance
        material.set_editor_property("two_sided", False)
    except Exception as e:
        unreal.log_warning(f"[EchoSetup] Could not set all material properties: {e}")

    save_asset(path)
    log_created("M_EchoMaster", path)

    log_manual(
        "Build the M_EchoMaster node graph in Material Editor:\n"
        "  1. Add MPC_GlobalSound collection parameter nodes\n"
        "  2. SphereMask: Center=LastImpactLocation, Radius=CurrentRippleRadius, Hardness=~80\n"
        "  3. Multiply SphereMask × RippleIntensity\n"
        "  4. Use result for Emissive Color (white × mask)\n"
        "  5. Base Color: very dark grey (0.02, 0.02, 0.02)\n"
        "  6. SmoothStep the mask edges for ring-shaped reveal"
    )


def _create_material_instance():
    """Create MI_EchoMaster — material instance of M_EchoMaster."""
    path = Paths.MI_ECHO_MASTER

    if asset_exists(path):
        log_exists("MI_EchoMaster", path)
        return

    # Parent material must exist
    parent = unreal.load_asset(Paths.M_ECHO_MASTER)
    if parent is None:
        unreal.log_error("[EchoSetup] M_EchoMaster not found. Run 06 after 01.")
        return

    ensure_directory(path)

    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    directory = path.rsplit("/", 1)[0]
    name = path.rsplit("/", 1)[1]

    factory = unreal.MaterialInstanceConstantFactoryNew()
    mi = asset_tools.create_asset(name, directory, unreal.MaterialInstanceConstant, factory)

    if mi is None:
        unreal.log_error("[EchoSetup] Failed to create MI_EchoMaster")
        return

    # Set parent material on the created instance (not on the factory)
    mi.set_editor_property("parent", parent)

    save_asset(path)
    log_created("MI_EchoMaster", path)


if __name__ == "__main__":
    run()
