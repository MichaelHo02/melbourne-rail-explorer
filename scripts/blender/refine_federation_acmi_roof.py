"""Fit ACMI upper envelope and existing cap to capture plane, retaining mesh backups."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
r=Path(bpy.data.filepath).resolve().parents[3];s=bpy.context.scene;key='federation_acmi_roof_revision'
if not s.get(key):
 d=json.loads((r/'assets/source/environment/federation-acmi-roof-fit.json').read_text());source=bpy.data.objects['survey_17199'];world=[source.matrix_world@v.co for v in source.data.vertices];base=min(v.z for v in world);oldtop=max(v.z for v in world);ring=[v for v in world if abs(v.z-base)<.001];c=d['plane']
 def height(x,y):return c[0]*x+c[1]*y+c[2]
 def within(x,y):
  inside=False
  for a,b in zip(ring,ring[1:]+ring[:1]):
   dx,dy=b.x-a.x,b.y-a.y;t=max(0,min(1,((x-a.x)*dx+(y-a.y)*dy)/max(dx*dx+dy*dy,1e-12)))
   if math.hypot(x-a.x-t*dx,y-a.y-t*dy)<.002:return True
   if (a.y>y)!=(b.y>y) and x<(b.x-a.x)*(y-a.y)/(b.y-a.y)+a.x:inside=not inside
  return inside
 jobs=[(source,set(range(len(source.data.vertices))),[p.index for p in source.data.polygons if p.normal.z>.9])];cladding=bpy.data.objects['Federation ACMI and Beer Deluxe - authored triangular cladding'];a=cladding.data.attributes['source_section'];ids={i for p,v in zip(cladding.data.polygons,a.data) if v.value==17199 for i in p.vertices};assert ids;jobs.append((cladding,ids,[]))
 for o in bpy.data.objects:
  if o.type!='MESH' or not o.name.startswith('Continuous surveyed roofs - authored finishes'):continue
  selected=[]
  for p in o.data.polygons:
   vs=[o.matrix_world@o.data.vertices[i].co for i in p.vertices]
   if p.normal.z>.9 and all(abs(v.z-oldtop)<.002 and within(v.x,v.y) for v in vs):selected.append(p.index)
  if not selected:continue
  ids={i for j in selected for i in o.data.polygons[j].vertices};assert not any(any(i in ids for i in p.vertices) for p in o.data.polygons if p.index not in selected),'Shared roof vertices need separate handling';jobs.append((o,ids,selected))
 assert any(faces for o,_,faces in jobs if o is not source),'No matching saved cap; abort before mutation'
 report={}
 for o,ids,faces in jobs:
  backup=o.data.copy();backup.name=o.name+' before ACMI slope';backup.use_fake_user=True;o['acmi_roof_original_mesh']=backup.name
  for i in ids:
   v=o.data.vertices[i];q=o.matrix_world@v.co;ratio=max(0,min(1,(q.z-base)/(oldtop-base)));q.z=base+ratio*(height(q.x,q.y)-base);v.co=o.matrix_world.inverted()@q
  if faces:
   slot=len(o.data.materials);o.data.materials.append(bpy.data.materials['Authored Federation Square zinc'])
   for i in faces:
    p=o.data.polygons[i];mat=o.data.materials[p.material_index]
    if not (mat and mat.use_nodes and any(n.type=='BSDF_TRANSPARENT' for n in mat.node_tree.nodes)):p.material_index=slot
  o.data.update();report[o.name]={'vertices':len(ids),'cap_faces':len(faces)}
 s[key]='captured-slope-v1';(r/'docs/federation-acmi-roof-audit.json').write_text(json.dumps({'objects':report,'base':base,'previous_top':oldtop,'fit_inliers':d['inliers'],'median_residual':d['median_residual'],'limits':d['limits'],'original_meshes_recoverable':True},indent=2)+'\n');print('ACMI_ROOF_SLOPE_APPLIED',report,flush=True)
else:print('ACMI_ROOF_ALREADY_APPLIED',flush=True)
