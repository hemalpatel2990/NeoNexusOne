"""
05_create_feedback.py — Create camera shake and force feedback assets.

Camera Shakes:
  CS_DropShake — subtle single-burst shake
  CS_SlamShake — violent multi-burst shake

Force Feedback Effects:
  FFE_DropFeedback — light rumble
  FFE_SlamFeedback — heavy rumble
"""

import unreal
from helpers import Paths, asset_exists, ensure_directory, save_asset, log_created, log_exists, log_manual


def _create_camera_shake(path: str, asset_name: str, duration: float, loc_amp: float, rot_amp: float):
    """
    Create a Blueprint based on LegacyCameraShake (UE5 renamed from MatineeCameraShake).
    Oscillation is configured via loc_oscillation (FVOscillator) and rot_oscillation (FROscillator).
    """
    if asset_exists(path):
        log_exists(asset_name, path)
        return

    ensure_directory(path)

    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    directory = path.rsplit("/", 1)[0]
    name = path.rsplit("/", 1)[1]

    try:
        factory = unreal.BlueprintFactory()
        # Try LegacyCameraShake first (UE5.4+), fall back to MatineeCameraShake
        parent_class = getattr(unreal, "LegacyCameraShake", None)
        if parent_class is None:
            parent_class = getattr(unreal, "MatineeCameraShake", None)
        if parent_class is None:
            raise RuntimeError("Neither LegacyCameraShake nor MatineeCameraShake found")

        factory.set_editor_property("parent_class", parent_class)
        bp = asset_tools.create_asset(name, directory, unreal.Blueprint, factory)

        if bp is None:
            raise RuntimeError("create_asset returned None")

        # Set CDO properties on the generated class
        cdo = unreal.get_default_object(bp.generated_class())
        if cdo is not None:
            cdo.set_editor_property("oscillation_duration", duration)

            # Location oscillation — FVOscillator with x, y, z sub-oscillators
            try:
                loc_osc = cdo.get_editor_property("loc_oscillation")
                if loc_osc is not None:
                    # Each axis is an FFOscillator with amplitude, frequency
                    loc_x = loc_osc.get_editor_property("x")
                    if loc_x is not None:
                        loc_x.set_editor_property("amplitude", loc_amp)
                        loc_x.set_editor_property("frequency", 15.0)
                    loc_z = loc_osc.get_editor_property("z")
                    if loc_z is not None:
                        loc_z.set_editor_property("amplitude", loc_amp * 0.5)
                        loc_z.set_editor_property("frequency", 12.0)
            except Exception as loc_e:
                unreal.log_warning(f"[EchoSetup] Could not set loc_oscillation for {asset_name}: {loc_e}")

            # Rotation oscillation — FROscillator with pitch, yaw, roll
            try:
                rot_osc = cdo.get_editor_property("rot_oscillation")
                if rot_osc is not None:
                    pitch = rot_osc.get_editor_property("pitch")
                    if pitch is not None:
                        pitch.set_editor_property("amplitude", rot_amp)
                        pitch.set_editor_property("frequency", 12.0)
                    roll = rot_osc.get_editor_property("roll")
                    if roll is not None:
                        roll.set_editor_property("amplitude", rot_amp * 0.3)
                        roll.set_editor_property("frequency", 10.0)
            except Exception as rot_e:
                unreal.log_warning(f"[EchoSetup] Could not set rot_oscillation for {asset_name}: {rot_e}")

        save_asset(path)
        log_created(asset_name, path)

    except Exception as e:
        unreal.log_warning(f"[EchoSetup] Camera shake creation failed for {asset_name}: {e}")
        # Fallback: create empty Blueprint with CameraShakeBase
        try:
            factory = unreal.BlueprintFactory()
            factory.set_editor_property("parent_class", unreal.CameraShakeBase)
            bp = asset_tools.create_asset(name, directory, unreal.Blueprint, factory)
            if bp:
                save_asset(path)
                log_created(f"{asset_name} (empty — needs manual tuning)", path)
        except Exception as e2:
            unreal.log_error(f"[EchoSetup] Failed to create camera shake {asset_name}: {e2}")

        log_manual(
            f"Open {asset_name} and set:\n"
            f"  Duration: {duration}s, LocAmplitude: {loc_amp}, RotAmplitude: {rot_amp}"
        )


def _create_force_feedback(path: str, asset_name: str, large_amp: float, small_amp: float, duration: float):
    """Create a UForceFeedbackEffect asset with channel entries."""
    if asset_exists(path):
        log_exists(asset_name, path)
        return

    ensure_directory(path)

    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    directory = path.rsplit("/", 1)[0]
    name = path.rsplit("/", 1)[1]

    try:
        factory = unreal.ForceFeedbackEffectFactory()
        ffe = asset_tools.create_asset(name, directory, unreal.ForceFeedbackEffect, factory)

        if ffe is None:
            unreal.log_error(f"[EchoSetup] Failed to create {asset_name}")
            return

        # Set up channel details
        # Property names: affects_left_large, affects_left_small, affects_right_large, affects_right_small
        channel_details = ffe.get_editor_property("channel_details")

        # Large motor channel (both sides)
        entry_large = unreal.ForceFeedbackChannelDetails()
        entry_large.set_editor_property("affects_left_large", True)
        entry_large.set_editor_property("affects_right_large", True)
        entry_large.set_editor_property("affects_left_small", False)
        entry_large.set_editor_property("affects_right_small", False)
        channel_details.append(entry_large)

        # Small motor channel (both sides)
        entry_small = unreal.ForceFeedbackChannelDetails()
        entry_small.set_editor_property("affects_left_large", False)
        entry_small.set_editor_property("affects_right_large", False)
        entry_small.set_editor_property("affects_left_small", True)
        entry_small.set_editor_property("affects_right_small", True)
        channel_details.append(entry_small)

        ffe.set_editor_property("duration", duration)

        save_asset(path)
        log_created(asset_name, path)

    except Exception as e:
        unreal.log_warning(f"[EchoSetup] Force feedback creation failed for {asset_name}: {e}")
        log_manual(
            f"Create {asset_name} manually as ForceFeedbackEffect:\n"
            f"  Large motor amplitude: {large_amp}, Small motor amplitude: {small_amp}, Duration: {duration}s"
        )


def run():
    # Camera shakes
    _create_camera_shake(
        Paths.CS_DROP_SHAKE, "CS_DropShake",
        duration=0.3, loc_amp=1.5, rot_amp=0.5
    )
    _create_camera_shake(
        Paths.CS_SLAM_SHAKE, "CS_SlamShake",
        duration=0.6, loc_amp=5.0, rot_amp=3.0
    )

    # Force feedback effects
    _create_force_feedback(
        Paths.FFE_DROP_FEEDBACK, "FFE_DropFeedback",
        large_amp=0.3, small_amp=0.15, duration=0.25
    )
    _create_force_feedback(
        Paths.FFE_SLAM_FEEDBACK, "FFE_SlamFeedback",
        large_amp=0.8, small_amp=0.5, duration=0.5
    )


if __name__ == "__main__":
    run()
