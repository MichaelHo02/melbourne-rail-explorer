"""Illustrative bay paint at official parking asset points; no occupancy inference."""
import bpy,json,math
from pathlib import Path
root=globals().get('root') or Path(bpy.data.filepath).resolve().parents[3];name='Mapped parking points - illustrative bay paint'
if not bpy.data.objects.get(name):
 d=json.loads((root/'assets/source/environment/city-parking-markings.json').read_text());v=[];f=[]
 v=[(x,y,.27) for x,y in d['paint_vertices']];f=d['paint_faces']
 m=bpy.data.meshes.new(name);m.from_pydata(v,[],f);mat=bpy.data.materials.new('Authored worn parking paint');mat.use_nodes=True;mat.diffuse_color=(.58,.59,.53,1);s=mat.node_tree.nodes.get('Principled BSDF');s.inputs['Base Color'].default_value=mat.diffuse_color;s.inputs['Roughness'].default_value=.9;m.materials.append(mat);m.update();o=bpy.data.objects.new(name,m);bpy.data.collections['GROUND - official horizontal geography, authored levels'].objects.link(o);o['limits']=d['limits'];o['bay_count']=len(d['records']);print('VERIFIED parking paint',len(d['records']),'bays',len(f),'triangles',flush=True)
