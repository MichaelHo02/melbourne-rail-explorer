"""Authored pole fixtures at selected public asset points; no operating-light claim."""
import bpy,json,math
from pathlib import Path
root=globals().get('root') or Path(bpy.data.filepath).resolve().parents[3];name='Mapped feature-light assets - authored pole fixtures'
if not bpy.data.objects.get(name):
 d=json.loads((root/'assets/source/environment/city-authored-feature-lights.json').read_text());verts=[];faces=[];indices=[]
 def box(x,y,z,sx,sy,sz,material):
  start=len(verts);verts.extend([(x+dx*sx/2,y+dy*sy/2,z+dz*sz/2) for dz in (-1,1) for dx,dy in [(-1,-1),(1,-1),(1,1),(-1,1)]]);faces.extend([tuple(start+i for i in f) for f in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]]);indices.extend([material]*6)
 for a in d['assets']:
  x,y=a['x'],a['y'];start=len(verts)
  for z,r in [(.32,.10),(4.82,.06)]:verts.extend([(x+r*math.cos(i*math.tau/8),y+r*math.sin(i*math.tau/8),z) for i in range(8)])
  faces.extend([tuple(start+i for i in range(7,-1,-1)),tuple(start+8+i for i in range(8))]);indices.extend([0,0])
  for i in range(8):faces.append((start+i,start+(i+1)%8,start+8+(i+1)%8,start+8+i));indices.append(0)
  box(x,y,4.86,.36,.24,.15,0);box(x,y-.125,4.86,.28,.015,.09,1)
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces)
 for label,color,rough,metal in [('Authored feature light dark metal',(.07,.085,.085),.55,.5),('Authored feature light lens',(.55,.61,.58),.25,.05)]:
  m=bpy.data.materials.get(label) or bpy.data.materials.new(label);m.use_nodes=True;s=m.node_tree.nodes.get('Principled BSDF');s.inputs['Base Color'].default_value=(*color,1);s.inputs['Roughness'].default_value=rough;s.inputs['Metallic'].default_value=metal;mesh.materials.append(m)
 for p,i in zip(mesh.polygons,indices):p.material_index=i
 mesh.update();obj=bpy.data.objects.new(name,mesh);bpy.data.collections['GROUND - official horizontal geography, authored levels'].objects.link(obj);obj['source_url']=d['source'];obj['limits']=d['limits'];obj['asset_count']=len(d['assets']);obj['asset_ids']=','.join(a['assetid'] for a in d['assets']);assert all(p.area>0 for p in mesh.polygons);print('VERIFIED mapped feature-light preview fixtures:',len(d['assets']))
