"""Deterministic, editable Melbourne vegetation prototypes. Positions come from
Urban Forest inventory at runtime; dimensions are authored, not surveyed.
Run Blender --background --factory-startup --python scripts/blender/build_urban_trees.py.
"""
import bpy, math, random, json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)

def material(name,color):
 m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1); p.inputs['Roughness'].default_value=.92
 return m
bark=material('mottled warm grey bark',(.29,.27,.22))
foliage=[material('foliage '+str(i),c) for i,c in enumerate([(.14,.23,.065),(.22,.31,.10),(.30,.37,.14),(.17,.28,.18)])]

# Shared materials per prototype: vertex colours preserve bark/foliage variation
# without multiplying every city's tree draw calls by the palette size.
coloured=material('urban tree vertex colours',(1,1,1))
attribute=coloured.node_tree.nodes.new('ShaderNodeVertexColor');attribute.layer_name='UrbanColor'
coloured.node_tree.links.new(attribute.outputs['Color'],coloured.node_tree.nodes.get('Principled BSDF').inputs['Base Color'])

cluster=material('urban leaf clusters',(1,1,1))
image=bpy.data.images.load(str(ROOT/'public/textures/surfaces/plane-leaf-cluster.png'));image.pack()
texture=cluster.node_tree.nodes.new('ShaderNodeTexImage');texture.image=image
shader=cluster.node_tree.nodes.get('Principled BSDF')
cluster.node_tree.links.new(texture.outputs['Color'],shader.inputs['Base Color'])
cluster.node_tree.links.new(texture.outputs['Alpha'],shader.inputs['Alpha'])

def mesh(name,verts,faces,mats,indices,textured=False):
 data=bpy.data.meshes.new(name); data.from_pydata(verts,[],faces); data.update()
 obj=bpy.data.objects.new(name,data); bpy.context.collection.objects.link(obj)
 data.materials.append(coloured)
 if textured:data.materials.append(cluster)
 colors=data.color_attributes.new(name='UrbanColor',type='FLOAT_COLOR',domain='CORNER')
 for polygon,i in zip(data.polygons,indices):
  polygon.material_index=1 if textured and i>0 else 0
  for loop in polygon.loop_indices:colors.data[loop].color=(.83+i*.04,.83+i*.04,.83+i*.04,1) if textured and i>0 else mats[i].diffuse_color
 uv=data.uv_layers.new(name='UVMap')
 for polygon in data.polygons:
  for loop in polygon.loop_indices:uv.data[loop].uv=[(0,0),(1,0),(1,1),(0,1)][data.loops[loop].vertex_index%4]
 return obj

