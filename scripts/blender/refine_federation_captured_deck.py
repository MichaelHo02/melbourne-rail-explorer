"""Partial captured-height Federation deck. Own materials; source geometry retained.
Idempotent revision guard prevents repeated elevation shifts.
"""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
root=Path(bpy.data.filepath).resolve().parents[3]
KEY='federation_captured_height_deck_revision'
def apply_federation_deck():
 if bpy.context.scene.get(KEY):
  assert bpy.context.scene[KEY]=='captured-height-v1'
  for label in ['Federation fitted captured-height deck','Federation approximate deck closure walls','Federation approximate building base closures']:assert bpy.data.objects.get(label),label
  print('Federation deck already applied; no duplicate shifts',flush=True);return
 sections=json.loads((root/'assets/source/environment/federation-ground-datum-sections.json').read_text());byid={p['id']:p for p in sections};report={}
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
 for p in sections:
  o=bpy.data.objects.get('survey_'+p['id'])
  if o:o.location.z+=p['offset'];report[o.name]=len(o.data.vertices)
 labels=['Authored grouped window bays - varied low rise','Authored low rise sill and lintel bands','Authored roof edge cornices','Authored rooftop equipment - illustrative','Continuous surveyed roofs - authored finishes','Authored short low-rise window bays','Federation Square - authored triangular cladding']
 for name in labels:
  o=bpy.data.objects.get(name)
  if not o or o.type!='MESH':continue
  m=o.data;attrib=m.attributes.get('source_section');changes={};conflicts=set();selected_faces=set()
  for f in m.polygons:
   p=byid.get(str(attrib.data[f.index].value)) if attrib else None
   if not p:
    v=f.center
    if not 35<v.x<320 or not -60<v.y<155:continue
    choices=[p for p in sections if p['id']!='20246' and p['base']-2<v.z<p['base']+p['height']+2 and (inside(v.x,v.y,p['ring']) or dist(v.x,v.y,p['ring'])<.4)]
    if not choices:continue
    p=min(choices,key=lambda p:abs(v.z-(p['base']+p['height'])))
   selected_faces.add(f.index)
   for j in f.vertices:
    if j in changes and abs(changes[j]-p['offset'])>.01:conflicts.add(j)
    changes[j]=p['offset']
  assert not conflicts,(name,len(conflicts))
  shared=[f.index for f in m.polygons if f.index not in selected_faces and any(j in changes for j in f.vertices)]
  assert not shared,(name,"selected vertices also belong to unselected faces",len(shared))
  print("OWNERSHIP_CLOSED",name,len(selected_faces),len(changes),flush=True)
  for j,d in changes.items():m.vertices[j].co.z+=d
  m.update();report[name]=len(changes)
 for name in ['Federation Square - authored gable roof profiles','Federation Square - authored gable edge trim','Federation Square - authored zinc seams']:
  o=bpy.data.objects.get(name)
  if o:o.location.z+=4;report[name]='whole object +4m'
 
 
 flat=bpy.data.objects['Federation Square - authored approximate sandstone plaza'];flat.hide_render=True;flat.hide_set(True)
 d=json.loads((root/'assets/source/environment/federation-fitted-deck.json').read_text())
 wall=bpy.data.materials.new('Authored Federation deck walls - approximate');wall.use_nodes=True;p=wall.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.32,.26,.20,1);p.inputs['Roughness'].default_value=.86
 for name,v,f,mat in [('Federation fitted captured-height deck',d['vertices'],d['faces'],flat.data.materials[0]),('Federation approximate deck closure walls',d['wall_vertices'],d['wall_faces'],wall)]:
  m=bpy.data.meshes.new(name);m.from_pydata(v,[],f);m.materials.append(mat);m.update();o=bpy.data.objects.new(name,m);flat.users_collection[0].objects.link(o);o['limits']=d['limits']
  assert all(p.area>0 for p in m.polygons)
 
 # Close presentation gaps between source-minimum building bases and fitted deck.
 from mathutils.bvhtree import BVHTree
 terrain=bpy.data.objects['Federation fitted captured-height deck'];bvh=BVHTree.FromObject(terrain,bpy.context.evaluated_depsgraph_get())
 vs=[];fs=[]
 for p in sections:
  if p['base']!=0:continue
  ring=p['ring'];top=p['offset'];n=len(ring)-1
  for i in range(n):
   a=ring[i];b=ring[(i+1)%n];base=[]
   for x,y in (a,b):
    loc,normal,index,distance=bvh.find_nearest(Vector((x,y,top)))
    base.append(loc.z if loc is not None else top)
   if max(top-base[0],top-base[1])<.05:continue
   j=len(vs);vs.extend([[a[0],a[1],top+.02],[b[0],b[1],top+.02],[b[0],b[1],min(top,base[1])-.05],[a[0],a[1],min(top,base[0])-.05]]);fs.append([j,j+1,j+2,j+3])
 m=bpy.data.meshes.new('Federation approximate building base closures');m.from_pydata(vs,[],fs);m.materials.append(wall);m.update();o=bpy.data.objects.new(m.name,m);flat.users_collection[0].objects.link(o);o['limits']='Authored base closures connect source minimum building extents to fitted captured terrain. Not surveyed podiums or entrance thresholds.'
 print('BUILDING_BASE_CLOSURES',len(fs),flush=True)
 # Raise mapped crowns and their trunk vertices together where deck supports them.
 shifts={}
 for o in bpy.data.objects:
  if not o.name.startswith('tree_') or o.hide_render:continue
  x,y=o.location.x,o.location.y
  if not (50<x<310 and -45<y<115):continue
  hit,normal,index,distance=bvh.ray_cast(Vector((x,y,20)),Vector((0,0,-1)),30)
  if hit is not None:
   dz=hit.z-.32;o.location.z+=dz;shifts[(round(x,3),round(y,3))]=dz;o['federation_ground_offset']=dz
 o=bpy.data.objects.get('Expanded authored tree trunks')
 if o:
  for i in range(0,len(o.data.vertices),8):
   vs2=[o.data.vertices[j] for j in range(i,min(i+8,len(o.data.vertices)))];x=sum(v.co.x for v in vs2)/len(vs2);y=sum(v.co.y for v in vs2)/len(vs2);dz=shifts.get((round(x,3),round(y,3)),0)
   for v in vs2:v.co.z+=dz
  o.data.update()
 print('GROUNDED_TREES',len(shifts),flush=True)
 bpy.context.scene[KEY]='captured-height-v1'
 bpy.context.scene['federation_deck_limits']=d['limits']+' '+d['remaining']
apply_federation_deck()
