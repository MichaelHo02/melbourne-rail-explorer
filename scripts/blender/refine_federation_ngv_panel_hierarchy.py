"""Nested authored NGV macro panels; retain opening and source mesh backups."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
r=Path(bpy.data.filepath).resolve().parents[3];s=bpy.context.scene;key='federation_ngv_panel_revision'
if not s.get(key):
 d=json.loads((r/'assets/source/environment/federation-ngv-panels.json').read_text());vs=d['vertices'];fs=d['faces'];mi=d['materials'];owners=d['owners'];jobs=[]
 for o in bpy.data.objects:
  if o.type!='MESH' or not o.name.startswith('Federation Square - authored triangular cladding'):continue
  attr=o.data.attributes.get('source_section')
  if not attr:continue
  records=[]
  for p,a in zip(o.data.polygons,attr.data):
   if a.value not in [16221,16222,16223]:continue
   m=o.data.materials[p.material_index]
   if m and m.use_nodes and any(n.type=='BSDF_TRANSPARENT' for n in m.node_tree.nodes):continue
   records.append({'face':p.index,'material':p.material_index})
  if records:jobs.append((o,records))
 assert jobs and fs
 mesh=bpy.data.meshes.new('NGV nested pinwheel façade');mesh.from_pydata(vs,[],fs)
 for label in ['sandstone','zinc','glass']:mesh.materials.append(bpy.data.materials['Authored Federation Square '+label])
 mesh.update();attr=mesh.attributes.new('source_section','INT','FACE')
 for p,m,sid in zip(mesh.polygons,mi,owners):p.material_index=m;attr.data[p.index].value=sid
 assert all(p.area>1e-10 for p in mesh.polygons)
 obj=bpy.data.objects.new('Federation NGV - nested pinwheel panels',mesh);jobs[0][0].users_collection[0].objects.link(obj)
 mask=bpy.data.materials['Federation Atrium clipped source mask'];recovery={}
 for o,records in jobs:
  backup=o.data.copy();backup.name=o.name+' before NGV nested panels';backup.use_fake_user=True;o['ngv_panel_original_mesh']=backup.name;slot=len(o.data.materials);o.data.materials.append(mask)
  for rec in records:o.data.polygons[rec['face']].material_index=slot
  recovery[o.name]={'mesh':backup.name,'faces':len(records)}
 limits=d['limits']
 obj['limits']=limits;obj['reference']='https://fedsquare.com/history-design';s[key]='visible-face-nested-five-v1'
 (r/'docs/federation-ngv-panel-audit.json').write_text(json.dumps({'triangles':len(fs),'recovery':recovery,'limits':limits,'reference':obj['reference']},indent=2)+'\n');print('NGV_NESTED_PANELS_APPLIED',len(fs),flush=True)
else:print('NGV_NESTED_PANELS_ALREADY_APPLIED',flush=True)
