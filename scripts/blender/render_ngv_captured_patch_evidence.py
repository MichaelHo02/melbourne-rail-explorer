import bpy,json
from pathlib import Path
from mathutils import Vector
r=Path(bpy.data.filepath).resolve().parents[3];d=json.loads((r/'assets/source/environment/ngv-local-captured-roof.json').read_text())
for o in bpy.data.objects:
 if o.type!='LIGHT':o.hide_render=True
m=bpy.data.meshes.new('Connected NGV captured roof evidence');m.from_pydata(d['vertices'],[],d['faces']);m.materials.append(bpy.data.materials['Authored Federation Square zinc']);m.update();o=bpy.data.objects.new(m.name,m);bpy.context.scene.collection.objects.link(o)
c=bpy.data.cameras.new('Captured roof inspection');co=bpy.data.objects.new(c.name,c);bpy.context.scene.collection.objects.link(co);co.location=(223,12,51);co.rotation_euler=(Vector((205,35,30))-co.location).to_track_quat('-Z','Y').to_euler();c.type='ORTHO';c.ortho_scale=24;s=bpy.context.scene;s.camera=co;s.render.engine='CYCLES';s.cycles.samples=24;s.render.resolution_x=1000;s.render.resolution_y=800;s.render.resolution_percentage=100;s.render.filepath=str(r/'docs/images/ngv-connected-captured-roof-evidence.png');bpy.ops.render.render(write_still=True);print('CAPTURED_PATCH_RENDERED_NO_SAVE',flush=True)
