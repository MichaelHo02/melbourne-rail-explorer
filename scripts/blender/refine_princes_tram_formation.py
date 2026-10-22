import bpy,json
from pathlib import Path
r=Path(bpy.data.filepath).resolve().parents[3];s=bpy.context.scene
if not s.get('princes_bridge_tram_formation_revision'):
 d=json.loads((r/'assets/source/environment/princes-bridge-tram-formation.json').read_text());col=bpy.data.objects['Municipal Princes Bridge carriageway 1425102'].users_collection[0]
 for p in d['parts']:
  name='Municipal Princes Bridge tram formation '+p['assetid'];m=bpy.data.meshes.new(name);m.from_pydata(p['vertices'],[],p['faces']);m.materials.append(bpy.data.materials['Authored asphalt']);m.update();o=bpy.data.objects.new(name,m);col.objects.link(o)
  for k in ['assetid','type','surface_material','area_m2']:o[k]=p[k]
  o['source_url']=d['source_url'];o['source_sha256']=d['source_sha256'];o['limits']=d['limits']
 s['princes_bridge_tram_formation_revision']='adjacent-labelled-mapped-formation-v1';print('TRAM_FORMATION_APPLIED',len(d['parts']),flush=True)

# Municipal classification is concrete, separate from HMA carriageways.
mat=bpy.data.materials.get('Authored Princes Bridge tram concrete') or bpy.data.materials.new('Authored Princes Bridge tram concrete');mat.use_nodes=True;mat.diffuse_color=(.22,.23,.225,1);bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.22,.23,.225,1);bs.inputs['Roughness'].default_value=.88
for p in json.loads((r/'assets/source/environment/princes-bridge-tram-formation.json').read_text())['parts']:
 assert p['surface_material']=='Concrete';o=bpy.data.objects['Municipal Princes Bridge tram formation '+p['assetid']];o.data.materials.clear();o.data.materials.append(mat)
