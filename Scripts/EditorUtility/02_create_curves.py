"""
02_create_curves.py — Create float curves for the ripple system.

  C_RippleRadius:    0→1 ease-out over normalized 0→1 time
  C_RippleIntensity: 1→0 fade over normalized 0→1 time

Timeline play rate (1/RippleDuration) is set in C++ to decouple curve shape from duration.
"""

import unreal
from helpers import Paths, asset_exists, ensure_directory, save_asset, log_created, log_exists, log_manual


def _create_curve(path: str, asset_name: str, keys: list):
    """
    Create a CurveFloat asset and add keyframes.

    keys: list of (time, value) tuples
    """
    if asset_exists(path):
        log_exists(asset_name, path)
        return

    ensure_directory(path)

    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    factory = unreal.CurveFloatFactory()
    directory = path.rsplit("/", 1)[0]
    name = path.rsplit("/", 1)[1]

    curve = asset_tools.create_asset(name, directory, unreal.CurveFloat, factory)

    if curve is None:
        unreal.log_error(f"[EchoSetup] Failed to create curve {asset_name}")
        return

    # Add keys via the FRichCurve::AddKey binding on CurveFloat.float_curve
    try:
        rich_curve = curve.float_curve
        for time_val, value in keys:
            rich_curve.add_key(time_val, value)
        log_created(asset_name, path)
    except Exception as e:
        unreal.log_warning(f"[EchoSetup] Could not add keyframes programmatically for {asset_name}: {e}")
        log_manual(
            f"Open {asset_name} in Curve Editor and add keys manually:\n"
            f"  Keys: {keys}\n"
            f"  Use Auto tangent mode for smooth interpolation."
        )
        log_created(f"{asset_name} (empty — needs manual keys)", path)

    save_asset(path)


def run():
    # C_RippleRadius: normalized 0→1 ease-out
    _create_curve(
        Paths.CURVE_RIPPLE_RADIUS,
        "C_RippleRadius",
        [(0.0, 0.0), (1.0, 1.0)]
    )

    # C_RippleIntensity: 1→0 fade
    _create_curve(
        Paths.CURVE_RIPPLE_INTENSITY,
        "C_RippleIntensity",
        [(0.0, 1.0), (1.0, 0.0)]
    )


if __name__ == "__main__":
    run()
