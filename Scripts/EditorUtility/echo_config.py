"""
echo_config.py — JSON-backed configuration for EchoLocation asset generation.

All tunable parameters for the EchoLocation asset pipeline are defined here
as a Python dataclass. Tech artists can edit the JSON file directly or use
the Editor Utility Widget to modify values before regenerating assets.

Config file location: Content/EchoLocation/Config/echo_config.json
"""

import json
import os
from dataclasses import dataclass, field, asdict

import unreal


# ---------------------------------------------------------------------------
# Config dataclass
# ---------------------------------------------------------------------------
@dataclass
class EchoConfig:
    """All tunable parameters for EchoLocation asset generation."""

    # --- Ripple System ---
    ripple_duration: float = 1.5
    drop_ripple_radius: float = 800.0
    slam_ripple_radius: float = 2000.0
    drop_intensity: float = 0.6
    slam_intensity: float = 1.0

    # --- Movement ---
    glide_speed: float = 600.0
    hover_height: float = 20.0
    hover_interp_speed: float = 10.0
    slam_jump_impulse: list = field(default_factory=lambda: [0.0, 0.0, 1200.0])
    gravity_scale: float = 2.0

    # --- Camera Shake: Drop ---
    drop_shake_duration: float = 0.3
    drop_shake_loc_amplitude: float = 1.5
    drop_shake_rot_amplitude: float = 0.5

    # --- Camera Shake: Slam ---
    slam_shake_duration: float = 0.6
    slam_shake_loc_amplitude: float = 5.0
    slam_shake_rot_amplitude: float = 3.0

    # --- Force Feedback ---
    drop_ffe_duration: float = 0.25
    drop_ffe_large_amplitude: float = 0.3
    drop_ffe_small_amplitude: float = 0.15
    slam_ffe_duration: float = 0.5
    slam_ffe_large_amplitude: float = 0.8
    slam_ffe_small_amplitude: float = 0.5

    # --- Material ---
    base_color: list = field(default_factory=lambda: [0.02, 0.02, 0.02])
    sphere_mask_hardness: float = 80.0
    emissive_multiplier: float = 1.0

    # --- Level Prototype ---
    floor_scale: float = 50.0
    wall_height: float = 300.0
    num_obstacles: int = 4
    obstacle_scale: float = 1.5
    ambient_light_intensity: float = 0.1
    ambient_light_color: list = field(default_factory=lambda: [100, 120, 140])

    # --- AI Noise ---
    drop_noise_volume: float = 0.5
    slam_noise_volume: float = 1.0

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------
    def to_dict(self) -> dict:
        """Convert config to a plain dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "EchoConfig":
        """Create an EchoConfig from a dictionary, ignoring unknown keys."""
        known = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in data.items() if k in known}
        return cls(**filtered)

    # ------------------------------------------------------------------
    # File I/O
    # ------------------------------------------------------------------
    def save(self, path: str = ""):
        """Save config to JSON. *path* is an absolute OS filesystem path."""
        if not path:
            path = _default_os_path()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)
        unreal.log(f"[EchoConfig] Saved config to {path}")

    @classmethod
    def load(cls, path: str = "") -> "EchoConfig":
        """Load config from JSON. Returns defaults if file doesn't exist."""
        if not path:
            path = _default_os_path()
        if not os.path.isfile(path):
            unreal.log(f"[EchoConfig] No config at {path}, using defaults")
            return cls()
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        unreal.log(f"[EchoConfig] Loaded config from {path}")
        return cls.from_dict(data)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _default_os_path() -> str:
    """Return the absolute OS filesystem path for the config JSON."""
    project_dir = unreal.Paths.project_dir()
    return os.path.join(
        project_dir, "Content", "EchoLocation", "Config", "echo_config.json"
    ).replace("\\", "/")


def get_config_path() -> str:
    """Public accessor for the default config OS path."""
    return _default_os_path()
