"""
01_create_mpc.py — Create MPC_GlobalSound Material Parameter Collection.

Parameters (matching EchoMPCParams in EchoTypes.h):
  - LastImpactLocation (Vector, default 0,0,0)
  - CurrentRippleRadius (Scalar, default 0)
  - RippleIntensity (Scalar, default 0)
"""

import unreal
import os
import sys
import importlib

try:
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    SCRIPT_DIR = os.path.join(unreal.Paths.project_dir(), "Scripts", "EditorUtility").replace("\\", "/")

if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import helpers
importlib.reload(helpers)
from helpers import Paths, MPCParams, asset_exists, ensure_directory, save_asset, log_created


def run():
    eal = unreal.EditorAssetLibrary
    path = Paths.MPC_GLOBAL_SOUND

    # Delete material instances and parent material FIRST to prevent render-thread
    # crash when MPC layout changes while compiled shaders still reference old layout.
    dependents = [Paths.MI_ECHO_MASTER, Paths.MI_ECHO_ENEMY, Paths.MI_ECHO_PLAYER, Paths.M_ECHO_MASTER]
    for dep in dependents:
        if eal.does_asset_exist(dep):
            eal.delete_asset(dep)
            unreal.log(f"[EchoSetup] Deleted {dep} (will be rebuilt by scripts 13/06)")

    # Delete and recreate the MPC from scratch for a clean layout
    if eal.does_asset_exist(path):
        eal.delete_asset(path)
        unreal.log("[EchoSetup] Deleted old MPC_GlobalSound")

    ensure_directory(path)
    factory = unreal.MaterialParameterCollectionFactoryNew()
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    directory, asset_name = path.rsplit("/", 1)
    mpc = asset_tools.create_asset(asset_name, directory, unreal.MaterialParameterCollection, factory)

    if not mpc:
        unreal.log_error("[EchoSetup] Failed to create MPC_GlobalSound")
        return

    # Build exact parameter lists
    def make_vector(name, default=unreal.LinearColor()):
        p = unreal.CollectionVectorParameter()
        p.set_editor_property("parameter_name", name)
        p.set_editor_property("default_value", default)
        return p

    def make_scalar(name, default=0.0):
        p = unreal.CollectionScalarParameter()
        p.set_editor_property("parameter_name", name)
        p.set_editor_property("default_value", default)
        return p

    vec_params = [
        make_vector(MPCParams.LAST_IMPACT_LOCATION),
        make_vector(MPCParams.PLAYER_WORLD_POSITION),
    ]
    scalar_params = [
        make_scalar(MPCParams.CURRENT_RIPPLE_RADIUS),
        make_scalar(MPCParams.RIPPLE_INTENSITY),
        make_scalar(MPCParams.RIPPLE_START_TIME),
        make_scalar(MPCParams.PROXIMITY_INTERFERENCE),
        make_scalar(MPCParams.SIGNAL_INTENSITY),
    ]

    mpc.set_editor_property("vector_parameters", vec_params)
    mpc.set_editor_property("scalar_parameters", scalar_params)
    unreal.log(f"[EchoSetup] Created MPC with {len(vec_params)} vector, {len(scalar_params)} scalar parameters")

    save_asset(path)
    log_created("MPC_GlobalSound (Fresh)", path)


if __name__ == "__main__":
    run()
