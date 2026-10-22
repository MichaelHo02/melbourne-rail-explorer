"""Authored thin glazing approximation for zero-thickness panes; no photographic textures."""
import bpy,json
from pathlib import Path
r=Path(bpy.data.filepath).resolve().parents[3];s=bpy.context.scene;key='federation_atrium_glazing_revision'
if not s.get(key):
 m=bpy.data.materials['Authored Atrium pale clear glazing'];old=m.copy();old.name=m.name+' before thin glazing';old.use_fake_user=True;m['thin_glazing_backup']=old.name
 ns=m.node_tree.nodes;ns.clear();out=ns.new('ShaderNodeOutputMaterial');clear=ns.new('ShaderNodeBsdfTransparent');clear.inputs['Color'].default_value=(.94,.97,.96,1);reflection=ns.new('ShaderNodeBsdfGlossy');reflection.inputs['Color'].default_value=(.94,.97,.96,1);reflection.inputs['Roughness'].default_value=.08;fresnel=ns.new('ShaderNodeFresnel');fresnel.inputs['IOR'].default_value=1.45;mix=ns.new('ShaderNodeMixShader');links=m.node_tree.links;links.new(fresnel.outputs[0],mix.inputs[0]);links.new(clear.outputs[0],mix.inputs[1]);links.new(reflection.outputs[0],mix.inputs[2]);links.new(mix.outputs[0],out.inputs['Surface']);m.diffuse_color=(.94,.97,.96,.15)
 limits='Authored thin-surface clear transmission and Fresnel reflections for zero-thickness prototype panes. No volumetric absorption or refraction, measured tint or exact glazing specification. Shape, framing and present-day condition remain approximate.';m['limits']=limits;s[key]='thin-fresnel-v1';(r/'docs/federation-atrium-glazing-audit.json').write_text(json.dumps({'backup':old.name,'roughness':.08,'ior':1.45,'tint':[.94,.97,.96],'geometry_changed':False,'limits':limits},indent=2)+'\n');print('ATRIUM_THIN_GLAZING_APPLIED',flush=True)
else:print('ATRIUM_THIN_GLAZING_ALREADY_APPLIED',flush=True)
