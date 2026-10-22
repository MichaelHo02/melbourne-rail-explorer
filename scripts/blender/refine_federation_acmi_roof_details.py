"""Reconcile previously illustrative trim/equipment with fitted ACMI roof plane."""
import bpy,json,math
from pathlib import Path
r=Path(bpy.data.filepath).resolve().parents[3];s=bpy.context.scene;key='federation_acmi_roof_detail_revision'
if not s.get(key):
 assert s.get('federation_acmi_roof_revision')=='captured-slope-v1';d=json.loads((r/'assets/source/environment/federation-acmi-roof-fit.json').read_text());audit=json.loads((r/'docs/federation-acmi-roof-audit.json').read_text());oldtop=audit['previous_top'];c=d['plane'];o=bpy.data.objects['survey_17199'];vs=[o.matrix_world@v.co for v in o.data.vertices];base=min(v.z for v in vs);ring=[v for v in vs if abs(v.z-base)<.001]
 def inside(x,y,margin=.4):
  hit=False
  for a,b in zip(ring,ring[1:]+ring[:1]):
   dx,dy=b.x-a.x,b.y-a.y;t=max(0,min(1,((x-a.x)*dx+(y-a.y)*dy)/max(dx*dx+dy*dy,1e-12)))
   if math.hypot(x-a.x-t*dx,y-a.y-t*dy)<margin:return True
   if (a.y>y)!=(b.y>y) and x<(b.x-a.x)*(y-a.y)/(b.y-a.y)+a.x:hit=not hit
  return hit
 report={}
 for name,band in [('Authored roof edge cornices',.4),('Authored rooftop equipment - illustrative',3)]:
  o=bpy.data.objects.get(name)
  if not o:continue
  selected=[p for p in o.data.polygons if all(inside(*(o.matrix_world@o.data.vertices[i].co)[:2]) and oldtop-.4<(o.matrix_world@o.data.vertices[i].co).z<oldtop+band for i in p.vertices)];ids={i for p in selected for i in p.vertices}
  if not ids:continue
  assert not any(any(i in ids for i in p.vertices) for p in o.data.polygons if p not in selected),'Shared detail vertices'
  backup=o.data.copy();backup.name=o.name+' before ACMI roof detail fit';backup.use_fake_user=True;o['acmi_roof_detail_original_mesh']=backup.name
  for i in ids:
   v=o.data.vertices[i];q=o.matrix_world@v.co;q.z+=c[0]*q.x+c[1]*q.y+c[2]-oldtop;v.co=o.matrix_world.inverted()@q
  o.data.update();report[name]={'faces':len(selected),'vertices':len(ids)}
 s[key]='illustrative-details-fit-v1';(r/'docs/federation-acmi-roof-detail-audit.json').write_text(json.dumps({'objects':report,'limits':'Existing generic cornice strips and illustrative equipment only reconciled vertically to fitted historical roof. Their placement, existence and construction remain authored assumptions. No additional real architectural details claimed. Original meshes recoverable.'},indent=2)+'\n');print('ACMI_ROOF_DETAILS_FITTED',report,flush=True)
