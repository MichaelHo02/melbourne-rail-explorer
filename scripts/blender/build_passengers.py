"""CC0 MakeHuman anatomy + original clothed Melbourne commuters. No addon required.
The source assets are graphical CC0 data, not MakeHuman/MPFB program code.
"""
import bpy,math,os,json,collections
import numpy as np
from mathutils import Vector,Matrix
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'../..'));SRC=os.path.join(ROOT,'assets/source/passengers')
bpy.context.preferences.filepaths.save_version=0
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for m in list(bpy.data.materials):bpy.data.materials.remove(m)
V=[];UV=[];GROUPS=collections.defaultdict(list);g=''
for line in open(os.path.join(SRC,'makehuman-base.obj')):
 p=line.split()
 if not p:continue
 if p[0]=='v':V.append(tuple(map(float,p[1:4])))
 elif p[0]=='vt':UV.append(tuple(map(float,p[1:3])))
 elif p[0]=='g':g=p[1]
 elif p[0]=='f':GROUPS[g].append([(int(x.split('/')[0])-1,int(x.split('/')[1])-1)for x in p[1:]])
SKEL=json.load(open(os.path.join(SRC,'makehuman-skeleton.json')));WEIGHTS=json.load(open(os.path.join(SRC,'makehuman-weights.json')))['weights'];BV=sorted({i for face in GROUPS['body']for i,uv in face})
V=np.array(V,dtype=float);BOTTOM=min(V[i,1]for i in BV);HEIGHT=max(V[i,1]for i in BV)-BOTTOM
# Normals from the genuine basemesh preserve eyelids, ears, noses and fingers.
NORMAL=np.zeros_like(V)
for face in GROUPS['body']:
 ids=[i for i,uv in face];a,b,c=V[ids[:3]];normal=np.cross(b-a,c-a)
 for i in ids:NORMAL[i]+=normal
NORMAL/=np.maximum(np.linalg.norm(NORMAL,axis=1)[:,None],1e-8)
HAND=np.zeros(len(V))
for bone,entries in WEIGHTS.items():
 if bone.startswith('finger') or bone.startswith('hand'):
  for i,w in entries:HAND[i]+=w

def xyz(v):return (float(v[0]),-float(v[2]),float(v[1]))
# Shared cloth normal map and vertex tint: all six people use the same materials.
def material(name,rough,metal=0,cloth=False):
 m=bpy.data.materials.new(name);m.use_nodes=True;nt=m.node_tree;p=nt.nodes.get('Principled BSDF');p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
 col=nt.nodes.new('ShaderNodeVertexColor');col.layer_name='Tint';nt.links.new(col.outputs['Color'],p.inputs['Base Color'])
 if cloth:
  size=256;y,x=np.mgrid[:size,:size];h=(np.sin(x*math.pi*.5)*np.cos(y*math.pi*.5))*.08;dy,dx=np.gradient(h);n=np.stack([-dx,-dy,np.ones_like(h)],axis=-1);n/=np.linalg.norm(n,axis=-1)[:,:,None]
  a=np.ones((size,size,4),np.float32);a[:,:,:3]=n*.5+.5;im=bpy.data.images.new('original_cloth_weave',width=size,height=size,alpha=False);im.colorspace_settings.name='Non-Color';im.pixels.foreach_set(a.ravel());im.filepath_raw='/tmp/passenger-cloth.png';im.file_format='PNG';im.save();im.pack()
  t=nt.nodes.new('ShaderNodeTexImage');t.image=im;normal=nt.nodes.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.18;nt.links.new(t.outputs['Color'],normal.inputs['Color']);nt.links.new(normal.outputs['Normal'],p.inputs['Normal'])
 M[name]=m;return m
M={};material('skin',.63);material('cloth',.83,cloth=True);material('leather',.58);material('hair',.72);material('eyes',.34)
ROOTS={}
def linear(color):return tuple(c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4 for c in color)+(1,)
def mesh(name,verts,faces,mat,color,parent,uvs=None):
 me=bpy.data.meshes.new(name);me.from_pydata([xyz(v)for v in verts],[],faces);me.update();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);o.parent=parent;o['kind']=mat;me.materials.append(M[mat])
 for p in me.polygons:p.use_smooth=True
 attr=me.color_attributes.new(name='Tint',type='FLOAT_COLOR',domain='CORNER')
 for d in attr.data:d.color=linear(color)
 uv=me.uv_layers.new(name='UVMap')
 if uvs:
  for p,coords in zip(me.polygons,uvs):
   for li,co in zip(p.loop_indices,coords):uv.data[li].uv=co
 else:
  for p in me.polygons:
   for li in p.loop_indices:
    v=verts[me.loops[li].vertex_index];uv.data[li].uv=(v[0]*6+v[2]*2,v[1]*6)
 return o
