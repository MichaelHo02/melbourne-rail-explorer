"""Original photo-informed Flinders Street viaduct kit, metres, reusable modules.
Blender --background --factory-startup --python scripts/blender/build_viaduct.py
"""
import bpy, math, os, json
import numpy as np
from mathutils import Vector
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'../..'))
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for m in list(bpy.data.materials):bpy.data.materials.remove(m)
def xyz(p):return (p[0],-p[2],p[1])
# Procedural image maps, authored here; no third-party textures/photos embedded.
def texture(name,kind,size=512):
 rng=np.random.default_rng(823+kind);yy,xx=np.mgrid[:size,:size];u=xx/size;v=yy/size
 noise=rng.random((size,size));coarse=rng.random((32,32));coarse=np.repeat(np.repeat(coarse,size//32,0),size//32,1)
 if kind==0:
  row=np.floor(v*24).astype(int);col=np.floor(u*10+.5*(row%2)).astype(int)
  fu=(u*10+.5*(row%2))%1;fv=(v*24)%1;edge=np.minimum(np.minimum(fu,1-fu)*.24,np.minimum(fv,1-fv)*.1)
  joint=edge<.006;brickval=rng.random((24,11))[row%24,col%11]
  c=np.array([.39,.185,.105])[None,None,:]+brickval[:,:,None]*np.array([.17,.12,.075])+noise[:,:,None]*.055
  c[joint]=np.array([.36,.34,.29]);height=np.where(joint,.05,.65)+noise*.10+coarse*.035
 elif kind==1:
  row=np.floor(v*8).astype(int);col=np.floor(u*5+.5*(row%2)).astype(int)
  fu=(u*5+.5*(row%2))%1;fv=(v*8)%1;joint=(np.minimum(fu,1-fu)<.02)|(np.minimum(fv,1-fv)<.028)
  tone=rng.random((8,6))[row%8,col%6];c=np.array([.23,.265,.28])[None,None,:]+tone[:,:,None]*.13+noise[:,:,None]*.065
  c[joint]=np.array([.16,.175,.17]);height=np.where(joint,.12,.6)+noise*.08+coarse*.08
 else:
  # Subtle oxide patches over charcoal-grey protective coating.
  oxide=(coarse>.85)&(noise>.68);c=np.tile(np.array([.25,.275,.265]),(size,size,1))+noise[:,:,None]*.045
  c[oxide]=np.array([.32,.20,.12]);height=noise*.025+oxide*.03
 rgba=np.ones((size,size,4),dtype=np.float32);rgba[:,:,:3]=np.clip(c,0,1)
 image=bpy.data.images.new(name+'_base',width=size,height=size,alpha=False);image.pixels.foreach_set(rgba.ravel());image.filepath_raw='/tmp/'+name+'_base.png';image.file_format='PNG';image.save();image.pack()
 dy,dx=np.gradient(height);normal=np.stack((-dx*2.7,-dy*2.7,np.ones_like(dx)),axis=-1);normal/=np.linalg.norm(normal,axis=-1,keepdims=True)
 rgba[:,:,:3]=normal*.5+.5
 nm=bpy.data.images.new(name+'_normal',width=size,height=size,alpha=False);nm.colorspace_settings.name='Non-Color';nm.pixels.foreach_set(rgba.ravel());nm.filepath_raw='/tmp/'+name+'_normal.png';nm.file_format='PNG';nm.save();nm.pack()
 return image,nm
M={}
for name,kind,metal,rough in [('aged_brick',0,0,.9),('melbourne_bluestone',1,0,.87),('heritage_iron',2,.62,.57)]:
 base,norm=texture(name,kind,512 if kind<2 else 256);m=bpy.data.materials.new(name);m.use_nodes=True;nt=m.node_tree;p=nt.nodes.get('Principled BSDF');p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 tex=nt.nodes.new('ShaderNodeTexImage');tex.image=base;nt.links.new(tex.outputs['Color'],p.inputs['Base Color'])
 tx=nt.nodes.new('ShaderNodeTexImage');tx.image=norm;nm=nt.nodes.new('ShaderNodeNormalMap');nm.inputs['Strength'].default_value=.55;nt.links.new(tx.outputs['Color'],nm.inputs['Color']);nt.links.new(nm.outputs['Normal'],p.inputs['Normal']);M[name]=m
ROOTS={}
def group(name,parent=None):
 o=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(o);o['module']=name
 if parent:o.parent=ROOTS[parent]
 ROOTS[name]=o;return o
group('masonry_arch_bay');group('riveted_girder_span');group('bluestone_pier')
for side in ['left','right']:
 group('railing_'+side,'riveted_girder_span');group('fascia_'+side,'riveted_girder_span')
ROOTS['masonry_arch_bay']['dimensions_metres']=[8,6.8,12]
ROOTS['riveted_girder_span']['dimensions_metres']=[8,3.2,16]
ROOTS['bluestone_pier']['dimensions_metres']=[8.8,5.05,2]
def uv_world(o,scale=2.4):
 # Dominant-axis planar UVs retain a physical brick/block scale after joining.
 mesh=o.data;uv=mesh.uv_layers.active or mesh.uv_layers.new(name='UVMap')
 for poly in mesh.polygons:
  n=poly.normal;axis=max(range(3),key=lambda a:abs(n[a]));axes=[a for a in range(3) if a!=axis]
  for li in poly.loop_indices:
   v=o.matrix_world@mesh.vertices[mesh.loops[li].vertex_index].co
   uv.data[li].uv=(v[axes[0]]/scale,v[axes[1]]/scale)
def finish(o,name,mat,parent):
 o.name=name;o.data.materials.append(M[mat]);o['join_group']=parent;o.parent=ROOTS[parent];uv_world(o);return o
def box(name,pos,dim,mat,parent,bevel=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=xyz(pos));o=bpy.context.object;o.dimensions=(dim[0],dim[2],dim[1]);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bevel:
  mod=o.modifiers.new('worn_edges','BEVEL');mod.width=bevel;mod.segments=2;bpy.ops.object.modifier_apply(modifier=mod.name)
  mod=o.modifiers.new('weighted_normals','WEIGHTED_NORMAL');bpy.ops.object.modifier_apply(modifier=mod.name)
 return finish(o,name,mat,parent)
def mesh(name,verts,faces,mat,parent):
 me=bpy.data.meshes.new(name);me.from_pydata([xyz(v) for v in verts],[],faces);me.update();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);return finish(o,name,mat,parent)
def beam(name,a,b,r,mat,parent,vertices=8):
 va,vb=Vector(xyz(a)),Vector(xyz(b));bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=(vb-va).length,location=(va+vb)/2);o=bpy.context.object;o.rotation_euler=(vb-va).to_track_quat('Z','Y').to_euler();return finish(o,name,mat,parent)
