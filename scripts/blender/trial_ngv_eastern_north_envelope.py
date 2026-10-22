"""Recoverable east-northern height correction; transition boundaries authored."""
import bpy,json,bmesh,math
from pathlib import Path
from mathutils import Vector
r=Path(bpy.data.filepath).resolve().parents[3];s=bpy.context.scene;key='federation_ngv_eastern_north_revision'
if not s.get(key):
 old=json.loads((r/'docs/federation-ngv-roof-regions-audit.json').read_text())['diagnostic_bands'][2]['plane'];d=json.loads((r/'assets/source/environment/ngv-eastern-north-roof-plane.json').read_text());new=d['plane'];report={};owners=[]
 for o in bpy.data.objects:
  if o.type!='MESH':continue
  if o.name=='survey_16222' or o.name.startswith('Continuous surveyed roofs - authored finishes') or o.name in ['NGV east Atrium exposed envelope closure','Atrium adjacent upper and lower cut closures'] or 'Federation Square - authored triangular cladding' in o.name or o.name=='Federation NGV - nested pinwheel panels':owners.append(o)
 ring=next(b['ring'] for b in json.loads((r/'public/data/buildings.json').read_text())['buildings'] if str(b['id'])=='16222');ring=[(x,-y) for x,y in ring]
 def within(q):
  x,y=q.x,q.y;inside=False
  for a,b in zip(ring,ring[1:]+ring[:1]):
   dx,dy=b[0]-a[0],b[1]-a[1];t=max(0,min(1,((x-a[0])*dx+(y-a[1])*dy)/max(dx*dx+dy*dy,1e-12)))
   if math.hypot(x-a[0]-t*dx,y-a[1]-t*dy)<.005:return True
   if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:inside=not inside
  return inside
 def previous_height(q):
  w=max(0,min(1,(q.y-95)/10));w=w*w*(3-2*w)
  return 32.4+(old[0]*q.x+old[1]*q.y+old[2]-32.4)*w
 for o in owners:
  attr=o.data.attributes.get('source_section');face_ids=[]
  for p in o.data.polygons:
   qs=[o.matrix_world@o.data.vertices[i].co for i in p.vertices]
   owned=o.name=='survey_16222' or (attr and attr.data[p.index].value==16222) or (o.name.startswith('Continuous surveyed roofs - authored finishes') and all(within(q) and 95<=q.y<=145 and abs(q.z-previous_height(q))<.005 for q in qs))
   if owned and max(q.x for q in qs)>235 and max(q.y for q in qs)>95:face_ids.append(p.index)
  if not face_ids:continue
  backup=o.data.copy();backup.name=o.name+' before eastern northern fit';backup.use_fake_user=True;o['ngv_eastern_north_original_mesh']=backup.name
  bm=bmesh.new();bm.from_mesh(o.data);bm.faces.ensure_lookup_table();layer=bm.faces.layers.int.new('ngv_east_fit_owner')
  for i in face_ids:bm.faces[i][layer]=1
  for axis,values in [(0,[235,237.5,240]),(1,[95,100,105])]:
   for value in values:
    fs=[f for f in bm.faces if f[layer]==1];geom=list(set(fs+[e for f in fs for e in f.edges]+[v for f in fs for v in f.verts]));co=Vector((0,0,30));co[axis]=value;no=Vector((0,0,0));no[axis]=1
    bmesh.ops.bisect_plane(bm,geom=geom,dist=.00001,plane_co=o.matrix_world.inverted()@co,plane_no=o.matrix_world.to_3x3().transposed()@no,clear_inner=False,clear_outer=False)
  bm.to_mesh(o.data);bm.free();o.data.update()
 for o in owners:
  # Only source-tagged NGV faces or geometrically matched northern caps.
  attr=o.data.attributes.get('source_section');ids=set()
  if o.name=='survey_16222':ids=set(range(len(o.data.vertices)))
  elif attr and ('cladding' in o.name.lower() or 'pinwheel' in o.name.lower()):ids={i for p,a in zip(o.data.polygons,attr.data) if a.value==16222 for i in p.vertices}
  elif o.name in ['NGV east Atrium exposed envelope closure','Atrium adjacent upper and lower cut closures']:ids=set(range(len(o.data.vertices)))
  elif o.name.startswith('Continuous surveyed roofs - authored finishes'):
   owner=o.data.attributes.get('ngv_east_fit_owner')
   if owner:ids={i for p,a in zip(o.data.polygons,owner.data) if a.value==1 for i in p.vertices}
  selected={i for i in ids if (o.matrix_world@o.data.vertices[i].co).x>235 and (o.matrix_world@o.data.vertices[i].co).y>95 and (o.matrix_world@o.data.vertices[i].co).z>27.9}
  if not selected:continue
  changed=0
  for i in selected:
   v=o.data.vertices[i];q=o.matrix_world@v.co;h0=old[0]*q.x+old[1]*q.y+old[2];h1=new[0]*q.x+new[1]*q.y+new[2];wx=max(0,min(1,(q.x-235)/5));wy=max(0,min(1,(q.y-95)/10));wx=wx*wx*(3-2*wx);wy=wy*wy*(3-2*wy);ratio=max(0,min(1,(q.z-27.9)/max(h0-27.9,.1)));q.z+=(h1-h0)*wx*wy*ratio;v.co=o.matrix_world.inverted()@q;changed+=1
  o.data.update();report[o.name]=changed
 # Source envelope contains coincident top caps underneath the dedicated roof.
 source=bpy.data.objects['survey_16222'];mask=bpy.data.materials['Federation Atrium clipped source mask'];slot=next((i for i,m in enumerate(source.data.materials) if m==mask),None)
 if slot is None:slot=len(source.data.materials);source.data.materials.append(mask)
 cap_records=[]
 for p in source.data.polygons:
  qs=[source.matrix_world@source.data.vertices[i].co for i in p.vertices]
  if p.normal.z>.55 and min(q.z for q in qs)>27.89:
   cap_records.append({'face':p.index,'material':p.material_index});p.material_index=slot
 text=bpy.data.texts.new('NGV eastern source cap original assignments.json');text.write(json.dumps(cap_records));source['ngv_eastern_cap_recovery']=text.name
 print('COINCIDENT_SOURCE_CAPS_MASKED',len(cap_records),flush=True)
 s[key]='captured-eastern-north-authored-transition-v1';(r/'docs/ngv-eastern-north-envelope-trial-audit.json').write_text(json.dumps({'objects':report,'plane':new,'inlier_cells':d['inlier_cells'],'median_residual_m':d['median_residual_m'],'limits':'Height correction supported by eastern2020 roof plane;235..240m and95..105m transition weights authored.27.9m deformation base retained. Sparse roof vertices may need matching subdivisions; no city save in this trial. Exact fold boundaries and skylights unresolved.'},indent=2)+'\n');print('EASTERN_NORTH_ENVELOPE_TRIAL',report,flush=True)
