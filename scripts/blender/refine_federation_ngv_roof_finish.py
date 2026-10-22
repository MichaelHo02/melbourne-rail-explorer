"""Geometrically matched NGV cap finish; no roof shape or photographic-texture changes."""
import bpy,json,math
from pathlib import Path
r=Path(bpy.data.filepath).resolve().parents[3];s=bpy.context.scene;key='federation_ngv_roof_finish_revision'
if not s.get(key):
 data=json.loads((r/'public/data/buildings.json').read_text())['buildings'];sections=[]
 for sid in [16221,16222,16223]:
  b=next(b for b in data if int(b['id'])==sid);o=bpy.data.objects['survey_'+str(sid)];sections.append((sid,[(x,-y) for x,y in b['ring']],max((o.matrix_world@v.co).z for v in o.data.vertices)))
 def contains(q,ring):
  x,y=q.x,q.y;inside=False
  for a,b in zip(ring,ring[1:]+ring[:1]):
   dx,dy=b[0]-a[0],b[1]-a[1];den=dx*dx+dy*dy;t=max(0,min(1,((x-a[0])*dx+(y-a[1])*dy)/den)) if den else 0
   if math.hypot(x-a[0]-t*dx,y-a[1]-t*dy)<.005:return True
   if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:inside=not inside
  return inside
 o=bpy.data.objects['Continuous surveyed roofs - authored finishes'];m=o.data;zinc=bpy.data.materials['Authored Federation Square zinc'];slot=next((i for i,a in enumerate(m.materials) if a==zinc),None)
 if slot is None:slot=len(m.materials);m.materials.append(zinc)
 records=[]
 for p in m.polygons:
  if m.materials[p.material_index].name!='Authored pale roof finish':continue
  qs=[o.matrix_world@m.vertices[i].co for i in p.vertices]
  for sid,ring,top in sections:
   if all(abs(q.z-top)<.005 and contains(q,ring) for q in qs):records.append({'face':p.index,'previous_material':p.material_index,'source_section':sid});break
 assert records,'No unambiguous NGV caps found'
 text=bpy.data.texts.new('NGV roof original material assignments.json');text.write(json.dumps(records));o['ngv_roof_finish_recovery']=text.name
 for rec in records:m.polygons[rec['face']].material_index=slot
 s[key]='matched-caps-zinc-v1';limits='Roof material type informed by municipal2018 heritage nomination. Flat cap matching uses source footprints and current section top heights, all vertices within5mm tolerance. Exact roof glazing distribution, folds, finish weathering and present-day specification unresolved; zinc colour authored. Existing geometry and Atrium masks unchanged.'
 (r/'docs/federation-ngv-roof-finish-audit.json').write_text(json.dumps({'changed_faces':len(records),'sections':[{'id':sid,'current_top':top} for sid,ring,top in sections],'recovery_text':text.name,'reference':'https://mvga-prod-files.s3.ap-southeast-4.amazonaws.com/public/about-council/committees-meetings/meeting-archive/MeetingAgendaItemAttachments/843/15077/DEC18%2520FMC2%2520AGENDA%2520ITEM%25206.4.pdf','limits':limits},indent=2)+'\n');print('NGV_ROOF_FINISH_APPLIED',len(records),flush=True)
else:print('NGV_ROOF_FINISH_ALREADY_APPLIED',flush=True)
