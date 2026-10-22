"""Add reversible small roof infill; preserve captured mesh and raw OBJ.

Boundary coordinates come from the May 2020 municipal scan. Selection
thresholds are authored cleanup assumptions, not measured roof design.
Run inside Blender after scan import and smoothing.
"""
import bpy,bmesh,json
from pathlib import Path
from mathutils import Vector
R=Path(bpy.data.filepath).resolve().parents[3];o=bpy.data.objects['Flinders station - municipal 2020 scan, authored colours'];bm=bmesh.new();bm.from_mesh(o.data);bm.verts.ensure_lookup_table();bm.edges.ensure_lookup_table();boundary={e for e in bm.edges if e.is_boundary};seen=set();loops=[];branched=0
for edge in sorted(boundary,key=lambda e:tuple(sorted(v.index for v in e.verts))):
 if edge in seen:continue
 group=set();todo=[edge]
 while todo:
  e=todo.pop()
  if e in group:continue
  group.add(e);seen.add(e)
  for v in e.verts:todo.extend(q for q in v.link_edges if q in boundary and q not in group)
 vertices={v for e in group for v in e.verts}
 if any(sum(e in group for e in v.link_edges)!=2 for v in vertices):branched+=1;continue
 ordered=[];v=min(vertices,key=lambda v:v.index);first=v;previous=None
 while True:
  ordered.append(v);options=[e for e in v.link_edges if e in group and e!=previous];e=min(options,key=lambda e:e.other_vert(v).index);v=e.other_vert(v);previous=e
  if v==first:break
  if len(ordered)>len(vertices):raise RuntimeError('invalid loop')
 points=[v.co.copy() for v in ordered];center=sum(points,Vector())/len(points);cross=sum(((points[i]-center).cross(points[(i+1)%len(points)]-center) for i in range(len(points))),Vector());area=cross.length/2;normal=cross.normalized();variance=max(abs((p-center).dot(normal)) for p in points);span=max(max(p[j] for p in points)-min(p[j] for p in points) for j in range(3));adjnormal=sum((f.normal for e in group for f in e.link_faces),Vector()).normalized()
 loops.append({'vertices':[v.index for v in ordered],'area':area,'span':span,'plane_deviation':variance,'center':list(center),'adjacent_up':adjnormal.z,'edge_count':len(group)})

selected=[l for l in loops if .005<l['area']<2 and l['span']<5 and l['plane_deviation']<.2 and l['adjacent_up']>.6 and 6<l['center'][2]<32]
name='Flinders scan conservative roof hole patches'
old=bpy.data.objects.get(name)
if old:bpy.data.objects.remove(old,do_unlink=True)
evaluated=o.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh()
assert len(evaluated.vertices)==len(o.data.vertices),'Roof patch vertex correspondence changed'
from mathutils.geometry import tessellate_polygon
verts=[];faces=[];materials=[]
for loop in selected:
 points=[evaluated.vertices[i].co.copy() for i in loop['vertices']]
 triangles=tessellate_polygon([points]); offset=len(verts);verts.extend(points)
 linked=[f for i in loop['vertices'] for f in bm.verts[i].link_faces]
 material=max(set(f.material_index for f in linked),key=lambda m:sum(f.material_index==m for f in linked))
 for triangle in triangles:
  ids=[v if isinstance(v,int) else next(i for i,p in enumerate(points) if (p-v).length<1e-7) for v in triangle]
  triangle=[points[i] for i in ids]
  if (triangle[1]-triangle[0]).cross(triangle[2]-triangle[0]).z<0:ids.reverse()
  faces.append(tuple(offset+i for i in ids));materials.append(material)
mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update()
patch=bpy.data.objects.new(name,mesh);o.users_collection[0].objects.link(patch);patch.matrix_world=o.matrix_world.copy()
for m in o.data.materials:mesh.materials.append(m)
for face,m in zip(mesh.polygons,materials):face.material_index=m;face.use_smooth=True
patch['provenance']='Authored infill supported by closed boundaries in municipal May 2020 scan; raw source and captured mesh unchanged.'
patch['limits']='Only small enclosed near-planar upward-facing gaps. Large tears, crop boundaries and branched openings remain unresolved.'
assert all(p.area>1e-9 for p in mesh.polygons)
audit={'source_object':o.name,'source_vertices':len(o.data.vertices),'source_triangles':len(o.data.polygons),'closed_loops':len(loops),'branched_components_rejected':branched,'patched_loops':len(selected),'raw_boundary_area_m2':sum(l['area'] for l in selected),'patch_triangles':len(faces),'selection':{'area_m2':[.005,2],'span_max_m':5,'plane_deviation_max_m':.2,'adjacent_normal_z_min':.6,'center_height_m':[6,32]},'limits':patch['limits'],'loops':selected}
(R/'docs/flinders-scan-roof-repair-audit.json').write_text(json.dumps(audit,indent=2)+'\n')
o.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh_clear();bm.free()
print('ROOF_REPAIR',json.dumps({k:v for k,v in audit.items() if k!='loops'}),flush=True)
