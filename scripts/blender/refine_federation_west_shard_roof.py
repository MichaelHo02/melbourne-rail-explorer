"""Reversible source-supported western shard roof, with closed replacement coverage."""
import bpy,json,math
from pathlib import Path
r=Path(bpy.data.filepath).resolve().parents[3];key='federation_west_shard_roof_revision'
if not bpy.context.scene.get(key):
 d=json.loads((r/'assets/source/environment/federation-west-shard-roof-fit.json').read_text());c=d['plane'];base=d['base'];top=d['old_top'];report={}
 def z(x,y):return c[0]*x+c[1]*y+c[2]
 def near(x,y,margin=.002):
  ring=d['ring'];inside=False;distance=1e9
  for a,b in zip(ring,ring[1:]+ring[:1]):
   if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:inside=not inside
   dx=b[0]-a[0];dy=b[1]-a[1];den=dx*dx+dy*dy;t=max(0,min(1,((x-a[0])*dx+(y-a[1])*dy)/den)) if den else 0;distance=min(distance,math.hypot(x-a[0]-t*dx,y-a[1]-t*dy))
  return inside or distance<margin
 for name in ['survey_4607','Federation Square - authored triangular cladding']:
  o=bpy.data.objects[name];backup=o.data.copy();backup.name=name+' before western roof';backup.use_fake_user=True;o['west_roof_original_mesh']=backup.name
  if name=='survey_4607':ids=set(range(len(o.data.vertices)))
  else:
   attr=o.data.attributes['source_section'];ids={j for p in o.data.polygons if attr.data[p.index].value==4607 for j in p.vertices}
  for j in ids:
   v=o.data.vertices[j];q=o.matrix_world@v.co;t=max(0,min(1,(q.z-base)/(top-base)));q.z=base+(z(q.x,q.y)-base)*t;v.co=o.matrix_world.inverted()@q
  o.data.update();report[name]=len(ids)
 mesh=bpy.data.meshes.new('Federation captured western shard roof');mesh.from_pydata(d['vertices'],[],d['faces']);mesh.materials.append(bpy.data.materials['Authored Federation Square zinc']);mesh.update()
 # Shapely constrained triangles consistently counterclockwise; enforce explicitly.
 if any(p.normal.z<0 for p in mesh.polygons):
  mesh.clear_geometry();mesh.from_pydata(d['vertices'],[],[tuple(reversed(f)) for f in d['faces']]);mesh.update()
 assert all(p.normal.z>0 and p.area>0 for p in mesh.polygons)
 o=bpy.data.objects.new(mesh.name,mesh);bpy.data.collections['CITY - reference-authored landmarks'].objects.link(o);o['source']='https://discover.data.vic.gov.au/dataset/city-of-melbourne-3d-textured-mesh-photomesh-2020';o['limits']=d['limits']
 mat=bpy.data.materials.new('Federation western roof covered cap mask');mat.use_nodes=True;ns=mat.node_tree.nodes;ns.clear();a=ns.new('ShaderNodeBsdfTransparent');b=ns.new('ShaderNodeOutputMaterial');mat.node_tree.links.new(a.outputs[0],b.inputs['Surface'])
 cap=bpy.data.objects['Continuous surveyed roofs - authored finishes'];selected=[]
 for p in cap.data.polygons:
  q=cap.matrix_world@p.center
  if abs(q.z-top)>.03 or p.normal.z<.9 or not 97<q.x<111 or not 72<q.y<97:continue
  if all(near(*(cap.matrix_world@cap.data.vertices[j].co)[:2]) for j in p.vertices):selected.append(p.index)
 assert selected,'No completely covered source caps found'
 idx=len(cap.data.materials);cap.data.materials.append(mat);original={str(i):cap.data.polygons[i].material_index for i in selected};txt=bpy.data.texts.new('Federation western cap original assignments.json');txt.write(json.dumps(original));cap['west_roof_cap_recovery']=txt.name
 for i in selected:cap.data.polygons[i].material_index=idx
 for label in ['Authored roof edge cornices','Authored rooftop equipment - illustrative']:
  detail=bpy.data.objects.get(label)
  if not detail:continue
  chosen=[]
  for p in detail.data.polygons:
   q=detail.matrix_world@p.center
   if not 97<q.x<112 or not 71<q.y<98 or abs(q.z-top)>1:continue
   if all(near(*(detail.matrix_world@detail.data.vertices[j].co)[:2],margin=.7) for j in p.vertices):chosen.append(p.index)
  if chosen:
   slot=len(detail.data.materials);detail.data.materials.append(mat);original={str(i):detail.data.polygons[i].material_index for i in chosen};txt=bpy.data.texts.new(label+' western roof recovery.json');txt.write(json.dumps(original));detail['west_roof_detail_recovery']=txt.name
   for i in chosen:detail.data.polygons[i].material_index=slot
   report[label+' hidden illustrative faces']=len(chosen)
 report['masked_fully_covered_cap_faces']=len(selected);report['replacement_faces']=len(mesh.polygons);report['limits']=d['limits'];(r/'docs/federation-west-shard-roof-audit.json').write_text(json.dumps(report,indent=2));bpy.context.scene[key]='captured-west-plane-v1';print('WEST_SHARD_APPLIED',report,flush=True)
else:print('WEST_SHARD_ALREADY_APPLIED',flush=True)
