"""Recoverable generic glazing tones; authored, not measured facade colours."""
import bpy,json
from pathlib import Path
r=Path(bpy.data.filepath).resolve().parents[3];s=bpy.context.scene
if not s.get('generic_glazing_response_revision'):
 names=['Authored slate blue glazing']+[f'Authored generic pane tonal variation {i}' for i in range(3)]
 colours=[(.035,.055,.061,1),(.026,.042,.048,1),(.044,.058,.06,1),(.038,.047,.045,1)];report=[]
 for name,colour in zip(names,colours):
  m=bpy.data.materials[name];backup=m.copy();backup.name=name+' before restrained glazing';backup.use_fake_user=True;m['restrained_glazing_original']=backup.name
  n=m.node_tree.nodes.get('Principled BSDF');assert n
  for l in list(m.node_tree.links):
   if l.to_node==n and l.to_socket in [n.inputs['Base Color'],n.inputs['Roughness']]:m.node_tree.links.remove(l)
  n.inputs['Base Color'].default_value=colour;n.inputs['Roughness'].default_value=.18;n.inputs['Metallic'].default_value=.18;n.inputs['Coat Weight'].default_value=.12;n.inputs['Coat Roughness'].default_value=.12;m.diffuse_color=colour
  m['limits']='Authored restrained opaque glazing proxy; tint and roughness illustrative. No measured facade schedule or interior reconstruction.'
  report.append({'material':name,'backup':backup.name,'base_colour':colour,'roughness':.18,'metallic':.18})
 s['generic_glazing_response_revision']='restrained-reflection-v1'
 (r/'docs/generic-glazing-response-audit.json').write_text(json.dumps({'materials':report,'limits':'Generic window materials only; named Eureka, Federation and Flinders scan glass retained. Procedural authored shading, no photographic textures. Exact window arrangements still illustrative.','verification':'Trial render pending.'},indent=2)+'\n')
 print('GENERIC_GLAZING_APPLIED',flush=True)
else:print('GENERIC_GLAZING_ALREADY_APPLIED',flush=True)
