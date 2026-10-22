"""Authored sediment-toned water informed by Melbourne Water; geometry unchanged."""
import bpy,json
from pathlib import Path
r=Path(bpy.data.filepath).resolve().parents[3];s=bpy.context.scene;m=bpy.data.materials['Authored Yarra water colour'];key='yarra_sediment_shading_revision'
if not s.get(key):
 backup=m.copy();backup.name=m.name+' before sediment shading';backup.use_fake_user=True;m['sediment_original_material']=backup.name
 low=(.055,.044,.026,1);high=(.125,.096,.052,1)
 for n in m.node_tree.nodes:
  if n.type=='VALTORGB':n.color_ramp.elements[0].color=low;n.color_ramp.elements[-1].color=high
  elif n.type=='BSDF_PRINCIPLED':
   n.inputs['Base Color'].default_value=(.09,.07,.038,1);n.inputs['Roughness'].default_value=.24;n.inputs['Metallic'].default_value=0;n.inputs['IOR'].default_value=1.333;n.inputs['Transmission Weight'].default_value=.02
  elif n.type=='BUMP':n.inputs['Strength'].default_value=.12;n.inputs['Distance'].default_value=.012
 m.diffuse_color=(.09,.07,.038,1);m['reference']='https://www.melbournewater.com.au/water-and-environment/water-management/rivers-and-creeks/yarra-river';m['limits']='Melbourne Water explains muddy lower-river colour from eroded clay. Ochre/brown palette, roughness and ripple strength authored, not measured water quality, current turbidity or time-varying simulation. Shared retained water surface includes dock water; exact spatial colour variation unresolved. Boundary and water level unchanged. No photographic textures.';s[key]='authored-sediment-v1';(r/'docs/yarra-sediment-shading-audit.json').write_text(json.dumps({'material':m.name,'backup':backup.name,'low':low,'high':high,'roughness':.24,'IOR':1.333,'geometry_changed':False,'limits':m['limits']},indent=2)+'\n');print('YARRA_SEDIMENT_SHADING_APPLIED',flush=True)
s.camera=bpy.data.objects['Aerial overview']
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA'
