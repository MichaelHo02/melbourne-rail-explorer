"""Apply isolated NGV study and save only /tmp preview artifacts."""
import bpy
from pathlib import Path
from mathutils import Vector
r=Path(__file__).resolve().parents[2];source=r/'scripts/blender/refine_ngv_platform_contact.py';exec(compile(source.read_text(),str(source),'exec'),{'__file__':str(source)})
s=bpy.context.scene;c=bpy.data.objects.new('NGV platform study',bpy.data.cameras.new('NGV platform study'));s.collection.objects.link(c);c.location=(430,-230,190);c.rotation_euler=(Vector((230,65,8))-c.location).to_track_quat('-Z','Y').to_euler();c.data.type='ORTHO';c.data.ortho_scale=235;c.data.clip_end=10000;s.camera=c;s.render.engine='CYCLES';s.cycles.samples=20;s.cycles.use_denoising=True;s.render.resolution_x=1400;s.render.resolution_y=1100;s.render.resolution_percentage=100;s.render.filepath='/tmp/ngv-platform-contact-study.png';bpy.ops.render.render(write_still=True);bpy.ops.wm.save_as_mainfile(filepath='/tmp/ngv-platform-contact-study.blend')
