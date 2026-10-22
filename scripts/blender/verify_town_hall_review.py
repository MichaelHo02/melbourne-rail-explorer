import bpy,json,hashlib
from pathlib import Path
R=Path(globals().get('root') or '/Users/holeminhthach/.codex/worktrees/blender-city-layout/train-simulator');checks={}
def geometry(m):return hashlib.sha256(repr(([tuple(v.co) for v in m.vertices],[tuple(p.vertices) for p in m.polygons])).encode()).hexdigest()
source=bpy.data.objects['survey_27725'];old=bpy.data.meshes[source['town_hall_review_original_mesh']];bad=set(json.loads(source['town_hall_review_original_mesh_removed_faces']));assert [tuple(v.co) for v in source.data.vertices]==[tuple(v.co) for v in old.vertices];assert [tuple(p.vertices) for p in source.data.polygons]==[tuple(p.vertices) for p in old.polygons if p.index not in bad]
a=json.loads((R/'docs/town-hall-review-audit.json').read_text())
for name,h in a.get('preserved_geometry_guards',{}).items():assert geometry(bpy.data.objects[name].data)==h,name;checks[name]=h
o=bpy.data.objects['Town Hall review authored portico and facade bays'];assert all(not any(n.type=='TEX_IMAGE' for n in m.node_tree.nodes) for m in o.data.materials);assert bpy.context.scene['town_hall_review_revision']=='source-fitted-portico-v1'
result={'source_vertex_positions_unchanged':True,'source_faces_removed_recoverably':sorted(bad),'outside_source_faces_connectivity_exact':True,'tower_roof_geometry_guards':checks,'authored_faces':len(o.data.polygons),'no_photographic_nodes_in_new_materials':True};(R/'docs/town-hall-review-verification.json').write_text(json.dumps(result,indent=2)+'\n');print('TOWN_HALL_REVIEW_VERIFIED',len(checks),len(o.data.polygons),flush=True)
