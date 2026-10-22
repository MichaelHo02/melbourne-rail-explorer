import bpy,json
from pathlib import Path
r=Path(bpy.data.filepath).resolve().parents[3];o=bpy.data.objects['Flinders station - municipal 2020 scan, authored colours'];b=bpy.data.meshes[o['lower_roof_original_mesh']];a=json.loads((r/'docs/flinders-concourse-roof-material-audit.json').read_text());changed=set(a['face_indices']);assert len(o.data.vertices)==len(b.vertices);assert all((v.co-w.co).length==0 for v,w in zip(o.data.vertices,b.vertices));assert len(o.data.polygons)==len(b.polygons)
for p,q in zip(o.data.polygons,b.polygons):
 assert tuple(p.vertices)==tuple(q.vertices);assert p.material_index==(4 if p.index in changed else q.material_index)
assert b.use_fake_user;assert bpy.context.scene.camera.name=='37 CBD aerial review';a['saved_verification']={'geometry_unchanged':True,'outside_materials_preserved':True,'recoverable_original':b.name};(r/'docs/flinders-concourse-roof-material-audit.json').write_text(json.dumps(a,indent=2)+'\n');print('VERIFIED_SAVED_LOWER_ROOF',len(changed),flush=True)
exec(compile((r/'scripts/blender/render_swanston_approach_detail.py').read_text().replace('observatory-swanston-approach-detail.png','observatory-flinders-lower-roof-material.png'),'render','exec'))
