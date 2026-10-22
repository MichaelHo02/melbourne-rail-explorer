"""Recorded gable forms on simple survey envelopes; pitch is authored."""
import bpy,json,math
from pathlib import Path
root=globals().get('root') or Path(bpy.data.filepath).resolve().parents[3];name='Recorded low-rise gables - authored pitch'
if not bpy.data.objects.get(name):
 d=json.loads((root/'assets/source/environment/city-survey-gables.json').read_text());rows=d['rows'];grid={}
 for r in rows:
  xs=[p[0] for p in r['ring']];ys=[p[1] for p in r['ring']]
  for ix in range(math.floor(min(xs)/50),math.floor(max(xs)/50)+1):
   for iy in range(math.floor(min(ys)/50),math.floor(max(ys)/50)+1):grid.setdefault((ix,iy),[]).append(r)
 def inside(x,y,r):
  hit=False
  for a,b in zip(r['ring'],r['ring'][1:]):
   if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:hit=not hit
  return hit
 def height(x,y,r):return r['top']-r['drop']*abs(x*r['normal'][0]+y*r['normal'][1]-r['mid'])/r['half']
 v=[];f=[];mi=[];mats=[];active=[]
 for r in rows:
  o=bpy.data.objects.get('survey_'+r['id'])
  if not o or o.hide_render:continue
  active.append(r);mat=o.data.materials[0]
  if mat not in mats:mats.append(mat)
  idx=mats.index(mat)
  # New roof triangles plus wall infills down to the original eave silhouette.
  for face in r['faces']:
   i=len(v);v.extend(face);f.append((i,i+1,i+2));mi.append(0)
  for a,b in zip(r['ring'],r['ring'][1:]):
   za,zb=height(*a,r),height(*b,r);i=len(v);v.extend([(*a,r['top']-r['drop']),(*b,r['top']-r['drop']),(*b,zb),(*a,za)]);f.append((i,i+1,i+2,i+3));mi.append(idx+1)
  # Retain the source coordinates; top boundary lowers only to authored eaves.
  for vert in o.data.vertices:
   if abs(vert.co.z-r['top'])<.03:vert.co.z=r['top']-r['drop']
  o['roof_basis']='Recorded Gable type; authored pitch/ridge direction; source maximum retained.'
 removed={}
 for o in list(bpy.data.objects):
  if o.type!='MESH' or not (o.name=='Continuous surveyed roofs - authored finishes' or any(t in o.name.lower() for t in ['window bays','window trim','rooftop equipment'])):continue
  keep=[]
  for p in o.data.polygons:
   x,y,z=p.center;cut=False
   for r in grid.get((math.floor(x/50),math.floor(y/50)),[]):
    if z>=height(x,y,r)-.05 and z<r['top']+4 and inside(x,y,r):cut=True;break
   if not cut:keep.append(p)
  if len(keep)==len(o.data.polygons):continue
  removed[o.name]=len(o.data.polygons)-len(keep);m=bpy.data.meshes.new(o.name+' recorded gable cutout');m.from_pydata([tuple(v.co) for v in o.data.vertices],[],[tuple(p.vertices) for p in keep])
  for mat in o.data.materials:m.materials.append(mat)
  for p,q in zip(m.polygons,keep):p.material_index=q.material_index
  m.update();o.data=m
 m=bpy.data.meshes.new(name);m.from_pydata(v,[],f);roof=bpy.data.materials['Authored light zinc roof finish'];m.materials.append(roof)
 for mat in mats:m.materials.append(mat)
 for p,i in zip(m.polygons,mi):p.material_index=i
 m.update();o=bpy.data.objects.new(name,m);bpy.data.collections['CITY - surveyed envelopes with authored facade materials'].objects.link(o);o['limits']=d['limits'];o['building_count']=len(active);o['cutouts']=json.dumps(removed);print('VERIFIED recorded gables',len(active),'faces',len(f),'cutouts',removed,flush=True)
endname='Recorded low-rise gable end infills'
if not bpy.data.objects.get(endname):
 d=json.loads((root/'assets/source/environment/city-survey-gables.json').read_text());v=[];f=[];mi=[];mats=[]
 for r in d['rows']:
  o=bpy.data.objects.get('survey_'+r['id'])
  if not o or o.hide_render:continue
  mat=o.data.materials[0]
  if mat not in mats:mats.append(mat)
  idx=mats.index(mat);nx,ny=r['normal']
  for a,b in zip(r['ring'],r['ring'][1:]):
   av=a[0]*nx+a[1]*ny-r['mid'];bv=b[0]*nx+b[1]*ny-r['mid']
   if av*bv<0:
    t=av/(av-bv);c=(a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1]));i=len(v);v.extend([(*a,r['top']-r['drop']),(*b,r['top']-r['drop']),(*c,r['top'])]);f.append((i,i+1,i+2));mi.append(idx)
 m=bpy.data.meshes.new(endname);m.from_pydata(v,[],f)
 for mat in mats:m.materials.append(mat)
 for p,i in zip(m.polygons,mi):p.material_index=i
 m.update();o=bpy.data.objects.new(endname,m);bpy.data.collections['CITY - surveyed envelopes with authored facade materials'].objects.link(o);print('VERIFIED gable end infills',len(f),flush=True)
