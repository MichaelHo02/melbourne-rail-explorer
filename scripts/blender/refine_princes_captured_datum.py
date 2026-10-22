import bpy,json
from pathlib import Path
from mathutils import Vector
r=Path(bpy.data.filepath).resolve().parents[3];s=bpy.context.scene
if not s.get('princes_bridge_captured_datum_revision'):
 fit=json.loads((r/'assets/source/environment/princes-bridge-captured-datum-fit.json').read_text());top=fit['authored_deck_top_m'];delta=top-9.5;changes={}
 for o in bpy.data.objects:
  if o.type!='MESH':continue
  if o.name.startswith('Municipal Princes Bridge') or o.name=='Princes Bridge - authored simplified balustrade':
   o['captured_datum_original_location']=list(o.location);o.location.z+=delta;changes[o.name]={'translation_z':delta}
 for name in ['Princes Bridge authored arch spandrels','Princes Bridge authored piers and abutments']:
  o=bpy.data.objects[name];backup=o.data.copy();backup.use_fake_user=True;o['captured_datum_original_mesh']=backup.name
  for v in o.data.vertices:v.co.z=.05+(v.co.z-.05)*(top-.8-.05)/(8.7-.05)
  o.data.update();changes[name]={'vertical_scale_above_foundation':(top-.8-.05)/(8.7-.05)}
 o=bpy.data.objects['Princes Bridge authored six arch ribs per span'];backup=o.data.copy();backup.use_fake_user=True;o['captured_datum_original_curve']=backup.name;scale=(top-.8-.05)/(8.7-.05)
 for sp in o.data.splines:
  for v in sp.points:v.co.z=.05+(v.co.z-.05)*scale
 changes[o.name]={'curve_vertical_scale':scale}
 o=bpy.data.objects['survey_36402'];o['captured_datum_original_location']=list(o.location);o.location.z=top-9.5-.01;changes[o.name]={'location_z':o.location.z}
 b=next(q for q in json.loads((r/'public/data/buildings.json').read_text())['buildings'] if str(q['id'])=='36402');ring=[(x,-y) for x,y in b['ring']]
 def inside(x,y):
  hit=False
  for a,c in zip(ring,ring[1:]):
   if (a[1]>y)!=(c[1]>y) and x<(c[0]-a[0])*(y-a[1])/(c[1]-a[1])+a[0]:hit=not hit
  return hit
 o=bpy.data.objects['Continuous surveyed roofs - authored finishes'];m=o.data;ids=set()
 for p in m.polygons:
  if 8.8<p.center.z<9.6 and inside(p.center.x,p.center.y):ids.update(p.vertices)
 assert ids;other=set(v for p in m.polygons if not set(p.vertices).issubset(ids) for v in p.vertices);assert not ids.intersection(other),'Shared bridge roof vertices need isolation'
 backup=m.copy();backup.use_fake_user=True;o['princes_datum_original_mesh']=backup.name
 for i in ids:m.vertices[i].co.z=top
 m.update();changes[o.name]={'vertices':len(ids),'deck_top':top}
 s['princes_bridge_captured_datum_revision']='historical-capture-flat-deck6.2-v1';(r/'docs/princes-bridge-captured-datum-audit.json').write_text(json.dumps({'fit':fit,'changes':changes},indent=2)+'\n');print('CAPTURED_BRIDGE_DATUM_APPLIED',changes,flush=True)
