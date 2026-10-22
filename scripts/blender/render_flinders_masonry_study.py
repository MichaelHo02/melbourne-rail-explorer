import bpy
from pathlib import Path
from mathutils import Vector
root=Path(bpy.data.filepath).resolve().parents[3];anchor=bpy.data.objects['Flinders Street - runtime placement'];name='25 Flinders masonry inspection';c=bpy.data.objects.get(name)
if not c:c=bpy.data.objects.new(name,bpy.data.cameras.new(name));bpy.data.collections['PREVIEW - lighting and aerial camera'].objects.link(c)
c.location=anchor.matrix_world@Vector((-245,48,32));target=anchor.matrix_world@Vector((-250,12.8,16));c.rotation_euler=(target-c.location).to_track_quat('-Z','Y').to_euler();c.location+=c.rotation_euler.to_quaternion()@Vector((0,0,600));c.data.type='ORTHO';c.data.ortho_scale=36;c.data.clip_end=10000;c.data.clip_start=max(.1,(c.location-target).length-15);c['limits']='Authored facade detail inspection; dimensions and ornament remain schematic.'
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
s=bpy.context.scene;s.camera=c;s.render.resolution_x=1400;s.render.resolution_y=1100;s.render.resolution_percentage=100;s.render.filepath=str(root/'docs/images/observatory-flinders-masonry-study.png');bpy.ops.render.render(write_still=True);print('VERIFIED Flinders masonry inspection render',flush=True)
