"""Fit existing illustrative glass boxes to rounded heads; no measured fenestration claim."""
import bpy,bmesh,math
obj=bpy.data.objects['FSS_glass'];old=obj.data
if not obj.get('arched_glazing_revision'):
 assert len(old.vertices)%24==0 and len(old.polygons)==len(old.vertices)//24*12
 verts=[];faces=[];changed=0
 for group in range(len(old.vertices)//24):
  start=group*24;points=[tuple(v.co) for v in old.vertices[start:start+24]];polys=old.polygons[group*12:group*12+12]
  assert all(start<=i<start+24 for p in polys for i in p.vertices)
  low=[min(p[j] for p in points) for j in range(3)];high=[max(p[j] for p in points) for j in range(3)];dims=[high[j]-low[j] for j in range(3)]
  offset=len(verts)
  if abs(dims[0]-1.8)<.001 and abs(dims[1]-.12)<.001 and abs(dims[2]-3.4)<.001:
   cx=(low[0]+high[0])/2;r=dims[0]/2;spring=high[2]-r
   profile=[(low[0],low[2]),(high[0],low[2])]+[(cx+r*math.cos(i*math.pi/12),spring+r*math.sin(i*math.pi/12)) for i in range(13)]
   n=len(profile)
   verts.extend([(x,y,z) for y in [low[1],high[1]] for x,z in profile]);faces.extend([tuple(offset+i for i in range(n-1,-1,-1)),tuple(offset+n+i for i in range(n))]);faces.extend([(offset+i,offset+(i+1)%n,offset+(i+1)%n+n,offset+i+n) for i in range(n)]);changed+=1
  else:
   verts.extend(points);faces.extend([tuple(offset+i-start for i in p.vertices) for p in polys])
 assert changed==282,changed
 mesh=bpy.data.meshes.new('Flinders fitted arched glazing');mesh.from_pydata(verts,[],faces)
 for m in old.materials:mesh.materials.append(m)
 bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free();mesh.update();obj.data=mesh;obj['arched_glazing_revision']=1;obj['limits']='282 existing illustrative window boxes fitted to semicircular heads with 12 segments. Position and overall width/height retained; exact openings, recess and mullions unmeasured.'
 print('VERIFIED fitted Flinders arch glazing',changed,flush=True)
else:print('VERIFIED retained fitted Flinders arch glazing',flush=True)
