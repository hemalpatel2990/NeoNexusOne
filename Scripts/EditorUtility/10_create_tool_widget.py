"""
10_create_tool_widget.py — Create Editor Utility Widget + Tools menu entries.

Creates:
  - EUW_EchoAssetGenerator (Editor Utility Widget Blueprint)
  - Tools > Echo Location > Generate Assets
  - Tools > Echo Location > Edit Config (JSON)
  - Tools > Echo Location > Reset to Defaults

Usage (from UE5 Output Log Cmd console):
    py "D:/Users/hemal/Documents/Unreal Projects/NeoNexusOne/Scripts/EditorUtility/10_create_tool_widget.py"

Or run via 00_run_all.py (which will include this in the pipeline).
"""

import os
import sys
import subprocess

import unreal

# Ensure our script directory is on the path
try:
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    SCRIPT_DIR = os.path.join(unreal.Paths.project_dir(), "Scripts", "EditorUtility")
    SCRIPT_DIR = SCRIPT_DIR.replace("\\", "/")

if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from helpers import Paths, ensure_directory, save_asset, log_created, log_exists, asset_exists, log_manual
from echo_config import EchoConfig, get_config_path


# ======================================================================
# EUW Blueprint Creation
# ======================================================================

def _create_euw_blueprint():
    """
    Create an empty Editor Utility Widget Blueprint at the Tools path.
    The actual widget layout (DetailsView + Generate button) must be designed
    in the UMG Widget Editor after creation.
    """
    path = Paths.EUW_ASSET_GENERATOR
    if asset_exists(path):
        log_exists("EUW_EchoAssetGenerator", path)
        return

    ensure_directory(path)

    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    directory, name = path.rsplit("/", 1)

    try:
        factory = unreal.BlueprintFactory()
        # EditorUtilityWidget is the base class for Editor Utility Widgets
        parent_class = getattr(unreal, "EditorUtilityWidget", None)
        if parent_class is None:
            unreal.log_warning(
                "[EchoTool] EditorUtilityWidget class not found. "
                "Ensure the Blutility / Editor Scripting Utilities plugin is enabled."
            )
            return

        factory.set_editor_property("parent_class", parent_class)
        bp = asset_tools.create_asset(name, directory, unreal.Blueprint, factory)

        if bp is None:
            unreal.log_error("[EchoTool] Failed to create EUW_EchoAssetGenerator")
            return

        save_asset(path)
        log_created("EUW_EchoAssetGenerator", path)

        log_manual(
            "Design the EUW_EchoAssetGenerator widget in the Widget Editor:\n"
            "  1. Open EUW_EchoAssetGenerator in the Content Browser\n"
            "  2. Add a DetailsView widget — bind it to an EchoConfig UObject\n"
            "     (or use a simple property list reading echo_config.json)\n"
            "  3. Add a 'Generate Assets' Button with OnClicked calling\n"
            "     Execute Python Script: echo_generator.generate_all()\n"
            "  4. Optionally add 'Reset to Defaults' and 'Open Config' buttons"
        )

    except Exception as e:
        unreal.log_warning(f"[EchoTool] EUW creation failed: {e}")
        log_manual("Create EUW_EchoAssetGenerator manually as an Editor Utility Widget Blueprint")


# ======================================================================
# Tools Menu Registration
# ======================================================================

