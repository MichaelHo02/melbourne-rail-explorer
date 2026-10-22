"""Authored zinc grain and standing seams on the existing landmark roof."""
import bpy
name='Flinders authored main roof seams'
if not bpy.data.objects.get(name):
 anchor=bpy.data.objects['Flinders Street - runtime placement'];curve=bpy.data.curves.new(name,'CURVE');curve.dimensions='3D';curve.bevel_depth=.04;curve.bevel_resolution=0
 def line(points):
  s=curve.splines.new('POLY');s.points.add(len(points)-1)
  for p,co in zip(s.points,points):p.co=(*co,1)
 for i in range(361):
  x=-291+i*.8;line([(x,-11.8,26.745),(x,0,29.145),(x,11.8,26.745)])
 for y,z in [(-11.8,26.76),(0,29.16),(11.8,26.76)]:line([(-291,y,z),(-3,y,z)])
 mat=bpy.data.materials.get('Authored station canopy seam zinc');curve.materials.append(mat);o=bpy.data.objects.new(name,curve);anchor.users_collection[0].objects.link(o);o.parent=anchor;o['limits']='Authored 0.8m standing-seam rhythm on the existing illustrative pitched roof; not measured original zinc roofing or seam schedule.';o['guide_count']=len(curve.splines)
 roof=bpy.data.materials['Authored Flinders weathered zinc'];nodes=roof.node_tree.nodes;links=roof.node_tree.links;shader=nodes.get('Principled BSDF');geom=nodes.new('ShaderNodeNewGeometry');geom.name='Authored roof metre coordinates';noise=nodes.new('ShaderNodeTexNoise');noise.name='Authored zinc weathering';noise.inputs['Scale'].default_value=1.8;noise.inputs['Detail'].default_value=3;links.new(geom.outputs['Position'],noise.inputs['Vector']);ramp=nodes.new('ShaderNodeValToRGB');ramp.name='Authored zinc tones';ramp.color_ramp.elements[0].color=(.16,.19,.18,1);ramp.color_ramp.elements[1].color=(.29,.32,.30,1);links.new(noise.outputs['Fac'],ramp.inputs['Fac']);links.new(ramp.outputs['Color'],shader.inputs['Base Color']);bump=nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.15;bump.inputs['Distance'].default_value=.008;links.new(noise.outputs['Fac'],bump.inputs['Height']);links.new(bump.outputs['Normal'],shader.inputs['Normal']);print('VERIFIED main roof seam guides:',len(curve.splines))
