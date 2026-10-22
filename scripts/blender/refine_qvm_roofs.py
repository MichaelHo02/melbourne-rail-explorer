"""Authored five market gables; historical plan plus retained footprint."""
import bpy,json
from pathlib import Path
root=globals().get('root') or Path(bpy.data.filepath).resolve().parents[3];name='Queen Victoria Market authored A-E roof ranges'
if not bpy.data.objects.get(name):
 d=json.loads((root/'assets/source/environment/qvm-authored-roofs.json').read_text());ox,oy=d['origin'];nx,ny=d['normal']
 def localy(x,y):return (x-ox)*nx+(y-oy)*ny
 def height(x,y):
  v=localy(x,y)
  if v>100:return 10
  i=min(4,max(0,round((v-8.2)/20.65)));return max(6.8,10-3.2*abs(v-(i*20.65+8.2))/8.2)
 obj=bpy.data.objects['survey_24605'];backup=obj.copy();backup.data=obj.data.copy();backup.name='REFERENCE original market envelope 24605';bpy.data.collections['CITY - reference-authored landmarks'].objects.link(backup);backup.hide_render=True;backup.hide_viewport=True
 for v in obj.data.vertices:
  if abs(v.co.z-10)<.05:v.co.z=height(v.co.x,v.co.y)
 row=json.loads((root/'assets/source/environment/qvm-source-audit.json').read_text())['survey_section'];ring=[(x,-y) for x,y in row['ring']]
 def inside(x,y):
  hit=False
  for a,b in zip(ring,ring[1:]):
   if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:hit=not hit
  return hit
 removed={}
 for label in ['Continuous surveyed roofs - authored finishes','Authored rooftop equipment - illustrative']:
  o=bpy.data.objects[label];keep=[p for p in o.data.polygons if not (9.9<=p.center.z<14 and localy(p.center.x,p.center.y)<100 and inside(p.center.x,p.center.y))];removed[label]=len(o.data.polygons)-len(keep);m=bpy.data.meshes.new(label+' QVM cutout');m.from_pydata([tuple(v.co) for v in o.data.vertices],[],[tuple(p.vertices) for p in keep])
  for mat in o.data.materials:m.materials.append(mat)
  for p,q in zip(m.polygons,keep):p.material_index=q.material_index
  m.update();o.data=m
 verts=[v for f in d['faces'] for v in f];faces=[(i,i+1,i+2) for i in range(0,len(verts),3)];m=bpy.data.meshes.new(name);m.from_pydata(verts,[],faces);mat=bpy.data.materials.new('Authored market galvanised roof');mat.use_nodes=True;mat.diffuse_color=(.38,.41,.40,1);s=mat.node_tree.nodes.get('Principled BSDF');s.inputs['Base Color'].default_value=mat.diffuse_color;s.inputs['Metallic'].default_value=.5;s.inputs['Roughness'].default_value=.5;m.materials.append(mat);m.update();o=bpy.data.objects.new(name,m);bpy.data.collections['CITY - reference-authored landmarks'].objects.link(o);o['limits']=d['limits'];o['removed_faces']=json.dumps(removed)
 print('VERIFIED market roof triangles',len(faces),'cutouts',removed,flush=True)
# Generic office fenestration is inappropriate for the documented open market sheds.
market=bpy.data.objects[name]
if not market.get('generic_facade_cutout'):
 row=json.loads((root/'assets/source/environment/qvm-source-audit.json').read_text())['survey_section'];ring=[(x,-y) for x,y in row['ring']]
 def market_inside(x,y):
  hit=False
  for a,b in zip(ring,ring[1:]):
   if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:hit=not hit
  if hit:return True
  for a,b in zip(ring,ring[1:]):
   dx,dy=b[0]-a[0],b[1]-a[1];t=max(0,min(1,((x-a[0])*dx+(y-a[1])*dy)/(dx*dx+dy*dy))) if dx*dx+dy*dy else 0
   if (x-a[0]-t*dx)**2+(y-a[1]-t*dy)**2<.5**2:return True
  return False
 total=0
 for o in list(bpy.data.objects):
  if o.type!='MESH' or not any(t in o.name.lower() for t in ['window','trim','cornice']):continue
  keep=[p for p in o.data.polygons if not (0<=p.center.z<14 and market_inside(p.center.x,p.center.y))]
  if len(keep)==len(o.data.polygons):continue
  total+=len(o.data.polygons)-len(keep);m=bpy.data.meshes.new(o.name+' market facade cutout');m.from_pydata([tuple(v.co) for v in o.data.vertices],[],[tuple(p.vertices) for p in keep])
  for mat in o.data.materials:m.materials.append(mat)
  for p,q in zip(m.polygons,keep):p.material_index=q.material_index
  m.update();o.data=m
 market['generic_facade_cutout']=total;print('VERIFIED market generic facade cutout',total,flush=True)
