"""Authored City Square surface interpretation; not an as-built reconstruction."""
import bpy,json
from pathlib import Path
R=Path(bpy.data.filepath).resolve().parents[3];d=json.loads((R/'assets/source/environment/city-square-authored-surfaces.json').read_text())
def material(name,lo,hi):
 m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*lo,1);n=m.node_tree.nodes;l=m.node_tree.links;n.clear();o=n.new('ShaderNodeOutputMaterial');s=n.new('ShaderNodeBsdfPrincipled');s.inputs['Roughness'].default_value=.88;l.new(s.outputs['BSDF'],o.inputs['Surface']);g=n.new('ShaderNodeNewGeometry');t=n.new('ShaderNodeTexNoise');t.inputs['Scale'].default_value=12;t.inputs['Detail'].default_value=2;l.new(g.outputs['Position'],t.inputs['Vector']);r=n.new('ShaderNodeValToRGB');r.color_ramp.elements[0].color=(*lo,1);r.color_ramp.elements[1].color=(*hi,1);l.new(t.outputs['Fac'],r.inputs['Fac']);l.new(r.outputs['Color'],s.inputs['Base Color']);return m
mats={'bluestone':bpy.data.materials['Authored central CBD bluestone - coverage illustrative'],'granite':material('Authored City Square granite interpretation',(.25,.235,.20),(.39,.36,.31)),'garden':material('Authored City Square garden soil interpretation',(.07,.055,.03),(.16,.12,.055))}
collection=bpy.data.collections['GROUND - official horizontal geography, authored levels']
for part in d['parts']:
 name='City Square authored '+part['finish']+' surface';old=bpy.data.objects.get(name)
 if old:bpy.data.objects.remove(old,do_unlink=True)
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(part['vertices'],[],part['faces']);mesh.materials.append(mats[part['finish']]);mesh.update();obj=bpy.data.objects.new(name,mesh);collection.objects.link(obj);obj['reference']=d['reference'];obj['limits']=d['limits'];obj['area_m2']=part['area_m2']
 assert all(p.normal.z>.99 for p in mesh.polygons)
 print('VERIFIED City Square surface',part['finish'],len(mesh.polygons),part['area_m2'],flush=True)
old=bpy.data.objects.get('Retained open space M010918_0')
if old:old.hide_render=True;old.hide_viewport=True;old['replacement']='City Square authored surface interpretation from public development plan'
