"""Consolidated NGV review from saved scene, no scene save or camera mutation on disk."""
import bpy
from pathlib import Path
from mathutils import Vector
r=Path(bpy.data.filepath).resolve().parents[3];s=bpy.context.scene;c=bpy.data.objects.new('Temporary NGV aerial readiness',bpy.data.cameras.new('Temporary NGV aerial readiness'));s.collection.objects.link(c);c.location=(430,-230,260);c.rotation_euler=(Vector((225,65,16))-c.location).to_track_quat('-Z','Y').to_euler();c.data.type='ORTHO';c.data.ortho_scale=265;c.data.clip_end=10000;s.camera=c;s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=True;s.render.resolution_x=1500;s.render.resolution_y=1100;s.render.resolution_percentage=100;s.render.filepath=str(r/'docs/images/observatory-ngv-aerial-readiness.png');bpy.ops.render.render(write_still=True)
