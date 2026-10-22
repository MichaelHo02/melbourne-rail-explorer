"""Reversible roof skins fitted to low captured Flinders canopies.

Own metal finish. 0.75m sampling and short-hole interpolation are authored
cleanup assumptions. Never modifies source mesh or imports photographic textures.
"""
import bpy,json,statistics,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(bpy.data.filepath).resolve().parents[3]
o=bpy.data.objects['Flinders station - municipal 2020 scan, authored colours'];deps=bpy.context.evaluated_depsgraph_get();ev=o.evaluated_get(deps);mesh=ev.to_mesh();tree=BVHTree.FromPolygons([v.co for v in mesh.vertices],[p.vertices[:] for p in mesh.polygons],all_triangles=True)
rings=[q['ring'] for q in json.loads((R/'assets/source/environment/flinders-scan-material-zones.json').read_text())['zones']]
def inside(x,y,ring):
 result=False
 for i,(ax,ay) in enumerate(ring):
  bx,by=ring[i-1]
  if (ay>y)!=(by>y) and x<(bx-ax)*(y-ay)/(by-ay)+ax:result=not result
 return result
step=.75; samples={};valid={};interpolated=[]
for i in range(-374,88):
 for j in range(-134,94):
  x=i*step;y=j*step
  if any(inside(x,y,r) for r in rings):continue
  p,n,f,d=tree.ray_cast(Vector((x,y,16)),Vector((0,0,-1)),16)
  if p and n.z>.6 and 4.7<p.z<6.2:samples[i,j]=p.z
valid.update(samples)
for i in range(-374,88):
 for j in range(-134,94):
  if (i,j) in samples or any(inside(i*step,j*step,r) for r in rings):continue
  support=[]
  for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:
   for distance in range(1,4):
    key=i+dx*distance,j+dy*distance
    if key in samples:support.append(samples[key]);break
  if len(support)==4 and max(support)-min(support)<.35:valid[i,j]=statistics.median(support);interpolated.append([i*step,j*step,valid[i,j]])
name='Flinders captured canopy fitted metal skins';old=bpy.data.objects.get(name)
if old:bpy.data.objects.remove(old,do_unlink=True)
verts=[];faces=[];lookup={};cells=0
for i,j in sorted(valid):
 keys=[(i,j),(i+1,j),(i+1,j+1),(i,j+1)]
 if not all(k in valid for k in keys):continue
 if max(valid[k] for k in keys)-min(valid[k] for k in keys)>.3:continue
 ids=[]
 for a,b in keys:
  if (a,b) not in lookup:
   # Match support heights, offset slightly to avoid coincident surfaces.
   lookup[a,b]=len(verts);verts.append((a*step,b*step,valid[a,b]+.055))
  ids.append(lookup[a,b])
 faces.extend([(ids[0],ids[1],ids[2]),(ids[0],ids[2],ids[3])]);cells+=1
m=bpy.data.materials.get('Flinders canopy authored charcoal zinc') or bpy.data.materials.new('Flinders canopy authored charcoal zinc');m.use_nodes=True;m.diffuse_color=(.16,.20,.19,1);nodes=m.node_tree.nodes;links=m.node_tree.links;s=nodes.get('Principled BSDF');s.inputs['Base Color'].default_value=m.diffuse_color;s.inputs['Metallic'].default_value=.45;s.inputs['Roughness'].default_value=.48
for node in list(nodes):
 if node.name.startswith('Authored canopy'):nodes.remove(node)
tex=nodes.new('ShaderNodeTexNoise');tex.name='Authored canopy fine metal grain';tex.inputs['Scale'].default_value=120;bump=nodes.new('ShaderNodeBump');bump.name='Authored canopy subtle grain';bump.inputs['Strength'].default_value=.08;bump.inputs['Distance'].default_value=.008;links.new(tex.outputs['Fac'],bump.inputs['Height']);links.new(bump.outputs['Normal'],s.inputs['Normal'])
me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.materials.append(m);me.update();obj=bpy.data.objects.new(name,me);o.users_collection[0].objects.link(obj);obj.matrix_world=o.matrix_world.copy()
for p in me.polygons:p.use_smooth=True
obj['source']='Municipal May 2020 scan roof coordinates; own metal finish, no photographic texture.';obj['limits']='Only low roof surfaces outside main station zones. Sampling0.75m, upward normal>0.6, captured height4.7–6.2m. Four-direction gap support within2.25m and spread<0.35m; skin offset0.055m authored. Large unsupported tears and sides remain.'
audit={'captured_support_samples':len(samples),'interpolated_samples':len(interpolated),'surface_cells':cells,'projected_surface_area_m2':cells*step*step,'triangles':len(faces),'vertices':len(verts),'source_mesh_vertices':len(o.data.vertices),'source_mesh_triangles':len(o.data.polygons),'limits':obj['limits'],'interpolated_points':interpolated}
assert faces and all(p.area>1e-9 and p.normal.z>0 for p in me.polygons)
(R/'docs/flinders-canopy-surface-repair-audit.json').write_text(json.dumps(audit,indent=2)+'\n');ev.to_mesh_clear();print('CANOPY_SURFACES',json.dumps({k:v for k,v in audit.items() if k!='interpolated_points'}),flush=True)
