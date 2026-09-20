"""Swann House envelope from 2023 survey; authored reference-based masonry detail.
Owner reference: https://orionig.com.au/projects/orion-house
City heritage assessment: c186-central-city-heritage-review-part-3.pdf.
No copied photography is embedded. Facade dimensions are interpretations.
"""
import bpy, importlib.util, json, math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('frontage',Path(__file__).with_name('build_viaduct_frontage.py'))
f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f)
f.reset_scene()
ids=['28379','28380','28381','28383'] # 28382 is below the pre-existing preparation size filter.
f.STRUCTURES['801838']={'objectIds':ids}
buildings=json.loads((ROOT/'public/data/buildings.json').read_text())['buildings']
stone=f.material('warm limestone render',(.49,.43,.32),.9)
base=f.material('rusticated base stone',(.31,.29,.24),.92)
roof=f.material('matte roof',(.23,.24,.22),.95)
glass=f.material('recessed blue grey windows',(.055,.095,.115),.32,.18)
bronze=f.material('dark bronze frames',(.105,.09,.065),.53,.4)
trim=f.material('pale stone cornices',(.59,.53,.41),.84)
envelope,sections=f.union_sections(buildings,'801838',(stone,base,roof))
# Base should occupy only the lower two principal levels, not 12 metres.
for p in envelope.data.polygons:
 if abs(p.normal.z)<.1:p.material_index=1 if p.center.z<7.5 else 0
batches={name:([],[],mat) for name,mat in [('windows',glass),('frames',bronze),('stone_details',trim)]}
def beam(kind,h,n,plane,a,b,low,high,depth=.12,projection=.12):
 verts,faces,_=batches[kind];f.add_box_beam(verts,faces,h,n,plane,a,b,low,high,depth,projection)
def inside(x,y,ring):
 hit=False
 for a,b in zip(ring,ring[1:]+ring[:1]):
  if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:hit=not hit
 return hit
for face in envelope.data.polygons:
 n=face.normal
 if abs(n.z)>.035:continue
 coords=[envelope.data.vertices[i].co for i in face.vertices];h=Vector((-n.y,n.x,0)).normalized()
 ring=[(p.dot(h),p.z) for p in coords];lo=min(p[1] for p in ring);hi=max(p[1] for p in ring)
 a=min(p[0] for p in ring);b=max(p[0] for p in ring);width=b-a
 if width<3 or hi-lo<2:continue
 plane=Vector((n.x,n.y,0))*coords[0].dot(n)
 bays=max(1,round(width/2.7));bay=width/bays
 for floor in range(12):
  bottom=1.2+floor*3.65;top=bottom+2.3
  if bottom<lo+.2 or top>hi-.2:continue
  for col in range(bays):
   center=a+(col+.5)*bay;left=center-.65;right=center+.65
   if not all(inside(x,y,ring) for x in [left,right] for y in [bottom,top]):continue
   # Dark shallow recess, slender bronze mullion and projecting stone sill.
   beam('windows',h,n,plane,left,right,bottom,top,.025,.026)
   for x in [left-.07,center-.025,right]:beam('frames',h,n,plane,x,x+.05,bottom,top,.055,.06)
   beam('stone_details',h,n,plane,left-.15,right+.15,bottom-.12,bottom,.19,.2)
  if floor in [1,9,10]:beam('stone_details',h,n,plane,a,b,top+.18,top+.35,.22,.24)
 # Repeated rustication courses distinguish the robust street base.
 if lo<7.5:
  for y in [i*.6 for i in range(1,13)]:
   if lo+.1<y<hi-.1:beam('stone_details',h,n,plane,a,b,y,y+.045,.055,.055)
 # The cornice follows each actual stepped roof edge, rather than changing it.
 if hi>25:
  beam('stone_details',h,n,plane,a-.06,b+.06,hi-.55,hi-.30,.4,.40)
  beam('stone_details',h,n,plane,a-.1,b+.1,hi-.26,hi-.08,.5,.5)
for name,(v,fs,mat) in batches.items():f.make_mesh_object('swann_'+name,v,fs,mat,'Reference-based masonry detailing; dimensions authored')
output=ROOT/'public/models/environment/swann-house.glb';source=ROOT/'assets/source/environment/swann-house.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(source))
bpy.ops.export_scene.gltf(filepath=str(output),export_format='GLB',export_yup=True,export_extras=True,export_animations=False)
manifest={'structureId':'801838','objectIds':ids,'address':'22–38 William Street, Swann House','identitySource':'City of Melbourne Building Outlines 2014, mccid 110151; centre contained by source polygon','geometrySource':f.SOURCE_URL,'licence':'CC BY 4.0','reference':'https://orionig.com.au/projects/orion-house','heritageReference':'https://mvga-prod-files.s3.ap-southeast-4.amazonaws.com/public/2024-07/c186-central-city-heritage-review-part-3.pdf','limitations':'2023 footprint sections and prepared relative heights control the envelope. Window rhythm, materials, cornice profiles and rustication are authored interpretations, not measured restoration drawings. Historical floor counts differ by source and are not used to change survey height.','boundsXZ':[min(p[0] for b in sections for p in b['ring']),min(p[1] for b in sections for p in b['ring']),max(p[0] for b in sections for p in b['ring']),max(p[1] for b in sections for p in b['ring'])],'height':max(b['base']+b['height'] for b in sections)}
(ROOT/'public/models/environment/swann-house.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('Exported',output,output.stat().st_size)
