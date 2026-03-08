"""
09_update_config.py — Update DefaultEngine.ini with GameDefaultMap and GlobalDefaultGameMode.

Depends on: 07_create_blueprints.py, 08_create_level.py

Sets:
  GameDefaultMap → /Game/EchoLocation/Maps/L_EchoPrototype
  GlobalDefaultGameMode → BP_EchoGameMode class path
"""

import os
import unreal
from helpers import Paths, log_created, log_manual


def run():
    # Resolve project config path
    project_dir = unreal.Paths.project_dir()
    config_path = os.path.join(project_dir, "Config", "DefaultEngine.ini")

    if not os.path.exists(config_path):
        unreal.log_error(f"[EchoSetup] DefaultEngine.ini not found at: {config_path}")
        return

    # Read existing content
    with open(config_path, "r", encoding="utf-8") as f:
        content = f.read()

    modified = False

    # --- Update GameDefaultMap ---
    old_map_line = "GameDefaultMap=/Engine/Maps/Templates/OpenWorld"
    new_map_line = f"GameDefaultMap={Paths.L_ECHO_PROTOTYPE}"

    if old_map_line in content:
        content = content.replace(old_map_line, new_map_line)
        modified = True
        unreal.log(f"[EchoSetup] Updated GameDefaultMap → {Paths.L_ECHO_PROTOTYPE}")
    elif new_map_line in content:
        unreal.log("[EchoSetup] GameDefaultMap already set correctly")
    else:
        # GameDefaultMap line might have been changed to something else — add/replace
        unreal.log_warning("[EchoSetup] GameDefaultMap line not found in expected form. Adding it.")
        # Find the [/Script/EngineSettings.GameMapsSettings] section and add after it
        section = "[/Script/EngineSettings.GameMapsSettings]"
        if section in content:
            # Replace any existing GameDefaultMap line in that section
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
                    # New section started without finding GameDefaultMap
                    if not map_set:
                        new_lines.append(new_map_line)
                        map_set = True
                    in_section = False
                new_lines.append(line)
            content = "\n".join(new_lines)
            modified = True

    # --- Add GlobalDefaultGameMode ---
    game_mode_class_path = f"{Paths.GAME_MODE_BP}.BP_EchoGameMode_C"
    global_gm_line = f"GlobalDefaultGameMode={game_mode_class_path}"

    if global_gm_line in content:
        unreal.log("[EchoSetup] GlobalDefaultGameMode already set correctly")
    else:
        # Add GlobalDefaultGameMode under GameMapsSettings section
        section = "[/Script/EngineSettings.GameMapsSettings]"
        if section in content:
            # Check if there's an existing GlobalDefaultGameMode line to replace
            lines = content.split("\n")
            new_lines = []
            gm_set = False
            for line in lines:
                if line.startswith("GlobalDefaultGameMode="):
                    new_lines.append(global_gm_line)
                    gm_set = True
                    continue
                new_lines.append(line)

            if not gm_set:
                # Insert after the GameDefaultMap line
                final_lines = []
                for line in new_lines:
                    final_lines.append(line)
                    if line.startswith("GameDefaultMap="):
                        final_lines.append(global_gm_line)
                new_lines = final_lines

            content = "\n".join(new_lines)
            modified = True
            unreal.log(f"[EchoSetup] Added GlobalDefaultGameMode → {game_mode_class_path}")

    # --- Write back ---
    if modified:
        with open(config_path, "w", encoding="utf-8") as f:
            f.write(content)
        log_created("DefaultEngine.ini updates", config_path)
    else:
        unreal.log("[EchoSetup] DefaultEngine.ini already up to date")


if __name__ == "__main__":
    run()