def sphere(name,center,radii,mat,color,parent,segments=16,rings=10):
 verts=[];faces=[]
 for j in range(rings+1):
  phi=math.pi*j/rings
  for i in range(segments):
   th=2*math.pi*i/segments;verts.append((center[0]+radii[0]*math.sin(phi)*math.cos(th),center[1]+radii[1]*math.cos(phi),center[2]+radii[2]*math.sin(phi)*math.sin(th)))
 for j in range(rings):
  for i in range(segments):faces.append((j*segments+i,j*segments+(i+1)%segments,(j+1)*segments+(i+1)%segments,(j+1)*segments+i))
 return mesh(name,verts,faces,mat,color,parent)
def cube(name,pos,dim,mat,color,parent,bevel=.007):
 bpy.ops.mesh.primitive_cube_add(size=1,location=xyz(pos));o=bpy.context.object;o.name=name;o.dimensions=(dim[0],dim[2],dim[1]);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bevel:
  mod=o.modifiers.new('softened_seams','BEVEL');mod.width=bevel;mod.segments=3;bpy.ops.object.modifier_apply(modifier=mod.name)
 o.parent=parent;o['kind']=mat;o.data.materials.append(M[mat]);at=o.data.color_attributes.new(name='Tint',type='FLOAT_COLOR',domain='CORNER')
 for d in at.data:d.color=linear(color)
 for p in o.data.polygons:p.use_smooth=True
 return o
def line(name,a,b,r,mat,color,parent):
 va,vb=Vector(xyz(a)),Vector(xyz(b));bpy.ops.mesh.primitive_cylinder_add(vertices=8,radius=r,depth=(vb-va).length,location=(va+vb)/2);o=bpy.context.object;o.rotation_euler=(vb-va).to_track_quat('Z','Y').to_euler();o.parent=parent;o['kind']=mat;o.data.materials.append(M[mat]);at=o.data.color_attributes.new(name='Tint',type='FLOAT_COLOR',domain='CORNER')
 for d in at.data:d.color=linear(color)
 return o
