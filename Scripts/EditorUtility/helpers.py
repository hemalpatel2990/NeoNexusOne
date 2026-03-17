"""
helpers.py — Shared constants and utility functions for EchoLocation editor scripts.
"""

import unreal

BASE = "/Game/EchoLocation"

class Paths:
    MPC_GLOBAL_SOUND     = f"{BASE}/Materials/MPC_GlobalSound"
    M_ECHO_MASTER        = f"{BASE}/Materials/M_EchoMaster"
    MI_ECHO_MASTER       = f"{BASE}/Materials/MI_EchoMaster"
    MI_ECHO_PLAYER       = f"{BASE}/Materials/MI_EchoPlayer"
    MI_ECHO_ENEMY        = f"{BASE}/Materials/MI_EchoEnemy"
    PAWN_BP              = f"{BASE}/Player/BP_EchoPawn"
    L_ECHO_PROTOTYPE     = f"{BASE}/Maps/L_EchoPrototype"

class MPCParams:
    LAST_IMPACT_LOCATION     = "LastImpactLocation"
    CURRENT_RIPPLE_RADIUS    = "CurrentRippleRadius"
    RIPPLE_INTENSITY         = "RippleIntensity"
    PLAYER_WORLD_POSITION    = "PlayerWorldPosition"
    RIPPLE_START_TIME        = "RippleStartTime"

def asset_exists(path: str) -> bool:
    return unreal.EditorAssetLibrary.does_asset_exist(path)

def ensure_directory(path: str):
    directory = path.rsplit("/", 1)[0]
    unreal.EditorAssetLibrary.make_directory(directory)

def save_asset(path: str):
    unreal.EditorAssetLibrary.save_asset(path, only_if_is_dirty=False)

def log_created(asset_name: str, path: str):
    unreal.log(f"[EchoSetup] Created: {asset_name} at {path}")
