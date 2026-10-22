"""Authored approximate canopy posts. Aerial scan does not resolve column bases.
Eight metre bays, .24m post diameter, .18m beams and local1.2m platform height
are presentation assumptions, not surveyed station construction dimensions.
"""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(bpy.data.filepath).resolve().parents[3];scan=bpy.data.objects['Flinders station - municipal 2020 scan, authored colours'];data=json.loads((R/'assets/source/environment/flinders-captured-canopy-panels.json').read_text());zones=[z['ring'] for z in json.loads((R/'assets/source/environment/flinders-scan-material-zones.json').read_text())['zones'] if z['source_id'] in ['1145','1146','1148']]
def inside(x,y,r):
 a=False
 for i,p in enumerate(r):
  q=r[i-1]
  if (p[1]>y)!=(q[1]>y) and x<(q[0]-p[0])*(y-p[1])/(q[1]-p[1])+p[0]:a=not a
 return a
def protect(v):return any(inside(v.x,v.y,r) for r in zones)
def roofz(v,p):
 c=p['plane_coefficients'];return c[0]*v.x+c[1]*v.y+c[2]+p['plane_lift_above_grid_m']
name='Flinders canopy authored approximate supports';old=bpy.data.objects.get(name)
if old:
 oldmesh=old.data;bpy.data.objects.remove(old,do_unlink=True)
 if oldmesh.users==0:bpy.data.meshes.remove(oldmesh)
bvh=BVHTree.FromObject(scan,bpy.context.evaluated_depsgraph_get());verts=[];faces=[];bases=[];skipped=0;assumed={}
angle=math.atan(.36);co=math.cos(angle);si=math.sin(angle)
def xy(u,v):return (co*u-si*v,si*u+co*v)
def box(a,b,width,depth):
 a=Vector(a);b=Vector(b);n=Vector((-(b-a).y,(b-a).x,0)).normalized()*width/2;start=len(verts);verts.extend([a+n,a-n,b-n,b+n,a+n-Vector((0,0,depth)),a-n-Vector((0,0,depth)),b-n-Vector((0,0,depth)),b+n-Vector((0,0,depth))]);faces.extend(tuple(start+j for j in f) for f in [(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)])
def post(x,y,z,top):
 start=len(verts)
 for h in [z,top]:
  for i in range(12):verts.append((x+.12*math.cos(i*math.tau/12),y+.12*math.sin(i*math.tau/12),h))
 for i in range(12):j=(i+1)%12;faces.append((start+i,start+j,start+12+j,start+12+i))
 faces.append(tuple(start+i for i in reversed(range(12))));faces.append(tuple(start+12+i for i in range(12)))
for p in data['panels']:
 ring=[(co*v[0]+si*v[1],-si*v[0]+co*v[1]) for v in p['boundaries'][0]];umin=min(q[0] for q in ring);umax=max(q[0] for q in ring)
 for u in range(math.ceil((umin+3)/8)*8,math.floor((umax-3)/8)*8+1,8):
  cross=[]
  for i,a in enumerate(ring):
   b=ring[i-1]
   if (a[0]>u)!=(b[0]>u):cross.append(a[1]+(u-a[0])*(b[1]-a[1])/(b[0]-a[0]))
  if len(cross)!=2:skipped+=1;continue
  lo,hi=sorted(cross)
  if hi-lo<3:skipped+=1;continue
  points=[]
  for v in [lo+.8,hi-.8]:
   x,y=xy(u,v)
   if any(inside(x,y,r) for r in p['boundaries'][1:]):continue
   rz=roofz(Vector((x,y,0)),p);hit,n,index,d=bvh.ray_cast(Vector((x,y,rz-.9)),Vector((0,0,-1)),8)
   assumed[(x,y)]=hit is None
   if hit is None:hit=Vector((x,y,1.2));n=Vector((0,0,1))
   if n.z<.6 or not -1.5<hit.z<rz-2.0 or protect(hit):continue
   points.append((x,y,hit.z,roofz(Vector((x,y,0)),p)-data['assumptions']['fascia_depth_m']))
  if len(points)!=2:skipped+=1;continue
  for x,y,z,top in points:post(x,y,z,top-.18);bases.append({'panel':p['index'],'point':[x,y,z],'top':top-.18,'base_assumed':assumed[(x,y)]})
  a,b=points;box((a[0],a[1],a[3]),(b[0],b[1],b[3]),.18,.18)
mesh=bpy.data.meshes.new('Flinders canopy authored approximate supports');mesh.from_pydata(verts,[],faces);mesh.update();mesh.materials.append(bpy.data.materials['FSS iron'] if bpy.data.materials.get('FSS iron') else bpy.data.materials['Flinders canopy authored folded zinc fascia']);obj=bpy.data.objects.new('Flinders canopy authored approximate supports',mesh);scan.users_collection[0].objects.link(obj)

obj.matrix_world=scan.matrix_world.copy();obj['source']=data['source'];obj['limits']='Approximate authored support arrangement. Aerial scan does not resolve column bases; local1.2m fallback platform height,8m bays,.24m post diameter and.18m crossbeams are assumptions.'
report={'support_posts':len(bases),'skipped_bays':skipped,'bases':bases,'faces':len(mesh.polygons),'limits':obj['limits'],'photographic_textures':False}
assert len(bases)>0 and all(p.area>1e-9 for p in mesh.polygons)
(R/'docs/flinders-canopy-support-repair-audit.json').write_text(json.dumps(report,indent=2)+'\n');print('CANOPY_SUPPORTS',len(bases),skipped,flush=True)
