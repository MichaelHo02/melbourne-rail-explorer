"""Forum Theatre survey envelope, with photo-informed Moorish facade and clock dome."""
import bpy,importlib.util,json,math,copy
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('frontage',Path(__file__).with_name('build_viaduct_frontage.py'));f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f);f.reset_scene()
ids=['20100','20101','20102','20103'];f.STRUCTURES['806370']={'objectIds':ids}
buildings=json.loads((ROOT/'public/data/buildings.json').read_text())['buildings']
tower=next(b for b in buildings if b['id']=='20100');tower_ring=tower['ring'][:-1];cx=sum(p[0] for p in tower_ring)/4;cz=sum(p[1] for p in tower_ring)/4;source_top=tower['height'];tower['height']=28
stone=f.material('Forum warm cream masonry',(.52,.43,.30),.92)
base=f.material('Forum sandstone base',(.36,.30,.22),.95)
trim=f.material('Forum carved pale stone',(.64,.55,.40),.89)
roof=f.material('Forum dark roof',(.12,.14,.13),.92)
glass=f.material('Forum recessed dark arches',(.035,.052,.05),.58)
copper=f.material('Forum aged copper dome',(.13,.24,.19),.64,.55)
bronze=f.material('Forum dome lattice bronze',(.29,.27,.14),.67,.45)
clock=f.material('Forum clock ivory',(.79,.76,.64),.84)
envelope,sections=f.union_sections(buildings,'806370',(stone,base,roof))
main=next(b for b in buildings if b['id']=='20101')
plinth=f.ring_mesh('Forum ground connection',main['ring'],-.94,main['base'])
plinth.data.materials.append(base);plinth['adaptation']='Authored plinth connects relative survey base to flat game terrain'
batches={k:([],[],m) for k,m in [('trim',trim),('glass',glass),('bronze',bronze),('clock',clock)]}
def polygon(kind,h,n,plane,points,projection=.05):
 vs,fs,_=batches[kind];start=len(vs);vs.extend(tuple(plane+h*x+Vector((0,0,y))+n*projection) for x,y in points);fs.append(tuple(range(start,len(vs))))
def strip(kind,h,n,plane,a,b,lo,hi,projection=.13):f.add_box_beam(*batches[kind][:2],h,n,plane,a,b,lo,hi,.10,projection)
def inside(x,y,ring):
 hit=False
 for a,b in zip(ring,ring[1:]+ring[:1]):
  if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:hit=not hit
 return hit
for face in envelope.data.polygons:
 n=face.normal
 if abs(n.z)>.03:continue
 pts=[envelope.data.vertices[i].co for i in face.vertices];h=Vector((-n.y,n.x,0)).normalized();ring=[(v.dot(h),v.z) for v in pts];a=min(p[0] for p in ring);b=max(p[0] for p in ring);lo=min(p[1] for p in ring);hi=max(p[1] for p in ring);plane=Vector((n.x,n.y,0))*pts[0].dot(n)
 if b-a<1:continue
 for y in [5,10.5,18,22.2,27.3]:
  if lo+.2<y<hi-.3:strip('trim',h,n,plane,a,b,y,y+.22,.3)
 bays=max(1,round((b-a)/3.3));step=(b-a)/bays
 for bottom in [6,12.3]:
  for col in range(bays):
   center=a+(col+.5)*step;r=min(.85,step*.3);spring=bottom+2.1
   if not all(inside(x,y,ring) for x in [center-r-.15,center+r+.15] for y in [bottom,spring+r+.15]):continue
   points=[(center-r,bottom),(center+r,bottom)]+[(center+r*math.cos(t*math.pi/12),spring+r*math.sin(t*math.pi/12)) for t in range(13)]
   polygon('glass',h,n,plane,points)
   for side in [-1,1]:strip('trim',h,n,plane,center+side*r-.12,center+side*r+.12,bottom,spring)
   for j in range(12):
    t=j*math.pi/12;u=(j+1)*math.pi/12
    polygon('trim',h,n,plane,[(center+(r+.15)*math.cos(t),spring+(r+.15)*math.sin(t)),(center+(r+.15)*math.cos(u),spring+(r+.15)*math.sin(u)),(center+r*math.cos(u),spring+r*math.sin(u)),(center+r*math.cos(t),spring+r*math.sin(t))],.15)
 # Clock faces only on the measured tower's upper shaft.
 if hi>27.9 and b-a<12 and lo<24:
  center=(a+b)/2;y=25;r=1.55
  polygon('clock',h,n,plane,[(center+r*math.cos(i*math.tau/48),y+r*math.sin(i*math.tau/48)) for i in range(48)],.18)
  for j in range(12):
   t=j*math.tau/12;x=center+1.25*math.cos(t);z=y+1.25*math.sin(t);strip('glass',h,n,plane,x-.065,x+.065,z-.13,z+.13,.20)
  strip('glass',h,n,plane,center-.05,center+.05,y,y+1.05,.22);strip('glass',h,n,plane,center,center+.8,y-.04,y+.04,.22)
