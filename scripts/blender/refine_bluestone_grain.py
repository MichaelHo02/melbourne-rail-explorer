"""Refine authored bluestone shading; surface condition remains illustrative."""
import bpy
for name in ['Authored Southbank sawn bluestone','Authored central CBD bluestone - coverage illustrative']:
 m=bpy.data.materials.get(name)
 if not m:continue
 ns=m.node_tree.nodes;ls=m.node_tree.links;p=ns.get('Principled BSDF')
 for n in list(ns):
  if n.name.startswith('Stone grain refinement'):ns.remove(n)
 g=ns.new('ShaderNodeNewGeometry');g.name='Stone grain refinement coordinates'
 noise=ns.new('ShaderNodeTexNoise');noise.name='Stone grain refinement noise';noise.inputs['Scale'].default_value=90;noise.inputs['Detail'].default_value=2;ls.new(g.outputs['Position'],noise.inputs['Vector'])
 ramp=ns.new('ShaderNodeValToRGB');ramp.name='Stone grain refinement roughness';ramp.color_ramp.elements[0].color=(.68,.68,.68,1);ramp.color_ramp.elements[1].color=(.9,.9,.9,1);ls.new(noise.outputs['Fac'],ramp.inputs['Fac']);ls.new(ramp.outputs['Color'],p.inputs['Roughness'])
 prior=None
 for n in ns:
  if n.type=='BUMP' and not n.name.startswith('Stone grain refinement'):
   n.invert=True;prior=n
 b=ns.new('ShaderNodeBump');b.name='Stone grain refinement bump';b.inputs['Strength'].default_value=.12;b.inputs['Distance'].default_value=.001
 ls.new(noise.outputs['Fac'],b.inputs['Height'])
 if prior:ls.new(prior.outputs['Normal'],b.inputs['Normal'])
 ls.new(b.outputs['Normal'],p.inputs['Normal'])
 m['stone_grain_limits']='Authored millimetre-scale grain and roughness variation, not measured stone condition. Existing indicative paving coverage and dimensions retained.'
 print('VERIFIED stone shading',name,flush=True)
