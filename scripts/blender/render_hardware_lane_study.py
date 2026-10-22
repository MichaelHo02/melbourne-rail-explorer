import bpy,json
from pathlib import Path
from mathutils import Vector
root=Path(bpy.data.filepath).resolve().parents[3];d=json.loads((root/'assets/source/environment/hardware-authored-paving.json').read_text());v=d['vertices'];x=sum(p[0] for p in v)/len(v);y=sum(p[1] for p in v)/len(v);name='24 Hardware Lane paving inspection';c=bpy.data.objects.get(name)
if not c:c=bpy.data.objects.new(name,bpy.data.cameras.new(name));bpy.data.collections['PREVIEW - lighting and aerial camera'].objects.link(c)
c.location=(x+20,y-25,120);target=Vector((x,y,1));c.rotation_euler=(target-c.location).to_track_quat('-Z','Y').to_euler();c.location+=c.rotation_euler.to_quaternion()@Vector((0,0,600));c.data.type='ORTHO';c.data.ortho_scale=110;c.data.clip_end=10000;bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True);s=bpy.context.scene;s.camera=c;s.render.resolution_x=1400;s.render.resolution_y=1100;s.render.resolution_percentage=100;s.render.filepath=str(root/'docs/images/observatory-hardware-lane-study.png');bpy.ops.render.render(write_still=True);print('VERIFIED Hardware Lane render',flush=True)
