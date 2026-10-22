"""Authored stone and simplified iron edging on retained Princes Bridge envelope."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
root=globals().get('root') or Path(bpy.data.filepath).resolve().parents[3];label='Princes Bridge - authored simplified balustrade'
if not bpy.data.objects.get(label):
 b=next(b for b in json.loads((root/'public/data/buildings.json').read_text())['buildings'] if str(b['id'])=='36402');ring=[(x,-y) for x,y in b['ring']];top=max(3,b['base']+b['height']);reference='https://mvga-prod-files.s3.ap-southeast-4.amazonaws.com/public/2024-07/central-city-heritage-study-review-1993-p5.pdf'
 mats=[]
 for name,color,rough,metal in [('Authored Princes Bridge bluestone',(.20,.23,.24),.9,0),('Authored Princes Bridge upper stone',(.36,.35,.32),.85,0),('Authored Princes Bridge iron',(.07,.085,.075),.5,.55)]:
  m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.use_nodes=True;s=m.node_tree.nodes.get('Principled BSDF');s.inputs['Base Color'].default_value=(*color,1);s.inputs['Roughness'].default_value=rough;s.inputs['Metallic'].default_value=metal;mats.append(m)
 original=bpy.data.objects['survey_36402'];original.data.materials[0]=mats[0]
 def inside(x,y):
  hit=False
  for a,c in zip(ring,ring[1:]):
   if (a[1]>y)!=(c[1]>y) and x<(c[0]-a[0])*(y-a[1])/(c[1]-a[1])+a[0]:hit=not hit
  return hit
 roof=bpy.data.objects['Continuous surveyed roofs - authored finishes'];roof.data.materials.append(mats[1]);index=len(roof.data.materials)-1;changed=0
 for p in roof.data.polygons:
  x,y,z=p.center
  if abs(z-top)<.001 and 65<=x<=147 and -186<=y<=-49 and inside(x,y):p.material_index=index;changed+=1
 verts=[];faces=[];segments=0;posts=0
 def beam(a,c,width):
  a=Vector(a);c=Vector(c);t=(c-a).normalized();u=t.cross(Vector((0,0,1)))
  if u.length<.01:u=Vector((1,0,0))
  u.normalize();v=t.cross(u).normalized();start=len(verts)
  for centre in [a,c]:verts.extend([tuple(centre+u*dx*width/2+v*dy*width/2) for dx,dy in [(-1,-1),(1,-1),(1,1),(-1,1)]])
  faces.extend([tuple(start+i for i in f) for f in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]])
 axis=Vector((.35,-.94))
 for a,c in zip(ring,ring[1:]):
  edge=Vector((c[0]-a[0],c[1]-a[1]));length=edge.length
  if length<8 or abs(edge.normalized().dot(axis))<.7:continue
  for h in [.25,1.10]:beam((*a,top+h),(*c,top+h),.08)
  count=max(1,math.ceil(length/1.5))
  for i in range(count+1):
   x=a[0]+edge.x*i/count;y=a[1]+edge.y*i/count;beam((x,y,top),(x,y,top+1.12),.075);posts+=1
  segments+=1
 mesh=bpy.data.meshes.new(label);mesh.from_pydata(verts,[],faces);mesh.materials.append(mats[2]);mesh.update();obj=bpy.data.objects.new(label,mesh);bpy.data.collections['CITY - reference-authored landmarks'].objects.link(obj);obj['reference']=reference;obj['source_id']='36402';obj['limits']='Retained bridge outline and preview height. Authored bluestone/upper-stone palette; simplified iron railing on long edges, 1.1 m height and 1.5 m post spacing. Exact balustrade ornament, stone distribution, arches, lamps, vertical datum and present-day condition unmeasured.';obj['edge_segments']=segments;obj['posts']=posts;assert changed>0 and segments>0 and all(p.area>0 for p in mesh.polygons);print('VERIFIED Princes Bridge authored finish:',changed,'cap faces',segments,'edges',posts,'posts')
