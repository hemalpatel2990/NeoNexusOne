"""
helpers.py — Shared constants and utility functions for EchoLocation editor scripts.

All asset paths are centralized here so scripts stay DRY.
"""

import unreal

# ---------------------------------------------------------------------------
# Content root
# ---------------------------------------------------------------------------
BASE = "/Game/EchoLocation"

# ---------------------------------------------------------------------------
# Asset paths (without class prefix — just the package path)
# ---------------------------------------------------------------------------
class Paths:
    # Core
    MPC_GLOBAL_SOUND     = f"{BASE}/Materials/MPC_GlobalSound"
    GAME_MODE_BP         = f"{BASE}/Core/BP_EchoGameMode"
    PLAYER_CONTROLLER_BP = f"{BASE}/Core/BP_EchoPlayerController"

    # Player
    PAWN_BP              = f"{BASE}/Player/BP_EchoPawn"

    # Curves
    CURVE_RIPPLE_RADIUS    = f"{BASE}/Curves/C_RippleRadius"
    CURVE_RIPPLE_INTENSITY = f"{BASE}/Curves/C_RippleIntensity"

    # Input
    IA_MOVE              = f"{BASE}/Input/IA_Move"
    IA_LOOK              = f"{BASE}/Input/IA_Look"
    IA_SLAM              = f"{BASE}/Input/IA_Slam"
    IMC_ECHO_DEFAULT     = f"{BASE}/Input/IMC_EchoDefault"

    # Feedback
    CS_DROP_SHAKE        = f"{BASE}/Feedback/CS_DropShake"
    CS_SLAM_SHAKE        = f"{BASE}/Feedback/CS_SlamShake"
    FFE_DROP_FEEDBACK    = f"{BASE}/Feedback/FFE_DropFeedback"
    FFE_SLAM_FEEDBACK    = f"{BASE}/Feedback/FFE_SlamFeedback"

    # Material
    M_ECHO_MASTER        = f"{BASE}/Materials/M_EchoMaster"
    MI_ECHO_MASTER       = f"{BASE}/Materials/MI_EchoMaster"

    # Level
    L_ECHO_PROTOTYPE     = f"{BASE}/Maps/L_EchoPrototype"

    # Config & Tools
    CONFIG_JSON          = f"{BASE}/Config/echo_config.json"
    EUW_ASSET_GENERATOR  = f"{BASE}/Tools/EUW_EchoAssetGenerator"

# ---------------------------------------------------------------------------
# C++ class paths (for Blueprint parent class assignment)
# ---------------------------------------------------------------------------
class CppClasses:
    ECHO_GAME_MODE        = "/Script/NeoNexusOne.EchoGameMode"
    ECHO_PLAYER_CONTROLLER = "/Script/NeoNexusOne.EchoPlayerController"
    ECHO_PAWN             = "/Script/NeoNexusOne.EchoPawn"

# ---------------------------------------------------------------------------
# MPC parameter names — must match EchoMPCParams in EchoTypes.h
# ---------------------------------------------------------------------------
class MPCParams:
    LAST_IMPACT_LOCATION   = "LastImpactLocation"
    CURRENT_RIPPLE_RADIUS  = "CurrentRippleRadius"
    RIPPLE_INTENSITY       = "RippleIntensity"

# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------
def asset_exists(path: str) -> bool:
    """Check if a UAsset already exists at the given path."""
    return unreal.EditorAssetLibrary.does_asset_exist(path)


def ensure_directory(path: str):
    """Create the directory for an asset path if it doesn't exist."""
    directory = path.rsplit("/", 1)[0]
    unreal.EditorAssetLibrary.make_directory(directory)


def save_asset(path: str):
    """Save an asset to disk."""
    unreal.EditorAssetLibrary.save_asset(path, only_if_is_dirty=False)


def log_created(asset_name: str, path: str):
    """Log successful asset creation."""
    unreal.log(f"[EchoSetup] Created: {asset_name} at {path}")


def log_exists(asset_name: str, path: str):
    """Log that an asset already exists (idempotent skip)."""
    unreal.log(f"[EchoSetup] Already exists, skipping: {asset_name} at {path}")


def log_manual(message: str):
    """Log a manual follow-up instruction."""
    unreal.log_warning(f"[EchoSetup] MANUAL STEP: {message}")
