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
ROOTS={};GAIT_RIGS={}
GAIT_GROUPS=['body','thigh_L','shin_L','foot_L','arm_L','thigh_R','shin_R','foot_R','arm_R']
def gait_region(bone):
 side=bone[-1] if bone.endswith(('.L','.R')) else None
 if side:
  if bone.startswith('upperleg'):return 'thigh_'+side
  if bone.startswith('lowerleg'):return 'shin_'+side
  if bone.startswith(('foot','toe')):return 'foot_'+side
  if bone.startswith(('upperarm','lowerarm','wrist','finger','hand','metacarpal')):return 'arm_'+side
 return 'body'
GAIT_WEIGHTS=[collections.defaultdict(float) for _ in V]
for bone,entries in WEIGHTS.items():
 for i,w in entries:GAIT_WEIGHTS[i][gait_region(bone)]+=w
def gait_weights(obj,weights):
 groups={name:obj.vertex_groups.new(name='gait_'+name) for name in GAIT_GROUPS}
 for i,row in enumerate(weights):
  total=sum(row.values()) or 1
  for name,w in row.items():
   if w>0:groups[name].add([i],w/total,'REPLACE')

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
 va,vb=Vector(xyz(a)),Vector(xyz(b));bpy.ops.mesh.primitive_cylinder_add(vertices=8,radius=r,depth=(vb-va).length,location=(va+vb)/2);o=bpy.context.object;o.name=name;o.rotation_euler=(vb-va).to_track_quat('Z','Y').to_euler();o.parent=parent;o['kind']=mat;o.data.materials.append(M[mat]);at=o.data.color_attributes.new(name='Tint',type='FLOAT_COLOR',domain='CORNER')
 for d in at.data:d.color=linear(color)
 return o