CONFIGS=[
 {'h':1.82,'width':1.02,'skin':(.49,.30,.21),'top':(.075,.095,.13),'pants':(.09,.10,.12),'hair':(.05,.035,.025),'style':'jacket','pose':'relaxed','bag':'shoulder'},
 {'h':1.68,'width':.96,'skin':(.68,.46,.34),'top':(.48,.35,.22),'pants':(.105,.13,.16),'hair':(.09,.052,.025),'style':'coat','pose':'phone','bag':'shoulder'},
 {'h':1.77,'width':1.08,'skin':(.22,.13,.085),'top':(.16,.22,.18),'pants':(.075,.12,.17),'hair':(.02,.018,.015),'style':'hoodie','pose':'relaxed','bag':'backpack'},
 {'h':1.72,'width':1.00,'skin':(.58,.37,.25),'top':(.35,.105,.11),'pants':(.13,.14,.15),'hair':(.035,.024,.019),'style':'knit','pose':'weightshift','bag':'shoulder'},
 {'h':1.85,'width':1.00,'skin':(.72,.50,.37),'top':(.23,.28,.33),'pants':(.09,.11,.14),'hair':(.30,.29,.27),'style':'jacket','pose':'relaxed','bag':'backpack'},
 {'h':1.65,'width':.94,'skin':(.39,.24,.16),'top':(.22,.24,.32),'pants':(.18,.16,.14),'hair':(.045,.028,.019),'style':'coat','pose':'relaxed','bag':'shoulder'},
]
for index,cfg in enumerate(CONFIGS,1):
 root=bpy.data.objects.new(f'commuter_{index:02}',None);bpy.context.collection.objects.link(root);ROOTS[root.name]=root;root['height_metres']=cfg['h'];root['pose']=cfg['pose'];root['source']='MakeHuman hm08 CC0; original clothing/hair/accessories'
 scale=cfg['h']/HEIGHT
 rest=V.copy()*scale;rest[:,1]-=BOTTOM*scale
 # Gentle proportion variation, strongest at torso; preserve facial anatomy.
 for i in range(len(rest)):
  if rest[i,1]<cfg['h']*.82:rest[i,0]*=cfg['width']
 joints={key:Vector(np.mean(rest[ids],axis=0))for key,ids in SKEL['joints'].items()}
 rotations={'upperarm01.L':('Z',[-28,-29,-31,-29,-28,-28][index-1]),'upperarm01.R':('Z',[29,31,29,30,28,30][index-1]),'lowerarm01.L':('X',42),'lowerarm01.R':('X',40),'upperleg01.L':('Z',-6),'upperleg01.R':('Z',6),'head':('Y',[-4,8,-6,5,0,-9][index-1])}
 if cfg['pose']=='phone':rotations.update({'upperarm01.L':('Z',-28),'lowerarm01.L':('X',-48),'head':('X',9)})
 # Relax the fingers by bending around each knuckle's local flexion axis.
 # MakeHuman's rest hands are splayed; a gentle curl preserves distinct digits.
 for side in ['L','R']:
  for finger in range(2,6):
   for joint,angle in [(1,13),(2,27),(3,18)]:
    rotations[f'finger{finger}-{joint}.{side}']=('X',-angle)
  rotations[f'finger1-2.{side}']=('Y',12 if side=='L'else -12)
 if cfg['pose']=='weightshift':rotations.update({'upperleg01.L':('Z',-4),'upperleg01.R':('Z',8),'spine02':('Z',-2)})
 if cfg['pose']=='step':rotations.update({'upperleg01.L':('X',-9),'upperleg01.R':('X',9),'lowerleg01.R':('X',-8),'upperarm01.L':('Z',-33),'upperarm01.R':('Z',36)})
 matrices={}
 def transform(bone):
  if bone in matrices:return matrices[bone]
  data=SKEL['bones'][bone];pm=transform(data['parent'])if data['parent']else Matrix.Identity(4);own=Matrix.Identity(4)
  if bone in rotations:
   axis,deg=rotations[bone];head=joints[data['head']];own=Matrix.Translation(head)@Matrix.Rotation(math.radians(deg),4,axis)@Matrix.Translation(-head)
  matrices[bone]=pm@own;return matrices[bone]
 for bone in SKEL['bones']:transform(bone)
 # Linear skinning from official CC0 vertex weights; freeze into posed mesh.
 posed=np.zeros_like(rest);total=np.zeros(len(rest))
 for bone,entries in WEIGHTS.items():
  matrix=matrices.get(bone,Matrix.Identity(4))
  for i,w in entries:
   posed[i]+=np.array(matrix@Vector(rest[i]))*w;total[i]+=w
 valid=total>0;posed[valid]/=total[valid,None];posed[~valid]=rest[~valid]
 def pose_point(point,bone='spine02'):return tuple(matrices.get(bone,Matrix.Identity(4))@Vector(point))
 def fromsource(point,bone='head'):
  p=np.array(point)*scale;p[1]-=BOTTOM*scale
  if p[1]<cfg['h']*.82:p[0]*=cfg['width']
  return pose_point(p,bone)
 # Cloth expansion is performed in rest-space before the same anatomical skinning.
 labels=[];faces_by=collections.defaultdict(list)
 for face in GROUPS['body']:
  ids=[i for i,uv in face];center=np.mean(V[ids],axis=0);hand=np.mean(HAND[ids])
  label='skin'if (center[1]>5.65 and abs(center[0])<.67) or center[1]>6.5 or hand>.35 else 'trousers'if center[1]<.35 else 'top'
  if center[1]<-7.0:continue # Foot anatomy is enclosed by authored shoes.
  faces_by[label].append(face)
 for label,faces in faces_by.items():
  ids=sorted({i for f in faces for i,uv in f});lookup={old:new for new,old in enumerate(ids)};positions=[]
  for i in ids:
   v=posed[i].copy()
   if label!='skin':
    # Loose garments soften anatomical contours, with slight gravity/wrinkle variation.
    puff=.019 if label=='trousers' else (.044 if cfg['style']in ['coat','hoodie']else .032)
    n=NORMAL[i].copy();n[1]*=.3;v+=n*puff
    if label=='top' and V[i,1]<1.0:v[1]-=.022
    if label=='top' and .6<V[i,1]<5.05 and abs(rest[i,0])<.20:
     # A loose elliptical garment hangs over the anatomical chest. This
     # removes the painted-on breast/nipple relief of an inflated basemesh.
     rr=rest[i].copy();width=.205*cfg['width'];section=math.sqrt(max(.08,1-(rr[0]/width)**2))
     target_z=(.155 if rr[2]>0 else -.115)*section
     blend=min(1,(V[i,1]-.6)/.7,(5.05-V[i,1])/.35)
     rr[2]=rr[2]*(1-blend)+target_z*blend
     v=np.array(pose_point(rr,'spine02'));v[0]+=NORMAL[i,0]*puff*.4
   positions.append(v)
  color=cfg['skin']if label=='skin'else cfg['pants']if label=='trousers'else cfg['top'];mat='skin'if label=='skin'else'cloth'
  o=mesh(label,positions,[[lookup[i]for i,uv in f]for f in faces],mat,color,root,[[UV[uv]for i,uv in f]for f in faces])
  if label!='skin':
   smooth=o.modifiers.new('tailored_cloth_relax','SMOOTH');smooth.factor=.6;smooth.iterations=12;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=smooth.name)
   seam=o.modifiers.new('closed_garment_seams','SOLIDIFY');seam.thickness=.016;seam.offset=-1;bpy.ops.object.modifier_apply(modifier=seam.name)
  # Keep facial anatomy detailed, remove redundant off-screen body topology.
  dec=o.modifiers.new('near_detail_budget','DECIMATE');dec.ratio=.66 if label=='skin'else .55;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=dec.name)
 # Eyes use the official helper sphere placement, tiny dark irises avoid doll eyes.
 for side in ['l','r']:
  faces=GROUPS[f'helper-{side}-eye'];ids=sorted({i for f in faces for i,uv in f});look={old:new for new,old in enumerate(ids)}
  mesh('eyeball',[pose_point(rest[i],'head')for i in ids],[[look[i]for i,uv in f]for f in faces],'eyes',(.70,.68,.63),root)
  centre=np.mean(V[ids],axis=0);centre[2]=max(V[i,2]for i in ids)+.012
  sphere('iris',fromsource(centre),(.0043,.0043,.0016),'eyes',(.042,.031,.019),root,12,6)
 # Hair follows anatomical scalp. Lower back hair and a bun vary silhouettes.
 hairfaces=[]
 for f in GROUPS['body']:
  c=np.mean(V[[i for i,uv in f]],axis=0);threshold=7.65 if c[2]>.55 else 6.75
  if c[1]>threshold and c[1]>6.6:hairfaces.append(f)
 ids=sorted({i for f in hairfaces for i,uv in f});look={old:new for new,old in enumerate(ids)}
 mesh('scalp_hair',[posed[i]+NORMAL[i]*.006 for i in ids],[[look[i]for i,uv in f]for f in hairfaces],'hair',cfg['hair'],root)
 if index in [2,6]:sphere('hair_bun',fromsource((0,7.1,-.72)),(.055,.06,.05),'hair',cfg['hair'],root,20,12)
 if index==4:
  sphere('back_hair',fromsource((0,6.66,-.51)),(.078,.14,.044),'hair',cfg['hair'],root,20,12)
 # A continuous ribbed collar covers the irregular cut edge of the basemesh.
 collar=[];collarfaces=[]
 for ring,(height,radius) in enumerate([(5.62,.080),(5.89,.074),(5.95,.064),(5.64,.067)]):
  for j in range(40):
   angle=j*2*math.pi/40;point=fromsource((0,height,.03),'spine01');collar.append((point[0]+radius*math.cos(angle),point[1],point[2]+radius*.84*math.sin(angle)))
 for k in range(4):
  for j in range(40):collarfaces.append((k*40+j,k*40+(j+1)%40,((k+1)%4)*40+(j+1)%40,((k+1)%4)*40+j))
 mesh('ribbed_collar',collar,collarfaces,'cloth',tuple(x*.77 for x in cfg['top']),root)
 # Thin eyebrow strips and swept scalp ridges read as hair, not plastic caps.
 for side in [-1,1]:
  a=fromsource((side*.23,7.64,1.04));b=fromsource((side*.57,7.61,.98));line('eyebrow',a,b,.0028,'hair',cfg['hair'],root)
 for j in range(9):
  x=(j-4)*.105
  a=fromsource((x,8.17,.53));b=fromsource((x+.08,8.27,.02))
  line('swept_hair',a,b,.004,'hair',tuple(min(1,x*1.18)for x in cfg['hair']),root)
 # Original shoes in local rest foot space, then posed with anatomical foot bone.
 for side,suffix in [(1,'L'),(-1,'R')]:
  footbone='foot.'+suffix;head=joints[SKEL['bones'][footbone]['head']];cx=head.x
  z0=head.z;yy=.035
  line('sock',pose_point((cx,.08,z0),footbone),pose_point((cx,.19,z0),footbone),.042,'cloth',cfg['pants'],root)
  verts=[];faces=[]
  rings=[(-.062,.035,.050),(-.045,.049,.072),(.035,.053,.073),(.11,.045,.051),(.158,.024,.039)]
  for z,half,high in rings:
   for j in range(12):
    a=2*math.pi*j/12;verts.append(pose_point((cx+half*math.cos(a),yy+max(0,math.sin(a))*high,z0+z),footbone))
  for k in range(len(rings)-1):
   for j in range(12):faces.append((k*12+j,k*12+(j+1)%12,(k+1)*12+(j+1)%12,(k+1)*12+j))
  faces.extend([tuple(range(11,-1,-1)),tuple((len(rings)-1)*12+j for j in range(12))]);mesh('shoe_upper',verts,faces,'leather',(.042,.038,.034),root)
  # Broader sole with a real heel/toe silhouette, not a sphere at the foot.
  soleverts=[pose_point((cx+dx,.025,z0+dz),footbone)for dx,dz in [(-.05,-.06),(.05,-.06),(.054,.07),(.035,.16),(-.035,.16),(-.054,.07)]]
  mesh('shoe_sole',soleverts,[tuple(range(6))],'leather',(.018,.019,.021),root)
 # Garment tailoring details: collar, jacket opening, lapels and buttons.
 collar_y=5.63;front_z=.86
 a=fromsource((-.55,collar_y,front_z),'spine01');b=fromsource((.55,collar_y,front_z),'spine01');line('neckline',a,b,.009,'cloth',tuple(min(1,x*1.25)for x in cfg['top']),root)
 if cfg['style'] in ['jacket','coat']:
  for side in [-1,1]:
   v=[fromsource((side*.08,5.22,1.08)),fromsource((side*.72,4.98,1.03)),fromsource((side*.16,3.65,1.30))]
   mesh('tailored_lapel',v,[(0,1,2)],'cloth',tuple(x*.70 for x in cfg['top']),root)
  for y in [3.0,2.25,1.5]:sphere('jacket_button',fromsource((.10,y,1.22)),(.004,.004,.002),'leather',(.1,.085,.066),root,8,4)
 elif cfg['style']=='hoodie':
  for side in [-1,1]:line('hood_drawstring',fromsource((side*.3,5.35,1.17)),fromsource((side*.33,4.4,1.42)),.0025,'cloth',(.58,.59,.54),root)
 # Practical commuter accessories, built at final world proportions.
 pelvis=pose_point((0,cfg['h']*.53,.01),'pelvis')if 'pelvis'in matrices else(0,cfg['h']*.53,.01)
 if cfg['bag']=='backpack':
  cube('backpack',pose_point((0,cfg['h']*.70,-.155)),(.25,.34,.12),'cloth',(.045,.052,.060),root,.04)
  for side in [-1,1]:line('backpack_strap',pose_point((side*.11,cfg['h']*.82,-.07)),pose_point((side*.14,cfg['h']*.64,.105)),.018,'cloth',(.035,.042,.050),root)
 else:
  color=(.19,.11,.055)if cfg['bag'] in ['briefcase','shoulder']else(.41,.39,.31)
  side=-1 if index%2 else 1;pos=(side*.24,cfg['h']*.43,.015)
  cube('commuter_bag',pos,(.075,.25,.25),'leather'if cfg['bag']!='tote'else'cloth',color,root,.02)
  if cfg['bag']=='shoulder':line('shoulder_strap',(side*.14,cfg['h']*.82,.03),(side*.24,cfg['h']*.48,.03),.012,'leather',color,root)
  else:
   for z in [-.07,.07]:line('bag_handle',(side*.24,cfg['h']*.545,z),(side*.24,cfg['h']*.60,z*.65),.006,'leather',color,root)
 if cfg['pose']=='phone':
  wrist=joints[SKEL['bones']['wrist.L']['tail']];point=pose_point(wrist,'wrist.L')
  cube('phone',point,(.066,.12,.010),'leather',(.018,.022,.027),root,.007)
 # One root origin at ground, not centre of mesh. Shoe soles define ground contact.
 bpy.context.view_layer.update();allmesh=[o for o in root.children if o.type=='MESH'];lowest=min((o.matrix_world@v.co).z for o in allmesh for v in o.data.vertices)
 for o in allmesh:o.location.z-=lowest
 # Join per material; all variants share GPU materials and the cloth texture.
 for mat in M:
  objs=[o for o in root.children if o.type=='MESH'and o.get('kind')==mat]
  if not objs:continue
  bpy.ops.object.select_all(action='DESELECT')
  for o in objs:o.select_set(True)
  bpy.context.view_layer.objects.active=objs[0];bpy.ops.object.join();o=bpy.context.object;o.name=f'{root.name}__{mat}';o.parent=root
  bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR');bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
 # Dedicated distance mesh retains coherent clothing/head silhouette.
 low=bpy.data.objects.new(f'commuter_{index:02}_low',None);bpy.context.collection.objects.link(low);ROOTS[low.name]=low
 for source in list(root.children):
  if source.type!='MESH':continue
  o=source.copy();o.data=source.data.copy();bpy.context.collection.objects.link(o);o.parent=low;o.name=source.name+'_low'
  mod=o.modifiers.new('distant_silhouette','DECIMATE');mod.ratio=.035;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
