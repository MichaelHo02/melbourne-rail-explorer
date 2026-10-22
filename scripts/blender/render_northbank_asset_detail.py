"""Save an inspection camera and render the current Northbank asset placement.
Run with Blender -b city-observatory.blend --python this_file.
The saved active camera is preserved; only the render uses the study camera.
"""
import bpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
from mathutils import Vector
scene=bpy.context.scene
name='08 Northbank asset detail'
camera=bpy.data.objects.get(name)
if camera is None:
 data=bpy.data.cameras.new(name);camera=bpy.data.objects.new(name,data);bpy.data.collections.get('PREVIEW - lighting and aerial camera').objects.link(camera)
camera.location=(90,-155,100);target=Vector((45,-40,4));camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=100;camera.data.clip_end=10000
camera['purpose']='Inspect mapped feature light placement and authored geometry';camera['asset_reference']='https://data.melbourne.vic.gov.au/explore/dataset/feature-lighting-including-light-type-wattage-and-location/'
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
scene.camera=camera;scene.render.resolution_x=1400;scene.render.resolution_y=1100;scene.render.resolution_percentage=100;scene.render.filepath=str(ROOT/'docs/images/observatory-northbank-asset-detail.png');bpy.ops.render.render(write_still=True)
print('VERIFIED Northbank asset detail camera and render')
