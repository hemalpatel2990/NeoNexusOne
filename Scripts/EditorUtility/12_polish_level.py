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

    actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actors = actor_subsystem.get_all_level_actors()

    # Check which polish actors already exist (idempotent)
    has_skylight = False
    has_fog = False
    has_navmesh = False

    for actor in actors:
        label = actor.get_actor_label()
        if label == "EchoSkyLight":
            has_skylight = True
        elif label == "EchoFog":
            has_fog = True
        elif label == "EchoNavMesh":
            has_navmesh = True

    # --- SkyLight ---
    if not has_skylight:
        try:
            sky = actor_subsystem.spawn_actor_from_class(
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
            fog = actor_subsystem.spawn_actor_from_class(
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
    ppv_actor = None
    for actor in actors:
        if actor.get_actor_label() == "EchoPPV":
            ppv_actor = actor
            break

    if not ppv_actor:
        try:
            ppv_actor = actor_subsystem.spawn_actor_from_class(unreal.PostProcessVolume, unreal.Vector(0, 0, 0))
            ppv_actor.set_actor_label("EchoPPV")
            unreal.log("[EchoSetup] Created EchoPPV")
        except Exception as e:
            unreal.log_error(f"Failed to create PPV: {e}")

    if ppv_actor:
        ppv_actor.set_editor_property("unbound", True)
        
        # Load the Material
        pp_mat = unreal.load_asset(Paths.M_ECHO_POST_PROCESS)
        
        # We will attempt to set the settings as a batch to bypass protected member errors
        new_settings = {
            "override_auto_exposure_method": True,
            "auto_exposure_method": unreal.AutoExposureMethod.AEM_MANUAL,
            "override_auto_exposure_bias": True,
            "auto_exposure_bias": -2.0,
            "override_bloom_intensity": True,
            "bloom_intensity": 1.5,
            "override_vignette_intensity": True,
            "vignette_intensity": 0.6
        }
        
        # Note: If blendables still fails, we'll log a manual instruction
        if pp_mat:
            try:
                # Attempting to construct the blendables array
                wb = unreal.WeightedBlendables(array=[unreal.WeightedBlendable(weight=1.0, object=pp_mat)])
                new_settings["blendables"] = wb
                unreal.log(f"[EchoSetup] Attempting to assign {Paths.M_ECHO_POST_PROCESS} via dictionary...")
            except Exception as e:
                unreal.log_warning(f"[EchoSetup] Could not prepare blendables dictionary: {e}")

        try:
            ppv_actor.set_editor_properties({"settings": new_settings})
            unreal.log("[EchoSetup] Applied PostProcessSettings successfully")
        except Exception as e:
            unreal.log_warning(f"[EchoSetup] Failed to apply settings via dictionary: {e}")
            log_manual(f"Select EchoPPV > Post Process Sections > Rendering Features > Post Process Materials > Array > Add {Paths.M_ECHO_POST_PROCESS}")
    else:
        unreal.log_warning("[EchoSetup] Could not find or create EchoPPV")

    # --- NavMeshBoundsVolume ---
    if not has_navmesh:
        try:
            nav = actor_subsystem.spawn_actor_from_class(
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