def _register_tools_menu():
    """Register Tools > Echo Location menu entries via ToolMenus API."""
    tool_menus = unreal.ToolMenus.get()

    # Get or extend the main LevelEditor Tools menu
    main_menu = tool_menus.find_menu("LevelEditor.MainMenu.Tools")
    if main_menu is None:
        unreal.log_warning("[EchoTool] Could not find LevelEditor.MainMenu.Tools menu")
        return

    # Add a section for our entries
    section_name = "EchoLocation"

    # --- Generate Assets ---
    entry_generate = unreal.ToolMenuEntry(
        name="EchoLocation_Generate",
        type=unreal.MultiBlockType.MENU_ENTRY,
    )
    entry_generate.set_label("Echo Location: Generate Assets")
    entry_generate.set_tool_tip("Generate all EchoLocation assets using current config")
    entry_generate.set_string_command(
        type=unreal.ToolMenuStringCommandType.PYTHON,
        custom_type="",
        string=(
            "import sys, os; "
            f"p = r'{SCRIPT_DIR}'; "
            "sys.path.insert(0, p) if p not in sys.path else None; "
            "from echo_config import EchoConfig; "
            "from echo_generator import generate_all; "
            "import importlib, echo_config, echo_generator; "
            "importlib.reload(echo_config); importlib.reload(echo_generator); "
            "cfg = echo_config.EchoConfig.load(); "
            "echo_generator.generate_all(cfg)"
        ),
    )
    main_menu.add_menu_entry(section_name, entry_generate)

    # --- Edit Config (JSON) ---
    config_os_path = get_config_path().replace("/", "\\\\")
    entry_edit = unreal.ToolMenuEntry(
        name="EchoLocation_EditConfig",
        type=unreal.MultiBlockType.MENU_ENTRY,
    )
    entry_edit.set_label("Echo Location: Edit Config (JSON)")
    entry_edit.set_tool_tip("Open echo_config.json in the default editor")
    entry_edit.set_string_command(
        type=unreal.ToolMenuStringCommandType.PYTHON,
        custom_type="",
        string=(
            "import sys, os, subprocess; "
            f"p = r'{SCRIPT_DIR}'; "
            "sys.path.insert(0, p) if p not in sys.path else None; "
            "from echo_config import EchoConfig, get_config_path; "
            "cfg_path = get_config_path(); "
            "EchoConfig().save(cfg_path) if not os.path.isfile(cfg_path) else None; "
            "os.startfile(cfg_path)"
        ),
    )
    main_menu.add_menu_entry(section_name, entry_edit)

    # --- Reset to Defaults ---
    entry_reset = unreal.ToolMenuEntry(
        name="EchoLocation_ResetConfig",
        type=unreal.MultiBlockType.MENU_ENTRY,
    )
    entry_reset.set_label("Echo Location: Reset Config to Defaults")
    entry_reset.set_tool_tip("Overwrite echo_config.json with default values")
    entry_reset.set_string_command(
        type=unreal.ToolMenuStringCommandType.PYTHON,
        custom_type="",
        string=(
            "import sys; "
            f"p = r'{SCRIPT_DIR}'; "
            "sys.path.insert(0, p) if p not in sys.path else None; "
            "from echo_config import EchoConfig, get_config_path; "
            "import importlib, echo_config; "
            "importlib.reload(echo_config); "
            "echo_config.EchoConfig().save(echo_config.get_config_path()); "
            "import unreal; unreal.log('[EchoTool] Config reset to defaults')"
        ),
    )
    main_menu.add_menu_entry(section_name, entry_reset)

    # Refresh the menus so changes appear immediately
    tool_menus.refresh_all_widgets()

    unreal.log("[EchoTool] Registered Tools > Echo Location menu entries")


# ======================================================================
# Ensure default config exists
# ======================================================================

def _ensure_default_config():
    """Write the default config JSON if it doesn't exist yet."""
    cfg_path = get_config_path()
    if not os.path.isfile(cfg_path):
        EchoConfig().save(cfg_path)
        unreal.log(f"[EchoTool] Created default config at {cfg_path}")
    else:
        unreal.log(f"[EchoTool] Config already exists at {cfg_path}")


# ======================================================================
# Public run()
# ======================================================================

def run():
    """Entry point — create EUW, register menus, ensure config."""
    unreal.log("[EchoTool] Setting up EchoLocation Asset Generator tooling...")

    _ensure_default_config()
    _create_euw_blueprint()
    _register_tools_menu()

    unreal.log("[EchoTool] Setup complete!")
    unreal.log("  - Tools > Echo Location > Generate Assets")
    unreal.log("  - Tools > Echo Location > Edit Config (JSON)")
    unreal.log("  - Tools > Echo Location > Reset Config to Defaults")


# Allow running as standalone or exec'd
if __name__ == "__main__":
    run()

run()
