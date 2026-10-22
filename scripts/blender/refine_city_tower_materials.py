"""Author consistent tower glazing; retained groups do not establish real colours."""
import bpy,json
from pathlib import Path
root=globals().get('root') or Path(bpy.data.filepath).resolve().parents[3]
groups=json.loads((root/'assets/source/environment/city-facade-groups.json').read_text())['groups']
collection=bpy.data.collections['CITY - surveyed envelopes with authored facade materials']
colours=[(.13,.19,.21),(.18,.23,.24),(.20,.24,.23),(.13,.17,.22),(.24,.23,.20),(.19,.23,.27),(.25,.28,.28),(.16,.21,.20)]
count=0;structures=set()
for obj in collection.objects:
 if not obj.name.startswith('survey_') or not obj.data.materials:continue
 source=str(obj.get('source_id'));group=groups.get(source)
 if not group or group['structure_height']<=45:continue
 first=obj.data.materials[0]
 if not first.name.startswith('Authored glass facade') and not first.name.startswith('Authored grouped tower glazing'):continue
 variant=(int(group['structure_id'])*2654435761>>8)%len(colours);label='Authored grouped tower glazing '+str(variant)+' - colour unverified';mat=bpy.data.materials.get(label)
 if not mat:
  mat=bpy.data.materials.new(label);mat.use_nodes=True;shader=mat.node_tree.nodes.get('Principled BSDF');shader.inputs['Base Color'].default_value=(*colours[variant],1);shader.inputs['Metallic'].default_value=.25;shader.inputs['Roughness'].default_value=.22+.025*(variant%4);shader.inputs['Coat Weight'].default_value=.22;shader.inputs['Coat Roughness'].default_value=.16;mat.diffuse_color=(*colours[variant],1);mat['limits']='Authored reflective facade finish; specific building colour and construction not measured'
 obj.data.materials[0]=mat;obj['tower_finish_basis']='Retained structure ID groups authored tint and roughness; modelled window geometry supplies grid';count+=1;structures.add(group['structure_id'])
bpy.context.scene['tower_material_sections']=count;bpy.context.scene['tower_material_structures']=len(structures)
print('VERIFIED grouped tower finishes:',count,'sections',len(structures),'structures')
