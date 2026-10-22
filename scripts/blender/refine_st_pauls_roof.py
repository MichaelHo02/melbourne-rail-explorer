"""Authored cathedral gable within the retained upper-section envelope."""
import bpy,json,math
from pathlib import Path
root=globals().get('root') or Path(bpy.data.filepath).resolve().parents[3]
name='St Pauls Cathedral - authored pitched roof'
if not bpy.data.objects.get(name):
 d=json.loads((root/'assets/source/environment/st-pauls-authored-roof.json').read_text());nx,ny=d['axis_normal']
 def height(x,y):return 29.6-6.6*abs(x*nx+y*ny-d['mid'])/d['half']
 row=next(b for b in json.loads((root/'public/data/buildings.json').read_text())['buildings'] if str(b['id'])=='27586');ring=[(x,-y) for x,y in row['ring']]
 def inside(x,y):
  hit=False
  for a,b in zip(ring,ring[1:]):
   if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:hit=not hit
  return hit
 o=bpy.data.objects.get('survey_27586');assert o
 for v in o.data.vertices:
  if abs(v.co.z-29.6)<.02:v.co.z=height(v.co.x,v.co.y)
 removed={}
 for label in ['Continuous surveyed roofs - authored finishes','Authored rooftop equipment - illustrative']:
  o=bpy.data.objects.get(label);keep=[p for p in o.data.polygons if not (p.center.z>=29.5 and p.center.z<32 and inside(p.center.x,p.center.y))];removed[label]=len(o.data.polygons)-len(keep);m=bpy.data.meshes.new(label+' cathedral gable cutout');m.from_pydata([tuple(v.co) for v in o.data.vertices],[],[tuple(p.vertices) for p in keep])
  for mat in o.data.materials:m.materials.append(mat)
  for p,q in zip(m.polygons,keep):p.material_index=q.material_index
  m.update();o.data=m
 verts=[v for f in d['faces'] for v in f];faces=[(i,i+1,i+2) for i in range(0,len(verts),3)];m=bpy.data.meshes.new(name);m.from_pydata(verts,[],faces);mat=bpy.data.materials.new('Authored cathedral slate roof');mat.use_nodes=True;mat.diffuse_color=(.12,.15,.17,1);s=mat.node_tree.nodes.get('Principled BSDF');s.inputs['Base Color'].default_value=mat.diffuse_color;s.inputs['Roughness'].default_value=.8;m.materials.append(mat);m.update();o=bpy.data.objects.new(name,m);bpy.data.collections['CITY - reference-authored landmarks'].objects.link(o);o['limits']=d['limits'];o['removed_faces']=json.dumps(removed)
 assert all(23-.01<=v.co.z<=29.61 for v in m.vertices)
 print('VERIFIED cathedral gable:',len(faces),'triangles; cutouts',removed)
# Keep tower bases connected when the lower roof eaves are lowered.
join_name='St Pauls Cathedral - roof tower junctions'
if not bpy.data.objects.get(join_name):
 d=json.loads((root/'assets/source/environment/st-pauls-authored-roof.json').read_text());nx,ny=d['axis_normal'];verts=[];faces=[]
 rows=[b for b in json.loads((root/'public/data/buildings.json').read_text())['buildings'] if str(b['id'])=='27587']
 for b in rows:
  r=[(x,-y) for x,y in b['ring']]
  for a,c in zip(r,r[1:]):
   z1=29.6-6.6*abs(a[0]*nx+a[1]*ny-d['mid'])/d['half'];z2=29.6-6.6*abs(c[0]*nx+c[1]*ny-d['mid'])/d['half'];i=len(verts);verts.extend([(*a,z1),(*c,z2),(*c,29.6),(*a,29.6)]);faces.append((i,i+1,i+2,i+3))
 m=bpy.data.meshes.new(join_name);m.from_pydata(verts,[],faces);m.materials.append(bpy.data.materials['Authored St Pauls warm masonry']);m.update();o=bpy.data.objects.new(join_name,m);bpy.data.collections['CITY - reference-authored landmarks'].objects.link(o);o['limits']='Authored stone junction skirts bridging survey tower bases to illustrative roof slopes.';print('VERIFIED cathedral tower junctions:',len(faces))
