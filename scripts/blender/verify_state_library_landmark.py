"""Read-only source-envelope and authored surface invariant checks."""
import bpy,json,hashlib
from pathlib import Path
R=Path(globals().get('root') or '/Users/holeminhthach/.codex/worktrees/blender-city-layout/train-simulator')
def geom(m):
 return hashlib.sha256(repr(([tuple(v.co) for v in m.vertices],[tuple(p.vertices) for p in m.polygons])).encode()).hexdigest()
checks={}
for o in bpy.data.objects:
 if 'state_library_original_mesh' in o:
  old=bpy.data.meshes[o['state_library_original_mesh']];assert geom(old)==geom(o.data),o.name;checks[o.name]=geom(o.data)
o=bpy.data.objects['State Library authored portico facade and dome'];assert len(o.data.polygons)>1100
assert all(not any(n.type=='TEX_IMAGE' for n in m.node_tree.nodes) for m in o.data.materials)
assert bpy.data.objects['survey_12852'].hide_render
assert bpy.context.scene['state_library_revision']=='portico-dome-v1'
assert len(checks)==15
result={'source_envelope_geometry_unchanged':checks,'authored_faces':len(o.data.polygons),'no_photographic_nodes_in_library_materials':True,'upper_envelope_recoverably_hidden':True};(R/'docs/state-library-verification.json').write_text(json.dumps(result,indent=2)+'\n');print('STATE_LIBRARY_VERIFIED',len(checks),len(o.data.polygons),flush=True)
