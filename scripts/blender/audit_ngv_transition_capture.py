"""Measure authored transition against retained capture; no scene mutation."""
import bpy,json,statistics
from pathlib import Path
from mathutils import Vector
r=Path(bpy.data.filepath).resolve().parents[3]
d=json.loads((r/'assets/source/environment/federation-ngv-complete-captured-roof.json').read_text())
o=bpy.data.objects['Continuous surveyed roofs - authored finishes'];rows=[]
for q in d['samples']:
 x,y,z=q
 if not (232<=x<=243 and 105<=y<=137):continue
 hit,p,n,i=o.ray_cast(o.matrix_world.inverted()@Vector((x,y,80)),Vector((0,0,-1)))
 if hit:
  p=o.matrix_world@p
  rows.append({'capture_xyz':q,'authored_z':p.z,'residual_m':p.z-z})
result={'source':d['source'],'capture':d['capture'],'scope':'Authored north-east transition, x232..243 y105..137','samples':rows,'median_absolute_residual_m':statistics.median(abs(v['residual_m']) for v in rows),'limits':'Capture includes raised features and artefacts; residuals are diagnostic, not correction targets. Original scene unchanged.'}
(r/'docs/ngv-transition-capture-audit.json').write_text(json.dumps(result,indent=2)+'\n')
print('TRANSITION_CAPTURE_AUDIT',len(rows),result['median_absolute_residual_m'],flush=True)
