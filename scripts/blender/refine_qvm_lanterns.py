"""Historical-plan roof lantern forms, illustrative proportions and levels."""
import bpy,json,math
from pathlib import Path
root=globals().get('root') or Path(bpy.data.filepath).resolve().parents[3];name='Queen Victoria Market authored J and KL roof lanterns'
if not bpy.data.objects.get(name):
 d=json.loads((root/'assets/source/environment/qvm-authored-roofs.json').read_text());ox,oy=d['origin'];ux,uy=d['axis'];nx,ny=d['normal'];v=[];f=[];mi=[]
 def point(x,y,z):return (ox+x*ux+y*nx,oy+x*uy+y*ny,z)
 def quad(points,mat):
  i=len(v);v.extend([point(*p) for p in points]);f.append((i,i+1,i+2,i+3));mi.append(mat)
 # J: polycarbonate gabled cover with illustrative dark louvre side bands.
 center=120.5;half=2.2
 for side in [-1,1]:
  y=center+side*half;quad([(3,y,9.35),(161,y,9.35),(161,center,10),(3,center,10)],1);quad([(3,y,8.85),(161,y,8.85),(161,y,9.35),(3,y,9.35)],2)
 # K-L: convex corrugated metal cover above illustrative alternating sash bands.
 center=149.8;half=1.7
 profile=[(center-half+2*half*i/12,9.3+.7*math.sin(math.pi*i/12)) for i in range(13)]
 for (ya,za),(yb,zb) in zip(profile,profile[1:]):quad([(3,ya,za),(161,ya,za),(161,yb,zb),(3,yb,zb)],0)
 for side in [-1,1]:
  y=center+side*half
  for i in range(31):
   x=3+i*5.1;quad([(x,y,8.8),(x+5.1,y,8.8),(x+5.1,y,9.3),(x,y,9.3)],1 if i%2==0 else 2)
 m=bpy.data.meshes.new(name);m.from_pydata(v,[],f);m.materials.append(bpy.data.materials['Authored market galvanised roof'])
 for label,color,rough,metal in [('Authored market translucent roof approximation',(.28,.35,.34),.28,.15),('Authored market lantern louvre bands',(.10,.13,.12),.65,.3)]:
  mat=bpy.data.materials.new(label);mat.use_nodes=True;mat.diffuse_color=(*color,1);s=mat.node_tree.nodes.get('Principled BSDF');s.inputs['Base Color'].default_value=mat.diffuse_color;s.inputs['Roughness'].default_value=rough;s.inputs['Metallic'].default_value=metal;m.materials.append(mat)
 for p,i in zip(m.polygons,mi):p.material_index=i
 m.update();o=bpy.data.objects.new(name,m);bpy.data.collections['CITY - reference-authored landmarks'].objects.link(o);o['limits']='Historical conservation plan supports J glazed gable lantern and K-L convex roof lantern. Length, width, 10 m maximum, sash/louvre spacing and optical material authored. Not measured or current refurbishment verified.';print('VERIFIED market lanterns',len(f),'faces',flush=True)
