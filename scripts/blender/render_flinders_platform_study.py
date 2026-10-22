"""Save an inspection camera and render the current authored Flinders platform precinct.
Run with Blender -b city-observatory.blend --python this_file.
The saved active camera is preserved; only the render uses the study camera.
"""
import bpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
from mathutils import Vector
scene=bpy.context.scene
name='11 Flinders platform inspection'
camera=bpy.data.objects.get(name)
if camera is None:
 data=bpy.data.cameras.new(name);camera=bpy.data.objects.new(name,data);bpy.data.collections.get('PREVIEW - lighting and aerial camera').objects.link(camera)
camera.location=(-320,-250,150);target=Vector((-160,-60,8));camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=320;camera.data.clip_end=10000
# Move the orthographic camera back without changing its projection, so
# foreground buildings cannot intersect the camera plane.
camera.location += camera.rotation_euler.to_quaternion() @ Vector((0,0,600))
camera['purpose']='Inspect authored Flinders platform precinct against retained survey sections';camera['architectural_reference']='https://www.ptv.vic.gov.au/assets/DTP1124-FlindersStreetStation-Precinct-Map_Degraves-Subway_web_Stage-1_v3.pdf'
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
scene.camera=camera;scene.render.resolution_x=1400;scene.render.resolution_y=1100;scene.render.resolution_percentage=100;scene.render.filepath=str(ROOT/'docs/images/observatory-flinders-platform-study.png');bpy.ops.render.render(write_still=True)
print('VERIFIED Flinders platform camera and render')
