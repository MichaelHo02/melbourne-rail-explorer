import bpy,json
from pathlib import Path
from mathutils import Vector
r=Path(bpy.data.filepath).resolve().parents[3];d=json.loads((r/'assets/source/environment/city-civic-surfaces.json').read_text());p=next(p for p in d['parts'] if p['source_id']=='M020718');x,y=p['centroid_xy'];name='26 Civic paving inspection';c=bpy.data.objects.get(name)
if not c:c=bpy.data.objects.new(name,bpy.data.cameras.new(name));bpy.data.collections['PREVIEW - lighting and aerial camera'].objects.link(c)
c.location=(x,y,500);target=Vector((x,y,2));c.rotation_euler=(target-c.location).to_track_quat('-Z','Y').to_euler();c.location+=c.rotation_euler.to_quaternion()@Vector((0,0,600));c.data.type='ORTHO';c.data.ortho_scale=190;c.data.clip_end=10000;c['source_id']='M020718';bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
s=bpy.context.scene;s.camera=c;s.render.resolution_x=1400;s.render.resolution_y=1100;s.render.resolution_percentage=100;s.render.filepath=str(r/'docs/images/observatory-civic-paving-study.png');bpy.ops.render.render(write_still=True);print('VERIFIED civic paving inspection render',flush=True)
