"""Save an inspection camera and render the current Southern Cross precinct.
Run with Blender -b city-observatory.blend --python this_file.
The saved active camera is preserved; only the render uses the study camera.
"""
import bpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
from mathutils import Vector
scene=bpy.context.scene
name='05 Southern Cross roof detail'
camera=bpy.data.objects.get(name)
if camera is None:
 data=bpy.data.cameras.new(name);camera=bpy.data.objects.new(name,data);bpy.data.collections.get('PREVIEW - lighting and aerial camera').objects.link(camera)
camera.location=(-1550,-450,400);target=Vector((-1270,-5,15));camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=420;camera.data.clip_end=10000
camera['purpose']='Inspect authored standing seams and dune surface';camera['architect_reference']='https://grimshaw.global/projects/rail-and-mass-transit/southern-cross-station/'
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
scene.camera=camera;scene.render.resolution_x=1400;scene.render.resolution_y=1100;scene.render.resolution_percentage=100;scene.render.filepath=str(ROOT/'docs/images/observatory-southern-cross-detail.png');bpy.ops.render.render(write_still=True)
print('VERIFIED Southern Cross roof detail camera and render')
