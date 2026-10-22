"""Trial height-supported eastern roof material correction; no file save."""
import bpy,json
from pathlib import Path
r=Path(bpy.data.filepath).resolve().parents[3];o=bpy.data.objects['Flinders station - municipal 2020 scan, authored colours'];rings=[q['ring'] for q in json.loads((r/'assets/source/environment/flinders-scan-material-zones.json').read_text())['zones']]
def inside(x,y,ring):
 hit=False
 for i,(ax,ay) in enumerate(ring):
  bx,by=ring[i-1]
  if (ay>y)!=(by>y) and x<(bx-ax)*(y-ay)/(by-ay)+ax:hit=not hit
 return hit
backup=o.data.copy();backup.name='Flinders scan before lower roof material correction';backup.use_fake_user=True;o['lower_roof_original_mesh']=backup.name
changed=[]
for p in o.data.polygons:
 if p.material_index==2 and p.normal.z>.35 and 10<p.center.z<15 and any(inside(p.center.x,p.center.y,ring) for ring in rings):changed.append(p.index);p.material_index=4
(r/'docs/flinders-concourse-roof-material-audit.json').write_text(json.dumps({'changed_faces':len(changed),'face_indices':changed,'limits':'Authored classification within retained station section zones, upward and pitched faces at10..15m; boundaries and exact roof finish remain unverified. Scan geometry unchanged.'},indent=2)+'\n')

bpy.context.scene['flinders_lower_roof_material_revision']='captured-lower-roof-zone-v1'
assert changed and len(o.data.polygons)==len(backup.polygons)
assert all(tuple(p.vertices)==tuple(q.vertices) for p,q in zip(o.data.polygons,backup.polygons))
assert all(n.type!='TEX_IMAGE' for m in o.data.materials for n in m.node_tree.nodes)
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print('SAVED_LOWER_ROOF_MATERIAL',len(changed),flush=True)
