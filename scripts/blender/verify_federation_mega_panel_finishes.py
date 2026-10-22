import bpy,json,hashlib
from pathlib import Path
r=Path(bpy.data.filepath).resolve().parents[3];a=json.loads((r/'docs/federation-mega-panel-audit.json').read_text());o=bpy.data.objects[a['object']];old=bpy.data.meshes[o['mega_finish_original_mesh']];assert old.use_fake_user;assert len(old.vertices)==len(o.data.vertices);assert len(old.polygons)==len(o.data.polygons)
assert all(tuple(a.co)==tuple(b.co) for a,b in zip(old.vertices,o.data.vertices));assert all(tuple(a.vertices)==tuple(b.vertices) for a,b in zip(old.polygons,o.data.polygons));changed={c['face']:c for c in a['changes']}
for p,q in zip(o.data.polygons,old.polygons):
 if p.index in changed:assert p.material_index==changed[p.index]['after'] and q.material_index==changed[p.index]['before']
 else:assert p.material_index==q.material_index
for g in a['groups']:assert all(o.data.polygons[i].material_index==g['material'] for i in g['faces'])
assert a['source_sha256']==hashlib.sha256((r/'assets/source/environment/federation-ngv-panels.json').read_bytes()).hexdigest();assert bpy.context.scene.camera.name=='37 CBD aerial review';assert not any(n.type=='TEX_IMAGE' for m in o.data.materials if m and m.use_nodes for n in m.node_tree.nodes)
a['saved_verification']={'geometry_unchanged':True,'material_assignments_checked':len(o.data.polygons),'intact_groups':len(a['groups']),'original_mesh_recoverable':True,'active_camera_preserved':True};(r/'docs/federation-mega-panel-audit.json').write_text(json.dumps(a,indent=2)+'\n');print('VERIFIED_SAVED_MEGA_FINISH',len(a['groups']),flush=True)
s=(r/'scripts/blender/render_federation_square_detail.py').read_text().replace('bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)','scene.render.engine="CYCLES";scene.cycles.samples=24;scene.cycles.use_denoising=True').replace('observatory-federation-square-detail.png','observatory-federation-mega-panel-finishes.png');exec(compile(s,'render','exec'))
