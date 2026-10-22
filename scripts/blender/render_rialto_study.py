"""Inspect retained Rialto candidate structure before reference-led modelling."""
import bpy
from pathlib import Path
from mathutils import Vector
root=Path(bpy.data.filepath).resolve().parents[3];name='22 Rialto retained envelope inspection';c=bpy.data.objects.get(name)
if not c:c=bpy.data.objects.new(name,bpy.data.cameras.new(name));bpy.data.collections['PREVIEW - lighting and aerial camera'].objects.link(c)
c.location=(-590,-410,300);target=Vector((-833,-51,130));c.rotation_euler=(target-c.location).to_track_quat('-Z','Y').to_euler();c.location+=c.rotation_euler.to_quaternion()@Vector((0,0,600));c.data.type='ORTHO';c.data.ortho_scale=330;c.data.clip_end=10000;c['limits']='Candidate structure 803943 located by retained public footprint and official address; exact facade and present-day podium unresolved.';bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True);s=bpy.context.scene;s.camera=c;s.render.resolution_x=1400;s.render.resolution_y=1100;s.render.resolution_percentage=100;s.render.filepath=str(root/'docs/images/observatory-rialto-envelope-study.png');bpy.ops.render.render(write_still=True);print('VERIFIED Rialto inspection render',flush=True)
