"""Municipal bridge footway, kerb and channel polygons; authored vertical datum."""
import bpy,json
from pathlib import Path
r=Path(bpy.data.filepath).resolve().parents[3];s=bpy.context.scene
if not s.get('princes_bridge_pavement_revision'):
 d=json.loads((r/'assets/source/environment/princes-bridge-authored-pavements.json').read_text());col=bpy.data.objects['Municipal Princes Bridge carriageway 1425102'].users_collection[0]
 for p in d['parts']:
  name='Municipal Princes Bridge '+p['type']+' '+p['assetid'];m=bpy.data.meshes.new(name);m.from_pydata(p['vertices'],[],p['faces']);m.materials.append(bpy.data.materials['Authored asphalt' if p['type']=='Road Footway' else 'Authored Princes Bridge bluestone']);m.update();o=bpy.data.objects.new(name,m);col.objects.link(o)
  for k in ['assetid','type','surface_material','area_m2']:o[k]=p[k]
  o['source_url']=d['source_url'];o['source_sha256']=d['source_sha256'];o['limits']=d['limits']
 s['princes_bridge_pavement_revision']='municipal-pavement-planforms-v1'
 print('BRIDGE_PAVEMENTS_APPLIED',len(d['parts']),flush=True)
