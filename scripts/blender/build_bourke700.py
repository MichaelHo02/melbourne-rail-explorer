"""700 Bourke: City survey envelope with authored Woods Bagot photo-based detail."""
import bpy, importlib.util, json, math, hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('frontage',Path(__file__).with_name('build_viaduct_frontage.py'))
f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f);f.reset_scene()
source=ROOT/'public/data/buildings.json';buildings=json.loads(source.read_text())['buildings']
ids=['3663','3664','3665','3666'];f.STRUCTURES['810894']={'objectIds':ids}
glass=f.material('charcoal solar glass',(.035,.055,.065),.34,.3)
base=f.material('pale concrete podium',(.53,.52,.46),.9)
roof=f.material('dark roof plant enclosure',(.06,.068,.065),.92)
frame=f.material('fine aluminium mullions',(.21,.23,.22),.55,.5)
white=f.material('pale triangular facade panels',(.65,.65,.59),.73)
colours=[f.material('fissure '+name,c,.65,.15) for name,c in [('orange',(.58,.15,.025)),('gold',(.56,.36,.055)),('green',(.18,.26,.075)),('red',(.40,.065,.028))]]
envelope,sections=f.union_sections(buildings,'810894',(glass,base,roof))
batches={name:([],[],mat) for name,mat in [('frames',frame),('white',white),*[(str(i),m) for i,m in enumerate(colours)]]}
def inside(x,y,ring):
 hit=False
 for a,b in zip(ring,ring[1:]+ring[:1]):
  if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:hit=not hit
 return hit
def tri(name,h,n,plane,points):
 vs,fs,_=batches[name];start=len(vs);vs.extend(tuple(plane+h*x+Vector((0,0,y))+n*.045) for x,y in points);fs.append(tuple(range(start,start+len(points))))
for face in envelope.data.polygons:
 n=face.normal
 if abs(n.z)>.03:continue
 coords=[envelope.data.vertices[i].co for i in face.vertices];h=Vector((-n.y,n.x,0)).normalized()
 ring=[(v.dot(h),v.z) for v in coords];a=min(v[0] for v in ring);b=max(v[0] for v in ring);low=min(v[1] for v in ring);high=max(v[1] for v in ring)
 face.material_index=1 if high<=6.2 else 0
 width=b-a
 if width<1 or high-low<2:continue
 plane=Vector((n.x,n.y,0))*coords[0].dot(n)
 cols=max(1,round(width/2.3));bay=width/cols
 for level in range(17):
  bottom=6.1+level*3.27;top=bottom+3.27
  for col in range(cols):
   left=a+col*bay+.06;right=a+(col+1)*bay-.06
   if not all(inside(x,y,ring) for x in [left,right] for y in [bottom+.06,top-.06]):continue
   # Narrow survey return walls carry the coloured triangular fissure palette.
   # Broader glazed fields have a sparse alternating pale triangle rhythm.
   if 3<width<18 and high-low>25:
    tri(str((level+col)%4),h,n,plane,[(left,bottom+.06),(right,top-.06),(left,top-.06)])
    tri(str((level+col+1)%4),h,n,plane,[(left,bottom+.06),(right,bottom+.06),(right,top-.06)])
   elif (col+level*3)%9==0:
    tri('white',h,n,plane,[(left,bottom+.06),(right,top-.06),(left,top-.06)])
   vs,fs,_=batches['frames']
   f.add_box_beam(vs,fs,h,n,plane,left-.035,left+.035,bottom,top,.07,.085)
   f.add_box_beam(vs,fs,h,n,plane,left,right,top-.055,top+.015,.07,.085)
for name,(vs,fs,mat) in batches.items():f.make_mesh_object('bourke700_'+name,vs,fs,mat,'Photo-informed facade articulation; spacing and colours authored')
# Keep the source footprint; no unmeasured apron or plant blocks are added.
for obj in bpy.data.objects:
 if obj.type=='MESH':obj.data.calc_loop_triangles()
triangles=sum(len(o.data.loop_triangles) for o in bpy.data.objects if o.type=='MESH')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'assets/source/environment/bourke700.blend'))
bpy.ops.export_scene.gltf(filepath=str(ROOT/'public/models/environment/bourke700.glb'),export_format='GLB',export_yup=True,export_extras=True)
manifest={'structureId':'810894','objectIds':ids,'address':'700–704 Bourke Street, Docklands','geometrySource':f.SOURCE_URL,'license':'CC BY 4.0','sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'reference':'https://www.woodsbagot.com/projects/national-australia-bank-docklands/','triangles':triangles,'limitations':'2023 survey footprint and prepared relative heights preserved. Glazing, pale triangles, coloured return facets and mullion spacing interpreted from architect photographs, not measured facade drawings. 2014 address record identifies the site but predates the full building geometry.'}
(ROOT/'public/models/environment/bourke700.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('Exported triangles',triangles)
