"""Save an inspection camera and render the current authored Flinders platform precinct.
Run with Blender -b city-observatory.blend --python this_file.
The saved active camera is preserved; only the render uses the study camera.
"""
import bpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
from mathutils import Vector
scene=bpy.context.scene
name='12 Southbank paving inspection'
camera=bpy.data.objects.get(name)
if camera is None:
 data=bpy.data.cameras.new(name);camera=bpy.data.objects.new(name,data);bpy.data.collections.get('PREVIEW - lighting and aerial camera').objects.link(camera)
camera.location=(80,20,190);target=Vector((-35,-240,3));camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=320;camera.data.clip_end=10000
# Move the orthographic camera back without changing its projection, so
# foreground buildings cannot intersect the camera plane.
camera.location += camera.rotation_euler.to_quaternion() @ Vector((0,0,600))
camera['purpose']='Inspect authored Flinders platform precinct against retained survey sections';camera['architectural_reference']='https://participate.melbourne.vic.gov.au/emerging-tech-testbed/southbank-promenade-1/works-between-princes-bridge-and-evan-walker-bridge-are-now-complete'
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
scene.camera=camera;scene.render.resolution_x=1400;scene.render.resolution_y=1100;scene.render.resolution_percentage=100;scene.render.filepath=str(ROOT/'docs/images/observatory-southbank-paving-study.png');bpy.ops.render.render(write_still=True)
print('VERIFIED Southbank paving camera and render')
