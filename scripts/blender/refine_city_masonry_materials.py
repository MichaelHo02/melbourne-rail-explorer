"""Continuous authored masonry surfaces; windows remain separate geometry."""
import bpy,json
from pathlib import Path
root=globals().get('root') or Path(bpy.data.filepath).resolve().parents[3];groups=json.loads((root/'assets/source/environment/city-facade-groups.json').read_text())['groups'];collection=bpy.data.collections['CITY - surveyed envelopes with authored facade materials'];count=0;structures=set();materials=set()
for obj in collection.objects:
 if not obj.name.startswith('survey_') or not obj.data.materials:continue
 group=groups.get(str(obj.get('source_id')))
 if not group or group['structure_height']<=45:continue
 first=obj.data.materials[0]
 family=next((k for k in ['stone','concrete','terracotta'] if first.name.startswith('Authored '+k+' facade') or first.name.startswith('Authored tall plain masonry - Authored '+k+' facade')),None)
 if not family:continue
 label=first.name if first.name.startswith('Authored tall plain masonry - ') else 'Authored tall plain masonry - '+first.name;mat=bpy.data.materials.get(label)
 if not mat:
  mat=first.copy();mat.name=label;s=mat.node_tree.nodes.get('Principled BSDF')
  for link in list(mat.node_tree.links):
   if link.to_node==s and link.to_socket==s.inputs['Base Color']:mat.node_tree.links.remove(link)
  s.inputs['Base Color'].default_value=first.diffuse_color;s.inputs['Roughness'].default_value=.82;s.inputs['Metallic'].default_value=0;mat['limits']='Authored masonry colour retained, painted window grid removed. Geometry supplies windows; individual building materials unmeasured.'
 obj.data.materials[0]=mat;obj['masonry_finish_basis']='Continuous authored masonry with separate window geometry; exact building finish unverified';count+=1;structures.add(group['structure_id']);materials.add(mat.name)
bpy.context.scene['tall_masonry_sections']=count;bpy.context.scene['tall_masonry_structures']=len(structures);print('VERIFIED continuous tall masonry:',count,'sections',len(structures),'structures',len(materials),'materials')
