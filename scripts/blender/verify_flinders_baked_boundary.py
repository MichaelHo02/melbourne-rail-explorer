import bpy,json
from pathlib import Path
from mathutils import Vector
r=Path(bpy.data.filepath).resolve().parents[3];o=bpy.data.objects['Flinders station - municipal 2020 scan, authored colours'];b=bpy.data.meshes[o['concourse_skin_original_mesh']];xyz=json.loads((r/'assets/source/environment/flinders-original-smoothed-vertices.json').read_text());cuts=json.loads((r/'assets/source/environment/flinders-roof-baked-overlap-cuts.json').read_text());assert all((o.data.vertices[i].co-Vector(v)).length<.00003 for i,v in enumerate(xyz));ix=0;uncut=0
for q in b.polygons:
 replacements=cuts.get(str(q.index))
 if replacements is None:
  p=o.data.polygons[ix];assert tuple(p.vertices)==tuple(q.vertices) and p.material_index==q.material_index;ix+=1;uncut+=1
 else:
  for tri in replacements:
   p=o.data.polygons[ix];assert p.material_index==q.material_index
   for vi,v in zip(p.vertices,tri):assert (o.data.vertices[vi].co-Vector(v)).length<.00003
   ix+=1
assert ix==len(o.data.polygons);assert all(not m.show_render and not m.show_viewport for m in o.modifiers if m.type=='SMOOTH');assert b.use_fake_user;assert bpy.data.meshes[o['concourse_pre_exact_mesh']].use_fake_user;assert bpy.context.scene.camera.name=='37 CBD aerial review';assert not any(n.type=='TEX_IMAGE' for m in bpy.data.materials if m.use_nodes for n in m.node_tree.nodes)
p=r/'docs/flinders-roof-baked-boundary-audit.json';a=json.loads(p.read_text());a['saved_verification']={'baked_source_vertices_match':len(xyz),'uncut_face_connectivity_and_materials_preserved':uncut,'replacement_coordinates_verified':True,'post_cut_smoothing_disabled':True,'original_and_prior_meshes_recoverable':True,'image_textures':0};p.write_text(json.dumps(a,indent=2)+'\n');print('VERIFIED_SAVED_BAKED_BOUNDARY',flush=True)
exec(compile((r/'scripts/blender/render_swanston_approach_detail.py').read_text().replace('observatory-swanston-approach-detail.png','observatory-flinders-baked-roof-boundary.png'),'render','exec'))
