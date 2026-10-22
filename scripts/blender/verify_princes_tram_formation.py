import bpy,json,math
from pathlib import Path
r=Path(bpy.data.filepath).resolve().parents[3];s=bpy.context.scene;assert s.get('princes_bridge_tram_formation_revision')=='adjacent-labelled-mapped-formation-v1';d=json.loads((r/'assets/source/environment/princes-bridge-tram-formation.json').read_text());checks=[]
for p in d['parts']:
 o=bpy.data.objects['Municipal Princes Bridge tram formation '+p['assetid']];assert o.data.materials[0].name=='Authored Princes Bridge tram concrete';assert len(o.data.vertices)==len(p['vertices']);assert len(o.data.polygons)==len(p['faces']);error=max(math.dist(tuple(v.co),q) for v,q in zip(o.data.vertices,p['vertices']));assert error<.00002;assert all(f.normal.z>.99 for f in o.data.polygons);checks.append({'assetid':p['assetid'],'type':p['type'],'faces':len(o.data.polygons),'coordinate_error_m':error,'area_m2':p['area_m2']})
assert s.camera.name=='37 CBD aerial review';assert not any(n.type=='TEX_IMAGE' for m in bpy.data.materials if m.use_nodes for n in m.node_tree.nodes)
(r/'docs/princes-bridge-tram-formation-audit.json').write_text(json.dumps({'saved_file_verification':checks,'limits':d['limits'],'source_url':d['source_url']},indent=2)+'\n');print('SAVED_BRIDGE_TRAM_FORMATION_VERIFIED',len(checks),flush=True)