def rivet(pos,parent):
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=.032,location=xyz(pos));o=bpy.context.object;return finish(o,'hot_rivet','heritage_iron',parent)
# Arch vault: profile in local Y/Z, clear tunnel runs across local X.
# 12m repeat: two 1.8m piers flank an 8.4m clear opening.
r=4.2;spring=-5.0;top=-.35;depth=8;steps=32
# Each strip fills above a curved intrados. Full side/end faces avoid boolean seams.
for j in range(steps):
 a=math.pi*j/steps;b=math.pi*(j+1)/steps;za=r*math.cos(a);zb=r*math.cos(b);ya=spring+r*math.sin(a);yb=spring+r*math.sin(b)
 verts=[(x,y,z) for x in [-4,4] for y,z in [(ya,za),(yb,zb),(top,zb),(top,za)]]
 mesh('vault_masonry',verts,[(0,1,2,3),(4,7,6,5),(0,4,5,1),(3,2,6,7)],'aged_brick','masonry_arch_bay')
for z in [-5.1,5.1]:
 box('vault_side_pier',(0,-3.56,z),(8,6.42,1.8),'aged_brick','masonry_arch_bay',.018)
 box('bluestone_plinth',(0,-6.25,z),(8.08,1.1,1.83),'melbourne_bluestone','masonry_arch_bay',.025)
# Radial masonry voussoirs model the arch ring on both street faces.
for side in [-1,1]:
 for j in range(32):
  a=math.pi*j/32+.005;b=math.pi*(j+1)/32-.005
  verts=[(x,spring+radius*math.sin(t),radius*math.cos(t)) for x in [side*4,side*4.13] for radius,t in [(r,a),(r,b),(r+.32,b),(r+.32,a)]]
  mesh('arch_ring_voussoir',verts,[(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)],'melbourne_bluestone','masonry_arch_bay')
 for z in [-5.1,5.1]:
  box('pilaster',(side*4.055,-3.5,z),(.16,5.6,.66),'aged_brick','masonry_arch_bay',.018)
  box('pilaster_cap',(side*4.13,-.82,z),(.28,.22,.91),'melbourne_bluestone','masonry_arch_bay',.024)
 box('masonry_cornice',(side*4.04,-.43,0),(.3,.25,12),'melbourne_bluestone','masonry_arch_bay',.028)
