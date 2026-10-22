"""Reference-led southern market shed hierarchy with authored setout."""
import bpy,json
from pathlib import Path
root=globals().get('root') or Path(bpy.data.filepath).resolve().parents[3];name='Queen Victoria Market authored F J KL roofs'
if not bpy.data.objects.get(name):
 d=json.loads((root/'assets/source/environment/qvm-south-authored-roofs.json').read_text());base=json.loads((root/'assets/source/environment/qvm-authored-roofs.json').read_text());ox,oy=base['origin'];ux,uy=base['axis'];nx,ny=base['normal'];row=json.loads((root/'assets/source/environment/qvm-source-audit.json').read_text())['survey_section'];ring=[(x,-y) for x,y in row['ring']]
 def inside(x,y):
  hit=False
  for a,b in zip(ring,ring[1:]):
   if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:hit=not hit
  return hit
 def localy(x,y):return (x-ox)*nx+(y-oy)*ny
 def world(x,y,z):return (ox+x*ux+y*nx,oy+x*uy+y*ny,z)
 bpy.data.objects['survey_24605'].hide_render=True;bpy.data.objects['survey_24605'].hide_viewport=True
 o=bpy.data.objects['Continuous surveyed roofs - authored finishes'];keep=[p for p in o.data.polygons if not (9.9<=p.center.z<11 and localy(p.center.x,p.center.y)>=100 and inside(p.center.x,p.center.y))];removed=len(o.data.polygons)-len(keep);m=bpy.data.meshes.new('Continuous roofs market south cutout');m.from_pydata([tuple(v.co) for v in o.data.vertices],[],[tuple(p.vertices) for p in keep])
 for mat in o.data.materials:m.materials.append(mat)
 for p,q in zip(m.polygons,keep):p.material_index=q.material_index
 m.update();o.data=m
 def mesh(label,verts,faces,mat):
  m=bpy.data.meshes.new(label);m.from_pydata(verts,[],faces);m.materials.append(mat);m.update();o=bpy.data.objects.new(label,m);bpy.data.collections['CITY - reference-authored landmarks'].objects.link(o);return o
 verts=[v for f in d['faces'] for v in f];faces=[(i,i+1,i+2) for i in range(0,len(verts),3)];o=mesh(name,verts,faces,bpy.data.materials['Authored market galvanised roof']);o['limits']=d['limits'];o['flat_caps_removed']=removed
 mesh('Queen Victoria Market southern asphalt',[(x,y,.34) for x,y,z in verts],faces,bpy.data.materials['Authored market shed asphalt'])
 v=[];f=[];posts=0
 def box(x,y,z,sx,sy,sz):
  i=len(v);v.extend([world(x+dx*sx/2,y+dy*sy/2,z+dz*sz) for dz in [0,1] for dx,dy in [(-1,-1),(1,-1),(1,1),(-1,1)]]);f.extend([tuple(i+j for j in q) for q in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]])
 for y,h in [(103.5,6.4),(112,6.4),(129,6.4),(131,4.8),(142,6.4),(158,6.4),(168.5,4.8)]:
  for i in range(32):
   x=2+i*5.1;px,py,_=world(x,y,0)
   if inside(px,py):box(x,y,.34,.16,.16,h);posts+=1
 steel=bpy.data.materials.new('Authored southern market steel supports');steel.use_nodes=True;steel.diffuse_color=(.12,.14,.13,1);s=steel.node_tree.nodes.get('Principled BSDF');s.inputs['Base Color'].default_value=steel.diffuse_color;s.inputs['Metallic'].default_value=.45;s.inputs['Roughness'].default_value=.6;o=mesh('Queen Victoria Market southern support columns',v,f,steel);o['posts']=posts;o['limits']='Authored 5.1 m setout, dimensions and levels. Exact steel/timber transitions and trusses unresolved.'
 v=[];f=[];box(82,111,.34,164,.28,6.46);brick=bpy.data.materials.new('Authored F shed pale brown masonry');brick.use_nodes=True;brick.diffuse_color=(.37,.29,.20,1);s=brick.node_tree.nodes.get('Principled BSDF');s.inputs['Base Color'].default_value=brick.diffuse_color;s.inputs['Roughness'].default_value=.84;mesh('Queen Victoria Market illustrative F shed dividing wall',v,f,brick)
 print('VERIFIED southern market roofs',len(faces),'triangles',posts,'posts',removed,'caps removed',flush=True)
