"""Captured entrance datum with approximate interior grade; reversible authored enclosure adjustment."""
import bpy,bmesh,json,hashlib
from pathlib import Path
r=Path(bpy.data.filepath).resolve().parents[3];s=bpy.context.scene;key='federation_atrium_floor_contact_revision'
if not s.get(key):
 evidence=json.loads((r/'docs/federation-entrance-ground-audit.json').read_text());north=evidence['median_z'];report={}
 def oldfloor(y):return 10.7+1.5*max(0,min(1,(139-y)/90))
 def newfloor(y):return north+(12.2-north)*max(0,min(1,(139-y)/90))
 roof=bpy.data.objects['Atrium capture guided glazed roof'];roof_hash=hashlib.sha256(str([tuple(v.co) for v in roof.data.vertices]).encode()).hexdigest()
 for name in ['Atrium assumed graded concrete floor','Atrium north west and southern glazing','Atrium authored200mm square steel frame']:
  o=bpy.data.objects[name];original=o.data;original.use_fake_user=True;o['floor_contact_original_mesh']=original.name;me=original.copy();o.data=me;changed=0
  for v in me.vertices:
   y,z=v.co.y,v.co.z;delta=newfloor(y)-oldfloor(y)
   if name.endswith('floor'):weight=1
   else:weight=max(0,min(1,(25.5-z)/(25.5-oldfloor(y))))
   if abs(delta*weight)>1e-6:v.co.z+=delta*weight;changed+=1
  if name.endswith('floor'):
   bm=bmesh.new();bm.from_mesh(me);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
  me.update();report[name]={'changed_vertices':changed,'faces':len(me.polygons),'backup':original.name}
 assert hashlib.sha256(str([tuple(v.co) for v in roof.data.vertices]).encode()).hexdigest()==roof_hash
 limits='Entrance datum from filtered May2020 ground cluster median. Whole interior grade to retained southern12.2m is authored approximation, not surveyed floor. Frame/glazing lower vertices follow linear vertical taper; roof and framing at/above25.5m unchanged. Adjacent closures and exact threshold unresolved.'
 s[key]='captured-entry-authored-grade-v1';(r/'docs/federation-atrium-floor-contact-audit.json').write_text(json.dumps({'north_z':north,'south_z':12.2,'objects':report,'roof_unchanged':True,'limits':limits},indent=2)+'\n');print('ATRIUM_FLOOR_CONTACT_APPLIED',report,flush=True)
else:print('ATRIUM_FLOOR_CONTACT_ALREADY_APPLIED',flush=True)
