"""Authored western ballast margins around retained official rail alignments."""
import bpy,json
from pathlib import Path
r=Path(bpy.data.filepath).resolve().parents[3];name='Western rail alignments - authored ballast margins'
if not bpy.data.objects.get(name):
 d=json.loads((r/'assets/source/environment/western-rail-ballast-margins.json').read_text());m=bpy.data.meshes.new(name);m.from_pydata(d['vertices'],[],d['faces']);m.materials.append(bpy.data.materials['Authored railway precinct aggregate']);m.update();assert all(p.normal.z>.99 for p in m.polygons);o=bpy.data.objects.new(name,m);bpy.data.collections['GROUND - official horizontal geography, authored levels'].objects.link(o);o['limits']=d['limits'];o['source_url']=d['source'];o['source_license']=d['license'];o['attribution']=d['attribution'];o['source_ufis']=','.join(map(str,d['source_ufis']));o['area_m2']=d['area_m2'];bpy.context.scene['western_rail_ballast_revision']='authored-six-point-four-v1';print('WESTERN_BALLAST_APPLIED',d['area_m2'],len(m.polygons),flush=True)
else:print('WESTERN_BALLAST_ALREADY_APPLIED',flush=True)
