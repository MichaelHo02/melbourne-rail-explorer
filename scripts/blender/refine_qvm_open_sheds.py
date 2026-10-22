"""Open A-E market sheds, reference-led timber supports with authored setout."""
import bpy,json,math
from pathlib import Path
root=globals().get('root') or Path(bpy.data.filepath).resolve().parents[3];name='Queen Victoria Market authored timber shed supports'
if not bpy.data.objects.get(name):
 d=json.loads((root/'assets/source/environment/qvm-authored-roofs.json').read_text());ox,oy=d['origin'];ux,uy=d['axis'];nx,ny=d['normal']
 def localy(v):return (v[0]-ox)*nx+(v[1]-oy)*ny
 def world(x,y,z):return (ox+x*ux+y*nx,oy+x*uy+y*ny,z)
 obj=bpy.data.objects['survey_24605'];old=obj.data;verts=[];faces=[];indices=[]
 # Clip the original envelope at the southern edge of the five open shed ranges.
 for p in old.polygons:
  points=[tuple(old.vertices[i].co) for i in p.vertices];out=[]
  for a,b in zip(points,points[1:]+points[:1]):
   av,bv=localy(a)-103,localy(b)-103
   if av>=0:out.append(a)
   if (av>=0)!=(bv>=0):
    t=av/(av-bv);out.append(tuple(a[i]+t*(b[i]-a[i]) for i in range(3)))
  if len(out)>=3:
   start=len(verts);verts.extend(out);faces.append(tuple(range(start,len(verts))));indices.append(p.material_index)
 m=bpy.data.meshes.new('Market retained southern envelope');m.from_pydata(verts,[],faces)
 for mat in old.materials:m.materials.append(mat)
 for p,i in zip(m.polygons,indices):p.material_index=i
 m.update();obj.data=m;obj['market_upper_sheds_open']=True
 row=json.loads((root/'assets/source/environment/qvm-source-audit.json').read_text())['survey_section'];ring=[(x,-y) for x,y in row['ring']]
 def inside(x,y):
  hit=False
  for a,b in zip(ring,ring[1:]):
   if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:hit=not hit
  return hit
 verts=[];faces=[];posts=0;beams=0
 def box(x,y,z,sx,sy,sz):
  start=len(verts);verts.extend([world(x+dx*sx/2,y+dy*sy/2,z+dz*sz) for dz in [0,1] for dx,dy in [(-1,-1),(1,-1),(1,1),(-1,1)]])
  faces.extend([tuple(start+i for i in q) for q in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]])
 for shed in range(5):
  for y in [shed*20.65+1,shed*20.65+15.4]:
   for i in range(31):
    x=2+i*5.2;px,py,_=world(x,y,0)
    if inside(px,py):box(x,y,.34,.229,.229,6.16);posts+=1
   # Beam intervals honour the discontinuities in the retained survey footprint.
   for i in range(160):
    x=1.5+i;px,py,_=world(x,y,0)
    if inside(px,py):box(x,y,6.5,1,.22,.30);beams+=1
 mat=bpy.data.materials.new('Authored market timber supports');mat.use_nodes=True;mat.diffuse_color=(.18,.13,.085,1);s=mat.node_tree.nodes.get('Principled BSDF');s.inputs['Base Color'].default_value=mat.diffuse_color;s.inputs['Roughness'].default_value=.82
 m=bpy.data.meshes.new(name);m.from_pydata(verts,[],faces);m.materials.append(mat);m.update();o=bpy.data.objects.new(name,m);bpy.data.collections['CITY - reference-authored landmarks'].objects.link(o);o['posts']=posts;o['limits']='Historical plan-led open timber sheds. 5.2 m post spacing and 229 mm posts; exact setout, beam extents, heights, trusses, stalls and current works authored or unresolved.'
 floorname='Queen Victoria Market authored shed asphalt';v=[(x,y,.34) for f in d['faces'] for x,y,z in f];m=bpy.data.meshes.new(floorname);m.from_pydata(v,[],[(i,i+1,i+2) for i in range(0,len(v),3)]);mat=bpy.data.materials.new('Authored market shed asphalt');mat.use_nodes=True;mat.diffuse_color=(.10,.11,.11,1);s=mat.node_tree.nodes.get('Principled BSDF');s.inputs['Base Color'].default_value=mat.diffuse_color;s.inputs['Roughness'].default_value=.92;m.materials.append(mat);m.update();o=bpy.data.objects.new(floorname,m);bpy.data.collections['GROUND - official horizontal geography, authored levels'].objects.link(o)
 print('VERIFIED market open sheds',posts,'posts',beams,'beam intervals',len(faces),'faces',flush=True)
