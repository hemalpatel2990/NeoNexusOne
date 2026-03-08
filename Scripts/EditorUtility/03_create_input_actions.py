"""
03_create_input_actions.py — Create Enhanced Input Action assets.

  IA_Move: Axis2D (WASD / left stick)
  IA_Look: Axis2D (mouse delta / right stick)
  IA_Slam: Digital/Bool (spacebar / gamepad face button)
"""

import unreal
from helpers import Paths, asset_exists, ensure_directory, save_asset, log_created, log_exists


def _create_input_action(path: str, asset_name: str, value_type):
    """Create a single UInputAction asset with the specified value type."""
    if asset_exists(path):
        log_exists(asset_name, path)
        return

    ensure_directory(path)

    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    directory = path.rsplit("/", 1)[0]
    name = path.rsplit("/", 1)[1]

    # UE5 Enhanced Input factory uses underscore naming convention
    factory = unreal.InputAction_Factory()
    action = asset_tools.create_asset(name, directory, None, factory)

    if action is None:
        unreal.log_error(f"[EchoSetup] Failed to create {asset_name}")
        return

    # Set the value type
    action.set_editor_property("value_type", value_type)

    save_asset(path)
    log_created(asset_name, path)


def run():
    # IA_Move — Axis2D for directional movement
    _create_input_action(
        Paths.IA_MOVE,
        "IA_Move",
        unreal.InputActionValueType.AXIS2D
    )

    # IA_Look — Axis2D for camera look
    _create_input_action(
        Paths.IA_LOOK,
        "IA_Look",
        unreal.InputActionValueType.AXIS2D
    )

    # IA_Slam — Digital (boolean press)
    _create_input_action(
        Paths.IA_SLAM,
        "IA_Slam",
        unreal.InputActionValueType.BOOLEAN
    )


if __name__ == "__main__":
    run()
