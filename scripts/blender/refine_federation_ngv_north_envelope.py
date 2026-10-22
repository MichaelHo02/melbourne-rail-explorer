"""Recoverable northern NGV envelope fit; transition boundaries authored."""
import bpy,json,math,bmesh
from pathlib import Path
from mathutils import Vector
r=Path(bpy.data.filepath).resolve().parents[3]
if not bpy.context.scene.get('federation_ngv_north_roof_revision'):
 d=json.loads((r/'docs/federation-ngv-roof-regions-audit.json').read_text());c=d['diagnostic_bands'][2]['plane']
 ring=next(b['ring'] for b in json.loads((r/'public/data/buildings.json').read_text())['buildings'] if str(b['id'])=='16222');ring=[(x,-y) for x,y in ring]
 def inside(x,y):
  result=False
  for a,b in zip(ring,ring[1:]+ring[:1]):
   dx,dy=b[0]-a[0],b[1]-a[1];t=max(0,min(1,((x-a[0])*dx+(y-a[1])*dy)/max(dx*dx+dy*dy,1e-12)))
   if math.hypot(x-a[0]-t*dx,y-a[1]-t*dy)<.005:return True
   if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:result=not result
  return result
 # Cut only unambiguous NGV cap faces, preserving unrelated roof geometry.
 for o in bpy.data.objects:
  if o.type!='MESH' or not (o.name.startswith('Continuous surveyed roofs - authored finishes') or o.name in ['survey_16222','NGV east Atrium exposed envelope closure','Atrium adjacent upper and lower cut closures'] or 'Federation Square - authored triangular cladding' in o.name):continue
  backup=o.data.copy();backup.name=o.name+' before NGV northern fit';backup.use_fake_user=True;o['ngv_north_original_mesh']=backup.name
  bm=bmesh.new();bm.from_mesh(o.data)
  for northing in [95,100,105]:
   faces=[f for f in bm.faces if (o.name in ['NGV east Atrium exposed envelope closure','Atrium adjacent upper and lower cut closures'] or all(inside(*(o.matrix_world@v.co)[:2]) for v in f.verts)) and max((o.matrix_world@v.co).z for v in f.verts)>27.9]
   geom=list(set(faces+[e for f in faces for e in f.edges]+[v for f in faces for v in f.verts]))
   if geom:bmesh.ops.bisect_plane(bm,geom=geom,dist=.00001,plane_co=o.matrix_world.inverted()@Vector((0,northing,32.4)),plane_no=o.matrix_world.to_3x3().transposed()@Vector((0,1,0)),clear_inner=False,clear_outer=False)
  bm.to_mesh(o.data);bm.free();o.data.update()
 report={}
 for o in bpy.data.objects:
  if o.type!='MESH':continue
  ids=set();attr=o.data.attributes.get('source_section')
  if o.name=='survey_16222':ids=set(range(len(o.data.vertices)))
  elif attr and 'cladding' in o.name.lower():ids={i for p,a in zip(o.data.polygons,attr.data) if a.value==16222 for i in p.vertices}
  elif o.name.startswith('Continuous surveyed roofs - authored finishes'):
   for p in o.data.polygons:
    qs=[o.matrix_world@o.data.vertices[i].co for i in p.vertices]
    if all(abs(q.z-32.4)<.005 and inside(q.x,q.y) for q in qs):ids.update(p.vertices)
  elif o.name in ['NGV east Atrium exposed envelope closure','Atrium adjacent upper and lower cut closures']:
   ids={v.index for v in o.data.vertices if o.name in ['NGV east Atrium exposed envelope closure','Atrium adjacent upper and lower cut closures'] or inside(*(o.matrix_world@v.co)[:2])}
  changed=0
  for i in ids:
   v=o.data.vertices[i];q=o.matrix_world@v.co
   if q.y<=95 or q.z<=27.9:continue
   w=max(0,min(1,(q.y-95)/10));w=w*w*(3-2*w)
   ratio=max(0,min(1,(q.z-27.9)/4.5));q.z+=(c[0]*q.x+c[1]*q.y+c[2]-32.4)*w*ratio
   v.co=o.matrix_world.inverted()@q;changed+=1
  if changed:o.data.update();report[o.name]=changed
 
 bpy.context.scene['federation_ngv_north_roof_revision']='captured-north-authored-transition-v1'
 (r/'docs/federation-ngv-north-roof-audit.json').write_text(json.dumps({'objects':report,'plane':c,'original_meshes':{o.name:o['ngv_north_original_mesh'] for o in bpy.data.objects if o.get('ngv_north_original_mesh')},'limits':'Northern May2020 capture plane from496cells; median residual0.179m.95–105m transition and27.9m deformation base are authored approximations. Southern roof regions, plant, glazing schedule and current condition unresolved. Closure ownership from retained NGV source records. No photographic textures.'},indent=2)+'\n')
 print('NGV_NORTHERN_ENVELOPE_APPLIED',report,flush=True)
else:print('NGV_NORTH_ALREADY_APPLIED',flush=True)
