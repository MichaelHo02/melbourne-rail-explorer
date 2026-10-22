"""Three reference-led iron arch spans beneath retained Princes Bridge deck."""
import bpy,json,math
from pathlib import Path
root=globals().get('root') or Path(bpy.data.filepath).resolve().parents[3];name='Princes Bridge authored arch spandrels'
if not bpy.data.objects.get(name):
 d=json.loads((root/'assets/source/environment/princes-bridge-arches.json').read_text());cx,cy=d['center'];ux,uy=d['axis'];nx,ny=d['normal']
 def point(x,y,z):return (cx+x*ux+y*nx,cy+x*uy+y*ny,z)
 obj=bpy.data.objects['survey_36402'];backup=obj.copy();backup.data=obj.data.copy();backup.name='REFERENCE Princes Bridge original solid envelope';obj.users_collection[0].objects.link(backup);backup.hide_render=True;backup.hide_viewport=True
 for v in obj.data.vertices:
  if v.co.z<1:v.co.z=8.7
 iron=bpy.data.materials.new('Authored Princes Bridge deep green iron');iron.use_nodes=True;iron.diffuse_color=(.06,.105,.09,1);s=iron.node_tree.nodes.get('Principled BSDF');s.inputs['Base Color'].default_value=iron.diffuse_color;s.inputs['Metallic'].default_value=.45;s.inputs['Roughness'].default_value=.55
 v=[];f=[];curve=bpy.data.curves.new('Princes Bridge authored six arch ribs per span','CURVE');curve.dimensions='3D';curve.bevel_depth=.24;curve.bevel_resolution=1
 for span in range(3):
  lo=-60+span*40+2;hi=-60+(span+1)*40-2;profile=[(lo+(hi-lo)*i/32,1.2+6.2*(1-(2*i/32-1)**2)) for i in range(33)]
  for y in [-14.5,-8.7,-2.9,2.9,8.7,14.5]:
   sp=curve.splines.new('POLY');sp.points.add(32)
   for p,(x,z) in zip(sp.points,profile):p.co=(*point(x,y,z),1)
  for y in [-14.8,14.8]:
   for (xa,za),(xb,zb) in zip(profile,profile[1:]):
    i=len(v);v.extend([point(xa,y,za),point(xb,y,zb),point(xb,y,8.7),point(xa,y,8.7)]);f.append((i,i+1,i+2,i+3))
 m=bpy.data.meshes.new(name);m.from_pydata(v,[],f);m.materials.append(iron);m.update();o=bpy.data.objects.new(name,m);bpy.data.collections['CITY - reference-authored landmarks'].objects.link(o);o['limits']=d['limits'];curve.materials.append(iron);o=bpy.data.objects.new(curve.name,curve);bpy.data.collections['CITY - reference-authored landmarks'].objects.link(o)
 v=[];f=[]
 def box(x,y,z,sx,sy,sz):
  i=len(v);v.extend([point(x+dx*sx/2,y+dy*sy/2,z+dz*sz) for dz in [0,1] for dx,dy in [(-1,-1),(1,-1),(1,1),(-1,1)]]);f.extend([tuple(i+j for j in q) for q in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]])
 for x in [-20,20]:box(x,0,.05,4,30,8.65)
 for lo,hi in [(d['length_bounds'][0],-58),(58,d['length_bounds'][1])]:box((lo+hi)/2,0,.05,hi-lo,30,8.65)
 stone=bpy.data.materials.new('Authored Princes Bridge pier bluestone');stone.use_nodes=True;stone.diffuse_color=(.19,.22,.23,1);s=stone.node_tree.nodes.get('Principled BSDF');s.inputs['Base Color'].default_value=stone.diffuse_color;s.inputs['Roughness'].default_value=.9;m=bpy.data.meshes.new('Princes Bridge authored piers and abutments');m.from_pydata(v,[],f);m.materials.append(stone);m.update();o=bpy.data.objects.new(m.name,m);bpy.data.collections['CITY - reference-authored landmarks'].objects.link(o);o['limits']='Authored core 120 m within longer retained approach footprint; pier width, 30 m span width, flat levels and materials approximate.';print('VERIFIED Princes Bridge arches 3 spans, 18 ribs,',192,'spandrel quads',flush=True)
