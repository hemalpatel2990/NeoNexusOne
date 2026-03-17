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
    path = Paths.MPC_GLOBAL_SOUND

    mpc = unreal.load_asset(path)
    if not mpc:
        ensure_directory(path)
        factory = unreal.MaterialParameterCollectionFactoryNew()
        asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
        directory, asset_name = path.rsplit("/", 1)
        mpc = asset_tools.create_asset(asset_name, directory, unreal.MaterialParameterCollection, factory)

    if not mpc:
        unreal.log_error("[EchoSetup] Failed to load/create MPC_GlobalSound")
        return

    # Add parameters if they don't exist
    vec_params = mpc.get_editor_property("vector_parameters")
    scalar_params = mpc.get_editor_property("scalar_parameters")

    def ensure_scalar(name, default=0.0):
        if not any(p.get_editor_property("parameter_name") == name for p in scalar_params):
            p = unreal.CollectionScalarParameter()
            p.set_editor_property("parameter_name", name)
            p.set_editor_property("default_value", default)
            scalar_params.append(p)
            unreal.log(f"[EchoSetup] Added scalar parameter: {name}")

    def ensure_vector(name, default=unreal.LinearColor()):
        if not any(p.get_editor_property("parameter_name") == name for p in vec_params):
            p = unreal.CollectionVectorParameter()
            p.set_editor_property("parameter_name", name)
            p.set_editor_property("default_value", default)
            vec_params.append(p)
            unreal.log(f"[EchoSetup] Added vector parameter: {name}")

    ensure_vector(MPCParams.LAST_IMPACT_LOCATION)
    ensure_vector(MPCParams.PLAYER_WORLD_POSITION)
    ensure_scalar(MPCParams.CURRENT_RIPPLE_RADIUS)
    ensure_scalar(MPCParams.RIPPLE_INTENSITY)
    ensure_scalar(MPCParams.RIPPLE_START_TIME)

    mpc.set_editor_property("vector_parameters", vec_params)
    mpc.set_editor_property("scalar_parameters", scalar_params)

    save_asset(path)
    log_created("MPC_GlobalSound (Updated)", path)


if __name__ == "__main__":
    run()
