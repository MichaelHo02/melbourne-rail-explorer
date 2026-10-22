"""Reduce aerial aliasing in authored Federation cobblestone response."""
import bpy,json
from pathlib import Path
root=Path(bpy.data.filepath).resolve().parents[3];m=bpy.data.materials['Authored Main Square sandstone pavers']
if not m.get('aerial_paving_revision'):
 backup=m.copy();backup.name='Federation paving before aerial response';backup.use_fake_user=True
 for n in m.node_tree.nodes:
  if n.type=='TEX_BRICK':
   n.inputs['Color1'].default_value=(.27,.15,.065,1);n.inputs['Color2'].default_value=(.38,.24,.115,1);n.inputs['Mortar'].default_value=(.18,.12,.07,1);n.inputs['Mortar Size'].default_value=.003
  if n.type=='BUMP':n.inputs['Strength'].default_value=.10;n.inputs['Distance'].default_value=.003
 m['aerial_paving_revision']='restrained-cobble-v1';m['limits']='Authored sandstone colours and shallower procedural joints; existing illustrative cobble dimensions retained. Not calibrated current stone colours or actual laying pattern; broader deck boundary unresolved.'
 assert not any(n.type=='TEX_IMAGE' for n in m.node_tree.nodes)
 (root/'docs/federation-paving-response-audit.json').write_text(json.dumps({'source':'https://fedsquare.com/venues/main-square','supplier_context':'https://anston.com.au/projects/federation-square/','material_backup':backup.name,'limits':m['limits'],'geometry_changed':False},indent=2));print('PAVING_RESPONSE_APPLIED',flush=True)
else:print('PAVING_RESPONSE_ALREADY_APPLIED',flush=True)