box('vault_deck',(0,-.29,0),(8,.14,12),'melbourne_bluestone','masonry_arch_bay',.01)
# Steel span: rail datum Y0, ballast/sleepers supplied by route integrator.
P='riveted_girder_span'
box('deck_plate',(0,-.285,0),(8,.13,16),'heritage_iron',P,.006)
for x in [-3.70,3.70]:
 box('longitudinal_web',(x,-.97,0),(.15,1.38,16),'heritage_iron',P,.006)
 for y in [-.29,-1.65]:box('girder_flange',(x,y,0),(.44,.1,16),'heritage_iron',P,.012)
 for z in np.arange(-7.75,8,.5):
  for y in [-.41,-1.53]:rivet((x+(.09 if x>0 else -.09),y,float(z)),P)
 for z in np.arange(-8,8.01,2):
  box('girder_stiffener',(x+(.10 if x>0 else -.10),-.97,float(z)),(.10,1.3,.13),'heritage_iron',P,.005)
  for y in [-.53,-.93,-1.36]:rivet((x+(.155 if x>0 else -.155),y,float(z)),P)
for z in np.arange(-7.9,8,2):
 box('cross_bearer',(0,-1.15,float(z)),(7.5,.44,.16),'heritage_iron',P,.008)
 for y in [-.94,-1.37]:box('bearer_flange',(0,y,float(z)),(7.56,.045,.33),'heritage_iron',P,.005)
for z in [-6,-2,2,6]:
 beam('underdeck_cross_brace',(-3.6,-1.47,z-1.8),(3.6,-1.47,z+1.8),.038,'heritage_iron',P)
 beam('underdeck_cross_brace',(3.6,-1.47,z-1.8),(-3.6,-1.47,z+1.8),.038,'heritage_iron',P)
# Heritage fascia and slender looping railing: inspected contractor photos.
for side,label in [(-1,'left'),(1,'right')]:
 x=side*3.99;F='fascia_'+label;R='railing_'+label
 box('fascia_backing',(x,-.54,0),(.08,.50,16),'heritage_iron',F,.01)
 for y in [-.81,-.26]:box('fascia_moulding',(x+side*.035,y,0),(.14,.075,16),'heritage_iron',F,.018)
 for z in np.arange(-7,8,2):
  # Three embossed panels each bay, with an inset rosette at centre.
  for zz in [z-.60,z+.60]:
   box('embossed_panel',(x+side*.061,-.54,float(zz)),(.025,.32,.88),'heritage_iron',F,.024)
   for y in [-.68,-.40]:box('panel_edge',(x+side*.084,y,float(zz)),(.026,.022,.83),'heritage_iron',F,.005)
   for e in [-.42,.42]:box('panel_edge',(x+side*.084,-.54,float(zz+e)),(.026,.29,.024),'heritage_iron',F,.005)
  box('boss_plaque',(x+side*.067,-.54,float(z)),(.035,.33,.29),'heritage_iron',F,.018)
  beam('rosette_boss',(x+side*.08,-.54,float(z)),(x+side*.13,-.54,float(z)),.087,'heritage_iron',F,12)
 for z in np.arange(-8,8.01,2):
  beam('fluted_fascia_post',(x+side*.095,-.83,float(z)),(x+side*.095,-.25,float(z)),.063,'heritage_iron',F,12)
  for y in [-.79,-.29]:beam('post_collar',(x+side*.095,y-.025,float(z)),(x+side*.095,y+.025,float(z)),.088,'heritage_iron',F,12)
  beam('railing_stanchion',(x,-.19,float(z)),(x,1.12,float(z)),.032,'heritage_iron',R)
  box('post_foot',(x,-.18,float(z)),(.18,.11,.19),'heritage_iron',R,.013)
 beam('continuous_handrail',(x,1.12,-8),(x,1.12,8),.037,'heritage_iron',R)
 beam('bottom_rail',(x,-.08,-8),(x,-.08,8),.025,'heritage_iron',R)
 for z in np.arange(-7.75,8,.5):
  # Tapered loop: narrow at top, curved U return below, intersected diagonal.
  coords=[(float(z-.23),1.08),(float(z+.18),.16),(float(z+.15),.05),(float(z),-.035),(float(z-.15),.05),(float(z-.18),.16),(float(z+.23),1.08)]
  for (za,ya),(zb,yb) in zip(coords,coords[1:]):beam('loop_railing',(x,ya,za),(x,yb,zb),.014,'heritage_iron',R,6)
