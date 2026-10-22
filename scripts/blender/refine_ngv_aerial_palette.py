"""Own reference-informed mineral palette; preserve geometry and recoverable materials."""
import bpy,json
from pathlib import Path
r=Path(bpy.data.filepath).resolve().parents[3];s=bpy.context.scene
key='ngv_aerial_palette_revision'
if not s.get(key):
 report={}
 for label,low,high,rough,metal in [('sandstone',(.34,.23,.18),(.46,.34,.27),.78,0),('zinc',(.105,.145,.139),(.19,.23,.215),.57,.45)]:
  m=bpy.data.materials['Authored Federation Square '+label];old=m.copy();old.name=m.name+' before NGV aerial palette';old.use_fake_user=True
  m['aerial_palette_backup']=old.name;m.diffuse_color=(*high,1)
  p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*high,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
  for n in m.node_tree.nodes:
   if n.type=='VALTORGB':n.color_ramp.elements[0].color=(*low,1);n.color_ramp.elements[-1].color=(*high,1)
  assert not any(n.type=='TEX_IMAGE' for n in m.node_tree.nodes)
  report[label]={'backup':old.name,'low':low,'high':high,'roughness':rough,'metallic':metal}
 s[key]='reference-mineral-aerial-v1'
 (r/'docs/ngv-aerial-palette-audit.json').write_text(json.dumps({'materials':report,'geometry_changed':False,'reference':'https://www.batessmart.com/projects/fed-square','limits':'Own warm mineral stone and muted green-grey zinc, informed visually by architect exterior references. No sampled colours or photographic textures. Shared Federation materials affected; panel distribution and present-day calibrated colours approximate.'},indent=2)+'\n')
 bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
exec((r/'scripts/blender/render_ngv_aerial_readiness.py').read_text().replace('observatory-ngv-aerial-readiness.png','observatory-ngv-aerial-palette.png'))
