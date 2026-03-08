"""
04_create_input_mapping.py — Create IMC_EchoDefault Input Mapping Context.

Depends on: 03_create_input_actions.py (IA_Move, IA_Look, IA_Slam must exist)

Binds:
  IA_Move  → W/A/S/D with Swizzle+Negate modifiers, Left Stick
  IA_Look  → Mouse2D, Right Stick
  IA_Slam  → Spacebar, Gamepad Face Button Bottom
"""

import unreal
from helpers import Paths, asset_exists, ensure_directory, save_asset, log_created, log_exists, log_manual


def run():
    path = Paths.IMC_ECHO_DEFAULT

    if asset_exists(path):
        log_exists("IMC_EchoDefault", path)
        return

    ensure_directory(path)

    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    directory = path.rsplit("/", 1)[0]
    name = path.rsplit("/", 1)[1]

    factory = unreal.InputMappingContext_Factory()
    imc = asset_tools.create_asset(name, directory, None, factory)

    if imc is None:
        unreal.log_error("[EchoSetup] Failed to create IMC_EchoDefault")
        return

    # Load the input actions
    ia_move = unreal.load_asset(Paths.IA_MOVE)
    ia_look = unreal.load_asset(Paths.IA_LOOK)
    ia_slam = unreal.load_asset(Paths.IA_SLAM)

    if not all([ia_move, ia_look, ia_slam]):
        unreal.log_error("[EchoSetup] Input actions not found. Run 03_create_input_actions.py first.")
        return

    try:
        # --- IA_Move mappings ---
        # W = forward (+Y) — needs Swizzle YXZ to map axis1D → Y component
        w_mapping = imc.map_key(ia_move, unreal.Key("W"))
        w_mapping.add_modifier(unreal.InputModifierSwizzleAxis())

        # S = backward (-Y) — Swizzle + Negate
        s_mapping = imc.map_key(ia_move, unreal.Key("S"))
        s_mapping.add_modifier(unreal.InputModifierSwizzleAxis())
        s_mapping.add_modifier(unreal.InputModifierNegate())

        # D = right (+X) — raw axis1D maps to X by default
        imc.map_key(ia_move, unreal.Key("D"))

        # A = left (-X) — Negate
        a_mapping = imc.map_key(ia_move, unreal.Key("A"))
        a_mapping.add_modifier(unreal.InputModifierNegate())

        # Left Stick (Gamepad)
        imc.map_key(ia_move, unreal.Key("Gamepad_Left2D"))

        # --- IA_Look mappings ---
        imc.map_key(ia_look, unreal.Key("Mouse2D"))
        imc.map_key(ia_look, unreal.Key("Gamepad_Right2D"))

        # --- IA_Slam mappings ---
        imc.map_key(ia_slam, unreal.Key("SpaceBar"))
        imc.map_key(ia_slam, unreal.Key("Gamepad_FaceButton_Bottom"))

        save_asset(path)
        log_created("IMC_EchoDefault", path)

    except Exception as e:
        # Key mapping API may differ across UE5 versions
        unreal.log_warning(f"[EchoSetup] IMC key binding automation failed: {e}")
        save_asset(path)
        log_created("IMC_EchoDefault (empty — needs manual bindings)", path)
        log_manual(
            "Open IMC_EchoDefault and add key mappings manually:\n"
            "  IA_Move: W (Swizzle YXZ), S (Swizzle YXZ + Negate), D, A (Negate), Gamepad Left Stick\n"
            "  IA_Look: Mouse2D, Gamepad Right Stick\n"
            "  IA_Slam: SpaceBar, Gamepad Face Button Bottom"
        )


if __name__ == "__main__":
    run()