CONFIGS=[
 {'h':1.82,'width':1.02,'skin':(.49,.30,.21),'top':(.075,.095,.13),'pants':(.09,.10,.12),'hair':(.05,.035,.025),'style':'jacket','pose':'relaxed','bag':'shoulder'},
 {'h':1.68,'width':.96,'skin':(.68,.46,.34),'top':(.48,.35,.22),'pants':(.105,.13,.16),'hair':(.09,.052,.025),'style':'coat','pose':'phone','bag':'shoulder'},
 {'h':1.77,'width':1.08,'skin':(.22,.13,.085),'top':(.16,.22,.18),'pants':(.075,.12,.17),'hair':(.02,.018,.015),'style':'hoodie','pose':'relaxed','bag':'backpack'},
 {'h':1.72,'width':1.00,'skin':(.58,.37,.25),'top':(.35,.105,.11),'pants':(.13,.14,.15),'hair':(.035,.024,.019),'style':'knit','pose':'weightshift','bag':'shoulder'},
 {'h':1.85,'width':1.00,'skin':(.72,.50,.37),'top':(.49,.61,.68),'pants':(.09,.11,.14),'hair':(.30,.29,.27),'style':'shirt','pose':'relaxed','bag':'backpack'},
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
  label='skin'if (center[1]>5.65 and abs(center[0])<.67) or center[1]>6.5 or hand>.12 else 'trousers'if center[1]<.35 else 'top'
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
    if label=='top' and V[i,1]<1.0:v[1]-=.035
    if label=='trousers' and V[i,1]>-.25:v[1]+=.032
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
  gait_weights(o,[GAIT_WEIGHTS[i] for i in ids])
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
 # Six different hairlines remove the identical bowl-cut silhouette.
 hairfaces=[]
 for f in GROUPS['body']:
  c=np.mean(V[[i for i,uv in f]],axis=0)
  front=[7.96,7.88,8.02,7.86,8.13,7.95][index-1]
  side=[7.18,6.85,7.3,6.75,7.1,6.85][index-1]
  threshold=(front+(.14*c[0]if index in[1,4,5]else 0))if c[2]>.55 else side
  if c[1]>threshold and c[1]>6.6:hairfaces.append(f)
 ids=sorted({i for f in hairfaces for i,uv in f});look={old:new for new,old in enumerate(ids)}
 mesh('scalp_hair',[posed[i]+NORMAL[i]*(.003 if index in[3,5]else .009)for i in ids],[[look[i]for i,uv in f]for f in hairfaces],'hair',cfg['hair'],root)
 if index==2:sphere('high_hair_bun',fromsource((0,7.55,-.76)),(.052,.065,.052),'hair',cfg['hair'],root,20,12)
 if index in[4,6]:
  # Connected side/back lobes form a shoulder-length style and a shorter bob.
  length=.12 if index==4 else .09
  for side in[-1,1]:sphere('side_hair',fromsource((side*.75,6.50 if index==4 else 6.75,.06)),(.043,length,.058),'hair',cfg['hair'],root,20,14)
  sphere('back_hair',fromsource((0,6.50 if index==4 else 6.75,-.56)),(.092,length,.058),'hair',cfg['hair'],root,24,14)
 # A smooth undershirt collar reaches inside the neckline instead of leaving
 # the serrated open edge of independently smoothed body pieces exposed.
 collar=[];collarfaces=[]
 collarcolour=tuple(x*.92 for x in cfg['top'])
 for height,rx,rz in[(5.43,.096,.087),(5.82,.09,.078),(5.98,.065,.059),(5.48,.058,.052)]:
  for j in range(40):
   a=j*2*math.pi/40;point=fromsource((0,height,.09),'spine01');collar.append((point[0]+rx*math.cos(a),point[1],point[2]+rz*math.sin(a)))
 for k in range(4):
  for j in range(40):collarfaces.append((k*40+j,k*40+(j+1)%40,((k+1)%4)*40+(j+1)%40,((k+1)%4)*40+j))
 mesh('continuous_neck_collar',collar,collarfaces,'cloth',collarcolour,root)
 # An overlapping elliptical hem replaces the black saw-tooth waist gap.
 hem=[];hemfaces=[];hem_y=(.35-BOTTOM)*scale
 for y,rx,rz in[(hem_y+.022,.211,.153),(hem_y-.026,.208,.152),(hem_y-.028,.184,.130),(hem_y+.018,.186,.13)]:
  for j in range(48):
   a=j*2*math.pi/48;hem.append(pose_point((math.sin(a)*rx*cfg['width'],y,math.cos(a)*rz),'spine02'))
 for k in range(4):
  for j in range(48):hemfaces.append((k*48+j,k*48+(j+1)%48,((k+1)%4)*48+(j+1)%48,((k+1)%4)*48+j))
 mesh('finished_waist_hem',hem,hemfaces,'cloth',tuple(x*.9 for x in cfg['top']),root)
 # Cuffs end at the wrist; the hand itself remains uncovered anatomical skin.
 for side in['L','R']:
  bone='wrist.'+side;wrist=np.array(pose_point(joints[SKEL['bones'][bone]['head']],bone))
  forearm=np.array(pose_point(joints[SKEL['bones']['lowerarm02.'+side]['head']],'lowerarm02.'+side))
  axis=wrist-forearm;axis/=np.linalg.norm(axis);u=np.cross(axis,np.array([0,0,1]));u/=np.linalg.norm(u);v=np.cross(axis,u)
  verts=[];faces=[]
  for along,r in[(-.024,.038),(.004,.036),(.004,.029),(-.024,.029)]:
   for j in range(20):
    a=2*math.pi*j/20;verts.append(wrist+axis*along+(u*math.cos(a)+v*math.sin(a))*r)
  for k in range(4):
   for j in range(20):faces.append((k*20+j,k*20+(j+1)%20,((k+1)%4)*20+(j+1)%20,((k+1)%4)*20+j))
  mesh('tailored_cuff',verts,faces,'cloth',tuple(x*.87 for x in cfg['top']),root)
 for side in[-1,1]:line('eyebrow',fromsource((side*.23,7.64,1.04)),fromsource((side*.57,7.61,.98)),.0028,'hair',cfg['hair'],root)
 # Original shoes in local rest foot space, then posed with anatomical foot bone.
 for side,suffix in [(1,'L'),(-1,'R')]:
  footbone='foot.'+suffix;head=joints[SKEL['bones'][footbone]['head']];cx=head.x
  z0=head.z;yy=.035
  line('sock',pose_point((cx,.08,z0),footbone),pose_point((cx,.25,z0),footbone),.045,'cloth',cfg['pants'],root)
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
 # Distinct clothing constructions, rather than six recoloured sweaters.
 if cfg['style']in['jacket','coat','shirt']:
  shirt=(.78,.81,.80)if index in[1,2]else tuple(min(1,x*1.04)for x in cfg['top'])if index==5 else(.72,.68,.62)
  levels=[(cfg['h']*.518,.070,.174),(cfg['h']*.67,.072,.171),(cfg['h']*.78,.080,.169),(cfg['h']*.84,.054,.113)]
  verts=[];faces=[]
  for y,width,z in levels:
   for j in range(9):
    x=(j/8*2-1)*width;verts.append(pose_point((x,y,z-.045*(x/width)**2)))
  for k in range(len(levels)-1):
   for j in range(8):faces.append((k*9+j,k*9+j+1,(k+1)*9+j+1,(k+1)*9+j))
  mesh('visible_shirt_front',verts,faces,'cloth',shirt,root)
  # Collar points lie above the shirt panel, with readable contrasting lapels.
  for side in[-1,1]:
   verts=[pose_point((side*.016,cfg['h']*.844,.124)),pose_point((side*.057,cfg['h']*.840,.126)),pose_point((side*.061,cfg['h']*.816,.161)),pose_point((side*.028,cfg['h']*.826,.151))]
   mesh('shirt_collar_point',verts,[(0,1,2,3)],'cloth',shirt,root)
  for y in[.56,.62,.68,.74,.80]:sphere('shirt_button',pose_point((0,cfg['h']*y,.178 if y<.78 else .151)),(.0028,.0028,.002),'leather',(.31,.33,.32),root,8,4)
 if cfg['style']in['jacket','coat']:
  bottom=cfg['h']*(.43 if cfg['style']=='coat'else .515)
  levels=[(bottom,.220,.164,.035),(cfg['h']*.60,.214,.169,.030),(cfg['h']*.74,.233,.179,.045),(cfg['h']*.82,.228,.162,.080),(cfg['h']*.843,.174,.116,.053),(cfg['h']*.858,.087,.075,.044)]
  verts=[];faces=[]
  for y,rx,rz,opening in levels:
   start=math.asin(opening/rx)
   for j in range(49):
    a=start+(2*math.pi-2*start)*j/48;verts.append(pose_point((math.sin(a)*rx*cfg['width'],y,math.cos(a)*rz+.003)))
  for k in range(len(levels)-1):
   for j in range(48):faces.append((k*49+j,k*49+j+1,(k+1)*49+j+1,(k+1)*49+j))
  jacket=mesh('open_outer_jacket',verts,faces,'cloth',cfg['top'],root)
  seam=jacket.modifiers.new('turned_jacket_edges','SOLIDIFY');seam.thickness=.005;seam.offset=-1;bpy.context.view_layer.objects.active=jacket;bpy.ops.object.modifier_apply(modifier=seam.name)
  for side in[-1,1]:
   verts=[pose_point((side*.073,cfg['h']*.829,.153)),pose_point((side*.137,cfg['h']*.801,.168)),pose_point((side*.038,cfg['h']*.731,.186)),pose_point((side*.063,cfg['h']*.772,.184))]
   mesh('visible_jacket_lapel',verts,[(0,1,2,3)],'cloth',tuple(x*.72 for x in cfg['top']),root)
   line('welt_pocket',pose_point((side*.09,cfg['h']*.58,.168)),pose_point((side*.177,cfg['h']*.58,.121)),.0027,'cloth',tuple(x*.6 for x in cfg['top']),root)
 elif cfg['style']=='hoodie':
  sphere('down_hood',pose_point((0,cfg['h']*.81,-.076),'spine01'),(.104,.087,.093),'cloth',tuple(x*.86 for x in cfg['top']),root,24,14)
  for side in[-1,1]:line('hood_drawstring',pose_point((side*.04,cfg['h']*.839,.11)),pose_point((side*.038,cfg['h']*.757,.183)),.0025,'cloth',(.61,.63,.57),root)
  for side in[-1,1]:line('kangaroo_pocket_seam',pose_point((side*.072,cfg['h']*.647,.174)),pose_point((side*.118,cfg['h']*.565,.15)),.0024,'cloth',tuple(x*.64 for x in cfg['top']),root)
 # Practical commuter accessories, built at final world proportions.
 pelvis=pose_point((0,cfg['h']*.53,.01),'pelvis')if 'pelvis'in matrices else(0,cfg['h']*.53,.01)
 if cfg['bag']=='backpack':
  cube('backpack',pose_point((0,cfg['h']*.70,-.155)),(.25,.34,.12),'cloth',(.045,.052,.060),root,.04)
  for side in [-1,1]:
   a=pose_point((side*.11,cfg['h']*.82,-.07));b=pose_point((side*.17,cfg['h']*.835,.08));c=pose_point((side*.17,cfg['h']*.675,.17))
   line('backpack_strap_top',a,b,.016,'cloth',(.035,.042,.050),root);line('backpack_strap_front',b,c,.016,'cloth',(.035,.042,.050),root)
 else:
  color=(.19,.11,.055)if cfg['bag'] in ['briefcase','shoulder']else(.41,.39,.31)
  side=-1 if index%2 else 1;pos=(side*.24,cfg['h']*.43,.015)
  cube('commuter_bag',pos,(.075,.25,.25),'leather'if cfg['bag']!='tote'else'cloth',color,root,.02)
  if cfg['bag']=='shoulder':
   line('shoulder_strap_top',(side*.14,cfg['h']*.82,.14),(side*.19,cfg['h']*.64,.10),.011,'leather',color,root)
   line('shoulder_strap_lower',(side*.19,cfg['h']*.64,.10),(side*.24,cfg['h']*.48,.03),.011,'leather',color,root)
  else:
   for z in [-.07,.07]:line('bag_handle',(side*.24,cfg['h']*.545,z),(side*.24,cfg['h']*.60,z*.65),.006,'leather',color,root)
 if cfg['pose']=='phone':
  wrist=joints[SKEL['bones']['wrist.L']['tail']];point=pose_point(wrist,'wrist.L')
  cube('phone',point,(.066,.12,.010),'leather',(.018,.022,.027),root,.007)
 # One root origin at ground, not centre of mesh. Shoe soles define ground contact.
 bpy.context.view_layer.update();allmesh=[o for o in root.children if o.type=='MESH'];lowest=min((o.matrix_world@v.co).z for o in allmesh for v in o.data.vertices)
 for o in allmesh:o.location.z-=lowest
 rig={}
 for side in ['L','R']:
  for label,bone in [('hip','upperleg01.'+side),('knee','lowerleg01.'+side),('ankle','foot.'+side),('shoulder','upperarm01.'+side)]:
   point=Vector(xyz(pose_point(joints[SKEL['bones'][bone]['head']],bone)));point.z-=lowest;rig[label+'_'+side]=point
 GAIT_RIGS[root.name]=rig
 # Authored props inherit the same deformation as their anatomical attachment.
 # Groups survive garment solidify/decimate and the material joins below.
 for o in allmesh:
  if o.vertex_groups:continue
  region='body'
  if o.name.startswith(('shoe_','sock','tailored_cuff','phone')):
   centre=sum((o.matrix_world@v.co for v in o.data.vertices),Vector())/max(1,len(o.data.vertices))
   side='L' if centre.x>0 else 'R'
   region=('arm_' if o.name.startswith(('tailored_cuff','phone')) else 'foot_')+side
  if o.name.startswith('sock'):
   heights=[(o.matrix_world@v.co).z for v in o.data.vertices];lo,hi=min(heights),max(heights);rows=[]
   for height in heights:
    blend=max(0,min(1,(height-lo)/(hi-lo)));blend=blend*blend*(3-2*blend)
    rows.append({'foot_'+side:1-blend,'shin_'+side:blend})
   gait_weights(o,rows)
  else:gait_weights(o,[{region:1} for _ in o.data.vertices])
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
# Three local-space idle shape keys per near mesh. Eight walking keys on both LODs.
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


# A one-metre-per-second commuter stride: 1.1 metres per complete left/right
# cycle. During the 60% stance interval each sole moves backwards by exactly
# 0.66 m relative to its root, cancelling forward root travel. During swing
# the foot lifts 9 cm, returning smoothly to the next contact. Two-bone IK
# preserves limb lengths instead of translating a rigid person up and down.
WALK_SAMPLES=8;WALK_STRIDE=1.1

def gait_matrices(rig,phase,phone=False):
 bob=-.060+.010*math.cos(phase*4*math.pi)
 body=Matrix.Translation((.006*math.sin(phase*2*math.pi),0,bob));result={'body':body}
 for side,offset in [('L',0),('R',.5)]:
  p=(phase+offset)%1
  if p<.6:forward=.33-WALK_STRIDE*p;lift=0
  else:
   swing=(p-.6)/.4;ease=swing*swing*(3-2*swing)
   forward=-.33+.66*ease;lift=.09*math.sin(math.pi*swing)
  hip=rig['hip_'+side];knee=rig['knee_'+side];ankle=rig['ankle_'+side]
  target_hip=body@hip;target_ankle=ankle+Vector((0,-forward,lift))
  upper=(knee-hip).length;lower=(ankle-knee).length
  direction=(target_ankle-target_hip).normalized();distance=min((target_ankle-target_hip).length,upper+lower-.0001)
  along=(upper*upper-lower*lower+distance*distance)/(2*distance)
  outward=Vector((0,-1,0));outward=(outward-direction*outward.dot(direction)).normalized()
  target_knee=target_hip+direction*along+outward*math.sqrt(max(0,upper*upper-along*along))
  result['thigh_'+side]=Matrix.Translation(target_hip)@(knee-hip).rotation_difference(target_knee-target_hip).to_matrix().to_4x4()@Matrix.Translation(-hip)
  result['shin_'+side]=Matrix.Translation(target_knee)@(ankle-knee).rotation_difference(target_ankle-target_knee).to_matrix().to_4x4()@Matrix.Translation(-knee)
  result['foot_'+side]=Matrix.Translation(target_ankle-ankle)
  shoulder=rig['shoulder_'+side]
  swing=math.radians(2 if phone and side=='L' else 9)*math.cos(p*2*math.pi)
  result['arm_'+side]=body@Matrix.Translation(shoulder)@Matrix.Rotation(swing,4,'X')@Matrix.Translation(-shoulder)
 return result

for name,root in ROOTS.items():
 base_name=name.removesuffix('_low');cfg=CONFIGS[int(base_name[-2:])-1];rig=GAIT_RIGS[base_name]
 root['walk_stride_metres']=WALK_STRIDE;root['walk_forward_axis']='+Z glTF / -Y Blender';root['walk_samples']=WALK_SAMPLES
 for o in root.children:
  if o.type!='MESH':continue
  basis=o.data.shape_keys.key_blocks['Basis'] if o.data.shape_keys else o.shape_key_add(name='Basis')
  group_names={g.index:g.name.removeprefix('gait_') for g in o.vertex_groups}
  weights=[[(group_names[g.group],g.weight) for g in v.groups if g.group in group_names] for v in o.data.vertices]
  world_basis=[o.matrix_local@v.co for v in basis.data];inverse=o.matrix_local.inverted()
  for sample in range(WALK_SAMPLES):
   key=o.shape_key_add(name=f'walk_{sample}');transforms=gait_matrices(rig,sample/WALK_SAMPLES,cfg['pose']=='phone')
   for i,world in enumerate(world_basis):
    row=weights[i];total=sum(w for _,w in row)
    posed=sum((transforms[region]@world*w for region,w in row),Vector())/total if total else transforms['body']@world
    key.data[i].co=inverse@posed


# Blender may initialise new shape-key values to one. Ship the neutral pose;
# the runtime supplies either idle or walking weights for each instance.
for root in ROOTS.values():
 for o in root.children:
  if o.type=='MESH' and o.data.shape_keys:
   for key in o.data.shape_keys.key_blocks:key.value=0

# Shipping roots overlap intentionally. Source review spacing is applied AFTER export.
bpy.ops.object.select_all(action='SELECT');bpy.ops.export_scene.gltf(filepath=os.path.join(ROOT,'public/models/passengers/commuters.glb'),export_format='GLB',use_selection=True,export_yup=True,export_animations=False,export_morph_normal=False,export_cameras=False,export_lights=False,export_extras=True)
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
bpy.ops.object.camera_add(location=(2.3,-10,2.5));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,.92))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=5.3;scene=bpy.context.scene;scene.camera=cam;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=False;scene.render.threads_mode='FIXED';scene.render.threads=4;scene.render.resolution_x=1600;scene.render.resolution_y=880;scene.render.resolution_percentage=100;scene.view_settings.view_transform='AgX';scene.render.image_settings.file_format='PNG';scene.render.filepath='/tmp/passengers-lineup.png'
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(SRC,'commuters.blend'))
if not os.environ.get('PASSENGERS_SKIP_RENDER'):bpy.ops.render.render(write_still=True)
print('PASSENGERS_READY',flush=True)
