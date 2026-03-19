"""
06_create_material.py — Create/Repair Material Instances with EchoColor.
"""

import unreal
import importlib
import helpers

importlib.reload(helpers)
from helpers import Paths, BASE, asset_exists, ensure_directory, save_asset


def run():
    # World: WorldSpace, Masked by Sonar, Vibrant Blue
    _setup_instance(Paths.MI_ECHO_MASTER, "MI_EchoMaster",
                    is_actor=False, is_player=False, use_flux=True,
                    echo_color=unreal.LinearColor(0.0, 200.0, 800.0, 1.0))
    # Obstacle: WorldSpace, Masked by Sonar, Vivid Purple
    _setup_instance(Paths.MI_ECHO_OBSTACLE, "MI_EchoObstacle",
                    is_actor=False, is_player=False, use_flux=True,
                    echo_color=unreal.LinearColor(400.0, 0.0, 800.0, 1.0))
    # Enemy: LocalSpace, Masked by Sonar, Hot Red
    _setup_instance(Paths.MI_ECHO_ENEMY, "MI_EchoEnemy",
                    is_actor=True, is_player=False, use_flux=True,
                    echo_color=unreal.LinearColor(800.0, 50.0, 0.0, 1.0))
    # Player: LocalSpace, Always Visible, Bright Green
    _setup_instance(Paths.MI_ECHO_PLAYER, "MI_EchoPlayer",
                    is_actor=True, is_player=True, use_flux=True,
                    echo_color=unreal.LinearColor(0.0, 800.0, 100.0, 1.0))


def _setup_instance(path, name, is_actor=False, is_player=False, use_flux=False, echo_color=None):
    parent = unreal.load_asset(Paths.M_ECHO_MASTER)
    if not parent:
        return

    mi = unreal.load_asset(path)
    if not mi:
        ensure_directory(path)
        dir, asset = path.rsplit("/", 1)
        mi = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            asset, dir, unreal.MaterialInstanceConstant,
            unreal.MaterialInstanceConstantFactoryNew())

    if mi:
        mi.set_editor_property("parent", parent)
        mel = unreal.MaterialEditingLibrary
        mel.set_material_instance_static_switch_parameter_value(mi, "IsActor", is_actor)
        mel.set_material_instance_static_switch_parameter_value(mi, "IsPlayer", is_player)
        mel.set_material_instance_static_switch_parameter_value(mi, "UseFluxLook", use_flux)
        if echo_color:
            mel.set_material_instance_vector_parameter_value(mi, "EchoColor", echo_color)
        save_asset(path)
        unreal.log(f"Saved {name} (IsActor={is_actor}, IsPlayer={is_player}, UseFluxLook={use_flux})")


if __name__ == "__main__":
    run()
