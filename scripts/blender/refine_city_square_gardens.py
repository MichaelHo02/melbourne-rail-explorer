"""Authored garden edges and planting on interpreted City Square bed locations."""
import bpy,bmesh,json,math,random
from pathlib import Path
from mathutils import Vector
R=Path(bpy.data.filepath).resolve().parents[3];d=json.loads((R/'assets/source/environment/city-square-authored-surfaces.json').read_text());name='City Square authored garden details';collection=bpy.data.collections.get(name)
if collection:
 for o in list(collection.objects):bpy.data.objects.remove(o,do_unlink=True)
else:
 collection=bpy.data.collections.new(name);bpy.context.scene.collection.children.link(collection)
v=[];faces=[]
for ring in d['garden_rings']:
 for i,a in enumerate(ring):
  b=ring[(i+1)%len(ring)];dx=b[0]-a[0];dy=b[1]-a[1];length=math.hypot(dx,dy);nx=-dy/length*.11;ny=dx/length*.11;k=len(v)
  for z in [.34,.8]:v.extend([(a[0]+nx,a[1]+ny,z),(b[0]+nx,b[1]+ny,z),(b[0]-nx,b[1]-ny,z),(a[0]-nx,a[1]-ny,z)])
  faces.extend([[k+j for j in q] for q in [[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]])
mesh=bpy.data.meshes.new(name);mesh.from_pydata(v,[],faces);mesh.materials.append(bpy.data.materials['Authored central CBD bluestone - coverage illustrative']);mesh.update();bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free();mesh.update();o=bpy.data.objects.new('City Square authored stone garden edges',mesh);collection.objects.link(o)
o['limits']='Plan-led bed locations; .22 m width and .46 m rise are authored assumptions, not measured wall profiles. Shared paving shader is an approximate stone finish.'
# Ray crossing tests keep shrubs within each bed, away from its edges.
def inside(x,y,ring):
 hit=False
 for i,a in enumerate(ring):
  b=ring[(i+1)%len(ring)]
  if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:hit=not hit
 return hit
nearby=[o.location.copy() for o in bpy.data.objects if o.name.startswith('tree_') and o.type=='MESH' and not o.hide_render and -60<o.location.x<70 and 190<o.location.y<330]
rng=random.Random(62026);count=0
for ring in d['garden_rings']:
 x0=min(a[0] for a in ring);x1=max(a[0] for a in ring);y0=min(a[1] for a in ring);y1=max(a[1] for a in ring);x=x0+.7
 while x<x1-.5:
  y=y0+.7
  while y<y1-.5:
   xx=x+rng.uniform(-.15,.15);yy=y+rng.uniform(-.15,.15)
   if all(inside(xx+dx,yy+dy,ring) for dx,dy in [(0,0),(.5,0),(-.5,0),(0,.5),(0,-.5)]) and not any((Vector((xx,yy,0))-Vector((t.x,t.y,0))).length<1.3 for t in nearby):
    shrub=bpy.data.objects.new('City Square authored shrub '+str(count),bpy.data.meshes['Authored fine foliage crown '+str(count%7)]);collection.objects.link(shrub);height=rng.uniform(.45,.8);shrub.location=(xx,yy,.34+height*.65);shrub.scale=(rng.uniform(.5,.75),rng.uniform(.5,.75),height);shrub.rotation_euler.z=rng.uniform(0,math.tau);shrub['limits']='Illustrative low foliage, not measured planting species, density or condition.';count+=1
   y+=1.25
  x+=1.25
collection['reference']=d['reference'];collection['limits']='Development-plan interpretation aligned approximately to old parcel; current installed geometry and planting unverified.'
print('VERIFIED City Square garden details',len(d['garden_rings']),'beds',len(faces),'wall faces',count,'illustrative shrubs',flush=True)
