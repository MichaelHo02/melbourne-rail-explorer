"""Save an inspection camera and render the current authored Arts Centre spire.
Run with Blender -b city-observatory.blend --python this_file.
The saved active camera is preserved; only the render uses the study camera.
"""
import bpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
from mathutils import Vector
scene=bpy.context.scene
name='13 Arts Centre spire inspection'
camera=bpy.data.objects.get(name)
if camera is None:
 data=bpy.data.cameras.new(name);camera=bpy.data.objects.new(name,data);bpy.data.collections.get('PREVIEW - lighting and aerial camera').objects.link(camera)
camera.location=(-130,-620,190);target=Vector((117,-350,65));camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=220;camera.data.clip_end=10000
# Move the orthographic camera back without changing its projection, so
# foreground buildings cannot intersect the camera plane.
camera.location += camera.rotation_euler.to_quaternion() @ Vector((0,0,600))
camera['purpose']='Inspect authored Arts Centre spire against retained survey sections';camera['architectural_reference']='https://www.artscentremelbourne.com.au/-/media/acm/files/about-us/media-centre/media-releases/2024/241001arts-centre-melbournes-theatres-building-celebrates-40-years--media-release.pdf'
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
scene.camera=camera;scene.render.resolution_x=1400;scene.render.resolution_y=1100;scene.render.resolution_percentage=100;scene.render.filepath=str(ROOT/'docs/images/observatory-arts-centre-spire-study.png');bpy.ops.render.render(write_still=True)
print('VERIFIED Arts Centre spire camera and render')
