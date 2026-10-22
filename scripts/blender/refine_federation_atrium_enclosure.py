"""Authored Atrium enclosure prototype; explicit geometry and elevation approximations."""
import bpy,json
from pathlib import Path
from mathutils import Vector
r=Path(bpy.data.filepath).resolve().parents[3];s=bpy.context.scene;key='federation_atrium_enclosure_revision'
if not s.get(key):
 assert s.get('federation_atrium_void_revision')
 d=json.loads((r/'assets/source/environment/federation-atrium-enclosure.json').read_text());col=bpy.data.collections.new('Federation Atrium - source guided authored enclosure');s.collection.children.link(col)
 def mat(name,color,metal=0,rough=.4,glass=False):
  m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
  if glass:p.inputs['Transmission Weight'].default_value=.85;p.inputs['IOR'].default_value=1.45
  m['limits']=d['limits'];return m
 glass=mat('Authored Atrium pale clear glazing',(.68,.79,.8),0,.13,True);steel=mat('Authored Atrium galvanised steel',(.39,.43,.43),.7,.28);floor=mat('Authored Atrium polished concrete',(.24,.25,.245),0,.3);wall=mat('Authored NGV Atrium boundary - approximate',(.21,.215,.2),.25,.48)
 def mesh(name,vs,fs,m):
  me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.materials.append(m);me.update();o=bpy.data.objects.new(name,me);col.objects.link(o);o['limits']=d['limits'];return o
 roof=mesh('Atrium capture guided glazed roof',d['roof_vertices'],d['roof_faces'],glass);mesh('Atrium assumed graded concrete floor',d['floor_ring'],[list(range(len(d['floor_ring'])))],floor)
 bv=[];bf=[];seen=set()
 def beam(a,b,w=.2):
  a,b=Vector(a),Vector(b);tag=tuple(sorted([tuple(round(v,3) for v in a),tuple(round(v,3) for v in b)]))
  if tag in seen:return
  seen.add(tag);z=(b-a).normalized();x=z.cross(Vector((0,0,1)))
  if x.length<.01:x=z.cross(Vector((0,1,0)))
  x.normalize();y=z.cross(x).normalized();k=len(bv)
  for p in [a,b]:
   for u,v in [(-1,-1),(1,-1),(1,1),(-1,1)]:bv.append(tuple(p+(x*u+y*v)*w/2))
  bf.extend([tuple(k+i for i in f) for f in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]])
 for f in d['roof_faces']:
  for j in range(3):beam(d['roof_vertices'][f[j]],d['roof_vertices'][f[(j+1)%3]])
 gv=[];gf=[];wv=[];wf=[]
 for rec in d['sides']:
  p=rec['points']
  if rec['edge']==0:
   # East side closes the surviving NGV envelope; north/south ends remain gallery openings.
   k=len(wv);wv.extend([p[0],p[1],[p[1][0],p[1][1],32.4],[p[0][0],p[0][1],32.4]]);wf.append((k,k+1,k+2,k+3));continue
  for tier in range(4):
   a=Vector(p[0]).lerp(Vector(p[3]),tier/4);b=Vector(p[1]).lerp(Vector(p[2]),tier/4);c=Vector(p[1]).lerp(Vector(p[2]),(tier+1)/4);e=Vector(p[0]).lerp(Vector(p[3]),(tier+1)/4);k=len(gv);gv.extend(map(tuple,[a,b,c,e]));gf.append((k,k+1,k+2,k+3))
   for u,v in [(a,b),(b,c),(c,e),(e,a),(a,c)]:beam(u,v)
 cv=[];cf=[]
 for quad in d['boundary_closures']:
  k=len(cv);cv.extend(quad);cf.append((k,k+1,k+2,k+3))
 mesh('Atrium adjacent upper and lower cut closures',cv,cf,wall)
 mesh('Atrium north west and southern glazing',gv,gf,glass);mesh('NGV east Atrium exposed envelope closure',wv,wf,wall);mesh('Atrium authored200mm square steel frame',bv,bf,steel)
 s[key]='source-guided-prototype-v1';print('ATRIUM_ENCLOSURE',len(seen),len(gf),len(d['roof_faces']),flush=True)
else:print('ATRIUM_ENCLOSURE_ALREADY_APPLIED',flush=True)
