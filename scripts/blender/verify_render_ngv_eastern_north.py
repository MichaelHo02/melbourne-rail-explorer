import bpy,json,collections
from pathlib import Path
from mathutils import Vector
r=Path(bpy.data.filepath).resolve().parents[3];s=bpy.context.scene
assert s.get('federation_ngv_eastern_north_revision')=='captured-eastern-north-authored-transition-v1'
roof=bpy.data.objects['Continuous surveyed roofs - authored finishes'];new=json.loads((r/'assets/source/environment/ngv-eastern-north-roof-plane.json').read_text())['plane']
def outside(mesh):
 return collections.Counter(tuple(round(float(c),5) for c in q) for v in mesh.vertices if not (194<= (q:=roof.matrix_world@v.co).x<=286 and -6<=q.y<=145))
backup=bpy.data.meshes[roof['ngv_eastern_north_original_mesh']];assert outside(roof.data)==outside(backup)
dg=bpy.context.evaluated_depsgraph_get();checks=[]
for x in [245,255]:
 for y in [110,125,135]:
  hit,q,n,i,o,m=s.ray_cast(dg,Vector((x,y,80)),Vector((0,0,-1)));target=new[0]*x+new[1]*y+new[2];assert hit and o.name==roof.name and abs(q.z-target)<.005;checks.append({'xy':[x,y],'error_m':abs(q.z-target)})
assert not any(n.type=='TEX_IMAGE' for m in bpy.data.materials if m.use_nodes for n in m.node_tree.nodes)
assert s.camera.name=='37 CBD aerial review'
audit=json.loads((r/'docs/ngv-eastern-north-envelope-audit.json').read_text());audit['saved_file_verification']={'roof_checks':checks,'unrelated_roofs_outside_precinct_unchanged':True,'no_image_texture_nodes':True,'active_camera_preserved':s.camera.name,'recovery_meshes':{o.name:o['ngv_eastern_north_original_mesh'] for o in bpy.data.objects if o.get('ngv_eastern_north_original_mesh')}};(r/'docs/ngv-eastern-north-envelope-audit.json').write_text(json.dumps(audit,indent=2)+'\n');print('SAVED_EASTERN_NORTH_FIT_VERIFIED',checks,flush=True)
import bpy
from pathlib import Path
from mathutils import Vector
s=bpy.context.scene;d=bpy.data.cameras.new('Southern NGV repair study');o=bpy.data.objects.new(d.name,d);s.collection.objects.link(o);o.location=(345,205,130);o.rotation_euler=(Vector((240,115,26))-o.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=140;d.clip_end=10000;s.camera=o;s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True;s.render.resolution_x=1200;s.render.resolution_y=900;s.render.resolution_percentage=100;s.render.filepath=str(Path(bpy.data.filepath).resolve().parents[3]/'docs/images/observatory-ngv-eastern-north.png');bpy.ops.render.render(write_still=True);print('NGV_SOUTH_STUDY_RENDERED_NO_SAVE',flush=True)
