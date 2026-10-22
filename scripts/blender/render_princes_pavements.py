import bpy
from pathlib import Path
r=Path(bpy.data.filepath).resolve().parents[3];s=bpy.context.scene;s.camera=bpy.data.objects['02 Flinders precinct'];s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True;s.render.resolution_x=1400;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.render.filepath=str(r/'docs/images/observatory-princes-pavements.png');bpy.ops.render.render(write_still=True)
