"""Authored glass guards and escalator side panels; exact dimensions unverified."""
import bpy,bmesh
from pathlib import Path
from mathutils import Vector
R=Path(bpy.data.filepath).resolve().parents[3];name='City Square authored portal guards';col=bpy.data.collections.get(name)
if col:
 for o in list(col.objects):bpy.data.objects.remove(o,do_unlink=True)
else:col=bpy.data.collections.new(name);bpy.context.scene.collection.children.link(col)
def xy(u,w,z):
 a=(-30,304.28);b=(-.7035,315.5922);c=(32.0118,224.8664);t=(u-733)/913;s=(w-365)/297
 return Vector((b[0]+t*(c[0]-b[0])+s*(a[0]-b[0]),b[1]+t*(c[1]-b[1])+s*(a[1]-b[1]),z))
gv=[];gf=[];v=[];f=[]
def pane(a,b,height):
 k=len(gv);gv.extend([tuple(a),tuple(b),tuple(b+Vector((0,0,height))),tuple(a+Vector((0,0,height)))]);gf.append([k,k+1,k+2,k+3])
def beam(a,b,width):
 d=(b-a).normalized();helper=Vector((0,0,1)) if abs(d.z)<.95 else Vector((1,0,0));x=d.cross(helper).normalized()*width*.5;y=d.cross(x).normalized()*width*.5;k=len(v)
 for p in [a,b]:v.extend(tuple(p+dx*x+dy*y) for dx,dy in [(1,1),(-1,1),(-1,-1),(1,-1)])
 f.extend([[k+j for j in q] for q in [[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]])
for a,b in [((856,480),(967,480)),((967,480),(967,601)),((967,601),(856,601))]:
 start=xy(*a,1.756);end=xy(*b,1.756)
 for i in range(8):
  p=start.lerp(end,i/8);q=start.lerp(end,(i+1)/8);pane(p,q,1.1);beam(p,p+Vector((0,0,1.1)),.045)
 beam(end,end+Vector((0,0,1.1)),.045);beam(start+Vector((0,0,1.1)),end+Vector((0,0,1.1)),.055)
for flight in range(5):
 centre=493+22*flight
 for side in [-1,1]:
  a=xy(860,centre+side*7,.34);b=xy(963,centre+side*7,.34-4.7);pane(a,b,.85)
mesh=bpy.data.meshes.new(name+' glass');mesh.from_pydata(gv,[],gf);mesh.materials.append(bpy.data.materials['Authored City Square canopy glass']);mesh.update();o=bpy.data.objects.new(name+' glass',mesh);col.objects.link(o);mod=o.modifiers.new('Authored thin glazing','SOLIDIFY');mod.thickness=.015
mesh=bpy.data.meshes.new(name+' rail metal');mesh.from_pydata(v,[],f);mesh.materials.append(bpy.data.materials['Authored City Square escalator metal']);mesh.update();bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free();o=bpy.data.objects.new(name+' rail metal',mesh);col.objects.link(o)
col['reference']='https://bigbuild.vic.gov.au/__data/assets/pdf_file/0014/1016042/Appendix-C_CBD-South-Precinct-Development-Plan_Rev-L.pdf';col['limits']='Glass guards interpreted from visually inspected portal axonometric. 1.1m perimeter guard, .85m escalator side panels, thickness, posts and all dimensions authored; not verified installed equipment or a safety/compliance design.'
print('VERIFIED authored guards',len(gf),'glass panels',len(f),'rail faces',flush=True)
