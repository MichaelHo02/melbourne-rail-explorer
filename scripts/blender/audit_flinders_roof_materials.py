"""Inspect current saved scan roof classifications; no scene mutation."""
import bpy,json
from pathlib import Path
from collections import defaultdict
r=Path(bpy.data.filepath).resolve().parents[3]
o=bpy.data.objects['Flinders station - municipal 2020 scan, authored colours']
rows=defaultdict(lambda:{'faces':0,'area_m2':0,'height_min':1e9,'height_max':-1e9})
for p in o.data.polygons:
 if p.normal.z<.35 or p.center.z<18:continue
 k=o.data.materials[p.material_index].name
 v=rows[k];v['faces']+=1;v['area_m2']+=p.area;v['height_min']=min(v['height_min'],p.center.z);v['height_max']=max(v['height_max'],p.center.z)
out={'object':o.name,'roof_selection':'Upward normal z >= 0.35; local height >= 18m; diagnostic includes domes and other upper surfaces, not roof ownership proof','materials':dict(rows),'modifiers':[{'name':m.name,'type':m.type} for m in o.modifiers],'limits':'Classification audit only. Geometry damage and material boundary accuracy require spatial review.'}
(r/'docs/flinders-current-roof-material-audit.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out),flush=True)
