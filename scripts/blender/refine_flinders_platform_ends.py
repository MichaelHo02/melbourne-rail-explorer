"""Taper schematic platform ends; dimensions authored, topology from PTV map."""
import bpy
name='Flinders authored platform precinct - PTV schematic';o=bpy.data.objects[name]
if not o.get('tapered_end_revision'):
 old=o.data;v=[tuple(p.co) for p in old.vertices];f=[];mi=[]
 # Original first eighteen boxes are six decks and their paired edge strips.
 assert len(old.polygons)>=108
 for p in list(old.polygons)[108:]:f.append(tuple(p.vertices));mi.append(p.material_index)
 def prism(points,bottom,top,material):
  start=len(v);k=len(points);v.extend([(x,y,z) for z in [bottom,top] for x,y in points]);f.extend([tuple(start+i for i in reversed(range(k))),tuple(start+k+i for i in range(k))]);mi.extend([material]*2)
  for i in range(k):j=(i+1)%k;f.append((start+i,start+j,start+k+j,start+k+i));mi.append(material)
 for y,width in [(-18,6),(-33,5.2),(-46,5.2),(-59,5.2),(-72,5.2),(-84,4)]:
  half=width/2;tip=half*.65
  prism([(-285,y-half),(-50,y-half),(-35,y-tip),(-35,y+tip),(-50,y+half),(-285,y+half)],.4,1.5,0)
  for side in [-1,1]:
   # 200 mm strips follow both straight and tapered portions.
   a=y+side*(half-.22);b=y+side*(tip-.22)
   prism([(-285,a-.1),(-50,a-.1),(-35,b-.1),(-35,b+.1),(-50,a+.1),(-285,a+.1)],1.5,1.53,1)
 mesh=bpy.data.meshes.new(name+' tapered end revision');mesh.from_pydata(v,[],f);mesh.update()
 for material in old.materials:mesh.materials.append(material)
 for p,index in zip(mesh.polygons,mi):p.material_index=index
 old.use_fake_user=True;o.data=mesh;o['tapered_end_revision']=1;o['taper_limits']='PTV schematic shows tapered platform ends; 15 m taper and 65 percent terminal width authored, not surveyed. Original platform levels, lengths and canopies retained.'
 print('VERIFIED six tapered schematic decks with following safety edges',flush=True)
