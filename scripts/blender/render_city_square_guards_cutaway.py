import bpy
from pathlib import Path
R=Path(bpy.data.filepath).resolve().parents[3]
for o in bpy.data.collections['City Square authored entrance canopy'].objects:o.hide_render=True
s=bpy.context.scene;s.camera=bpy.data.objects['33 City Square portal detail'];s.render.resolution_x=1400;s.render.resolution_y=1100;s.render.resolution_percentage=100;s.render.filepath=str(R/'docs/images/observatory-city-square-guards-cutaway.png')
bpy.ops.render.render(write_still=True)
print('VERIFIED diagnostic canopy hidden in memory only; saved scene unchanged',flush=True)
