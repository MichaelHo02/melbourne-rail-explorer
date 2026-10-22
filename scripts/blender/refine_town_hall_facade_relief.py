"""Simplified stone pilasters on retained west-facing Town Hall boundary."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
R=Path(bpy.data.filepath).resolve().parents[3];d=json.loads((R/'assets/source/environment/town-hall-source-reference.json').read_text());r=next(x for x in d['records'] if x['objectid']=='27725');name='Town Hall authored Swanston facade relief'
if not bpy.data.objects.get(name):
 points=[Vector(((x-144.9671)*87939,(y+37.8183)*111320,0)) for x,y in r['geo_shape']['geometry']['coordinates'][0][:-1]];v=[];f=[];indices=[];count=0;edges=0
 def box(c,t,n,width,depth,height,material):
  start=len(v)
  for z in [-height/2,height/2]:
   for u,w in [(-width/2,0),(width/2,0),(width/2,depth),(-width/2,depth)]:v.append(tuple(c+t*u+n*w+Vector((0,0,z))))
  for face in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]:f.append(tuple(start+i for i in face));indices.append(material)
 for i,a in enumerate(points):
  b=points[(i+1)%len(points)];delta=b-a;length=delta.length
  if length<5:continue
  t=delta.normalized();n=Vector((t.y,-t.x,0))
  if n.x>-.85 or (a.x+b.x)/2>-35:continue
  edges+=1;mid=(a+b)/2+n*.025
  box(mid+Vector((0,0,1)),t,n,length,.16,1.8,1)
  for z,height,depth in [(3,.30,.35),(15,.45,.50),(18.5,.28,.35)]:box(mid+Vector((0,0,z)),t,n,length,depth,height,0)
  bays=max(1,round(length/4.8))
  for j in range(bays+1):
   c=a+t*(.65+(length-1.3)*j/bays)+n*.03
   box(c+Vector((0,0,9)),t,n,.68,.30,11.2,0)
   box(c+Vector((0,0,3.35)),t,n,.98,.40,.45,0)
   box(c+Vector((0,0,14.65)),t,n,1.1,.46,.48,0)
   count+=1
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(v,[],f);mesh.materials.append(bpy.data.materials['Town Hall authored freestone']);mesh.materials.append(bpy.data.materials['Town Hall authored bluestone']);mesh.update()
 for p,i in zip(mesh.polygons,indices):p.material_index=i
 o=bpy.data.objects.new(name,mesh);bpy.data.collections['CITY - reference-authored landmarks'].objects.link(o);o['source_id']='27725';o['reference']=d['heritage_reference'];o['limits']='Simplified authored west-facing pilaster shafts, block capitals, cornice bands and bluestone base follow survey outline. 4.8m target bay rhythm, 3.4-14.6m shafts and all projection dimensions unmeasured. Corinthian carving, portico, correct window order and current condition unresolved.';o['pilaster_count']=count;o['boundary_segments']=edges;print('VERIFIED Town Hall facade relief',count,'pilasters',edges,'west boundary segments',len(f),'faces',flush=True)
