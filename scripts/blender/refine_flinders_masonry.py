"""Procedural painted masonry joints guided by restoration evidence, not measured courses."""
import bpy
from pathlib import Path
root=Path(bpy.data.filepath).resolve().parents[3]
mat=bpy.data.objects['FSS_brick'].data.materials[0];nodes=mat.node_tree.nodes;links=mat.node_tree.links
for n in list(nodes):
 if n.name.startswith('FSS authored masonry '):nodes.remove(n)
def node(kind,label):
 n=nodes.new(kind);n.name='FSS authored masonry '+label;return n
coord=node('ShaderNodeTexCoord','local metres');split=node('ShaderNodeSeparateXYZ','coordinates');links.new(coord.outputs['Object'],split.inputs[0])
front=node('ShaderNodeCombineXYZ','long wall');end=node('ShaderNodeCombineXYZ','end wall')
for n,first,last in [(front,'X','Y'),(end,'Y','X')]:
 links.new(split.outputs[first],n.inputs['X']);links.new(split.outputs['Z'],n.inputs['Y']);links.new(split.outputs[last],n.inputs['Z'])
g=node('ShaderNodeNewGeometry','normal');transform=node('ShaderNodeVectorTransform','object normal');transform.vector_type='NORMAL';transform.convert_from='WORLD';transform.convert_to='OBJECT';links.new(g.outputs['Normal'],transform.inputs['Vector'])
ns=node('ShaderNodeSeparateXYZ','normal axes');links.new(transform.outputs['Vector'],ns.inputs[0]);absolute=node('ShaderNodeMath','absolute normal');absolute.operation='ABSOLUTE';links.new(ns.outputs['X'],absolute.inputs[0]);threshold=node('ShaderNodeMath','end face');threshold.operation='GREATER_THAN';threshold.inputs[1].default_value=.7;links.new(absolute.outputs[0],threshold.inputs[0])
mix=node('ShaderNodeMixRGB','wall projection');links.new(threshold.outputs[0],mix.inputs[0]);links.new(front.outputs[0],mix.inputs[1]);links.new(end.outputs[0],mix.inputs[2])
brick=node('ShaderNodeTexBrick','painted courses');links.new(mix.outputs[0],brick.inputs['Vector'])
base=tuple(mat.diffuse_color)
brick.inputs['Color1'].default_value=tuple(c*.94 for c in base[:3])+(1,);brick.inputs['Color2'].default_value=tuple(c*1.04 for c in base[:3])+(1,);brick.inputs['Mortar'].default_value=(.025,.019,.017,1)
for key,value in [('Scale',1),('Mortar Size',.006),('Mortar Smooth',.003),('Bias',0),('Brick Width',.60),('Row Height',.25)]:brick.inputs[key].default_value=value
brick.offset=.5;brick.offset_frequency=2
shader=nodes.get('Principled BSDF');links.new(brick.outputs['Color'],shader.inputs['Base Color']);bump=node('ShaderNodeBump','joint relief');bump.invert=True;bump.inputs['Strength'].default_value=.15;bump.inputs['Distance'].default_value=.003;links.new(brick.outputs['Fac'],bump.inputs['Height']);links.new(bump.outputs['Normal'],shader.inputs['Normal'])
mat['masonry_reference']='https://localjobsfirst.vic.gov.au/commissioner/newsroom/news-items/flinders-st-redevelopment'
mat['masonry_limits']='Authored 0.60 by 0.25 m courses, 6 mm dark joints and 3 mm relief; actual course dimensions and painted joint pattern unmeasured. Procedural only; no image textures.'
bpy.context.scene['flinders_masonry_revision']=1
assert not any(n.type=='TEX_IMAGE' for n in nodes)
print('VERIFIED Flinders procedural masonry, local metre projections, zero photographic textures',flush=True)
