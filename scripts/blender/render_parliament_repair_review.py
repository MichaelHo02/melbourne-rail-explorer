"""Inspect integrated Parliament from saved canonical scene; no save/hiding."""
import bpy
from pathlib import Path
from mathutils import Vector
r=Path(bpy.data.filepath).resolve().parents[3];s=bpy.context.scene
c=bpy.data.objects.new('Parliament saved review',bpy.data.cameras.new('Parliament saved review'));s.collection.objects.link(c);c.location=(410,670,150);c.rotation_euler=(Vector((590,805,12))-c.location).to_track_quat('-Z','Y').to_euler();c.data.type='ORTHO';c.data.ortho_scale=145;c.data.clip_end=10000;s.camera=c
s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True;s.render.resolution_x=1400;s.render.resolution_y=1100;s.render.resolution_percentage=100;s.render.filepath=str(r/'docs/images/observatory-parliament-repaired.png');bpy.ops.render.render(write_still=True)
