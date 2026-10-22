"""Author aggregate ground margins from retained Flinders ordinary rail lines."""
import bpy,json
from pathlib import Path
R=Path(bpy.data.filepath).resolve().parents[3];name='Flinders authored rail ground margins';o=bpy.data.objects.get(name)
if o:bpy.data.objects.remove(o,do_unlink=True)
d=json.loads((R/'assets/source/environment/flinders-authored-ground-margins.json').read_text());mesh=bpy.data.meshes.new(name);mesh.from_pydata(d['vertices'],[],d['faces']);mesh.materials.append(bpy.data.materials['Authored railway precinct aggregate']);mesh.update();assert all(p.normal.z>.99 for p in mesh.polygons);o=bpy.data.objects.new(name,mesh);bpy.data.collections['GROUND - official horizontal geography, authored levels'].objects.link(o)
for k in ['source_url','source_sha256','area_m2','limits','license','attribution']:o[k]=d[k]
o['source_ufis']=','.join(map(str,d['source_ufis']));print('VERIFIED rail ground margins applied',len(mesh.polygons),d['area_m2'],flush=True)
