"""Authored generic paving on source-classified civic parcels."""
import bpy,json
from pathlib import Path
root=Path(bpy.data.filepath).resolve().parents[3];d=json.loads((root/'assets/source/environment/city-civic-surfaces.json').read_text());count=0
for part in d['parts']:
 name='Civic inventory authored paving '+part['source_id'];o=bpy.data.objects.get(name)
 if not o:
  m=bpy.data.meshes.new(name);m.from_pydata(part['vertices'],[],part['faces']);m.materials.append(bpy.data.materials['Authored stone pavement']);m.update();o=bpy.data.objects.new(name,m);bpy.data.collections['GROUND - official horizontal geography, authored levels'].objects.link(o)
  for key in ['source_id','name','area_m2']:o[key]=part[key]
  o['source_url']=d['source']['url'];o['source_sha256']=d['source_sha256'];o['limits']=d['limits']
 assert all(p.normal.z>0 for p in o.data.polygons);count+=1
bpy.context.scene['civic_inventory_paving_count']=count
print('VERIFIED civic paving parcels',count,'area',sum(p['area_m2'] for p in d['parts']),flush=True)
