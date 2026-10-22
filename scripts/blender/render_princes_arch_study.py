import bpy
from pathlib import Path
from mathutils import Vector
root=Path(bpy.data.filepath).resolve().parents[3];name='20 Princes Bridge river inspection';c=bpy.data.objects.get(name)
if not c:c=bpy.data.objects.new(name,bpy.data.cameras.new(name));bpy.data.collections['PREVIEW - lighting and aerial camera'].objects.link(c)
c.location=(-70,-150,46);c.rotation_euler=(Vector((104,-110,6))-c.location).to_track_quat('-Z','Y').to_euler();c.location+=c.rotation_euler.to_quaternion()@Vector((0,0,600));c.data.type='ORTHO';c.data.ortho_scale=170;c.data.clip_end=10000;bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True);s=bpy.context.scene;s.camera=c;s.render.resolution_x=1400;s.render.resolution_y=1100;s.render.filepath=str(root/'docs/images/observatory-princes-arches-study.png');bpy.ops.render.render(write_still=True);print('VERIFIED Princes Bridge river render',flush=True)
