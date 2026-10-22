"""Save an inspection camera and render the current authored date-palm grove.
Run with Blender -b city-observatory.blend --python this_file.
The saved active camera is preserved; only the render uses the study camera.
"""
import bpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
from mathutils import Vector
scene=bpy.context.scene
name='09 Date palm grove inspection'
camera=bpy.data.objects.get(name)
if camera is None:
 data=bpy.data.cameras.new(name);camera=bpy.data.objects.new(name,data);bpy.data.collections.get('PREVIEW - lighting and aerial camera').objects.link(camera)
camera.location=(680,-440,110);target=Vector((602,-313,4));camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=110;camera.data.clip_end=10000
camera['purpose']='Inspect authored date palm morphology at retained inventory points';camera['botanical_reference']='https://vicflora.rbg.vic.gov.au/flora/taxon/a3860b68-24a3-424a-8906-1f43be6d3497'
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
scene.camera=camera;scene.render.resolution_x=1400;scene.render.resolution_y=1100;scene.render.resolution_percentage=100;scene.render.filepath=str(ROOT/'docs/images/observatory-date-palm-grove.png');bpy.ops.render.render(write_still=True)
print('VERIFIED Date palm grove camera and render')
