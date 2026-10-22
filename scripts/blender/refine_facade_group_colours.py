"""Unify arbitrary generic finishes within public structure groups."""
import bpy,json,collections
from pathlib import Path
root=globals().get('root') or Path(bpy.data.filepath).resolve().parents[3]
groups=json.loads((root/'assets/source/environment/city-facade-groups.json').read_text())['groups']
marker='structure_colour_consistency_v1'
if not bpy.context.scene.get(marker):
 structures=collections.defaultdict(list)
 for obj in bpy.data.objects:
  key=str(obj.get('source_id'))
  if not obj.name.startswith('survey_') or obj.type!='MESH' or not obj.data.materials or key not in groups:continue
  mat=obj.data.materials[0]
  if mat and (mat.name.startswith('Authored plain masonry - Authored ') or any(mat.name.startswith('Authored '+kind+' facade') for kind in ['stone','concrete','terracotta','glass'])):structures[groups[key]['structure_id']].append(obj)
 records=[]
 for structure,objects in structures.items():
  if len({obj.data.materials[0].name for obj in objects})<2:continue
  # Dominant vertical area, not a measured material classification.
  anchor=max(objects,key=lambda obj:sum(p.area for p in obj.data.polygons if abs(p.normal.z)<.5))
  finish=anchor.data.materials[0];changes=[]
  for obj in objects:
   previous=obj.data.materials[0].name
   if previous==finish.name:continue
   obj['previous_generic_facade_material']=previous;obj.data.materials[0]=finish
   obj['colour_basis']='Authored finish consistent within source structure group; actual material and colour unverified'
   changes.append({'section':obj.get('source_id'),'previous':previous})
  records.append({'structure':structure,'anchor_section':anchor.get('source_id'),'finish':finish.name,'changes':changes})
 bpy.context.scene[marker]=len(records)
 (root/'assets/source/environment/city-facade-colour-consistency.json').write_text(json.dumps({'source':'city-facade-groups.json','groups':records,'limits':'Dominant vertical-area generic finish applied within retained structure IDs. Actual colours, mixed material zones, podium differentiation and current condition unverified. Individually authored landmark finishes excluded.'},indent=2)+'\n')
 print('VERIFIED facade colour consistency',len(records),'groups',sum(len(r['changes']) for r in records),'changed sections',flush=True)
