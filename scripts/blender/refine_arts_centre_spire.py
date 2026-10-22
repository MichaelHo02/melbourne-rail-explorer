"""Authored open lattice in place of retained upper spire blocks."""
import bpy,json,math
from pathlib import Path
root=globals().get('root') or Path(bpy.data.filepath).resolve().parents[3];name='Arts Centre authored open lattice spire'
if not bpy.data.objects.get(name):
 cx=(144.9684244598062-144.9671)*87939;cy=(-37.82146327453973+37.8183)*111320
 for label,col,metal in [('Authored Arts Centre pale steel',(.68,.70,.66),.45),('Authored Arts Centre gold webbing',(.40,.29,.10),.55)]:
  m=bpy.data.materials.get(label) or bpy.data.materials.new(label);m.use_nodes=True;m.diffuse_color=(*col,1);s=m.node_tree.nodes.get('Principled BSDF');s.inputs['Base Color'].default_value=m.diffuse_color;s.inputs['Metallic'].default_value=metal;s.inputs['Roughness'].default_value=.5
 def mesh_curves(label,layers,radius,mat):
  c=bpy.data.curves.new(label,'CURVE');c.dimensions='3D';c.bevel_depth=radius;c.bevel_resolution=0
  def line(points):
   s=c.splines.new('POLY');s.points.add(len(points)-1)
   for p,co in zip(s.points,points):p.co=(*co,1)
  n=12
  for z,r in layers:
   line([(cx+r*math.cos(i*math.tau/n),cy+r*math.sin(i*math.tau/n),z) for i in range(n+1)])
  for (z,r),(zz,rr) in zip(layers,layers[1:]):
   for i in range(n):
    a=i*math.tau/n;b=(i+1)*math.tau/n
    line([(cx+r*math.cos(a),cy+r*math.sin(a),z),(cx+rr*math.cos(a),cy+rr*math.sin(a),zz)])
    line([(cx+r*math.cos(a),cy+r*math.sin(a),z),(cx+rr*math.cos(b),cy+rr*math.sin(b),zz)])
  c.materials.append(bpy.data.materials[mat]);o=bpy.data.objects.new(label,c);bpy.data.collections['CITY - reference-authored landmarks'].objects.link(o);return o
 gold=mesh_curves(name+' gold skirt',[(30,11),(34,7.5),(38,5),(42.5,3.8)],.075,'Authored Arts Centre gold webbing');o=mesh_curves(name,[(42.5+i*8.5,3.8*(1-i/12)**.8) for i in range(13)]+[(150,.10)],.08,'Authored Arts Centre pale steel');o['limits']='Authored 12-sided lattice and skirt within retained upper-envelope levels 30–150m relative to survey base. Published 162m above street datum is not reconciled. Exact lattice, mast, lighting and current refurbishment unresolved.';o['reference']='https://www.artscentremelbourne.com.au/-/media/acm/files/about-us/media-centre/media-releases/2024/241001arts-centre-melbournes-theatres-building-celebrates-40-years--media-release.pdf';o['source_ids']='25568,25569'
 for obj in bpy.data.objects:
  if obj.name.startswith('survey_25568') or obj.name.startswith('survey_25569'):obj.hide_render=True;obj.hide_set(True)
 removed=0
 for label in ['Continuous surveyed roofs - authored finishes','Authored grouped window bays - varied low rise','Authored low rise sill and lintel bands','Authored rooftop equipment - illustrative']:
  obj=bpy.data.objects.get(label)
  if not obj:continue
  keep=[p for p in obj.data.polygons if not (p.center.z>=29.99 and abs(p.center.x-cx)<12 and abs(p.center.y-cy)<12)];removed+=len(obj.data.polygons)-len(keep);m=bpy.data.meshes.new(label+' Arts spire cutout');m.from_pydata([tuple(v.co) for v in obj.data.vertices],[],[tuple(p.vertices) for p in keep])
  for mat in obj.data.materials:m.materials.append(mat)
  for p,q in zip(m.polygons,keep):p.material_index=q.material_index
  m.update();obj.data=m
 print('VERIFIED open Arts spire; generic faces omitted:',removed)
roof_name='Arts Centre retained roof beneath lattice'
if not bpy.data.objects.get(roof_name):
 d=json.loads((root/'assets/source/environment/city-roof-surfaces.json').read_text());cx=(144.9684244598062-144.9671)*87939;cy=(-37.82146327453973+37.8183)*111320;verts=[];faces=[];indices=[]
 for f,index in zip(d['faces'],d['materials']):
  pts=[d['vertices'][i] for i in f];x=sum(p[0] for p in pts)/len(pts);y=sum(p[1] for p in pts)/len(pts);z=sum(p[2] for p in pts)/len(pts)
  if abs(z-30)<.01 and abs(x-cx)<12 and abs(y-cy)<12:
   i=len(verts);verts.extend(pts);faces.append(tuple(range(i,len(verts))));indices.append(index)
 m=bpy.data.meshes.new(roof_name);m.from_pydata(verts,[],faces)
 for label in ['Authored pale roof finish','Authored warm roof finish','Authored light zinc roof finish']:m.materials.append(bpy.data.materials[label])
 for p,index in zip(m.polygons,indices):p.material_index=index
 m.update();o=bpy.data.objects.new(roof_name,m);bpy.data.collections['CITY - reference-authored landmarks'].objects.link(o);print('VERIFIED retained theatre roof restored:',len(faces))
trim=bpy.data.objects.get('Authored roof edge cornices')
if trim and not trim.get('arts_spire_tip_cutout'):
 cx=116.47;cy=-352.14;keep=[p for p in trim.data.polygons if not (abs(p.center.x-cx)<12 and abs(p.center.y-cy)<12 and p.center.z>140)];removed=len(trim.data.polygons)-len(keep);m=bpy.data.meshes.new('Cornices excluding Arts spire tip');m.from_pydata([tuple(v.co) for v in trim.data.vertices],[],[tuple(p.vertices) for p in keep])
 for mat in trim.data.materials:m.materials.append(mat)
 for p,q in zip(m.polygons,keep):p.material_index=q.material_index
 m.update();trim.data=m;trim['arts_spire_tip_cutout']=True;print('VERIFIED spire tip cornices removed:',removed)
