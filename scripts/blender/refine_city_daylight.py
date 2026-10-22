"""Authored procedural daylight: directional sky fill, without photographic maps.
Sun angles inherit the scene's existing artistic lighting. Not live weather or
an astronomically calibrated Melbourne timestamp. Previous world is retained.
"""
import bpy, math, json
from pathlib import Path
from mathutils import Vector
root = Path(bpy.data.filepath).resolve().parents[3]
scene = bpy.context.scene
# Preserve the established presentation preset when rebuilding the scene.
scene.view_settings.view_transform = 'AgX'
scene.view_settings.look = 'AgX - Medium High Contrast'
scene.view_settings.exposure = .45
name = 'Melbourne authored procedural daylight'
previous = scene.world
world = bpy.data.worlds.get(name)
if world is None:
    world = bpy.data.worlds.new(name)
if previous != world:
    previous.use_fake_user = True
    world['previous_world_name'] = previous.name
world.use_nodes = True
nodes = world.node_tree.nodes
nodes.clear()
output = nodes.new('ShaderNodeOutputWorld')
background = nodes.new('ShaderNodeBackground')
background.inputs['Strength'].default_value = .12
sky = nodes.new('ShaderNodeTexSky')
sky.sky_type = 'MULTIPLE_SCATTERING'
sky.sun_disc = False  # Existing SUN supplies direct light; avoid a second sun.
sun = next(obj for obj in scene.objects if obj.type == 'LIGHT' and obj.data.type == 'SUN')
sun.data.color = (1, .96, .88)
sun.data.angle = .09
direction = -(sun.rotation_euler.to_matrix() @ Vector((0, 0, -1)))
sky.sun_elevation = math.asin(direction.z)
sky.sun_rotation = math.atan2(direction.y, direction.x)
sky.altitude = 0
sky.air_density = 1
sky.aerosol_density = 1.2
sky.ozone_density = 1
world.node_tree.links.new(sky.outputs['Color'], background.inputs['Color'])
world.node_tree.links.new(background.outputs['Background'], output.inputs['Surface'])
world['limits'] = 'Authored clear daylight atmosphere, aligned to existing scene SUN. Atmospheric densities and strength artistic; not measured weather or calibrated time. No photographic environment map.'
world['reference'] = 'https://docs.blender.org/manual/en/5.1/render/shader_nodes/textures/sky.html'
scene.world = world
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces.active.shading.use_scene_world = True
            area.spaces.active.shading.use_scene_lights = True
report = {
    'world': world.name,
    'retained_previous_world': world['previous_world_name'],
    'sky_model': sky.sky_type,
    'sun_disc': sky.sun_disc,
    'existing_sun': sun.name,
    'sun_elevation_deg': math.degrees(sky.sun_elevation),
    'sun_rotation_deg': math.degrees(sky.sun_rotation),
    'sky_strength': background.inputs['Strength'].default_value,
    'no_photographic_map': not any(n.type == 'TEX_ENVIRONMENT' or n.type == 'TEX_IMAGE' for n in nodes),
    'limits': world['limits'],
    'reference': world['reference'],
}
(root / 'docs/city-daylight-audit.json').write_text(json.dumps(report, indent=2) + '\n')
print('CITY_DAYLIGHT', json.dumps(report), flush=True)
