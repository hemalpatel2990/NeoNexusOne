"""
01_create_mpc.py — Create MPC_GlobalSound Material Parameter Collection.

Parameters (matching EchoMPCParams in EchoTypes.h):
  - LastImpactLocation (Vector, default 0,0,0)
  - CurrentRippleRadius (Scalar, default 0)
  - RippleIntensity (Scalar, default 0)
"""

import unreal
from helpers import Paths, MPCParams, asset_exists, ensure_directory, save_asset, log_created, log_exists


def run():
    path = Paths.MPC_GLOBAL_SOUND

    if asset_exists(path):
        log_exists("MPC_GlobalSound", path)
        return

    ensure_directory(path)

    # Create the MPC asset via AssetTools
    factory = unreal.MaterialParameterCollectionFactoryNew()
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()

    # Extract directory and asset name from path
    directory = path.rsplit("/", 1)[0]
    asset_name = path.rsplit("/", 1)[1]

    mpc = asset_tools.create_asset(asset_name, directory, unreal.MaterialParameterCollection, factory)

    if mpc is None:
        unreal.log_error("[EchoSetup] Failed to create MPC_GlobalSound")
        return

    # Add vector parameter: LastImpactLocation
    vec_param = unreal.CollectionVectorParameter()
    vec_param.set_editor_property("parameter_name", MPCParams.LAST_IMPACT_LOCATION)
    vec_param.set_editor_property("default_value", unreal.LinearColor(0.0, 0.0, 0.0, 0.0))
    mpc.get_editor_property("vector_parameters").append(vec_param)

    # Add scalar parameters
    radius_param = unreal.CollectionScalarParameter()
    radius_param.set_editor_property("parameter_name", MPCParams.CURRENT_RIPPLE_RADIUS)
    radius_param.set_editor_property("default_value", 0.0)
    mpc.get_editor_property("scalar_parameters").append(radius_param)

    intensity_param = unreal.CollectionScalarParameter()
    intensity_param.set_editor_property("parameter_name", MPCParams.RIPPLE_INTENSITY)
    intensity_param.set_editor_property("default_value", 0.0)
    mpc.get_editor_property("scalar_parameters").append(intensity_param)

    save_asset(path)
    log_created("MPC_GlobalSound", path)


if __name__ == "__main__":
    run()
