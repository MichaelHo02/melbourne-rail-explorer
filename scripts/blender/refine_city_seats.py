"""Shared authored wooden benches at explicit public seat inventory points."""
import bpy,json,math
from pathlib import Path
root=globals().get('root') or Path(bpy.data.filepath).resolve().parents[3];name='Authored wooden-batten seat mesh'
if not bpy.data.meshes.get(name):
 v=[];f=[];mi=[]
 def box(x,y,z,sx,sy,sz,mat):
  i=len(v);v.extend([(x+dx*sx/2,y+dy*sy/2,z+dz*sz) for dz in [0,1] for dx,dy in [(-1,-1),(1,-1),(1,1),(-1,1)]])
  for q in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]:f.append(tuple(i+j for j in q));mi.append(mat)
 for j in range(5):box(0,-.22+j*.11,.43,1.8,.085,.06,0)
 for j in range(4):box(0,.26,.58+j*.1,1.8,.055,.075,0)
 for x in [-.65,.65]:box(x,0,0,.07,.42,.43,1);box(x,.26,.43,.055,.055,.55,1)
 m=bpy.data.meshes.new(name);m.from_pydata(v,[],f)
 for label,col,metal in [('Authored seat weathered battens',(.24,.15,.075),0),('Authored seat dark metal supports',(.08,.10,.10),.4)]:
  mat=bpy.data.materials.new(label);mat.use_nodes=True;mat.diffuse_color=(*col,1);s=mat.node_tree.nodes.get('Principled BSDF');s.inputs['Base Color'].default_value=mat.diffuse_color;s.inputs['Roughness'].default_value=.8 if metal==0 else .55;s.inputs['Metallic'].default_value=metal;m.materials.append(mat)
 for p,i in zip(m.polygons,mi):p.material_index=i
 m.update()
d=json.loads((root/'assets/source/environment/city-authored-seats.json').read_text());added=0
for r in d['records']:
 label='Mapped wooden seat '+r['assetid']
 if bpy.data.objects.get(label):continue
 o=bpy.data.objects.new(label,bpy.data.meshes[name]);bpy.data.collections['GROUND - official horizontal geography, authored levels'].objects.link(o);o.location=(*r['preview_xy'],.32);o.rotation_euler.z=(int(r['assetid'])%18)*math.pi/9;o['source_asset_id']=r['assetid'];o['source_url']=d['source'];o['limits']=d['limits'];added+=1
print('VERIFIED mapped wooden seats:',len(d['records']),'new:',added)
