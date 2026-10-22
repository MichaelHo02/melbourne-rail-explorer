import bpy,json
from pathlib import Path
from mathutils import Vector
root=Path(bpy.data.filepath).resolve().parents[3];rows=[]
for file in ['city-survey-gables.json','city-survey-hips.json']:rows+=json.loads((root/'assets/source/environment'/file).read_text())['rows']
centers=[(sum(x for x,y in r['ring'])/len(r['ring']),sum(y for x,y in r['ring'])/len(r['ring'])) for r in rows];x,y=max(centers,key=lambda a:sum((a[0]-b[0])**2+(a[1]-b[1])**2<80**2 for b in centers));name='17 Recorded low-rise roofs inspection';c=bpy.data.objects.get(name)
if not c:c=bpy.data.objects.new(name,bpy.data.cameras.new(name));bpy.data.collections['PREVIEW - lighting and aerial camera'].objects.link(c)
c.location=(x+90,y-120,135);c.rotation_euler=(Vector((x,y,8))-c.location).to_track_quat('-Z','Y').to_euler();c.location+=c.rotation_euler.to_quaternion()@Vector((0,0,600));c.data.type='ORTHO';c.data.ortho_scale=220;c.data.clip_end=10000;bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True);s=bpy.context.scene;s.camera=c;s.render.resolution_x=1400;s.render.resolution_y=1100;s.render.filepath=str(root/'docs/images/observatory-lowrise-roofs-study.png');bpy.ops.render.render(write_still=True);print('VERIFIED lowrise roof inspection',x,y,flush=True)