def tree(kind,seed):
 rng=random.Random(seed); verts=[]; faces=[]; ids=[]
 def branch(a,b,r1,r2):
  a,b=Vector(a),Vector(b); axis=(b-a).normalized(); u=axis.cross(Vector((0,1,0))).normalized(); v=axis.cross(u)
  n=len(verts)
  for p,r in [(a,r1),(b,r2)]:
   for k in range(6):verts.append(tuple(p+r*(u*math.cos(k*math.tau/6)+v*math.sin(k*math.tau/6))))
  for k in range(6):faces.append((n+k,n+(k+1)%6,n+6+(k+1)%6,n+6+k));ids.append(0)
 def leaf(p,size,angle,shade,narrow=False):
  p=Vector(p); u=Vector((math.cos(angle),math.sin(angle),rng.uniform(-1.0,1.0)))*size
  v=Vector((-math.sin(angle),math.cos(angle),rng.uniform(-.9,.9)))*size*(.19 if narrow else .52)
  n=len(verts); fold=Vector((0,0,size*.12)); verts.extend([tuple(p-u),tuple(p+v+fold),tuple(p+u),tuple(p-v+fold)])
  for tri in [(0,1,2),(0,2,3)]:faces.append(tuple(n+i for i in tri));ids.append(shade)
 if kind=='palm':
  branch((0,0,0),(.08,0,6.5),.32,.21)
  for k in range(16):
   angle=k*math.tau/16; prev=Vector((.08,0,6.3)); end=None
   for j in range(1,9):
    t=j/8; end=Vector((math.cos(angle)*3.4*t,math.sin(angle)*3.4*t,6.3+2.1*math.sin(t*math.pi*.8)-1.6*t))
    branch(prev,end,.035*(1-t)+.008,.008)
    for sign in [-1,1]:
     center=end+Vector((-math.sin(angle)*sign*.32,math.cos(angle)*sign*.32,-.08))
     leaf(center,.42*(1-t*.6),angle+sign*.9,1+k%3,True)
    prev=end
 else:
  gum=kind=='gum'; height=10 if gum else 8; radius=3.4 if gum else 4
  branch((0,0,0),(.12,-.08,height*.58),.30,.13)
  for k in range(9):
   angle=k*2.39996; z=height*(.38+.045*k); start=(.1,0,z)
   end=(math.cos(angle)*radius*rng.uniform(.65,1),math.sin(angle)*radius*rng.uniform(.65,1),height*(.72+.025*k))
   middle=tuple(Vector(start).lerp(Vector(end),.55)+Vector((0,0,.35)))
   branch(start,middle,.13-k*.007,.065);branch(middle,end,.065,.016)
   for j in range(72 if kind in ['plane','elm'] else 150):
    a=rng.random()*math.tau; r=math.sqrt(rng.random())*(1.65 if gum else 1.9); zoff=rng.uniform(-1.7,1.7)*math.sqrt(max(0,1-(r/2.0)**2))
    center=(end[0]+math.cos(a)*r,end[1]+math.sin(a)*r,end[2]+zoff)
    leaf(center,rng.uniform(.23,.48) if gum else rng.uniform(.55,.85),rng.random()*math.tau,4 if gum else 1+rng.randrange(3),gum)
  for k in range(6):
   a=k*math.tau/6;branch((math.cos(a)*.6,math.sin(a)*.6,.02),(0,0,.6),.075,.11)
 obj=mesh(kind,verts,faces,[bark,*foliage],ids,kind in ['plane','elm'])
 # Each prototype is a single mesh with shared material primitives for instancing.
 obj['dimensions']='Authored botanical silhouette; not surveyed tree height or canopy.'
 return obj
for k,seed in [('plane',42),('gum',91),('elm',73),('palm',18)]:tree(k,seed)
out=ROOT/'public/models/environment/urban-trees.glb'; out.parent.mkdir(parents=True,exist_ok=True)
source=ROOT/'assets/source/environment/urban-trees.blend'; source.parent.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(source))
# Runtime shares the external alpha texture across all instances. Keep it packed
# in the editable Blender source but omit its duplicate from the GLB payload.
for input in [shader.inputs['Base Color'],shader.inputs['Alpha']]:
 for link in list(input.links):cluster.node_tree.links.remove(link)
attribute=cluster.node_tree.nodes.new('ShaderNodeVertexColor');attribute.layer_name='UrbanColor'
cluster.node_tree.links.new(attribute.outputs['Color'],shader.inputs['Base Color'])
bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',export_yup=True,export_extras=True)
(ROOT/'public/models/environment/urban-trees.json').write_text(json.dumps({'generator':'scripts/blender/build_urban_trees.py','prototypes':['plane','gum','elm','palm'],'placementSource':'City of Melbourne Urban Forest inventory, CC BY 4.0','sourceUrl':'https://data.melbourne.vic.gov.au/explore/dataset/trees-with-species-and-dimensions-urban-forest/','dimensions':'Authored species-class proportions; raw diameter field units are not assumed.','triangles':sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in bpy.context.scene.objects if o.type=='MESH')},indent=2)+'\n')
print('Exported',out, out.stat().st_size)
