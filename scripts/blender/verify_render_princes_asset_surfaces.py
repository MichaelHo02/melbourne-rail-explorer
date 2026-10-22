import bpy,json,math
from pathlib import Path
r=Path(bpy.data.filepath).resolve().parents[3];s=bpy.context.scene;assert s.get('princes_bridge_asset_surface_revision')=='municipal-asset-polygons-v1';d=json.loads((r/'assets/source/environment/princes-bridge-authored-asset-surfaces.json').read_text());checks=[]
for p in d['parts']:
 o=bpy.data.objects['Municipal Princes Bridge carriageway '+p['assetid']];assert len(o.data.polygons)==len(p['faces']);error=max(math.dist(tuple(v.co),q) for v,q in zip(o.data.vertices,p['vertices']));assert error<.00002;assert all(f.normal.z>.99 for f in o.data.polygons);checks.append({'assetid':p['assetid'],'coordinate_error_m':error,'faces':len(o.data.polygons)})
assert bpy.data.objects['Vicmap bridge carriageway on survey 36402'].hide_render;assert s.camera.name=='37 CBD aerial review';assert not any(n.type=='TEX_IMAGE' for m in bpy.data.materials if m.use_nodes for n in m.node_tree.nodes);p=r/'docs/princes-bridge-asset-surface-audit.json';a=json.loads(p.read_text());a['saved_file_verification']=checks;p.write_text(json.dumps(a,indent=2)+'\n');print('SAVED_PRINCES_ASSETS_VERIFIED',checks,flush=True)
"""Fresh saved-scene precinct review; active camera unchanged on disk."""
import bpy
from pathlib import Path
r=Path(bpy.data.filepath).resolve().parents[3];s=bpy.context.scene;s.camera=bpy.data.objects['02 Flinders precinct'];s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True;s.render.resolution_x=1400;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.render.filepath=str(r/'docs/images/observatory-princes-asset-surfaces.png');bpy.ops.render.render(write_still=True);print('FLINDERS_STREET_REVIEW_RENDERED_NO_SAVE',flush=True)
