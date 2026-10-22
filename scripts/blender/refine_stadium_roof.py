"""Replace a generic survey roof block with authored closed moving-panel geometry."""
import bpy,bmesh,json
from pathlib import Path
root=Path(bpy.data.filepath).resolve().parents[3];d=json.loads((root/'assets/source/environment/stadium-authored-roof.json').read_text());scene=bpy.context.scene
if not scene.get('stadium_authored_roof_revision'):
 ring=d['outer_ring_xy']
 def inside(x,y):
  result=False
  for i,(a,b) in enumerate(ring):
   c,e=ring[i-1]
   if (b>y)!=(e>y) and x<(c-a)*(y-b)/(e-b)+a:result=not result
  return result
 removed={}
 for name,roof in [('Continuous surveyed roofs - authored finishes',True),('Authored grouped window bays - varied low rise',False),('Authored low rise sill and lintel bands',False)]:
  o=bpy.data.objects.get(name)
  if not o:continue
  bm=bmesh.new();bm.from_mesh(o.data);cut=[]
  for f in bm.faces:
   c=f.calc_center_median()
   if inside(c.x,c.y) and (all(abs(v.co.z-40.7)<.01 for v in f.verts) if roof else 31.5<c.z<40.71):cut.append(f)
  if cut:
   backup=o.data.copy();backup.name='REFERENCE before stadium roof correction '+o.data.name;backup.use_fake_user=True;bmesh.ops.delete(bm,geom=cut,context='FACES_ONLY');bm.to_mesh(o.data);o.data.update()
  removed[name]=len(cut);bm.free()
 original=bpy.data.objects['survey_934'];original.hide_render=True;original.hide_set(True);original['replacement']='Authored stadium fixed roof and closed panels';original['limits']='Retained hidden reference envelope; original capture20230511.'
 def material(name,color,metal):
  m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*color,1);s=m.node_tree.nodes.get('Principled BSDF');s.inputs['Base Color'].default_value=m.diffuse_color;s.inputs['Roughness'].default_value=.62;s.inputs['Metallic'].default_value=metal;m['limits']='Authored pale roof coating; actual cladding/colour unverified.';return m
 fixedmat=material('Authored stadium fixed roof pale metal',(.45,.48,.47),.25);panelmat=material('Authored stadium moving panel pale coating',(.61,.63,.61),.2)
 collection=original.users_collection[0]
 def mesh(name,part,mat):
  m=bpy.data.meshes.new(name);m.from_pydata(part['vertices'],[],part['faces']);m.materials.append(mat);m.update();o=bpy.data.objects.new(name,m);collection.objects.link(o);o['limits']=d['limits'];o['reference']='https://www.slideshare.net/slideshow/iabse-2002/54054492';assert all(p.area>0 and p.normal.z>0 for p in m.polygons);return o
 mesh('Authored stadium fixed sloping roof',d['fixed'],fixedmat)
 for p in d['panels']:mesh('Authored stadium closed moving panel '+str(p['side']),p,panelmat)
 cx,cy=d['centroid_xy'];ux,uy=d['across_axis'];vx,vy=d['long_axis'];curve=bpy.data.curves.new('Authored stadium panel seam guides','CURVE');curve.dimensions='3D';curve.bevel_depth=.035;curve.bevel_resolution=0
 for u in range(-52,53,4):
  spline=curve.splines.new('POLY');spline.points.add(1);z=40.7-1.7*(u/52)**2+.035
  for point,v in zip(spline.points,[-84,84]):point.co=(cx+u*ux+v*vx,cy+u*uy+v*vy,z,1)
 curve.materials.append(material('Authored stadium seam grey metal',(.22,.25,.24),.45));o=bpy.data.objects.new(curve.name,curve);collection.objects.link(o);o['limits']='Illustrative4m joint rhythm and35mm radius; actual seam setout unmeasured.'
 scene['stadium_authored_roof_revision']=1;scene['stadium_roof_removed_generic_faces']=json.dumps(removed);print('VERIFIED stadium roof replacement',removed,flush=True)
else:print('VERIFIED retained authored stadium roof',flush=True)
