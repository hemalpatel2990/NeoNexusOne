"""
12_polish_level.py — Add atmospheric actors to L_EchoPrototype.

Depends on: 08_create_level.py (L_EchoPrototype must exist)

Adds the remaining level elements:
  - SkyLight (very low intensity for minimal ambient fill)
  - ExponentialHeightFog (dark atmospheric haze)
  - PostProcessVolume (infinite unbound, near-black exposure, bloom for emissive glow)
  - NavMeshBoundsVolume (covers the arena for AI pathfinding)
"""

import sys
import os
import unreal

try:
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    SCRIPT_DIR = os.path.join(unreal.Paths.project_dir(), "Scripts", "EditorUtility").replace("\\", "/")

if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from helpers import Paths, asset_exists, log_created, log_manual


def run():
    _polish_level()


def _polish_level():
    """Open L_EchoPrototype and spawn atmospheric + navigation actors."""
    path = Paths.L_ECHO_PROTOTYPE
    if not asset_exists(path):
        unreal.log_error("[EchoSetup] L_EchoPrototype not found. Run 08_create_level first.")
        return

    # Load the level
    level_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    level_subsystem.load_level(path)

    editor_level_lib = unreal.EditorLevelLibrary
    actors = editor_level_lib.get_all_level_actors()

    # Check which polish actors already exist (idempotent)
    has_skylight = False
    has_fog = False
    has_ppv = False
    has_navmesh = False

    for actor in actors:
        label = actor.get_actor_label()
        if label == "EchoSkyLight":
            has_skylight = True
        elif label == "EchoFog":
            has_fog = True
        elif label == "EchoPPV":
            has_ppv = True
        elif label == "EchoNavMesh":
            has_navmesh = True

    # --- SkyLight ---
    if not has_skylight:
        try:
            sky = editor_level_lib.spawn_actor_from_class(
                unreal.SkyLight, unreal.Vector(0, 0, 500)
            )
            if sky:
                sky.set_actor_label("EchoSkyLight")
                light_comp = sky.get_component_by_class(unreal.SkyLightComponent)
                if light_comp:
                    light_comp.set_editor_property("intensity", 0.05)
                    light_comp.set_editor_property("source_type", unreal.SkyLightSourceType.SLS_SPECIFIED_CUBEMAP)
                unreal.log("[EchoSetup] Created: EchoSkyLight (intensity 0.05)")
        except Exception as e:
            unreal.log_warning(f"[EchoSetup] SkyLight creation failed: {e}")
            log_manual("Add a SkyLight actor with very low intensity (~0.05)")
    else:
        unreal.log("[EchoSetup] EchoSkyLight already exists, skipping")

    # --- ExponentialHeightFog ---
    if not has_fog:
        try:
            fog = editor_level_lib.spawn_actor_from_class(
                unreal.ExponentialHeightFog, unreal.Vector(0, 0, 0)
            )
            if fog:
                fog.set_actor_label("EchoFog")
                fog_comp = fog.get_component_by_class(unreal.ExponentialHeightFogComponent)
                if fog_comp:
                    fog_comp.set_editor_property("fog_density", 0.02)
                    fog_comp.set_editor_property("fog_height_falloff", 0.5)
                    fog_comp.set_editor_property("fog_inscattering_color", unreal.LinearColor(0.01, 0.01, 0.02, 1.0))
                    fog_comp.set_editor_property("start_distance", 500.0)
                unreal.log("[EchoSetup] Created: EchoFog (density 0.02, dark inscattering)")
        except Exception as e:
            unreal.log_warning(f"[EchoSetup] Fog creation failed: {e}")
            log_manual("Add ExponentialHeightFog: density=0.02, dark inscattering color")
    else:
        unreal.log("[EchoSetup] EchoFog already exists, skipping")

    # --- PostProcessVolume ---
    if not has_ppv:
        try:
            ppv = editor_level_lib.spawn_actor_from_class(
                unreal.PostProcessVolume, unreal.Vector(0, 0, 0)
            )
            if ppv:
                ppv.set_actor_label("EchoPPV")
                # Infinite unbound volume — applies to the whole level
                ppv.set_editor_property("unbound", True)

                settings = ppv.get_editor_property("settings")
                if settings:
                    # Auto-exposure off, locked to very dark
                    settings.set_editor_property("override_auto_exposure_method", True)
                    settings.set_editor_property("auto_exposure_method", unreal.AutoExposureMethod.AEM_MANUAL)

                    settings.set_editor_property("override_auto_exposure_bias", True)
                    settings.set_editor_property("auto_exposure_bias", -2.0)

                    # Bloom for emissive glow
                    settings.set_editor_property("override_bloom_intensity", True)
                    settings.set_editor_property("bloom_intensity", 1.5)

                    settings.set_editor_property("override_bloom_threshold", True)
                    settings.set_editor_property("bloom_threshold", 0.5)

                    # Slight vignette for horror framing
                    settings.set_editor_property("override_vignette_intensity", True)
                    settings.set_editor_property("vignette_intensity", 0.6)

                unreal.log("[EchoSetup] Created: EchoPPV (manual exposure -2, bloom 1.5, vignette 0.6)")
        except Exception as e:
            unreal.log_warning(f"[EchoSetup] PostProcessVolume creation failed: {e}")
            log_manual(
                "Add PostProcessVolume (Infinite Unbound):\n"
                "  Auto Exposure: Manual, Bias=-2\n"
                "  Bloom: Intensity=1.5, Threshold=0.5\n"
                "  Vignette: 0.6"
            )
    else:
        unreal.log("[EchoSetup] EchoPPV already exists, skipping")

    # --- NavMeshBoundsVolume ---
    if not has_navmesh:
        try:
            nav = editor_level_lib.spawn_actor_from_class(
                unreal.NavMeshBoundsVolume, unreal.Vector(0, 0, 150)
            )
            if nav:
                nav.set_actor_label("EchoNavMesh")
                # Scale to cover the arena (floor is 50x50x100 units = 5000x5000)
                nav.set_actor_scale3d(unreal.Vector(100, 100, 10))
                unreal.log("[EchoSetup] Created: EchoNavMesh (arena-sized bounds)")
                log_manual("After adding NavMeshBoundsVolume: Build > Build Paths in the editor")
        except Exception as e:
            unreal.log_warning(f"[EchoSetup] NavMeshBoundsVolume creation failed: {e}")
            log_manual(
                "Add NavMeshBoundsVolume covering the arena:\n"
                "  Location: (0, 0, 150), Scale: (100, 100, 10)\n"
                "  Then Build > Build Paths"
            )
    else:
        unreal.log("[EchoSetup] EchoNavMesh already exists, skipping")

    # Save the level
    unreal.EditorLevelLibrary.save_current_level()
    unreal.log("[EchoSetup] L_EchoPrototype polish complete")


if __name__ == "__main__":
    run()
