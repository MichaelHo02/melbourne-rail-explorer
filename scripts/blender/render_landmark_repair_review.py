"""Fresh saved-scene repair previews; no canonical save or object hiding."""
import bpy
from pathlib import Path
from mathutils import Vector
r=Path(bpy.data.filepath).resolve().parents[3];s=bpy.context.scene
views=[('NGV platform repair',(430,-230,190),(230,65,8),235,'observatory-ngv-platform-repaired.png'),('State Library repair',(-370,805,190),(-165,949,20),150,'observatory-state-library-repaired.png')]
for name,pos,target,scale,file in views:
 c=bpy.data.objects.new(name,bpy.data.cameras.new(name));s.collection.objects.link(c);c.location=pos;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();c.data.type='ORTHO';c.data.ortho_scale=scale;c.data.clip_end=10000;s.camera=c
 s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True;s.render.resolution_x=1400;s.render.resolution_y=1100;s.render.resolution_percentage=100;s.render.filepath=str(r/'docs/images'/file);bpy.ops.render.render(write_still=True)
