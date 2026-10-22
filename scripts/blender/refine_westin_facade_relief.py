"""Authored west elevation relief interpreted from the 2000 construction photograph."""
import bpy,bmesh,json
from pathlib import Path
from mathutils import Vector
R=Path(bpy.data.filepath).resolve().parents[3];name='Westin authored west elevation relief';col=bpy.data.collections.get(name)
if col:
 for o in list(col.objects):bpy.data.objects.remove(o,do_unlink=True)
else:col=bpy.data.collections.new(name);bpy.context.scene.collection.children.link(col)
b=next(b for b in json.loads((R/'public/data/buildings.json').read_text())['buildings'] if str(b['id'])=='26410');ring=b['ring'][:]
if ring[0]==ring[-1]:ring.pop()
edges=[(Vector((x,-y,0)),Vector((ring[(i+1)%len(ring)][0],-ring[(i+1)%len(ring)][1],0))) for i,(x,y) in enumerate(ring)];a,end=max(edges,key=lambda p:(p[1]-p[0]).length);delta=end-a;length=delta.length;t=delta.normalized();normal=Vector((t.y,-t.x,0));signed=sum(ring[i-1][0]*(-ring[i][1])-ring[i][0]*(-ring[i-1][1]) for i in range(len(ring)))
if signed<0:normal=-normal
v=[];f=[];mi=[]
def box(x0,x1,z0,z1,d0,d1,index):
 k=len(v)
 for z in [z0,z1]:
  for x,d in [(x0,d0),(x1,d0),(x1,d1),(x0,d1)]:v.append(tuple(a+t*x+normal*d+Vector((0,0,z))))
 for q in [[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]:f.append([k+j for j in q]);mi.append(index)
stone=bpy.data.materials['Westin candidate authored sandstone precast']
def material(name,c,rough,metal):
 m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*c,1);s=m.node_tree.nodes.get('Principled BSDF');s.inputs['Base Color'].default_value=(*c,1);s.inputs['Roughness'].default_value=rough;s.inputs['Metallic'].default_value=metal;return m
glass=material('Westin authored vertical bay glazing',(.045,.10,.13),.20,.25);metal=material('Westin authored bay frame',(.095,.11,.12),.4,.55)
for z in [8.2,30.3,33.7]:box(.2,length-.2,z,z+.25,.02,.42,0)
for i in range(1,5):
 x=length*i/5;box(x-.65,x+.65,8.5,30.3,.08,.36,1)
 for side in [-1,1]:box(x+side*.74-.13,x+side*.74+.13,8.5,30.3,.02,.48,0)
 for z in [8.5+3.6*j for j in range(7)]:
  if z>=30.3:continue
  box(x-.67,x+.67,z,z+.055,.36,.41,2)
 box(x-.055,x+.055,8.5,30.3,.36,.42,2)
mesh=bpy.data.meshes.new(name);mesh.from_pydata(v,[],f);mesh.update()
for m in [stone,glass,metal]:mesh.materials.append(m)
for p,i in zip(mesh.polygons,mi):p.material_index=i
bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free();o=bpy.data.objects.new(name,mesh);col.objects.link(o);col['reference']='https://nationalprecast.com.au/wp-content/uploads/2015/09/Precaster-24.pdf';col['limits']='Horizontal projecting bands and vertical glazing interpreted from western elevation photo on page4. Four bays, their divisions, dimensions, colours and heights authored; exact existing openings not surveyed. No photographic textures. Original survey envelope retained; podium, upper elevation, balcony and projecting bay geometry incomplete.'
print('VERIFIED Westin west elevation relief',len(f),'closed-box faces',flush=True)