# Dome fills the tower's upper survey volume; the source roof height is retained.
def cylinder(name,x,z,base_y,height,r1,r2,mat):
 bpy.ops.mesh.primitive_cone_add(vertices=24,radius1=r1,radius2=r2,depth=height,location=f.game_to_blender(x,base_y+height/2,z));o=bpy.context.object;o.name=name;o.data.materials.append(mat)
cylinder('Forum dome drum',cx,cz,28,1.1,3.4,3.4,stone)
verts=[];faces=[]
for j in range(13):
 t=j*math.pi/24;r=3.6*math.cos(t);y=29.1+4.7*math.sin(t)
 for i in range(48):verts.append(f.game_to_blender(cx+r*math.cos(i*math.tau/48),y,cz+r*math.sin(i*math.tau/48)))
for j in range(12):
 for i in range(48):faces.append((j*48+i,j*48+(i+1)%48,(j+1)*48+(i+1)%48,(j+1)*48+i))
f.make_mesh_object('Forum copper dome',verts,faces,copper,'Authored dome silhouette within surveyed tower height')
cylinder('Forum dome finial',cx,cz,33.8,source_top-33.8,.13,.025,bronze)
for x,z in tower_ring:cylinder('Forum corner minaret',cx+(x-cx)*.87,cz+(z-cz)*.87,26.7,3.1,.18,.12,trim);cylinder('Forum minaret cap',cx+(x-cx)*.87,cz+(z-cz)*.87,29.8,.65,.27,.015,copper)
for name,(vs,fs,mat) in batches.items():f.make_mesh_object('Forum '+name,vs,fs,mat,'Authored photo-informed facade detail')
for o in bpy.data.objects:
 if o.type=='MESH':o.data.calc_loop_triangles()
triangles=sum(len(o.data.loop_triangles) for o in bpy.data.objects if o.type=='MESH')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'assets/source/environment/forum.blend'))
bpy.ops.export_scene.gltf(filepath=str(ROOT/'public/models/environment/forum.glb'),export_format='GLB',export_yup=True,export_extras=True)
(ROOT/'public/models/environment/forum.json').write_text(json.dumps({'structureId':'806370','objectIds':ids,'geometrySource':f.SOURCE_URL,'license':'CC BY 4.0','reference':'https://whatson.melbourne.vic.gov.au/things-to-do/forum-melbourne','triangles':triangles,'limitations':'Survey footprint and total tower height preserved. Upper rectangular tower extrusion replaced by photo-informed copper dome, finial and minarets. Arches, cornices, clock and material palette are authored approximations, not measured conservation drawings. An authored footprint plinth connects the main section to flat game ground.'},indent=2)+'\n')
print('Forum triangles',triangles)
