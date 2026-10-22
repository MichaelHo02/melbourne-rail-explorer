"""Authored kerb relief along retained unioned road boundaries."""
import bpy, math
from collections import Counter
name='Authored kerbs - retained road edges'
if not bpy.data.objects.get(name):
 road=bpy.data.objects['Continuous Vicmap road surface'];counts=Counter();points={}
 for p in road.data.polygons:
  coords=[tuple(round(v,3) for v in road.data.vertices[i].co[:2]) for i in p.vertices]
  for i,a in enumerate(coords):
   b=coords[(i+1)%len(coords)];key=tuple(sorted((a,b)));counts[key]+=1;points[key]=(a,b)
 verts=[];faces=[];segments=0
 for key,count in counts.items():
  if count!=1:continue
  a,b=points[key];dx=b[0]-a[0];dy=b[1]-a[1];length=math.hypot(dx,dy)
  if length<.5:continue
  if any(abs(a[k]-bound)<.02 and abs(b[k]-bound)<.02 for k,bound in [(0,-2000),(0,1250),(1,-800),(1,1750)]):continue
  # Upward road winding places its interior on the left, paving on the right.
  nx=dy/length*.16;ny=-dx/length*.16;start=len(verts)
  for z in (.255,.38):verts.extend([(a[0],a[1],z),(b[0],b[1],z),(b[0]+nx,b[1]+ny,z),(a[0]+nx,a[1]+ny,z)])
  faces.extend([tuple(start+i for i in f) for f in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]]);segments+=1
 mat=bpy.data.materials.get('Authored kerb concrete') or bpy.data.materials.new('Authored kerb concrete');mat.use_nodes=True;s=mat.node_tree.nodes.get('Principled BSDF');s.inputs['Base Color'].default_value=(.38,.39,.36,1);s.inputs['Roughness'].default_value=.88
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.materials.append(mat);mesh.update();obj=bpy.data.objects.new(name,mesh);road.users_collection[0].objects.link(obj)
 obj['source_url']=road['source_url'];obj['segments']=segments;obj['limits']='Edges derived from retained unioned road surfaces. Width .16 m and rise .125 m authored. Clipped map boundaries omitted. Driveways, intersection ramps and actual kerb profiles unmeasured; refinement required.'
 assert segments>0 and all(p.area>0 for p in mesh.polygons)
 print('VERIFIED authored kerb segments:',segments)
