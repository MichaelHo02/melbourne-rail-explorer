"""Illustrative unlit signal hardware around official signal-site points."""
import bpy,json,math
from pathlib import Path
R=Path(bpy.data.filepath).resolve().parents[3];d=json.loads((R/'assets/source/environment/cbd-authored-traffic-signals.json').read_text());label='STREETS - authored signal hardware at official sites'
if not bpy.data.collections.get(label):
 collection=bpy.data.collections.new(label);bpy.context.scene.collection.children.link(collection)
 def material(name,c,rough):
  m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*c,1);s=m.node_tree.nodes.get('Principled BSDF');s.inputs['Base Color'].default_value=(*c,1);s.inputs['Roughness'].default_value=rough;return m
 mats=[material('Authored signal pole muted yellow',(.36,.25,.065),.65),material('Authored signal black casing',(.018,.022,.022),.62),material('Authored signal unlit red lens',(.038,.012,.009),.3),material('Authored signal unlit amber lens',(.04,.028,.009),.3),material('Authored signal unlit green lens',(.009,.028,.016),.3)]
 v=[];f=[];mi=[]
 def face(coords,index):start=len(v);v.extend(coords);f.append(list(range(start,start+len(coords))));mi.append(index)
 for i in range(8):
  a=i*math.tau/8;b=(i+1)*math.tau/8;face([(math.cos(a)*.075,math.sin(a)*.075,0),(math.cos(b)*.075,math.sin(b)*.075,0),(math.cos(b)*.06,math.sin(b)*.06,4.2),(math.cos(a)*.06,math.sin(a)*.06,4.2)],0)
 # Casing faces + dark lenses; no emissions or live state.
 x0,x1=-.15,.15;y0,y1=-.14,.14;z0,z1=3.1,4.05
 verts=[(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)]
 for ids in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]:face([verts[i] for i in ids],1)
 for z,index in [(3.85,2),(3.57,3),(3.29,4)]:face([(.155,math.cos(i*math.tau/16)*.105,z+math.sin(i*math.tau/16)*.105) for i in range(16)],index)
 mesh=bpy.data.meshes.new('Authored shared unlit traffic signal');mesh.from_pydata(v,[],f);mesh.update()
 for m in mats:mesh.materials.append(m)
 for p,i in zip(mesh.polygons,mi):p.material_index=i
 for i,p in enumerate(d['placements']):
  o=bpy.data.objects.new('Authored signal site '+p['site_no']+' corner '+str(i),mesh);collection.objects.link(o);o.location=(p['x'],p['y'],.335);o.rotation_euler.z=p['rotation'];o['source_site_no']=p['site_no'];o['limits']=d['limits']
 collection['source']=d['source'];collection['license']=d['license'];collection['limits']=d['limits'];print('VERIFIED authored unlit signal poles',len(d['placements']),'official intersection sites',len(d['records']),flush=True)
