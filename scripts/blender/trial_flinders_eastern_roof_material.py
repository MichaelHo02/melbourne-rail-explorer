"""Trial height-supported eastern roof material correction; no file save."""
import bpy,json
from pathlib import Path
r=Path(bpy.data.filepath).resolve().parents[3];o=bpy.data.objects['Flinders station - municipal 2020 scan, authored colours'];ring=next(q['ring'] for q in json.loads((r/'assets/source/environment/flinders-scan-material-zones.json').read_text())['zones'] if q['source_id']=='1148')
def inside(x,y):
 hit=False
 for i,(ax,ay) in enumerate(ring):
  bx,by=ring[i-1]
  if (ay>y)!=(by>y) and x<(bx-ax)*(y-ay)/(by-ay)+ax:hit=not hit
 return hit
changed=[]
for p in o.data.polygons:
 if p.material_index==2 and p.normal.z>.7 and 10<p.center.z<15 and inside(p.center.x,p.center.y):changed.append(p.index);p.material_index=4
(r/'docs/flinders-eastern-roof-material-trial-audit.json').write_text(json.dumps({'changed_faces':len(changed),'face_indices':changed,'limits':'Authored classification within surveyed section1148, upward faces at10..15m; boundaries and exact roof finish remain unverified. Scan geometry unchanged.'},indent=2)+'\n')
exec(compile((r/'scripts/blender/render_swanston_approach_detail.py').read_text().replace('observatory-swanston-approach-detail.png','observatory-flinders-eastern-roof-material-trial.png'),'render','exec'))
