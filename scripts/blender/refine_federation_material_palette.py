"""Reference-informed own sandstone/zinc palette; no sampled or photographic textures."""
import bpy,json
from pathlib import Path
r=Path(bpy.data.filepath).resolve().parents[3];s=bpy.context.scene;key='federation_material_palette_revision'
if not s.get(key):
 report={}
 for label,low,high,rough,metal in [('sandstone',(.19,.125,.074),(.32,.23,.15),.8,0),('zinc',(.075,.079,.072),(.145,.15,.139),.48,.55),('glass',(.026,.046,.042),(.026,.046,.042),.2,.12)]:
  m=bpy.data.materials['Authored Federation Square '+label];backup=m.copy();backup.name=m.name+' before warm mineral palette';backup.use_fake_user=True;m['palette_backup']=backup.name;m.diffuse_color=(*high,1);p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*high,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
  for n in m.node_tree.nodes:
   if n.type=='VALTORGB':n.color_ramp.elements[0].color=(*low,1);n.color_ramp.elements[-1].color=(*high,1)
  assert not any(n.type=='TEX_IMAGE' for n in m.node_tree.nodes);m['limits']='Authored linear-space warm sandstone and dark neutral zinc colours, visually informed by official2024 exterior reference. No sampled pixel values; exact finish distribution and current colour calibration unverified.';report[label]={'backup':backup.name,'low':low,'high':high}
 s[key]='warm-mineral-v1';(r/'docs/federation-material-palette-audit.json').write_text(json.dumps({'materials':report,'geometry_changed':False,'reference':'https://fedsquare.com/plan-your-event/atrium','limits':m['limits']},indent=2));print('FEDERATION_PALETTE_UPDATED',flush=True)
else:print('FEDERATION_PALETTE_ALREADY_APPLIED',flush=True)
