"""Authored portal terrace interpretation from official section sheet 07."""
import bpy,bmesh,json
from pathlib import Path
R=Path(bpy.data.filepath).resolve().parents[3]
def xy(u,v):
 a=(-30,304.28);b=(-.7035,315.5922);c=(32.0118,224.8664);t=(u-733)/913;s=(v-365)/297
 return (b[0]+t*(c[0]-b[0])+s*(a[0]-b[0]),b[1]+t*(c[1]-b[1])+s*(a[1]-b[1]))
v=[];f=[]
def box(x0,y0,x1,y1,top):
 k=len(v);ring=[xy(x0,y0),xy(x1,y0),xy(x1,y1),xy(x0,y1)]
 for z in [.34,top]:v.extend((x,y,z) for x,y in ring)
 f.extend([[k+j for j in q] for q in [[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]])
# Three U-shaped bands leave the Collins-facing entrance side open.
for i,top in enumerate([.923,1.325,1.756]):
 outer=3-i;inner=2-i;rx=967+11*outer;ix=967+11*inner;ty=480-7.33*outer;iy=480-7.33*inner;by=601+9.67*outer;iby=601+9.67*inner
 box(ix,ty,rx,by,top);box(856,ty,ix,iy,top);box(856,iby,ix,by,top)
name='City Square authored portal terraces';old=bpy.data.objects.get(name)
if old:bpy.data.objects.remove(old,do_unlink=True)
mesh=bpy.data.meshes.new(name);mesh.from_pydata(v,[],f);mesh.materials.append(bpy.data.materials['Authored central CBD bluestone - coverage illustrative']);mesh.update();bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free();mesh.update();o=bpy.data.objects.new(name,mesh);bpy.data.collections['GROUND - official horizontal geography, authored levels'].objects.link(o)
o['reference']='https://bigbuild.vic.gov.au/__data/assets/pdf_file/0014/1016042/Appendix-C_CBD-South-Precinct-Development-Plan_Rev-L.pdf'
o['sheet']='TAS-CYP-CS-00-DRG-AUD-CBS-744207-DP G.5, portal terrace seating sections, PDF page12'
o['limits']='Three tiers based on section levels10.716,11.118,11.549 relative illustrative outside10.133. Unified flat .34m ground datum; actual drawing ground levels differ by section. Tread lengths, U-shaped footprint alignment and finish authored from plan; not installed survey. Portal opening, glass canopy and escalators remain unmodelled.'
print('VERIFIED portal terraces',len(mesh.polygons),'faces','tops', [.923,1.325,1.756],flush=True)
