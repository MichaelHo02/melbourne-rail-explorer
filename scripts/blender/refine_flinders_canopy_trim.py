"""Illustrative standing seams and edge trim on schematic platform canopies."""
import bpy
from pathlib import Path
root=globals().get('root') or Path(bpy.data.filepath).resolve().parents[3];name='Flinders authored canopy seams and edges'
if not bpy.data.objects.get(name):
 anchor=bpy.data.objects['Flinders Street - runtime placement'];curve=bpy.data.curves.new(name,'CURVE');curve.dimensions='3D';curve.bevel_depth=.025;curve.bevel_resolution=0;count=0
 def line(points):
  global count
  s=curve.splines.new('POLY');s.points.add(len(points)-1)
  for p,co in zip(s.points,points):p.co=(*co,1)
  count+=1
 for y in [-33,-46,-59,-72]:
  for i in range(221):
   x=-265+i;line([(x,y-2.9,6.885),(x,y,7.685),(x,y+2.9,6.885)])
  for offset,z in [(-2.9,6.9),(0,7.7),(2.9,6.9)]:line([(-265,y+offset,z),(-45,y+offset,z)])
 mat=bpy.data.materials.get('Authored station canopy seam zinc') or bpy.data.materials.new('Authored station canopy seam zinc');mat.use_nodes=True;mat.diffuse_color=(.19,.23,.22,1);p=mat.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=mat.diffuse_color;p.inputs['Metallic'].default_value=.55;p.inputs['Roughness'].default_value=.5;curve.materials.append(mat);o=bpy.data.objects.new(name,curve);anchor.users_collection[0].objects.link(o);o.parent=anchor;o['limits']='Authored 1m seam spacing, shallow trim and 25mm radius on four schematic pitched canopies; exact material, roof profile and construction schedule unmeasured.';o['guide_count']=count
 print('VERIFIED canopy trim:',count,'guides')
