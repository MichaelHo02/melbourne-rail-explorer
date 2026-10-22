import bpy,json
from pathlib import Path
r=Path(bpy.data.filepath).resolve().parents[3];path=r/'docs/st-pauls-cornice-finish-audit.json';a=json.loads(path.read_text());o=bpy.data.objects[a['object']];old=bpy.data.meshes[a['backup_mesh']];assert old.use_fake_user;assert len(old.vertices)==len(o.data.vertices);assert len(old.polygons)==len(o.data.polygons);assert all(tuple(p.co)==tuple(q.co) for p,q in zip(old.vertices,o.data.vertices));assert all(tuple(p.vertices)==tuple(q.vertices) for p,q in zip(old.polygons,o.data.polygons));changes={c['face']:c for c in a['changes']}
for p,q in zip(o.data.polygons,old.polygons):
 if p.index in changes:assert p.material_index==changes[p.index]['after'] and q.material_index==changes[p.index]['before'] and o.data.materials[p.material_index].name=='Authored St Pauls warm masonry'
 else:assert p.material_index==q.material_index
assert bpy.context.scene.camera.name=='37 CBD aerial review';a['saved_verification']={'all_vertices_and_connectivity_unchanged':True,'all_material_assignments_checked':len(o.data.polygons),'changed_faces':len(changes),'recovery_mesh_verified':True};path.write_text(json.dumps(a,indent=2)+'\n');print('VERIFIED_CATHEDRAL_CORNICE',len(changes),flush=True)
code=(r/'scripts/blender/render_st_pauls_study.py').read_text().replace('bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)','scene.render.engine="CYCLES";scene.cycles.samples=24;scene.cycles.use_denoising=True').replace('observatory-st-pauls-study.png','observatory-st-pauls-stone-cornices.png');exec(compile(code,'render','exec'))
