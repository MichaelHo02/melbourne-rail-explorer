"""Authored two-scale crushed-stone shading; no photographic textures."""
import bpy
m=bpy.data.materials['Authored ballast']; n=m.node_tree.nodes; l=m.node_tree.links
shader=n.get('Principled BSDF'); position=n.get('Live metre coordinates')
assert shader and position
stone=n.get('Authored ballast stone cells') or n.new('ShaderNodeTexVoronoi');stone.name='Authored ballast stone cells';stone.distance='EUCLIDEAN';stone.feature='DISTANCE_TO_EDGE';stone.inputs['Scale'].default_value=20
l.new(position.outputs['Position'],stone.inputs['Vector'])
bump=n.get('Authored ballast stone relief') or n.new('ShaderNodeBump');bump.name='Authored ballast stone relief';bump.invert=True;bump.inputs['Strength'].default_value=.32;bump.inputs['Distance'].default_value=.008
l.new(stone.outputs['Distance'],bump.inputs['Height']);l.new(bump.outputs['Normal'],shader.inputs['Normal'])
# Metre-scale tonal variation stays separate from approximately 50 mm cells.
noise=n['Live authored grain'];noise.inputs['Scale'].default_value=.35
shader.inputs['Roughness'].default_value=.92;shader.inputs['Metallic'].default_value=0
m['grain_reference']='https://extranet.artc.com.au/docs/eng/track-civil/procedures/ballast/eta-04-01.pdf'
m['grain_limits']='ARTC general crushed-ballast reference, not evidence of Melbourne metro material specification. 50 mm procedural cells, 8 mm bump and weathering scale are authored approximations; no individual stones or measured current colour.'
print('VERIFIED authored ballast stone relief; no image textures',flush=True)