for root in ROOTS.values():
 for obj in root.children:
  if obj.type=='MESH':obj.data.validate(clean_customdata=False)
# Three local-space shape keys per near mesh; distant LODs remain static.
# Head motion rotates around the base of the skull with a soft neck blend.
# Breathing changes the upper rib cage by only 2 mm; pelvis/feet never move.
for name,root in ROOTS.items():
 if name.endswith('_low'):continue
 h=CONFIGS[int(name[-2:])-1]['h'];neck=Vector((0,0,h*.858))
 for o in root.children:
  if o.type!='MESH':continue
  basis=o.shape_key_add(name='Basis')
  for keyname,angle in [('look_left',8),('look_right',-8),('breathe',0)]:
   key=o.shape_key_add(name=keyname)
   for i,vertex in enumerate(basis.data):
    v=vertex.co.copy();world=o.matrix_local@v
    if angle:
     weight=max(0,min(1,(world.z-h*.842)/(h*.055)));weight=weight*weight*(3-2*weight)
     target=neck+Matrix.Rotation(math.radians(angle),3,'Z')@(world-neck)
     world=world.lerp(target,weight)
    else:
     vertical=max(0,1-abs((world.z-h*.745)/(h*.13)))
     lateral=max(0,1-abs(world.x)/.25)
     if world.z<h*.86 and abs(world.x)<.25:
      world.y-=.0020*vertical*lateral;world.x+=.0012*vertical*(1 if world.x>0 else -1)
    key.data[i].co=o.matrix_local.inverted()@world

