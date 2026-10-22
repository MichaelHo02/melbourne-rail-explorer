import bpy
from pathlib import Path
from mathutils import Vector
r=Path(bpy.data.filepath).resolve().parents[3];name='32 City Square precinct inspection';c=bpy.data.objects.get(name)
if not c:c=bpy.data.objects.new(name,bpy.data.cameras.new(name));bpy.data.collections['PREVIEW - lighting and aerial camera'].objects.link(c)
c.location=(-65,180,220);target=Vector((6,263,5));c.rotation_euler=(target-c.location).to_track_quat('-Z','Y').to_euler();c.location+=c.rotation_euler.to_quaternion()@Vector((0,0,600));c.data.type='ORTHO';c.data.ortho_scale=145;c.data.clip_end=10000
c['limits']='Inspection of location-based City Square candidate; existing older parcel and generic buildings are not the completed Metro Tunnel precinct.'
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
s=bpy.context.scene;s.camera=c;s.render.resolution_x=1400;s.render.resolution_y=1100;s.render.resolution_percentage=100;s.render.filepath=str(r/'docs/images/observatory-city-square-existing-study.png');bpy.ops.render.render(write_still=True)
