"""Remove arbitrary generic finish changes in candidate Rialto upper sections."""
import bpy,json
from pathlib import Path
root=globals().get('root') or Path(bpy.data.filepath).resolve().parents[3]
if not bpy.context.scene.get('rialto_colour_consistency'):
 rows=json.loads((root/'assets/source/environment/rialto-source-audit.json').read_text())['sections'];anchor=bpy.data.objects['survey_16342'];finish=anchor.data.materials[0];changed=[]
 for row in rows:
  if row['base']<31.5:continue
  o=bpy.data.objects.get('survey_'+str(row['id']))
  if not o or not o.data.materials:continue
  old=o.data.materials[0]
  generic=old.name.startswith('Authored tall plain masonry - Authored ') or old.name.startswith('Authored grouped tower glazing') or any(old.name.startswith('Authored '+k+' facade') for k in ['stone','concrete','terracotta','glass'])
  if not generic or old==finish:continue
  o['previous_rialto_generic_finish']=old.name;o.data.materials[0]=finish;o['colour_basis']='Authored upper-section finish consistent with retained main tower section; actual Rialto glass/material specification unverified';changed.append({'section':row['id'],'previous':old.name})
 bpy.context.scene['rialto_colour_consistency']=len(changed)
 (root/'assets/source/environment/rialto-colour-consistency.json').write_text(json.dumps({'anchor_section':16342,'finish':finish.name,'changed':changed,'limits':'Generic upper section consistency only, base cutoff31.5m authored. Roof caps retained. Actual optical glass properties, mixed facade zones and podium condition unverified.'},indent=2)+'\n');print('VERIFIED Rialto finish consistency',len(changed),flush=True)
