"""Isolated two-tile roof evidence; own zinc, never save trial scene."""
import bpy,json
from pathlib import Path
from mathutils import Vector
r=Path(bpy.data.filepath).resolve().parents[3];d=json.loads((r/'assets/source/environment/federation-ngv-complete-captured-roof.json').read_text())
for o in bpy.data.objects:
 if o.type!='LIGHT':o.hide_render=True
m=bpy.data.meshes.new('NGV two-tile original upward roof evidence');m.from_pydata(d['vertices'],[],d['faces']);m.materials.append(bpy.data.materials['Authored Federation Square zinc']);m.update();o=bpy.data.objects.new(m.name,m);bpy.context.scene.collection.objects.link(o)
c=bpy.data.cameras.new('NGV complete capture evidence');co=bpy.data.objects.new(c.name,c);bpy.context.scene.collection.objects.link(co);co.location=(350,-90,150);co.rotation_euler=(Vector((239,65,25))-co.location).to_track_quat('-Z','Y').to_euler();c.type='ORTHO';c.ortho_scale=190;s=bpy.context.scene;s.camera=co;s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True;s.render.resolution_x=1200;s.render.resolution_y=1100;s.render.resolution_percentage=100;s.render.filepath=str(r/'docs/images/ngv-complete-captured-roof-evidence.png');bpy.ops.render.render(write_still=True);print('TWO_TILE_CAPTURE_EVIDENCE_RENDERED_NO_SAVE',len(m.polygons),flush=True)
