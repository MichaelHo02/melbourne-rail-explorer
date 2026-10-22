"""Authored tonal adjustment to generic roof materials; no photo textures."""
import bpy
palettes={'Authored pale roof finish':((.18,.20,.20),(.32,.34,.33),0,.82),'Authored warm roof finish':((.22,.20,.17),(.36,.32,.25),0,.85),'Authored light zinc roof finish':((.25,.28,.29),(.42,.45,.44),.25,.70)}
for name,(dark,light,metal,rough) in palettes.items():
 m=bpy.data.materials[name];r=m.node_tree.nodes.get('Live authored tones');assert r
 if 'previous_roof_tones' not in m:m['previous_roof_tones']=str([tuple(e.color) for e in r.color_ramp.elements])
 r.color_ramp.elements[0].color=(*dark,1);r.color_ramp.elements[1].color=(*light,1);s=m.node_tree.nodes.get('Principled BSDF');s.inputs['Metallic'].default_value=metal;s.inputs['Roughness'].default_value=rough;m['limits']='Authored generic roof tonal depth and surface response; individual real roof finish and reflectance unmeasured.'
bpy.context.scene['generic_roof_tonal_pass']='Three existing authored roof finishes toned down; lighting unchanged';print('VERIFIED generic roof tone materials',len(palettes),flush=True)
