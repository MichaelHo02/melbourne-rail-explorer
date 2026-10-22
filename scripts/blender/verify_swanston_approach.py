import bpy,json,math
from pathlib import Path
r=Path(bpy.data.filepath).resolve().parents[3];s=bpy.context.scene;assert s.get('swanston_approach_overlap_cut_revision')=='mapped-planform-subtraction-v1';d=json.loads((r/'assets/source/environment/swanston-approach-authored-surfaces.json').read_text());checks=[]
for p in d['parts']:
 o=bpy.data.objects['Municipal Swanston bridge approach '+p['assetid']];assert len(o.data.vertices)==len(p['vertices']);assert len(o.data.polygons)==len(p['faces']);error=max(math.dist(tuple(v.co),q) for v,q in zip(o.data.vertices,p['vertices']));assert error<.00003;checks.append({'assetid':p['assetid'],'coordinate_error_m':error,'faces':len(o.data.polygons)})
cuts=json.loads((r/'assets/source/environment/swanston-approach-overlap-cuts.json').read_text());outside=[]
for name,replacements in cuts.items():
 if not replacements:continue
 o=bpy.data.objects[name];backup=bpy.data.meshes[o['swanston_approach_original_mesh']];assert backup.use_fake_user;assert all((v.co-q.co).length<1e-6 for v,q in zip(o.data.vertices,backup.vertices));remaining={(tuple(p.vertices),p.material_index) for p in o.data.polygons}
 assert all((tuple(p.vertices),p.material_index) in remaining for p in backup.polygons if str(p.index) not in replacements);outside.append(name)
assert s.camera.name=='37 CBD aerial review';assert not any(n.type=='TEX_IMAGE' for m in bpy.data.materials if m.use_nodes for n in m.node_tree.nodes);p=r/'docs/swanston-approach-surface-audit.json';a=json.loads(p.read_text());a['saved_file_verification']={'mapped_assets':checks,'outside_faces_preserved':outside,'image_textures':0};p.write_text(json.dumps(a,indent=2)+'\n');print('SAVED_SWANSTON_APPROACH_VERIFIED',len(checks),flush=True)
