"""Partial captured-height street reconciliation; no photographic textures.
Apply only to saved fitted-deck revision. Revision guard prevents repeat shifts.
"""
import bpy,json,math,bmesh
from pathlib import Path
import numpy as np
from mathutils import Vector
root=Path(bpy.data.filepath).resolve().parents[3]
KEY='federation_street_levels_revision'
def apply_street_levels():
 if bpy.context.scene.get(KEY):
  assert bpy.context.scene[KEY]=='captured-streets-v1'
  print('Street reconciliation already applied; no duplicate shifts',flush=True);return
 assert bpy.context.scene.get('federation_captured_height_deck_revision')=='captured-height-v1'
 model=json.loads((root/'assets/source/environment/federation-street-level-model.json').read_text());samples=np.array(model['samples']);cache={};audit={}
 def field(x,y):
  key=(round(x,3),round(y,3))
  if key in cache:return cache[key]
  edge=min(x+80,260-x,y+60,250-y);w=max(0,min(1,edge/50))
  if not w:return (0,0)
  ds=((samples[:,:2]-[x,y])**2).sum(axis=1);ids=np.argpartition(ds,7)[:8];d=float(np.min(ds))**.5;w*=max(0,min(1,(40-d)/28));weights=1/np.maximum(ds[ids],1);h=float((samples[ids,2]*weights).sum()/weights.sum());cache[key]=(h,w);return h,w
 def intersects(a,b):return max(a.x,b.x)>-80 and min(a.x,b.x)<260 and max(a.y,b.y)>-60 and min(a.y,b.y)<250
 labels=['Continuous Vicmap road surface','Continuous authored pavement bands','Authored kerbs - retained road edges','Authored CBD junction crossings - illustrative','Authored CBD midblock lane guides - illustrative','Authored illustrative lane dashes']
 for name in labels:
  o=bpy.data.objects.get(name)
  if not o or o.hide_render:continue
  m=o.data;before=len(m.vertices);bm=bmesh.new();bm.from_mesh(m)
  for step in range(9):
   edges=[e for e in bm.edges if e.calc_length()>8 and intersects(e.verts[0].co,e.verts[1].co)]
   if not edges:break
   bmesh.ops.subdivide_edges(bm,edges=edges,cuts=1,use_grid_fill=True)
  bm.to_mesh(m);bm.free();count=0
  for v in m.vertices:
   h,w=field(v.co.x,v.co.y)
   if w<=0:continue
   v.co.z+=(h-.255)*w
   if name=='Continuous authored pavement bands':v.co.z+=.18*w
   count+=1
  m.update();audit[name]={'before_vertices':before,'after_vertices':len(m.vertices),'shifted':count};print('STREET_LIFT',name,audit[name],flush=True)
 # Refit bounded base ground while preserving the City Square portal cut-out.
 for name,d in json.loads((root/'assets/source/environment/federation-street-ground-patch.json').read_text()).items():
  o=bpy.data.objects[name];old=o.data;m=bpy.data.meshes.new(name+' street context patch');m.from_pydata(d['vertices'],[],d['faces']);
  for mat in old.materials:m.materials.append(mat)
  for f,mi in zip(m.polygons,d['materials']):f.material_index=mi
  for v in m.vertices:
   h,w=field(v.co.x,v.co.y);v.co.z+=(h-.255)*w
  m.update();o.data=m;audit[name]={'vertices':len(m.vertices),'faces':len(m.polygons)}
 # City Square details share the same bounded ground deformation.
 for o in bpy.data.objects:
  if not o.name.startswith('City Square '):continue
  if o.type=='MESH' and o.data.users==1:
   matrix=o.matrix_world;inverse=matrix.inverted()
   for v in o.data.vertices:
    world=matrix@v.co;h,w=field(world.x,world.y);world.z+=(h-.255)*w;v.co=inverse@world
   o.data.update()
  else:
   h,w=field(o.location.x,o.location.y);o.location.z+=(h-.255)*w
 # Match all section-owned details, with shared-vertex isolation assertions.
 sections=model['sections'];byid={p['id']:p for p in sections}
 def inside(x,y,r):
  a=False
  for i,p in enumerate(r):
   q=r[i-1]
   if (p[1]>y)!=(q[1]>y) and x<(q[0]-p[0])*(y-p[1])/(q[1]-p[1])+p[0]:a=not a
  return a
 def dist(x,y,r):
  best=1e9
  for i,a in enumerate(r):
   b=r[i-1];dx=b[0]-a[0];dy=b[1]-a[1];den=dx*dx+dy*dy;t=max(0,min(1,((x-a[0])*dx+(y-a[1])*dy)/den)) if den else 0;best=min(best,math.hypot(x-a[0]-t*dx,y-a[1]-t*dy))
  return best
 shifted_surveys=set()
 for p in sections:
  pool=[o for o in bpy.data.objects if o.name.startswith('survey_'+p['id']) and str(o.get('source_id',''))==p['id'] and o.name not in shifted_surveys]
  if not pool:continue
  cx=sum(x for x,y in p['ring'])/len(p['ring']);cy=sum(y for x,y in p['ring'])/len(p['ring'])
  def distance(o):
   vs=o.data.vertices;return (sum(v.co.x for v in vs)/len(vs)-cx)**2+(sum(v.co.y for v in vs)/len(vs)-cy)**2
  o=min(pool,key=distance);o.location.z+=p['offset'];shifted_surveys.add(o.name)
 for name in ['Authored grouped window bays - varied low rise','Authored low rise sill and lintel bands','Authored roof edge cornices','Authored rooftop equipment - illustrative','Continuous surveyed roofs - authored finishes','Authored short low-rise window bays']:
  o=bpy.data.objects.get(name)
  if not o:continue
  m=o.data;changes={};chosen=set();conflicts=set()
  # Resolve whole connected strips: triangulation must not split an owner.
  parent=list(range(len(m.vertices)))
  def find(i):
   while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
   return i
  for f in m.polygons:
   component_root=find(f.vertices[0])
   for j in f.vertices[1:]:parent[find(j)]=component_root
  groups={}
  for f in m.polygons:groups.setdefault(find(f.vertices[0]),[]).append(f)
  for component in groups.values():
   ids={j for f in component for j in f.vertices};v=sum((m.vertices[j].co for j in ids),Vector())/len(ids)
   if not -180<v.x<350 or not -150<v.y<400:continue
   choices=[p for p in sections if p['base']-2<v.z<p['base']+p['height']+2 and (inside(v.x,v.y,p['ring']) or dist(v.x,v.y,p['ring'])<.4)]
   if not choices:continue
   p=min(choices,key=lambda p:abs(v.z-p['base']-p['height'])*10+dist(v.x,v.y,p['ring']))
   for f in component:chosen.add(f.index)
   for j in ids:changes[j]=p['offset']
  assert not conflicts,(name,'conflicting heights',len(conflicts))
  shared=[f.index for f in m.polygons if f.index not in chosen and any(j in changes for j in f.vertices)];assert not shared,(name,'shared unselected faces',len(shared))
  for j,d in changes.items():m.vertices[j].co.z+=d
  m.update();audit[name]={'shifted_vertices':len(changes)}
 offset=next(p['offset'] for p in sections if p['structure_id']=='819362')
 for o in bpy.data.objects:
  if o.name.startswith('St Pauls Cathedral -'):o.location.z+=offset
  if o.name.startswith('Authored signal site '):
   h,w=field(o.location.x,o.location.y);o.location.z+=(h-.255)*w
 shifts={}
 for o in bpy.data.objects:
  if not o.name.startswith('tree_') or o.hide_render or o.get('federation_ground_offset') is not None:continue
  h,w=field(o.location.x,o.location.y)
  if not w:continue
  dz=(h+.125-.32)*w;o.location.z+=dz;shifts[(round(o.location.x,3),round(o.location.y,3))]=dz
 o=bpy.data.objects.get('Expanded authored tree trunks')
 if o:
  for i in range(0,len(o.data.vertices),8):
   vs=[o.data.vertices[j] for j in range(i,min(i+8,len(o.data.vertices)))];x=sum(v.co.x for v in vs)/len(vs);y=sum(v.co.y for v in vs)/len(vs);dz=shifts.get((round(x,3),round(y,3)),0)
   for v in vs:v.co.z+=dz
  o.data.update()
 audit['trees']=len(shifts);audit['cathedral_offset']=offset;(root/'docs/federation-street-level-audit.json').write_text(json.dumps(audit,indent=2))
 bpy.context.scene[KEY]='captured-streets-v1'
 bpy.context.scene['federation_street_levels_limits']=model['limits']
apply_street_levels()