# Tapered bluestone support pier. Wide transverse wall supports one two-track strip.
verts=[(x,y,z) for y,w,d in [(-6.8,8.7,2),(-2.15,8.25,1.64)] for x,z in [(-w/2,-d/2),(w/2,-d/2),(w/2,d/2),(-w/2,d/2)]]
mesh('battered_bluestone_pier',verts,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'melbourne_bluestone','bluestone_pier')
box('pier_cap',(0,-1.95,0),(8.8,.4,2),'melbourne_bluestone','bluestone_pier',.045)
box('pier_footing',(0,-6.55,0),(8.8,.5,2),'melbourne_bluestone','bluestone_pier',.03)
for x in [-3.7,3.7]:box('bearing_pad',(x,-1.71,0),(.7,.08,.72),'heritage_iron','bluestone_pier',.015)
# Distant span (<1000 triangles): preserves deck/girder/railing silhouette without rivets.
group('low_detail');ROOTS['low_detail']['dimensions_metres']=[8,3.2,16]
box('low_deck',(0,-.285,0),(8,.13,16),'heritage_iron','low_detail')
for x in [-3.70,3.70]:
 box('low_web',(x,-.97,0),(.15,1.38,16),'heritage_iron','low_detail')
 for y in [-.29,-1.65]:box('low_flange',(x,y,0),(.44,.1,16),'heritage_iron','low_detail')
for side,label in [(-1,'left'),(1,'right')]:
 g='low_detail_railing_'+label;group(g,'low_detail');x=side*3.99
 for z in [-8,-6,-4,-2,0,2,4,6,8]:box('low_railing_post',(x,.47,z),(.055,1.25,.055),'heritage_iron',g)
 for y in [-.08,1.12]:box('low_rail',(x,y,0),(.06,.055,16),'heritage_iron',g)
# Batch each module/group by material; retain hierarchy for removing interior railings.
parts={}
for o in list(bpy.context.scene.objects):
 if o.type=='MESH':parts.setdefault((o['join_group'],o.data.materials[0].name),[]).append(o)
for (g,m),objs in parts.items():
 bpy.ops.object.select_all(action='DESELECT')
 for o in objs:o.select_set(True)
 bpy.context.view_layer.objects.active=objs[0];bpy.ops.object.join();o=bpy.context.object;o.name=g+'__'+m;o.parent=ROOTS[g]
 bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR');bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
# Export source-neutral modules all at the same origin. Runtime selects one root.
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.gltf(filepath=os.path.join(ROOT,'public/models/environment/railway-viaduct.glb'),export_format='GLB',use_selection=True,export_yup=True,export_animations=False,export_cameras=False,export_lights=False,export_extras=True)
for o in bpy.context.scene.objects:
 if o.get('join_group','').startswith('low_detail'):o.hide_render=True
# Review composition only: two kits side by side, no presentation transform exported.
ROOTS['masonry_arch_bay'].location=(12,0,0)
ROOTS['riveted_girder_span'].location=(-6,0,0);ROOTS['bluestone_pier'].location=(-6,0,0)
world=bpy.data.worlds.new('Morning review');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.30,.37,.43,1);world.node_tree.nodes['Background'].inputs[1].default_value=.65;bpy.context.scene.world=world
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-6.85));ground=bpy.context.object;ground.name='Review ground';ground.data.materials.append(M['melbourne_bluestone']);uv_world(ground)
for pos,energy,size in [((4,-9,18),6500,13),((-18,12,10),3500,12),((12,15,9),4200,10)]:
 bpy.ops.object.light_add(type='AREA',location=pos);o=bpy.context.object;o.data.energy=energy;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,-2))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(35,-37,17));cam=bpy.context.object;cam.rotation_euler=(Vector((3,0,-2.1))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=43;scene=bpy.context.scene;scene.camera=cam
scene.render.engine='CYCLES';scene.cycles.samples=32;scene.render.resolution_x=1800;scene.render.resolution_y=1150;scene.render.resolution_percentage=100;scene.view_settings.view_transform='AgX';scene.render.image_settings.file_format='PNG';scene.render.filepath='/tmp/railway-viaduct-review.png'
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,'assets/source/environment/railway-viaduct.blend'));bpy.ops.render.render(write_still=True)
print('VIADUCT_READY')
