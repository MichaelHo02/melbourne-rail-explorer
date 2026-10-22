"""Restrained authored edge relief on explicitly flat low-rise roof classes."""
import bpy,json
from pathlib import Path
R=Path(bpy.data.filepath).resolve().parents[3];name='Authored flat low-rise parapet relief'
if not bpy.data.objects.get(name):
 d=json.loads((R/'assets/source/environment/city-authored-flat-parapets.json').read_text());v=[];f=[]
 for part in d['parts']:
  start=len(v);v.extend(part['vertices']);f.extend([[start+i for i in face] for face in part['faces']])
 m=bpy.data.meshes.new(name);m.from_pydata(v,[],f);m.update();material=bpy.data.materials.get('Authored parapet pale coping') or bpy.data.materials.new('Authored parapet pale coping');material.use_nodes=True;p=material.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.30,.32,.30,1);p.inputs['Roughness'].default_value=.85;m.materials.append(material)
 o=bpy.data.objects.new(name,m);bpy.data.collections['GROUND - official horizontal geography, authored levels'].objects.link(o);o['source_url']=d['source'];o['source_ids']=','.join(str(p['id']) for p in d['parts']);o['limits']=d['limits'];o['roof_count']=len(d['parts']);print('VERIFIED authored parapets',len(d['parts']),len(m.polygons),'faces',flush=True)
