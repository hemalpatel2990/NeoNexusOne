"""
08_create_level.py — Create L_EchoPrototype level.

Depends on: 06_create_material.py, 07_create_blueprints.py

Creates a minimal prototype level:
  - Large flat floor with MI_EchoMaster material
  - Boundary walls
  - A few obstacle cubes
  - PlayerStart actor
  - Directional light (dim, for minimal ambient)
"""

import unreal
from helpers import Paths, asset_exists, ensure_directory, save_asset, log_created, log_exists, log_manual


def run():
    path = Paths.L_ECHO_PROTOTYPE

    if asset_exists(path):
        log_exists("L_EchoPrototype", path)
        return

    ensure_directory(path)

    try:
        # Create a new level
        editor_level_lib = unreal.EditorLevelLibrary
        asset_tools = unreal.AssetToolsHelpers.get_asset_tools()

        # Create a new empty level
        # UE5: Use EditorAssetLibrary or LevelEditorSubsystem
        level_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)

        # Create and save a new blank level
        success = level_subsystem.new_level(path)

        if not success:
            unreal.log_error("[EchoSetup] Failed to create new level")
            return

        # Load the echo material instance for level geometry
        mi_echo = unreal.load_asset(Paths.MI_ECHO_MASTER)

        # --- Floor ---
        floor = editor_level_lib.spawn_actor_from_class(
            unreal.StaticMeshActor,
            unreal.Vector(0.0, 0.0, 0.0)
        )
        if floor:
            floor.set_actor_label("Floor")
            mesh_comp = floor.static_mesh_component
            plane_mesh = unreal.load_asset("/Engine/BasicShapes/Plane")
            if plane_mesh:
                mesh_comp.set_static_mesh(plane_mesh)
            floor.set_actor_scale3d(unreal.Vector(50.0, 50.0, 1.0))  # Large floor
            if mi_echo:
                mesh_comp.set_material(0, mi_echo)

        # --- Walls (4 boundary walls) ---
        wall_configs = [
            ("Wall_North", unreal.Vector(0.0, 2500.0, 150.0), unreal.Vector(50.0, 1.0, 3.0), unreal.Rotator(0, 0, 0)),
            ("Wall_South", unreal.Vector(0.0, -2500.0, 150.0), unreal.Vector(50.0, 1.0, 3.0), unreal.Rotator(0, 0, 0)),
            ("Wall_East", unreal.Vector(2500.0, 0.0, 150.0), unreal.Vector(1.0, 50.0, 3.0), unreal.Rotator(0, 0, 0)),
            ("Wall_West", unreal.Vector(-2500.0, 0.0, 150.0), unreal.Vector(1.0, 50.0, 3.0), unreal.Rotator(0, 0, 0)),
        ]

        cube_mesh = unreal.load_asset("/Engine/BasicShapes/Cube")
        for wall_name, location, scale, rotation in wall_configs:
            wall = editor_level_lib.spawn_actor_from_class(
                unreal.StaticMeshActor,
                location
            )
            if wall:
                wall.set_actor_label(wall_name)
                wmc = wall.static_mesh_component
                if cube_mesh:
                    wmc.set_static_mesh(cube_mesh)
                wall.set_actor_scale3d(scale)
                if mi_echo:
                    wmc.set_material(0, mi_echo)

        # --- Obstacle cubes ---
        obstacle_positions = [
            unreal.Vector(500.0, 300.0, 50.0),
            unreal.Vector(-400.0, -600.0, 50.0),
            unreal.Vector(800.0, -200.0, 50.0),
            unreal.Vector(-200.0, 700.0, 50.0),
        ]
        for i, pos in enumerate(obstacle_positions):
            obs = editor_level_lib.spawn_actor_from_class(
                unreal.StaticMeshActor,
                pos
            )
            if obs:
                obs.set_actor_label(f"Obstacle_{i}")
                omc = obs.static_mesh_component
                if cube_mesh:
                    omc.set_static_mesh(cube_mesh)
                obs.set_actor_scale3d(unreal.Vector(1.5, 1.5, 1.5))
                if mi_echo:
                    omc.set_material(0, mi_echo)

        # --- PlayerStart ---
        player_start = editor_level_lib.spawn_actor_from_class(
            unreal.PlayerStart,
            unreal.Vector(0.0, 0.0, 100.0)
        )
        if player_start:
            player_start.set_actor_label("PlayerStart_Echo")

        # --- Dim directional light for minimal ambient ---
        dir_light = editor_level_lib.spawn_actor_from_class(
            unreal.DirectionalLight,
            unreal.Vector(0.0, 0.0, 500.0)
        )
        if dir_light:
            dir_light.set_actor_label("DimDirectionalLight")
            light_comp = dir_light.get_component_by_class(unreal.DirectionalLightComponent)
            if light_comp:
                light_comp.set_editor_property("intensity", 0.1)
                light_comp.set_editor_property("light_color", unreal.Color(100, 120, 140, 255))

        # Save the level
        unreal.EditorLevelLibrary.save_current_level()

        log_created("L_EchoPrototype", path)
        log_manual(
            "Level polish still needed:\n"
            "  1. Add SkyLight with very low intensity for ambient\n"
            "  2. Add ExponentialHeightFog for atmosphere\n"
            "  3. Build navigation mesh for AI\n"
            "  4. Add PostProcessVolume for darkness effect"
        )

    except Exception as e:
        unreal.log_error(f"[EchoSetup] Level creation failed: {e}")
        log_manual(
            "Create L_EchoPrototype manually:\n"
            "  - Large floor plane (50x50 scale) with MI_EchoMaster\n"
            "  - 4 boundary walls\n"
            "  - A few obstacle cubes\n"
            "  - PlayerStart at origin\n"
            "  - Dim directional light"
        )


if __name__ == "__main__":
    run()
