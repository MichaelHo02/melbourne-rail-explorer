"""Add restrained authored separation guides on selected official road alignments."""
import bpy,json
from pathlib import Path
R=Path(bpy.data.filepath).resolve().parents[3];name='Authored CBD midblock lane guides - illustrative'
if not bpy.data.objects.get(name):
 d=json.loads((R/'assets/source/environment/cbd-authored-lane-guides.json').read_text());mesh=bpy.data.meshes.new(name);mesh.from_pydata(d['vertices'],[],d['faces']);mesh.materials.append(bpy.data.materials['Authored worn lane paint']);mesh.update();assert all(p.normal.z>.99 for p in mesh.polygons)
 o=bpy.data.objects.new(name,mesh);bpy.data.collections['GROUND - official horizontal geography, authored levels'].objects.link(o);o['source_url']=d['source'];o['source_ufis']=','.join(map(str,d['ufis']));o['limits']=d['limits'];o['dash_count']=d['dash_count'];print('VERIFIED midblock lane guides',d['dash_count'],'upward strips',flush=True)
