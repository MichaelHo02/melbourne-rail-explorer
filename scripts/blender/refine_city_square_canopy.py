"""Authored entrance canopy from official artist impression; dimensions approximate."""
import bpy,bmesh,math
from pathlib import Path
from mathutils import Vector
R=Path(bpy.data.filepath).resolve().parents[3];name='City Square authored entrance canopy';col=bpy.data.collections.get(name)
if col:
 for o in list(col.objects):bpy.data.objects.remove(o,do_unlink=True)
else:col=bpy.data.collections.new(name);bpy.context.scene.collection.children.link(col)
def xy(u,v,z):
 a=(-30,304.28);b=(-.7035,315.5922);c=(32.0118,224.8664);t=(u-733)/913;s=(v-365)/297
 return Vector((b[0]+t*(c[0]-b[0])+s*(a[0]-b[0]),b[1]+t*(c[1]-b[1])+s*(a[1]-b[1]),z))
def roof(u,v):return xy(u,v,8.05-(v-435)/226*.5)
def mat(name,color,rough,metal=0,glass=False):
 m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*color,1);s=m.node_tree.nodes.get('Principled BSDF');s.inputs['Base Color'].default_value=(*color,1);s.inputs['Roughness'].default_value=rough;s.inputs['Metallic'].default_value=metal
 if glass:s.inputs['Transmission Weight'].default_value=1;s.inputs['IOR'].default_value=1.45
 return m
steel=mat('Authored City Square canopy pale steel',(.67,.69,.67),.35,.3);glass=mat('Authored City Square canopy glass',(.82,.9,.95),.08,glass=True)
v=[];f=[]
def beam(a,b,width):
 direction=(b-a).normalized();helper=Vector((0,0,1)) if abs(direction.z)<.95 else Vector((1,0,0));x=direction.cross(helper).normalized()*width*.5;y=direction.cross(x).normalized()*width*.5;k=len(v)
 for p in [a,b]:v.extend([tuple(p+x+y),tuple(p-x+y),tuple(p-x-y),tuple(p+x-y)])
 f.extend([[k+i for i in q] for q in [[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]])
for u in [835,1010]:
 for w in [450,646]:
  foot=xy(u,w,.34);fork=xy(u,w,2.65);beam(foot,fork,.32)
  for du,dw in [(-22,-22),(-22,22),(22,-22),(22,22)]:beam(fork,roof(u+du,max(435,min(661,w+dw))),.22)
# Roof secondary grid and perimeter; 21x22 panes, pitch interpreted visually.
for i in range(22):
 u=810+225*i/21;beam(roof(u,435),roof(u,661),.075 if i not in [0,21] else .16)
for j in range(23):
 w=435+226*j/22;beam(roof(810,w),roof(1035,w),.075 if j not in [0,22] else .16)
for u in [835,922.5,1010]:beam(roof(u,435)-Vector((0,0,.12)),roof(u,661)-Vector((0,0,.12)),.2)
mesh=bpy.data.meshes.new(name+' steel');mesh.from_pydata(v,[],f);mesh.materials.append(steel);mesh.update();bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free();o=bpy.data.objects.new(name+' steel',mesh);col.objects.link(o)
pv=[];pf=[]
for i in range(21):
 for j in range(22):
  u0=810+225*i/21;u1=810+225*(i+1)/21;w0=435+226*j/22;w1=435+226*(j+1)/22;k=len(pv);pv.extend(tuple(roof(u,w)+Vector((0,0,.05))) for u,w in [(u0,w0),(u0,w1),(u1,w1),(u1,w0)]);pf.append([k,k+1,k+2,k+3])
mesh=bpy.data.meshes.new(name+' glazing');mesh.from_pydata(pv,[],pf);mesh.materials.append(glass);mesh.update();assert all(p.normal.z>.99 for p in mesh.polygons);o=bpy.data.objects.new(name+' glazing',mesh);col.objects.link(o)
col['reference']='https://bigbuild.vic.gov.au/use-metro-tunnel/stations/town-hall/design';col['limits']='Authored canopy interpreted from official artist impression image2. Approximate footprint, .5m roof fall, 7.55–8.05m roof level, four branching supports and21x22 pane grid; not measured or as-built. Exact primary steelwork, louvres, joints and optics unfinished. Portal below remains flat; opening and escalators unmodelled.'
print('VERIFIED authored canopy',len(f),'steel faces',len(pf),'glass panes',flush=True)
