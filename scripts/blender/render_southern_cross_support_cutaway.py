"""Render an explanatory cutaway; saved scene visibility remains unchanged."""
import bpy
from pathlib import Path
root=Path(__file__).resolve().parents[2];scene=bpy.context.scene
roof=bpy.data.objects['Southern Cross - authored dune roof'];seams=bpy.data.objects['Southern Cross - authored standing seams']
previous=[(o,o.hide_render) for o in (roof,seams)];camera=scene.camera;path=scene.render.filepath
try:
 for o,state in previous:o.hide_render=True
 scene.camera=bpy.data.objects['05 Southern Cross roof detail'];scene.render.resolution_x=1400;scene.render.resolution_y=1100;scene.render.resolution_percentage=100;scene.render.filepath=str(root/'docs/images/observatory-southern-cross-support-cutaway.png');bpy.ops.render.render(write_still=True)
finally:
 for o,state in previous:o.hide_render=state
 scene.camera=camera;scene.render.filepath=path
print('VERIFIED support cutaway rendered; scene visibility restored without saving')
