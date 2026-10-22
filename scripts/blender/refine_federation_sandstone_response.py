"""Recoverable authored buff sandstone response; colours estimated, no photo textures."""
import bpy,json
from pathlib import Path
r=Path(bpy.data.filepath).resolve().parents[3];s=bpy.context.scene;key='federation_sandstone_response_revision'
if not s.get(key):
 m=bpy.data.materials['Authored Federation Square sandstone'];backup=m.copy();backup.name=m.name+' before buff response';backup.use_fake_user=True;m['buff_response_backup']=backup.name;ramps=[n for n in m.node_tree.nodes if n.type=='VALTORGB'];assert len(ramps)==1
 colours=[(.28,.19,.115,1),(.40,.29,.19,1)];old=[list(e.color) for e in ramps[0].color_ramp.elements]
 for e,c in zip(ramps[0].color_ramp.elements,colours):e.color=c
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Roughness'].default_value=.8;m.diffuse_color=(.34,.24,.15,1);s[key]='authored-buff-ramp-v1';m['limits']='Authored buff sandstone colour estimates and roughness. Official material identity retained; values not measured or current-condition verified. Procedural noise only.';(r/'docs/federation-sandstone-response-audit.json').write_text(json.dumps({'before_ramp':old,'after_ramp':colours,'backup':backup.name,'reference':'https://fedsquare.com/history-design','limits':m['limits']},indent=2)+'\n');print('BUFF_SANDSTONE_RESPONSE_APPLIED',flush=True)
