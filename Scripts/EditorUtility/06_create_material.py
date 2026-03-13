"""
06_create_material.py — Repair Material Instances with Refined Logic.
"""

import unreal
import importlib
import helpers

importlib.reload(helpers)
from helpers import Paths, BASE, asset_exists, ensure_directory, save_asset

def run():
    # World: WorldSpace, Masked by Sonar
    _setup_instance(Paths.MI_ECHO_MASTER, "MI_EchoMaster", is_actor=False, is_player=False, use_flux=False)
    # Enemy: LocalSpace, Masked by Sonar
    _setup_instance(Paths.MI_ECHO_ENEMY, "MI_EchoEnemy", is_actor=True, is_player=False, use_flux=False)
    # Player: LocalSpace, Always Visible
    _setup_instance(Paths.MI_ECHO_PLAYER, "MI_EchoPlayer", is_actor=True, is_player=True, use_flux=False)

def _setup_instance(path, name, is_actor=False, is_player=False, use_flux=False):
    parent = unreal.load_asset(Paths.M_ECHO_MASTER)
    if not parent: return
    
    mi = unreal.load_asset(path)
    if not mi:
        ensure_directory(path)
        dir, asset = path.rsplit("/", 1)
        mi = unreal.AssetToolsHelpers.get_asset_tools().create_asset(asset, dir, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())

    if mi:
        mi.set_editor_property("parent", parent)
        unreal.MaterialEditingLibrary.set_material_instance_static_switch_parameter_value(mi, "IsActor", is_actor)
        unreal.MaterialEditingLibrary.set_material_instance_static_switch_parameter_value(mi, "IsPlayer", is_player)
        unreal.MaterialEditingLibrary.set_material_instance_static_switch_parameter_value(mi, "UseFluxLook", use_flux)
        save_asset(path)
        unreal.log(f"Saved {name} (IsActor={is_actor}, IsPlayer={is_player}, UseFluxLook={use_flux})")

if __name__ == "__main__":
    run()
