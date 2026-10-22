import bpy,json
from pathlib import Path
from mathutils import Vector
r=Path(bpy.data.filepath).resolve().parents[3];out=[];dg=bpy.context.evaluated_depsgraph_get()
for x in range(75,135,2):
 for y in range(-150,-55,2):
  hit,p,n,i,o,m=bpy.context.scene.ray_cast(dg,Vector((x,y,20)),Vector((0,0,-1)))
  if hit and 7<p.z<11:out.append({'point':list(p),'object':o.name})
from collections import Counter
print('HIGH_BRIDGE_OVERLAPS',Counter(q['object'] for q in out),out[:8],flush=True)
(r/'docs/princes-bridge-datum-overlap-study.json').write_text(json.dumps(out,indent=2)+'\n')
