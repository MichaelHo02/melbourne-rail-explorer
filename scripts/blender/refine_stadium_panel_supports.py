"""Illustrative three-dimensional panel trusses using historical span and depth."""
import bpy,bmesh,json,math
from pathlib import Path
root=Path(bpy.data.filepath).resolve().parents[3];d=json.loads((root/'assets/source/environment/stadium-authored-roof.json').read_text());scene=bpy.context.scene
if not scene.get('stadium_panel_support_revision'):
 for name,part in [('Authored stadium fixed sloping roof',d['fixed'])]+[('Authored stadium closed moving panel '+str(p['side']),p) for p in d['panels']]:
  o=bpy.data.objects[name];mesh=bpy.data.meshes.new(name+' lower panel datum');mesh.from_pydata(part['vertices'],[],part['faces'])
  for m in o.data.materials:mesh.materials.append(m)
  mesh.update();o.data=mesh;o['limits']=d['limits']
 ring=d['outer_ring_xy']
 def inside(x,y):
  result=False
  for i,(a,b) in enumerate(ring):
   c,e=ring[i-1]
   if (b>y)!=(e>y) and x<(c-a)*(y-b)/(e-b)+a:result=not result
  return result
 o=bpy.data.objects['Continuous surveyed roofs - authored finishes'];bm=bmesh.new();bm.from_mesh(o.data);cut=[f for f in bm.faces if all(abs(v.co.z-31.3)<.01 for v in f.verts) and inside(f.calc_center_median().x,f.calc_center_median().y)]
 backup=o.data.copy();backup.name='REFERENCE before lowered stadium panel datum';backup.use_fake_user=True
 if cut:bmesh.ops.delete(bm,geom=cut,context='FACES_ONLY');bm.to_mesh(o.data);o.data.update()
 bm.free()
 old=bpy.data.objects.get('Authored stadium panel seam guides')
 if old:old.hide_render=True;old.hide_set(True)
 cx,cy=d['centroid_xy'];ux,uy=d['across_axis'];vx,vy=d['long_axis']
 def world(u,v,z):return(cx+u*ux+v*vx,cy+u*uy+v*vy,z)
 curve=bpy.data.curves.new('Authored stadium three-dimensional panel supports','CURVE');curve.dimensions='3D';curve.bevel_depth=.15;curve.bevel_resolution=1
 def line(points):
  s=curve.splines.new('POLY');s.points.add(len(points)-1)
  for p,co in zip(s.points,points):p.co=(*co,1)
 bays=16;bottom=28.7
 for u in [-47,-5,5,47]:
  stations=[-82.5+i*165/bays for i in range(bays+1)];tops=[bottom+12*(1-(v/82.5)**2) for v in stations]
  line([world(u,v,z) for v,z in zip(stations,tops)])
  for side in [-.65,.65]:
   line([world(u+side,v,bottom+.15) for v in stations])
   for i in range(bays):
    line([world(u,stations[i],tops[i]),world(u+side,stations[i+1],bottom+.15)])
    line([world(u+side,stations[i],bottom+.15),world(u,stations[i+1],tops[i+1])])
  for v,z in zip(stations,tops):line([world(u-.65,v,bottom+.15),world(u,v,z),world(u+.65,v,bottom+.15)])
 mat=bpy.data.materials.get('Authored stadium support steel') or bpy.data.materials.new('Authored stadium support steel');mat.use_nodes=True;mat.diffuse_color=(.39,.42,.41,1);s=mat.node_tree.nodes.get('Principled BSDF');s.inputs['Base Color'].default_value=mat.diffuse_color;s.inputs['Metallic'].default_value=.65;s.inputs['Roughness'].default_value=.5;curve.materials.append(mat);o=bpy.data.objects.new(curve.name,curve);bpy.data.objects['Authored stadium fixed sloping roof'].users_collection[0].objects.link(o);o['reference']='https://www.slideshare.net/slideshow/iabse-2002/54054492';o['limits']='Four illustrative triangular-section panel supports: historic165m clear span and12m depth. Parabolic chords,16bays,1.3m cross-width,0.15m member radius and setout authored. Exact member topology, supports and current as-built geometry unverified.'
 scene['stadium_panel_support_revision']=1;print('VERIFIED stadium panel supports',len(curve.splines),'members; removed underlying cap faces',len(cut),flush=True)
else:print('VERIFIED retained stadium panel supports',flush=True)
# The former31.3m cap extends beyond section934; use its own retained925 footprint.
ring925=[(x,-y) for x,y in next(b for b in json.loads((root/'public/data/buildings.json').read_text())['buildings'] if b['id']=='925')['ring']]
def within925(x,y):
 result=False
 for i,(a,b) in enumerate(ring925):
  c,e=ring925[i-1]
  if (b>y)!=(e>y) and x<(c-a)*(y-b)/(e-b)+a:result=not result
 return result
o=bpy.data.objects['Continuous surveyed roofs - authored finishes'];bm=bmesh.new();bm.from_mesh(o.data);cut=[f for f in bm.faces if all(abs(v.co.z-31.3)<.01 for v in f.verts) and within925(f.calc_center_median().x,f.calc_center_median().y)]
if cut:
 backup=o.data.copy();backup.name='REFERENCE remaining stadium925 cap';backup.use_fake_user=True;bmesh.ops.delete(bm,geom=cut,context='FACES_ONLY');bm.to_mesh(o.data);o.data.update()
bm.free();print('VERIFIED remaining925 cap cleanup',len(cut),flush=True)
name='Authored stadium retained lower roof perimeter';part=d['perimeter_flange'];o=bpy.data.objects.get(name)
if not o:
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(part['vertices'],[],part['faces']);mesh.materials.append(bpy.data.materials['Authored stadium fixed roof pale metal']);mesh.update();o=bpy.data.objects.new(name,mesh);bpy.data.objects['Authored stadium fixed sloping roof'].users_collection[0].objects.link(o);o['limits']='Retained925 footprint minus934 footprint, flat authored31.36m closure surface; exact material and current junction geometry unverified.';o['source_ids']='925,934';o['area_m2']=part['area_m2']
print('VERIFIED retained roof perimeter closure',len(o.data.polygons),part['area_m2'],flush=True)
