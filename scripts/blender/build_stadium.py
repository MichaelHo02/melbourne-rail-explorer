"""Surveyed stadium shell with original interior opening and authored roof trusses."""
import bpy,importlib.util,json,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('frontage',Path(__file__).with_name('build_viaduct_frontage.py'));f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f);f.reset_scene()
raw=json.loads((ROOT/'src/data/stadium-source.json').read_text())['records'];ids=sorted(r['objectid'] for r in raw)
f.STRUCTURES['808392']={'objectIds':ids};buildings=json.loads((ROOT/'public/data/buildings.json').read_text())['buildings']
wall=f.material('stadium silver grey cladding',(.32,.35,.36),.77,.22)
base=f.material('stadium concrete concourse',(.37,.36,.32),.95)
roof=f.material('stadium roof metal',(.38,.43,.45),.72,.3)
steel=f.material('pale exposed roof steel',(.65,.69,.66),.7,.25)
dark=f.material('dark open concourse bands',(.035,.055,.063),.65)
envelope,sections=f.union_sections(buildings,'808392',(wall,base,roof))
hole=next(r for r in raw if r['objectid']=='920')['geo_shape']['geometry']['coordinates'][1]
hole=[[(lon-144.9671)*87939,-(lat+37.8183)*111320] for lon,lat in hole]
cutter=f.ring_mesh('surveyed central opening',hole,-2,70)
bpy.context.view_layer.objects.active=envelope
mod=envelope.modifiers.new('retain surveyed central opening','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True)
if not envelope.data.polygons:raise RuntimeError('Empty stadium union')
center=sum((Vector(f.game_to_blender(x,80,z)) for x,z in hole),Vector())/len(hole)
if envelope.ray_cast(center,Vector((0,0,-1)))[0]:raise RuntimeError('Surveyed stadium opening was filled')
bands=([],[]);frames=([],[])
for face in envelope.data.polygons:
 n=face.normal
 if abs(n.z)>.03:continue
 pts=[envelope.data.vertices[i].co for i in face.vertices];h=Vector((-n.y,n.x,0)).normalized();a=min(p.dot(h) for p in pts);b=max(p.dot(h) for p in pts);lo=min(p.z for p in pts);hi=max(p.z for p in pts)
 if b-a<.5:continue
 plane=Vector((n.x,n.y,0))*pts[0].dot(n)
 # The source's individual concourse storeys control these horizontal bands.
 if hi-lo>2:
  f.add_box_beam(*bands,h,n,plane,a+.04,b-.04,lo+.35,min(hi-.25,lo+1.65),.06,.065)
  f.add_box_beam(*frames,h,n,plane,a,b,hi-.18,hi,.12,.16)
  bays=max(1,round((b-a)/6))
  for bay in range(bays+1):
   center=a+(b-a)*bay/bays
   f.add_box_beam(*frames,h,n,plane,max(a,center-.16),min(b,center+.16),lo,hi,.28,.30)
f.make_mesh_object('concourse ribbon glazing',*bands,dark,'Authored dark horizontal concourse bands')
f.make_mesh_object('stadium horizontal fascia',*frames,steel,'Authored pale floor edges')
# Long edges of the recorded opening establish the roof's orientation.
ring=hole[:-1] if math.dist(hole[0],hole[-1])<.01 else hole
edges=sorted([(math.dist(a,b),a,b) for a,b in zip(ring,ring[1:]+ring[:1])],reverse=True)[:2]
verts=[];faces=[]
def beam(a,b,r=.14):
 a,b=Vector(a),Vector(b);axis=(b-a).normalized();u=axis.cross(Vector((0,0,1))).normalized();v=axis.cross(u);start=len(verts)
 for p in [a,b]:
  for k in range(4):verts.append(tuple(p+(u*math.cos(k*math.pi/2)+v*math.sin(k*math.pi/2))*r))
 for k in range(4):faces.append((start+k,start+(k+1)%4,start+4+(k+1)%4,start+4+k))
for _,a,b in edges:
 a=Vector(f.game_to_blender(a[0],34,a[1]));b=Vector(f.game_to_blender(b[0],34,b[1]));direction=(b-a).normalized();a-=direction*32;b+=direction*32
 lows=[];tops=[]
 for i in range(33):
  t=i/32;p=a.lerp(b,t);lows.append(p);tops.append(p+Vector((0,0,1.5+9*math.sin(math.pi*t))))
 for i in range(32):
  beam(lows[i],lows[i+1],.23);beam(tops[i],tops[i+1],.23);beam(lows[i],tops[i],.13);beam(lows[i],tops[i+1],.13)
f.make_mesh_object('stadium roof lattice girders',verts,faces,steel,'Authored roof truss silhouette aligned to surveyed opening; not engineering geometry')
for o in bpy.data.objects:
 if o.type=='MESH':o.data.calc_loop_triangles()
triangles=sum(len(o.data.loop_triangles) for o in bpy.data.objects if o.type=='MESH')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'assets/source/environment/stadium.blend'))
bpy.ops.export_scene.gltf(filepath=str(ROOT/'public/models/environment/stadium.glb'),export_format='GLB',export_yup=True,export_extras=True)
(ROOT/'public/models/environment/stadium.json').write_text(json.dumps({'structureId':'808392','objectIds':ids,'geometrySource':f.SOURCE_URL,'license':'CC BY 4.0','reference':'https://www.aurecongroup.com/projects/property/marvel-stadium','triangles':triangles,'limitations':'2023 envelope and recorded central opening retained, relative heights follow prepared source. Concourse bands and roof trusses are visual interpretations of the engineer reference. No interior seating or 2024 redevelopment reconstruction. Roof is shown open; no moving mechanism.'},indent=2)+'\n')
print('Stadium triangles',triangles)