# Shipping roots overlap intentionally. Source review spacing is applied AFTER export.
bpy.ops.object.select_all(action='SELECT');bpy.ops.export_scene.gltf(filepath=os.path.join(ROOT,'public/models/passengers/commuters.glb'),export_format='GLB',use_selection=True,export_yup=True,export_animations=False,export_cameras=False,export_lights=False,export_extras=True)
for name,root in ROOTS.items():
 if name.endswith('_low'):
  for o in root.children:o.hide_render=True
 else:root.location.x=(int(name[-2:])-3.5)*.75
# Soft daylight photographic lineup, eye-level camera, neutral backdrop.
world=bpy.data.worlds.new('Passenger studio');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.40,.45,.5,1);world.node_tree.nodes['Background'].inputs[1].default_value=.65;bpy.context.scene.world=world
mat=bpy.data.materials.new('studio');mat.diffuse_color=(.12,.14,.16,1)
bpy.ops.mesh.primitive_plane_add(size=200);bpy.context.object.data.materials.append(mat)
for pos,energy,size in [((-4,-5,7),1800,5),((4,2,5),1300,4)]:
 bpy.ops.object.light_add(type='AREA',location=pos);o=bpy.context.object;o.data.energy=energy;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,1))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(3,-9,3));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,.92))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=5.3;scene=bpy.context.scene;scene.camera=cam;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=False;scene.render.threads_mode='FIXED';scene.render.threads=4;scene.render.resolution_x=1600;scene.render.resolution_y=880;scene.render.resolution_percentage=100;scene.view_settings.view_transform='AgX';scene.render.image_settings.file_format='PNG';scene.render.filepath='/tmp/passengers-lineup.png'
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(SRC,'commuters.blend'));bpy.ops.render.render(write_still=True);print('PASSENGERS_READY')
