import bpy
from pathlib import Path
from mathutils import Vector
R=Path(bpy.data.filepath).resolve().parents[3];p=R/'scripts/blender/refine_city_square_guards.py';exec(compile(p.read_text(),str(p),'exec'))
name='33 City Square portal detail';c=bpy.data.objects.get(name)
if not c:c=bpy.data.objects.new(name,bpy.data.cameras.new(name));bpy.data.collections['PREVIEW - lighting and aerial camera'].objects.link(c)
c.location=(-47,251,42);target=Vector((-11.6,291.4,1));c.rotation_euler=(target-c.location).to_track_quat('-Z','Y').to_euler();c.location+=c.rotation_euler.to_quaternion()@Vector((0,0,600));c.data.type='ORTHO';c.data.ortho_scale=45;c.data.clip_end=10000
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
s=bpy.context.scene;s.camera=c;s.render.resolution_x=1400;s.render.resolution_y=1100;s.render.resolution_percentage=100;s.render.filepath=str(R/'docs/images/observatory-city-square-guards-study.png');bpy.ops.render.render(write_still=True)
