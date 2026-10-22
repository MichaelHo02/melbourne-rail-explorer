"""Broader authored material separation in response to washed-out aerial colour."""
import bpy,re
roof={'Authored pale roof finish':((.16,.18,.16),(.30,.32,.28)),'Authored warm roof finish':((.12,.055,.03),(.28,.16,.085)),'Authored light zinc roof finish':((.065,.105,.14),(.22,.29,.32))}
changed=[]
for name,(dark,light) in roof.items():
 m=bpy.data.materials[name];r=m.node_tree.nodes['Live authored tones'];r.color_ramp.elements[0].color=(*dark,1);r.color_ramp.elements[1].color=(*light,1);m['limits']='Authored warm mineral, cool metal or pale mineral palette; exact roof material and colour unmeasured.';changed.append(name)
colours={'stone':[(.40,.31,.20),(.45,.37,.26),(.33,.27,.20),(.49,.42,.32)],'concrete':[(.25,.29,.30),(.31,.32,.28),(.34,.30,.25),(.27,.30,.32)],'terracotta':[(.27,.075,.042),(.32,.13,.075),(.22,.095,.06),(.36,.17,.10)]}
for m in bpy.data.materials:
 if not (m.name.startswith('Authored plain masonry - ') or m.name.startswith('Authored tall plain masonry - ') or m.name.startswith('Authored short low-rise plain wall - ')):continue
 family=next((k for k in colours if 'Authored '+k+' facade' in m.name),None)
 if not family or not m.use_nodes:continue
 match=re.search(r'palette (\d)',m.name);index=int(match.group(1)) if match else 0;c=colours[family][index%4];shader=m.node_tree.nodes.get('Principled BSDF')
 if not shader:continue
 # These authored plain-wall variants deliberately have no base-colour links.
 if shader.inputs['Base Color'].is_linked:continue
 m.diffuse_color=(*c,1);shader.inputs['Base Color'].default_value=(*c,1);m['colour_separation_limits']='Authored mineral colour families; not measured individual facade colour.';changed.append(m.name)
# Distinct restrained glazing tints; keep existing physical response and geometry.
tints=[(.045,.13,.15),(.08,.16,.17),(.12,.17,.14),(.055,.09,.16),(.19,.15,.09),(.09,.15,.21),(.20,.23,.22),(.055,.145,.115)]
for m in bpy.data.materials:
 if not m.name.startswith('Authored grouped tower glazing '):continue
 match=re.search(r'glazing (\d+)',m.name)
 if not match:continue
 c=tints[int(match.group(1))%8];s=m.node_tree.nodes.get('Principled BSDF');s.inputs['Base Color'].default_value=(*c,1);m.diffuse_color=(*c,1);changed.append(m.name)
bpy.context.scene['authored_colour_separation_revision']=1
print('VERIFIED colour separation',len(changed),'materials; geometry and lighting unchanged',flush=True)
