import bpy,json
from pathlib import Path
R=Path(bpy.data.filepath).resolve().parents[3];name='QVM authored interior carpark asphalt'
if not bpy.data.objects.get(name):
 d=json.loads((R/'assets/source/environment/qvm-authored-carpark-surface.json').read_text());m=bpy.data.meshes.new(name);m.from_pydata(d['vertices'],[],d['faces']);m.materials.append(bpy.data.materials['Authored asphalt']);m.update();assert all(p.normal.z>.99 for p in m.polygons);o=bpy.data.objects.new(name,m);bpy.data.collections['GROUND - official horizontal geography, authored levels'].objects.link(o);o['source_url']=d['source'];o['limits']=d['limits'];o['area_m2']=d['area_m2'];print('VERIFIED QVM interior asphalt',d['area_m2'],flush=True)
