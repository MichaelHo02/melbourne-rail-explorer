"""Authored three-spire silhouette on retained cathedral tower footprints."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
root=globals().get('root') or Path(bpy.data.filepath).resolve().parents[3];name='St Pauls Cathedral - authored three spires'
if not bpy.data.objects.get(name):
 data=json.loads((root/'public/data/buildings.json').read_text());towers=[b for b in data['buildings'] if str(b['id'])=='27587'];central=next(b for b in data['buildings'] if str(b['id'])=='27583');polys=[[(x,-y) for x,y in b['ring'][:-1]] for b in towers]
 def inside(x,y,ring):
  hit=False
  for i,a in enumerate(ring):
   c=ring[(i+1)%len(ring)]
   if (a[1]>y)!=(c[1]>y) and x<(c[0]-a[0])*(y-a[1])/(c[1]-a[1])+a[0]:hit=not hit
  return hit
 def near(x,y,ring):
  if inside(x,y,ring):return True
  for i,a in enumerate(ring):
   b=ring[(i+1)%len(ring)];dx,dy=b[0]-a[0],b[1]-a[1];t=max(0,min(1,((x-a[0])*dx+(y-a[1])*dy)/max(dx*dx+dy*dy,1e-9)))
   if math.hypot(x-a[0]-t*dx,y-a[1]-t*dy)<.25:return True
  return False
 verts=[];faces=[];indices=[]
 def face(points,mat):
  start=len(verts);verts.extend(points);faces.append(tuple(range(start,start+len(points))));indices.append(mat)
 def cone(cx,cy,r,base,tip,mat):
  for i in range(8):
   a=i*math.tau/8;c=(i+1)*math.tau/8;face([(cx+r*math.cos(a),cy+r*math.sin(a),base),(cx+r*math.cos(c),cy+r*math.sin(c),base),(cx,cy,tip)],mat)
 for b,ring in zip(towers,polys):
  # Area centroid of retained outline; the widest tower is the central one.
  area=sum(a[0]*ring[(i+1)%len(ring)][1]-ring[(i+1)%len(ring)][0]*a[1] for i,a in enumerate(ring));cx=sum((a[0]+ring[(i+1)%len(ring)][0])*(a[0]*ring[(i+1)%len(ring)][1]-ring[(i+1)%len(ring)][0]*a[1]) for i,a in enumerate(ring))/(3*area);cy=sum((a[1]+ring[(i+1)%len(ring)][1])*(a[0]*ring[(i+1)%len(ring)][1]-ring[(i+1)%len(ring)][0]*a[1]) for i,a in enumerate(ring))/(3*area)
  is_central=inside(cx,cy,[(x,-y) for x,y in central['ring'][:-1]]);shoulder=53.6 if is_central else 38;tip=93.2 if is_central else 53.6
  for i,a in enumerate(ring):
   c=ring[(i+1)%len(ring)];points=[(*a,b['base']),(*c,b['base']),(*c,shoulder),(*a,shoulder)]
   if area<0:points.reverse()
   face(points,0)
  radius=min(math.dist((cx,cy),a) for a in ring)*.72;cone(cx,cy,radius,shoulder,tip,1)
  for i in range(4):
   a=i*math.tau/4+math.pi/4;px=cx+radius*.95*math.cos(a);py=cy+radius*.95*math.sin(a);cone(px,py,.35,shoulder-1,shoulder+2.5,0)
 mats=[]
 for label,color in [('Authored St Pauls warm masonry',(.50,.40,.28)),('Authored St Pauls spire stone',(.38,.30,.21))]:
  m=bpy.data.materials.get(label) or bpy.data.materials.new(label);m.use_nodes=True;m.diffuse_color=(*color,1);s=m.node_tree.nodes.get('Principled BSDF');s.inputs['Base Color'].default_value=(*color,1);s.inputs['Roughness'].default_value=.88;mats.append(m)
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces)
 for m in mats:mesh.materials.append(m)
 for p,i in zip(mesh.polygons,indices):p.material_index=i
 mesh.update();obj=bpy.data.objects.new(name,mesh);bpy.data.collections['CITY - reference-authored landmarks'].objects.link(obj);obj['source_ids']='27583,27587';obj['reference']='https://cathedral.org.au/wp-content/uploads/2022/11/2022-English-Guide-Sheet-Final.pdf';obj['limits']='Three retained tower footprints and survey-relative upper levels. Authored octagonal taper, shoulder heights, corner pinnacles and stone palette. Exact spire geometry, ornament, nave and facade details/current condition unresolved; survey heights not identical to published architectural heights.'
 for original in bpy.data.objects:
  if original.name.startswith('survey_27583') or original.name.startswith('survey_27587'):original.hide_render=True;original.hide_set(True);original['replacement']=name
 # Remove matching flat caps and generic upper-storey windows, preserving old mesh data.
 removed=0
 for target in ['Continuous surveyed roofs - authored finishes','Authored grouped window bays - varied low rise','Authored low rise sill and lintel bands']:
  old=bpy.data.objects.get(target)
  if not old:continue
  keep=[];materials=[];local_removed=0
  for p in old.data.polygons:
   x,y,z=p.center;cut=z>=29.59 and any(near(x,y,ring) for ring in polys)
   if cut:local_removed+=1;continue
   keep.append(tuple(p.vertices));materials.append(p.material_index)
  if not local_removed:continue
  replacement=bpy.data.meshes.new(target+' cathedral cutouts');replacement.from_pydata([tuple(v.co) for v in old.data.vertices],[],keep)
  for m in old.data.materials:replacement.materials.append(m)
  for p,i in zip(replacement.polygons,materials):p.material_index=i
  replacement.update();old.data=replacement;removed+=local_removed
 assert len(towers)==3 and all(p.area>0 for p in mesh.polygons);print('VERIFIED authored St Pauls silhouette:',len(mesh.polygons),'faces; generic faces omitted:',removed)

# Flat-roof equipment is not applicable to the authored tapered spires.
plant=bpy.data.objects.get('Authored rooftop equipment - illustrative')
if plant and not plant.get('st_pauls_cutout'):
 rows=[b for b in json.loads((root/'public/data/buildings.json').read_text())['buildings'] if str(b['id'])=='27587'];rings=[[(x,-y) for x,y in b['ring']] for b in rows]
 def plant_inside(x,y,ring):
  hit=False
  for a,b in zip(ring,ring[1:]):
   if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:hit=not hit
  return hit
 keep=[p for p in plant.data.polygons if not (p.center.z>=29.59 and any(plant_inside(p.center.x,p.center.y,r) for r in rings))];removed=len(plant.data.polygons)-len(keep)
 mesh=bpy.data.meshes.new('Authored roof equipment excluding cathedral spires');mesh.from_pydata([tuple(v.co) for v in plant.data.vertices],[],[tuple(p.vertices) for p in keep])
 for m in plant.data.materials:mesh.materials.append(m)
 mesh.update();plant.data=mesh;plant['st_pauls_cutout']=True;plant['cathedral_equipment_faces_omitted']=removed;print('VERIFIED cathedral flat-roof equipment omitted:',removed)
