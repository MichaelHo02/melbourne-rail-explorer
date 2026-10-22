"""Unsaved study: captured lower roof planes with authored northing transition."""
import bpy,json,math,bmesh
from mathutils import Vector
from pathlib import Path
r=Path(bpy.data.filepath).resolve().parents[3];d=json.loads((r/'docs/federation-ngv-combined-southern-plane-diagnostic.json').read_text());planes=[d['planes'][i]['plane'] for i in [1,0]]
ring=next(b['ring'] for b in json.loads((r/'public/data/buildings.json').read_text())['buildings'] if str(b['id'])=='16221');ring=[(x,-y) for x,y in ring]
def inside(x,y):
 result=False
 for a,b in zip(ring,ring[1:]+ring[:1]):
  dx,dy=b[0]-a[0],b[1]-a[1];t=max(0,min(1,((x-a[0])*dx+(y-a[1])*dy)/max(dx*dx+dy*dy,1e-12)))
  if math.hypot(x-a[0]-t*dx,y-a[1]-t*dy)<.005:return True
  if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:result=not result
 return result
# Subdivide only the recovered lower-cap faces so support-bound transitions
# can move roof vertices together with the already tessellated cladding.
roof=bpy.data.objects['Continuous surveyed roofs - authored finishes']
recs=json.loads(bpy.data.texts[roof['ngv_lower_roof_finish_recovery']].as_string())
bm=bmesh.new();bm.from_mesh(roof.data);bm.faces.ensure_lookup_table()
layer=bm.faces.layers.int.new('ngv_lower_profile_owner')
for rec in recs:bm.faces[rec['face']][layer]=1
for axis,values in [(0,[211,213,220,230,232]),(1,[-5,-2,0,18,20,22,47,50])]:
 for value in values:
  faces=[f for f in bm.faces if f[layer]==1];geom=list(set(faces+[e for f in faces for e in f.edges]+[v for f in faces for v in f.verts]));co=Vector((0,0,23.9));co[axis]=value;normal=Vector((0,0,0));normal[axis]=1
  bmesh.ops.bisect_plane(bm,geom=geom,dist=.00001,plane_co=roof.matrix_world.inverted()@co,plane_no=roof.matrix_world.to_3x3().transposed()@normal,clear_inner=False,clear_outer=False)
bm.to_mesh(roof.data);bm.free();roof.data.update()
report={}
for o in bpy.data.objects:
 if o.type!='MESH':continue
 ids=set();attr=o.data.attributes.get('source_section')
 if o.name=='survey_16221':ids=set(range(len(o.data.vertices)))
 elif attr and ('cladding' in o.name.lower() or 'pinwheel' in o.name.lower()):
  ids={i for p,a in zip(o.data.polygons,attr.data) if a.value==16221 for i in p.vertices}
 elif o.name.startswith('Continuous surveyed roofs - authored finishes'):
  for p in o.data.polygons:
   qs=[o.matrix_world@o.data.vertices[i].co for i in p.vertices]
   if all(abs(q.z-23.9)<.005 and inside(q.x,q.y) for q in qs):ids.update(p.vertices)
 changed=0
 for i in ids:
  v=o.data.vertices[i];q=o.matrix_world@v.co
  if not (211<=q.x<=232 and -5<=q.y<=50 and 8.4<q.z<=24.1):continue
  w=max(0,min(1,(q.y-18)/4));w=w*w*(3-2*w);hs=[c[0]*q.x+c[1]*q.y+c[2] for c in planes];h=hs[0]*(1-w)+hs[1]*w
  # Return to retained envelope outside measured support; boundaries approximate.
  edge=max(0,min(1,(q.x-211)/2,(232-q.x)/2,(q.y+5)/3,(50-q.y)/3));ratio=max(0,min(1,(q.z-8.4)/15.5));q.z+=(h-23.9)*ratio*edge
  v.co=o.matrix_world.inverted()@q;changed+=1
 if changed:o.data.update();report[o.name]=changed
print('UNSAVED_LOWER_ROOF_PROFILE_STUDY',json.dumps(report),flush=True)
exec(compile((r/'scripts/blender/render_ngv_south_repair_study.py').read_text().replace('observatory-ngv-south-before-repair.png','observatory-ngv-lower-captured-profile-trial.png'),'study_render','exec'))
