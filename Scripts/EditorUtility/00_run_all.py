"""
00_run_all.py — Master orchestrator that runs all EchoLocation editor setup scripts in order.

Usage — from the UE5 OUTPUT LOG Cmd console (bottom bar, NOT the Python console):

    py "D:/Users/hemal/Documents/Unreal Projects/NeoNexusOne/Scripts/EditorUtility/00_run_all.py"

Or — from the PYTHON console (Output Log > dropdown > Python):

    exec(open(r"D:/Users/hemal/Documents/Unreal Projects/NeoNexusOne/Scripts/EditorUtility/00_run_all.py").read())

Or — from File > Execute Python Script in the Editor menu.
"""

import sys
import os
import importlib
import unreal

# Resolve script directory — __file__ may not exist when exec()'d
try:
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    # Fallback: derive from project directory
    SCRIPT_DIR = os.path.join(unreal.Paths.project_dir(), "Scripts", "EditorUtility")
    # Normalize to forward slashes for consistency
    SCRIPT_DIR = SCRIPT_DIR.replace("\\", "/")

if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

# Script execution order (respects dependency chain)
SCRIPTS = [
    "01_create_mpc",
    "02_create_curves",
    "03_create_input_actions",
    "04_create_input_mapping",       # depends on 03
    "05_create_feedback",
    "06_create_material",            # depends on 01
    "07_create_blueprints",          # depends on all prior
    "08_create_level",               # depends on 06, 07
    "09_update_config",              # depends on 07, 08
    "10_create_tool_widget",         # Tools menu + EUW
    "11_build_material_graph",       # depends on 01, 06 (wires M_EchoMaster node graph)
    "12_polish_level",               # depends on 08 (SkyLight, fog, PPV, nav mesh)
]


def run():
    unreal.log("=" * 60)
    unreal.log("[EchoSetup] Starting Milestone 1 asset creation...")
    unreal.log("=" * 60)

    success_count = 0
    fail_count = 0

    for script_name in SCRIPTS:
        unreal.log(f"\n--- Running {script_name} ---")
        try:
            # Import (or reimport if already loaded) and run
            module = importlib.import_module(script_name)
            importlib.reload(module)  # Ensure latest version
            module.run()
            success_count += 1
        except Exception as e:
            unreal.log_error(f"[EchoSetup] FAILED: {script_name} — {e}")
            import traceback
            unreal.log_error(traceback.format_exc())
            fail_count += 1

    unreal.log("\n" + "=" * 60)
    unreal.log(f"[EchoSetup] Complete! {success_count} succeeded, {fail_count} failed.")
    unreal.log("=" * 60)

    if fail_count > 0:
        unreal.log_warning("[EchoSetup] Some scripts failed. Check errors above and run failed scripts individually.")

    unreal.log("\n[EchoSetup] Next steps:")
    unreal.log("  1. Build M_EchoMaster node graph (SphereMask ring shader)")
    unreal.log("  2. Verify curve keyframes in C_RippleRadius and C_RippleIntensity")
    unreal.log("  3. Check IMC_EchoDefault key bindings")
    unreal.log("  4. Tune camera shake params in CS_DropShake / CS_SlamShake")
    unreal.log("  5. Polish L_EchoPrototype (lighting, nav mesh, post-process)")
    unreal.log("  6. Play-In-Editor to test!")


# Allow running as standalone script
if __name__ == "__main__":
    run()

# Also run when exec'd
run()
