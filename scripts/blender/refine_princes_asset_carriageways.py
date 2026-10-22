"""Recoverable municipal carriageway polygons on retained Princes Bridge deck."""
import bpy,json
from pathlib import Path
r=Path(bpy.data.filepath).resolve().parents[3];s=bpy.context.scene;key='princes_bridge_asset_surface_revision'
if not s.get(key):
 d=json.loads((r/'assets/source/environment/princes-bridge-authored-asset-surfaces.json').read_text());assert len(d['parts'])==2;old=bpy.data.objects['Vicmap bridge carriageway on survey 36402'];old['asset_replacement_original_hide_render']=old.hide_render;old['asset_replacement_original_hide_viewport']=old.hide_viewport;old.hide_render=True;old.hide_viewport=True
 for p in d['parts']:
  name='Municipal Princes Bridge carriageway '+p['assetid'];m=bpy.data.meshes.new(name);m.from_pydata(p['vertices'],[],p['faces']);m.materials.append(bpy.data.materials['Authored asphalt']);m.update();o=bpy.data.objects.new(name,m);old.users_collection[0].objects.link(o);o['source_url']=d['source_url'];o['source_sha256']=d['source_sha256'];o['assetid']=p['assetid'];o['source_surface_material']=p['surface_material'];o['limits']=d['limits'];o['area_m2']=p['area_m2']
 s[key]='municipal-asset-polygons-v1';(r/'docs/princes-bridge-asset-surface-audit.json').write_text(json.dumps({'assets':[p['assetid'] for p in d['parts']],'area_m2':sum(p['area_m2'] for p in d['parts']),'original_buffer_retained':old.name,'limits':d['limits']},indent=2)+'\n');print('PRINCES_ASSET_SURFACES_APPLIED',flush=True)

# Repair triangulator winding in existing recoverable assets.
d=json.loads((r/"assets/source/environment/princes-bridge-authored-asset-surfaces.json").read_text())
for p in d["parts"]:
 o=bpy.data.objects["Municipal Princes Bridge carriageway "+p["assetid"]];o.data.clear_geometry();o.data.from_pydata(p["vertices"],[],p["faces"]);o.data.update()
