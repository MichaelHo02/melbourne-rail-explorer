"""Restrained generic roof weathering, authored colour estimates and recoverable shaders."""
import bpy,json
from pathlib import Path
r=Path(bpy.data.filepath).resolve().parents[3];s=bpy.context.scene;key='generic_roof_weathering_revision'
if not s.get(key):
 report={}
 for name in ['Authored pale roof finish','Authored warm roof finish','Authored light zinc roof finish']:
  m=bpy.data.materials[name];ramps=[n for n in m.node_tree.nodes if n.type=='VALTORGB'];assert len(ramps)==1;old=[list(e.color) for e in ramps[0].color_ramp.elements];assert len(old)==2;backup=m.copy();backup.name=name+' before restrained weathering';backup.use_fake_user=True;m['roof_weathering_backup']=backup.name;mean=[(old[0][j]+old[1][j])/2 for j in range(3)]
  for e,c in zip(ramps[0].color_ramp.elements,old):
   q=[mean[j]+.25*(c[j]-mean[j]) for j in range(3)]
   if name=='Authored light zinc roof finish':lum=.2126*q[0]+.7152*q[1]+.0722*q[2];q=[.3*v+.7*lum for v in q]
   e.color=(*q,1)
  report[name]={'before':old,'after':[list(e.color) for e in ramps[0].color_ramp.elements],'backup':backup.name}
 s[key]='quarter-contrast-neutral-zinc-v1';(r/'docs/city-roof-weathering-audit.json').write_text(json.dumps({'materials':report,'limits':'Generic illustrative roof palette, not a material inventory. Ramp contrast reduced to25%; zinc blue tint desaturated70%. Source geometry, assignment patterns and landmark-specific finishes retained. No photographic textures.'},indent=2)+'\n');print('ROOF_WEATHERING_REFINED',flush=True)
