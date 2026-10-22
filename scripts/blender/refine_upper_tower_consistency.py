"""Unify arbitrary generic finishes within public structure groups."""
import bpy,json,collections
from pathlib import Path
root=globals().get('root') or Path(bpy.data.filepath).resolve().parents[3]
groups=json.loads((root/'assets/source/environment/city-facade-groups.json').read_text())['groups']
marker='upper_tower_colour_consistency_v1'
rows={str(b['id']):b for b in json.loads((root/'public/data/buildings.json').read_text())['buildings']}
excluded={'803943','815210','819362','811022','810427','813491'}
if not bpy.context.scene.get(marker):
 structures=collections.defaultdict(list)
 for obj in bpy.data.objects:
  key=str(obj.get('source_id'))
  if not obj.name.startswith('survey_') or obj.type!='MESH' or not obj.data.materials or key not in groups:continue
  if groups[key]['structure_height']<=45 or groups[key]['structure_id'] in excluded or rows.get(key,{}).get('base',0)<20:continue
  mat=obj.data.materials[0]
  if mat and (mat.name.startswith('Authored tall plain masonry - Authored ') or mat.name.startswith('Authored grouped tower glazing') or any(mat.name.startswith('Authored '+kind+' facade') for kind in ['stone','concrete','terracotta','glass'])):structures[groups[key]['structure_id']].append(obj)
 records=[]
 for structure,objects in structures.items():
  if len({obj.data.materials[0].name for obj in objects})<2:continue
  # Dominant vertical area, not a measured material classification.
  anchor=max(objects,key=lambda obj:sum(p.area for p in obj.data.polygons if abs(p.normal.z)<.5))
  finish=anchor.data.materials[0];changes=[]
  for obj in objects:
   previous=obj.data.materials[0].name
   if previous==finish.name:continue
   obj['previous_upper_tower_material']=previous;obj.data.materials[0]=finish
   obj['colour_basis']='Authored finish consistent within source structure group; actual material and colour unverified'
   changes.append({'section':obj.get('source_id'),'previous':previous})
  records.append({'structure':structure,'anchor_section':anchor.get('source_id'),'finish':finish.name,'changes':changes})
 bpy.context.scene[marker]=len(records)
 (root/'assets/source/environment/city-upper-tower-consistency.json').write_text(json.dumps({'source':'city-facade-groups.json','groups':records,'limits':'Dominant vertical-area generic finish applied only to eligible sections base>=20m in source groups height>45m; selected bespoke landmarks excluded. Actual colours, mixed material zones, podium differentiation and current condition unverified. Individually authored landmark finishes excluded.'},indent=2)+'\n')
 print('VERIFIED upper tower colour consistency',len(records),'groups',sum(len(r['changes']) for r in records),'changed sections',flush=True)
