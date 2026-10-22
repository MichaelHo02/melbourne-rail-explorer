import bpy
from pathlib import Path
from mathutils import Vector
r=Path(bpy.data.filepath).resolve().parents[3];s=bpy.context.scene;c=bpy.data.objects.new('Temporary Swanston approach review',bpy.data.cameras.new('Temporary Swanston approach review'));s.collection.objects.link(c);c.location=(180,-190,300);c.rotation_euler=(Vector((52,18,6))-c.location).to_track_quat('-Z','Y').to_euler();c.data.type='ORTHO';c.data.ortho_scale=210;c.data.clip_end=10000;s.camera=c;s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True;s.render.resolution_x=1200;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.render.filepath=str(r/'docs/images/observatory-swanston-approach-detail.png');bpy.ops.render.render(write_still=True)
