import bpy,json,hashlib
from pathlib import Path
R=Path(globals().get('root') or '/Users/holeminhthach/.codex/worktrees/blender-city-layout/train-simulator')
def geom(m):return hashlib.sha256(repr(([tuple(v.co) for v in m.vertices],[tuple(p.vertices) for p in m.polygons])).encode()).hexdigest()
checks={}
for o in bpy.data.objects:
 if 'parliament_original_mesh' in o:
  old=bpy.data.meshes[o['parliament_original_mesh']];assert geom(old)==geom(o.data),o.name;checks[o.name]=geom(o.data)
o=bpy.data.objects['Parliament authored built colonnade and steps'];assert len(checks)==14;assert all(not any(n.type=='TEX_IMAGE' for n in m.node_tree.nodes) for m in o.data.materials);assert bpy.context.scene['parliament_revision']=='built-colonnade-v1';assert max(v.co.z for v in o.data.vertices)<26
result={'source_envelope_geometry_unchanged':checks,'authored_faces':len(o.data.polygons),'no_photographic_nodes_in_new_materials':True,'no_unbuilt_dome':True,'source_envelopes_retained_recoverably':True};(R/'docs/parliament-verification.json').write_text(json.dumps(result,indent=2)+'\n');print('PARLIAMENT_VERIFIED',len(checks),len(o.data.polygons),flush=True)
