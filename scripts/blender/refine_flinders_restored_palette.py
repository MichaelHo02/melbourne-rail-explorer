"""Authored muted restoration palette informed by primary restoration records."""
import bpy,json
from pathlib import Path
root=Path(bpy.data.filepath).resolve().parents[3]
reference='https://assets.ctfassets.net/j001bqnk84dk/1Ettb2QUEi8Lpt9QsWfOMi/3d7d79aa7a321122b17616960243b255/dulux_case__study_flinders_st_web.pdf'
palette={'FSS_ochre':((.73,.66,.54),'10YR 7/4'), 'FSS_lightstone':((.78,.72,.62),'10YR 7/4'), 'FSS_brick':((.43,.15,.13),'10R 3/8'), 'FSS_iron':((.12,.17,.15),'10GY 2/2')}
changes=[]
for name,(rgb,munsell) in palette.items():
 obj=bpy.data.objects[name];mat=obj.data.materials[0];s=mat.node_tree.nodes.get('Principled BSDF')
 if 'pre_restoration_palette' not in mat:mat['pre_restoration_palette']=list(s.inputs['Base Color'].default_value)
 rgba=tuple(c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4 for c in rgb)+(1,)
 for l in list(mat.node_tree.links):
  if l.to_node==s and l.to_socket==s.inputs['Base Color']:mat.node_tree.links.remove(l)
 mat.diffuse_color=rgba;s.inputs['Base Color'].default_value=rgba;s.inputs['Roughness'].default_value=.78 if name!='FSS_iron' else .45
 mat['restoration_reference']=reference;mat['documented_munsell_family']=munsell;mat['limits']='Authored RGB approximation guided by documented restoration palette; not a measured or calibrated Munsell conversion. Existing schematic material zones retained.'
 changes.append({'object':name,'material':mat.name,'authored_srgb':rgb,'reference_munsell':munsell})
bpy.context.scene['flinders_restored_palette_revision']=1
(root/'assets/source/environment/flinders-restoration-palette.json').write_text(json.dumps({'source':reference,'reference_page':4,'government_reference':'https://www.premier.vic.gov.au/flinders-street-station-be-repainted-its-original-colours','changes':changes,'limits':'Exact paint appearance, light calibration, facade material boundaries and present-day weathering unverified. No photographic textures used.'},indent=2)+'\n')
print('VERIFIED Flinders restored palette',len(changes),'materials',flush=True)
