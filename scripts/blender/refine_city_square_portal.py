"""Cut authored ground and add illustrative descending entrance escalators."""
import bpy,bmesh,json
from pathlib import Path
from mathutils import Vector
R=Path(bpy.data.filepath).resolve().parents[3];d=json.loads((R/'assets/source/environment/city-square-authored-portal.json').read_text());col=bpy.data.collections['GROUND - official horizontal geography, authored levels']
for part in d['parts']:
 name='Authored ground with City Square portal' if part['name']=='base' else 'City Square authored bluestone surface';old=bpy.data.objects.get(name);material=bpy.data.materials['Authored neutral urban ground' if part['name']=='base' else 'Authored central CBD bluestone - coverage illustrative']
 if old:bpy.data.objects.remove(old,do_unlink=True)
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(part['vertices'],[],part['faces']);mesh.materials.append(material);mesh.update();assert all(p.normal.z>.99 for p in mesh.polygons);o=bpy.data.objects.new(name,mesh);col.objects.link(o);o['limits']=d['limits']
base=bpy.data.objects['Authored flat ground'];base.hide_render=True;base.hide_viewport=True;base['replacement']='Authored ground with City Square portal'
name='City Square authored descending portal';collection=bpy.data.collections.get(name)
if collection:
 for o in list(collection.objects):bpy.data.objects.remove(o,do_unlink=True)
else:collection=bpy.data.collections.new(name);bpy.context.scene.collection.children.link(collection)
def material(name,color,rough):
 m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*color,1);p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;return m
wall=material('Authored City Square portal concrete',(.22,.225,.21),.88);dark=material('Authored City Square portal recess',(.018,.022,.023),.9);metal=material('Authored City Square escalator metal',(.23,.25,.26),.4);metal.node_tree.nodes.get('Principled BSDF').inputs['Metallic'].default_value=.65
ring=d['ring']
if sum(ring[i][0]*ring[(i+1)%4][1]-ring[(i+1)%4][0]*ring[i][1] for i in range(4))<0:ring.reverse()
v=[(x,y,z) for z in [.34,-5.25] for x,y in ring];f=[[i,(i+1)%4,(i+1)%4+4,i+4] for i in range(4)]+[[4,5,6,7]];mesh=bpy.data.meshes.new(name+' walls');mesh.from_pydata(v,[],f);mesh.materials.append(wall);mesh.materials.append(dark);mesh.update();mesh.polygons[-1].material_index=1;o=bpy.data.objects.new(name+' walls',mesh);collection.objects.link(o)
def xy(u,w,z):
 a=(-30,304.28);b=(-.7035,315.5922);c=(32.0118,224.8664);t=(u-733)/913;s=(w-365)/297
 return Vector((b[0]+t*(c[0]-b[0])+s*(a[0]-b[0]),b[1]+t*(c[1]-b[1])+s*(a[1]-b[1]),z))
v=[];f=[]
def box(u0,w0,u1,w1,z):
 ring=[xy(u0,w0,z),xy(u1,w0,z),xy(u1,w1,z),xy(u0,w1,z)];k=len(v)
 for dz in [-.18,0]:v.extend(tuple(p+Vector((0,0,dz))) for p in ring)
 f.extend([[k+j for j in q] for q in [[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]])
def beam(a,b,width):
 direction=(b-a).normalized();x=direction.cross(Vector((0,0,1))).normalized()*width*.5;y=direction.cross(x).normalized()*width*.5;k=len(v)
 for p in [a,b]:v.extend(tuple(p+dx*x+dy*y) for dx,dy in [(1,1),(-1,1),(-1,-1),(1,-1)])
 f.extend([[k+j for j in q] for q in [[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]])
for flight in range(5):
 centre=493+22*flight
 for step in range(36):
  u0=860+103*step/36;u1=860+103*(step+1)/36;box(u0,centre-5,u1,centre+5,.34-4.7*step/36)
 for side in [-1,1]:beam(xy(860,centre+side*7,.34+.85),xy(963,centre+side*7,.34-4.7+.85),.075)
mesh=bpy.data.meshes.new(name+' steps');mesh.from_pydata(v,[],f);mesh.materials.append(metal);mesh.update();bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free();o=bpy.data.objects.new(name+' steps and rails',mesh);collection.objects.link(o)
collection['reference']='https://www.premier.vic.gov.au/upgraded-city-square-ready-rock-n-roll';collection['limits']='Five escalators supported by official release. 36 steps each, 4.7m descent, widths, rails, concrete recess and floor depths authored visual approximation, not actual equipment dimensions or complete concourse. Opening aligned approximately to old parcel and development plan. Station interiors and balustrades incomplete.'
print('VERIFIED authored portal',d['hole_area_m2'],'m2','five flights',180,'steps',len(f),'metal faces',flush=True)
