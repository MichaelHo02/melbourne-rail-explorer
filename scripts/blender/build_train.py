"""Reproducible metre-scale HCMT reconstruction and gameplay cab. Run Blender --background --python this.py."""
import bpy, math, os, json
from mathutils import Vector
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'../..'))
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for m in bpy.data.materials: bpy.data.materials.remove(m)
M={}
def mat(name,color,metal=0,rough=.5,emit=0):
 m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 if emit:p.inputs['Emission Color'].default_value=(*color,1);p.inputs['Emission Strength'].default_value=emit
 M[name]=m;return m
mat('brushed_aluminium',(.58,.63,.67),.65,.3);mat('metro_blue',(.012,.16,.30),.38,.3);mat('safety_yellow',(.96,.67,.035),.12,.38)
mat('window_glass',(.018,.052,.070),.55,.17);mat('rubber',(.026,.034,.039),.05,.66);mat('bogie_steel',(.13,.16,.18),.7,.46)
mat('ceramic_white',(.84,.9,.93),.3,.4);mat('headlight',(.96,.91,.68),0,.2,3);mat('red_marker',(.75,.015,.009),0,.3,2)
mat('livery_cyan',(.025,.49,.72),.25,.3);mat('livery_sky',(.06,.31,.59),.25,.3);mat('livery_mid',(.025,.20,.42),.25,.3);mat('livery_navy',(.015,.085,.22),.25,.3);mat('nose_graphite',(.12,.135,.15),.35,.34)
mat('cab_graphite',(.062,.082,.092),.14,.6);mat('cab_slate',(.13,.19,.22),.2,.55);mat('screen',(.03,.35,.46),0,.3,.6);mat('green_led',(.15,.8,.43),0,.3,1)
def xyz(p):return (p[0],-p[2],p[1])
def box(name,pos,dim,material,bevel=0,group='car'):
 bpy.ops.mesh.primitive_cube_add(size=1,location=xyz(pos));o=bpy.context.object;o.name=name;o.dimensions=(dim[0],dim[2],dim[1]);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(M[material]);o['group']=group
 if bevel:
  mod=o.modifiers.new('Manufactured edge radii','BEVEL');mod.width=bevel;mod.segments=3
  bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
  mod=o.modifiers.new('Weighted surface normals','WEIGHTED_NORMAL');bpy.ops.object.modifier_apply(modifier=mod.name)
 return o
def cyl(name,pos,radius,depth,material,axis='x',group='car'):
 bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=radius,depth=depth,location=xyz(pos));o=bpy.context.object;o.name=name
 if axis=='x':o.rotation_euler[1]=math.pi/2
 o.data.materials.append(M[material]);o['group']=group
 for p in o.data.polygons:p.use_smooth=len(p.vertices)==4
 return o
def beam(name,a,b,r,material,group='car'):
 va,vb=Vector(xyz(a)),Vector(xyz(b));bpy.ops.mesh.primitive_cylinder_add(vertices=8,radius=r,depth=(vb-va).length,location=(va+vb)/2);o=bpy.context.object;o.name=name;o.rotation_euler=(vb-va).to_track_quat('Z','Y').to_euler();o.data.materials.append(M[material]);o['group']=group;return o
# The HCMT's recognisable tall, raked cab is a lofted surface, not a box.
def meshobj(name,verts,faces,material,group='car',smooth=False):
 mesh=bpy.data.meshes.new(name);mesh.from_pydata([xyz(v) for v in verts],[],faces);mesh.update()
 o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);o.data.materials.append(M[material]);o['group']=group
 if smooth:
  for p in mesh.polygons:p.use_smooth=True
 return o
profile=[(-1.32,.99),(-1.48,1.2),(-1.48,3.18),(-1.40,3.48),(-1.18,3.70),(-.72,3.81),(.72,3.81),(1.18,3.70),(1.40,3.48),(1.48,3.18),(1.48,1.2),(1.32,.99)]
def shell(name,start,end,group):
 n=len(profile);verts=[(x,y,z) for z in [start,end] for x,y in profile]
 faces=[(j,(j+1)%n,n+(j+1)%n,n+j) for j in range(n)]+[tuple(range(n-1,-1,-1)),tuple(n+j for j in range(n))]
 return meshobj(name,verts,faces,'brushed_aluminium',group,True)
shell('HCMT_carbody',-8.1,11.13,'car')
shell('trailer_extension',-11.13,-8.1,'trailer')
box('trailer_front_gangway',(0,2.20,-11.3),(1.25,2.3,.34),'rubber',.10,'trailer')
# Smoothly varying front silhouette, traced from the supplied HCMT photograph.
def nose_values(y):
 pts=[(.82,1.09,-11.02),(1.10,1.30,-11.24),(1.48,1.39,-11.36),(1.98,1.34,-11.30),(2.50,1.25,-10.94),(3.02,1.13,-10.52),(3.50,1.0,-10.10),(3.80,.73,-9.78)]
 for i in range(len(pts)-1):
  a,b=pts[i],pts[i+1]
  if y<=b[0]:
   t=max(0,(y-a[0])/(b[0]-a[0]));
   return a[1]+(b[1]-a[1])*t,a[2]+(b[2]-a[2])*t
 return pts[-1][1],pts[-1][2]
def front_surface(name,lo,hi,width,material,offset=0):
 verts=[];rows=18;cols=20
 for j in range(rows+1):
  y=lo+(hi-lo)*j/rows;w,z=nose_values(y)
  for i in range(cols+1):
   u=-1+2*i/cols;x=u*w*width
   verts.append((x,y,z+.20*(x/w)**2-offset))
 faces=[(j*(cols+1)+i,j*(cols+1)+i+1,(j+1)*(cols+1)+i+1,(j+1)*(cols+1)+i) for j in range(rows) for i in range(cols)]
 return meshobj(name,verts,faces,material,'nose',True)
front_surface('HCMT_white_nose_rim',.82,3.80,1,'ceramic_white')
front_surface('HCMT_dark_nose',.84,3.76,.89,'nose_graphite',.012)
front_surface('HCMT_tall_windscreen',2.02,3.51,.79,'window_glass',.025)
# Characteristic broad-top, rounded-bottom yellow identification panel.
verts=[];rows=10;cols=16
for j in range(rows+1):
 y=1.40+.56*j/rows;w,z=nose_values(y);u=j/rows;half=.56+.30*min(1,u*2)
 for i in range(cols+1):
  k=-1+2*i/cols;verts.append((k*half,y,z+.20*(k*half/w)**2-.035))
faces=[(j*(cols+1)+i,j*(cols+1)+i+1,(j+1)*(cols+1)+i+1,(j+1)*(cols+1)+i) for j in range(rows) for i in range(cols)]
meshobj('HCMT_yellow_panel',verts,faces,'safety_yellow','nose',True)
# Blue side wrap and its geometric livery are real geometry with shared colours.
import random
random.seed(12)
for side in [-1,1]:
 verts=[];rows=14;cols=4
 for j in range(rows+1):
  y=.99+(3.77-.99)*j/rows;w,z=nose_values(y)
  for i in range(cols+1):
   u=i/cols;backwidth=1.48 if y<3.18 else 1.48-(y-3.18)*1.02;verts.append((side*(w+(backwidth-w)*u),y,(z+.20)*(1-u)+(-8.09)*u))
 faces=[(j*(cols+1)+i,j*(cols+1)+i+1,(j+1)*(cols+1)+i+1,(j+1)*(cols+1)+i) for j in range(rows) for i in range(cols)]
 meshobj('HCMT_blue_cab_side',verts,faces,'livery_cyan','nose',True)
 # Large triangulated wrap panels follow the same curved side surface.
 def on_side(u,y):
  w,z=nose_values(y);backwidth=1.48 if y<3.18 else 1.48-(y-3.18)*1.02
  return (side*(w+(backwidth-w)*u+.012),y,(z+.20)*(1-u)+(-8.09)*u)
 livery_uv=[(0,1.04),(.48,1.04),(1,1.04),(0,1.78),(.58,1.65),(1,1.82),(0,2.67),(.44,2.48),(1,2.77),(0,3.42),(.61,3.38),(1,3.42)]
 for j in range(3):
  for k in range(2):
   a=j*3+k;b=a+1;c=a+4;d=a+3
   for tri in [(a,b,c),(a,c,d)]:
    # Tessellate in UV so each livery panel follows the rounded shell without clipping.
    av,bv,cv=[livery_uv[n] for n in tri];pv=[];pf=[];lookup={};steps=8
    for r in range(steps+1):
     for q in range(steps+1-r):
      aa=r/steps;bb=q/steps;cc=1-aa-bb;lookup[(r,q)]=len(pv);pv.append(on_side(av[0]*aa+bv[0]*bb+cv[0]*cc,av[1]*aa+bv[1]*bb+cv[1]*cc))
    for r in range(steps):
     for q in range(steps-r):
      pf.append((lookup[(r,q)],lookup[(r+1,q)],lookup[(r,q+1)]))
      if q<steps-r-1:pf.append((lookup[(r+1,q)],lookup[(r+1,q+1)],lookup[(r,q+1)]))
    meshobj('nose_wrap_triangle',pv,pf,random.choice(['livery_cyan','livery_cyan','livery_sky','livery_mid','livery_navy']),'nose',True)
 # Polygon wrap on flat cabin-side panel, following the train's real identity.
 zs=[-8.08,-7.60,-7.12,-6.55];ys=[1.02,1.72,2.7,3.38]
 for j in range(len(ys)-1):
  for k in range(len(zs)-1):
   corners=[(side*1.495,ys[j],zs[k]),(side*1.495,ys[j],zs[k+1]),(side*1.495,ys[j+1],zs[k+1]),(side*1.495,ys[j+1],zs[k])]
   for tri in [(0,1,2),(0,2,3)]:meshobj('cab_livery_polygon',[corners[n] for n in tri],[(0,1,2)],random.choice(['livery_cyan','livery_sky','livery_mid','livery_navy']),'nose')
 # Driver's side door and tall narrow front quarterlight.
 box('driver_door_reveal',(side*1.513,2.09,-8.0),(.033,2.12,.61),'rubber',.075,'nose')
 box('driver_door',(side*1.535,2.09,-8.0),(.029,2.04,.54),'livery_cyan',.07,'nose')
 box('driver_door_glass',(side*1.558,2.75,-8.0),(.018,.80,.37),'window_glass',.075,'nose')
 box('cab_quarterlight',(side*1.36,2.76,-9.18),(.03,.86,.30),'window_glass',.10,'nose')
 box('door_handle',(side*1.569,1.92,-8.23),(.028,.19,.025),'bogie_steel',.01,'nose')
 # Continuous blue-and-white roofline is a defining HCMT detail.
 box('white_roofline',(side*1.429,3.46,1.49),(.06,.29,19.2),'ceramic_white',.03)
 box('blue_roofline',(side*1.477,3.38,1.49),(.024,.18,19.2),'livery_cyan',.016)
 # Silver sidewalls separate each bank of rounded rectangular windows.
 for z in [-7.33,-3.65,-1.85,2.8,4.55,9.35]:
  box('window_gasket',(side*1.491,2.64,z),(.032,1.06,1.55),'rubber',.085,'trailer' if z==-7.33 else 'car')
  box('passenger_window',(side*1.516,2.64,z),(.025,.95,1.41),'window_glass',.075,'trailer' if z==-7.33 else 'car')
  box('window_divider',(side*1.535,2.65,z),(.012,.92,.037),'rubber',.004,'trailer' if z==-7.33 else 'car')
 for z in [-5.62,.57,7.07]:
  box('door_recess',(side*1.505,2.11,z),(.028,2.15,1.57),'rubber',.075)
  for leaf in [-1,1]:
   group=f'door_{"L" if side<0 else "R"}_{z}_{"minus" if leaf<0 else "plus"}'
   box(group,(side*1.54,2.12,z+leaf*.363),(.048,2.08,.71),'livery_mid',.045,group)
   box('door_window',(side*1.575,2.69,z+leaf*.363),(.025,.85,.51),'window_glass',.055,group)
   box('door_edge',(side*1.583,2.12,z+leaf*.019),(.016,2.02,.026),'rubber',.002,group)
  box('door_step',(side*1.52,1.05,z),(.13,.09,1.67),'bogie_steel',.02)
  cyl('door_request',(side*1.59,2.05,z+.95),.045,.02,'safety_yellow')
 # Narrow polygon strips around intermediate doorway, as on the source photo.
 for centre in [.57,9.5]:
  for j in range(3):
   z=centre+.98;y=1.10+j*.73
   meshobj('door_livery_polygon',[(side*1.513,y,z),(side*1.513,y+.73,z),(side*1.513,y+.38,z+.53)],[(0,1,2)],['livery_cyan','livery_sky','livery_mid'][j])
# Close the rounded roof over the sloped cab, flush with the passenger roof.
meshobj('HCMT_cab_roof',[(-.73,3.80,-9.78),(.73,3.80,-9.78),(.85,3.80,-8.03),(-.85,3.80,-8.03)],[(0,1,2,3)],'ceramic_white','nose',True)
for x in [-1,1]:
 # Low paired round headlights, not the rectangular units of the old model.
 o=cyl('HCMT_headlamp_recess',(x*.98,1.01,-11.15),.09,.045,'rubber',axis='z',group='nose');o.rotation_euler[0]=math.pi/2
 o=cyl('HCMT_headlamp',(x*.98,1.01,-11.18),.051,.05,'headlight',axis='z',group='nose');o.rotation_euler[0]=math.pi/2
# Windshield wipers conform to the rake.
beam('windscreen_wiper',(-.54,2.1,-11.265),(-.32,3.05,-10.54),.012,'rubber','nose')
beam('windscreen_wiper',(.43,2.1,-11.265),(.65,2.98,-10.60),.012,'rubber','nose')
box('coupler',(0,.78,-11.35),(.32,.23,.35),'bogie_steel',.04)
# Metro wordmark/cab destination are editable source text, converted for delivery.
def lettering(name,text,pos,size,rotation,material,group):
 curve=bpy.data.curves.new(name,'FONT');curve.body=text;curve.align_x='CENTER';curve.align_y='CENTER';curve.size=size;curve.extrude=.0004
 o=bpy.data.objects.new(name,curve);bpy.context.collection.objects.link(o);o.location=xyz(pos);o.rotation_euler=rotation;o.data.materials.append(M[material]);o['group']=group
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH')
lettering('PTV_nose','PT>',(0,1.72,-11.401),.15,(math.pi/2,0,math.pi),'rubber','nose')
for side in [-1,1]:
 lettering('Metro_wordmark','METRO',(side*1.522,2.30,-7.35),.18,(math.pi/2,0,side*math.pi/2),'ceramic_white','nose')
 # Two slender peaks evoke the outline M identifier in the supplied reference.
 points=[(-7.7,2.52),(-7.61,3.05),(-7.39,2.53),(-7.17,3.05),(-7.08,2.52)]
 for a,b in zip(points,points[1:]):beam('Metro_outline',(side*1.523,a[1],a[0]),(side*1.523,b[1],b[0]),.009,'ceramic_white','nose')
box('underframe',(0,.89,0),(2.6,.36,20.2),'rubber',.08)
for z in [-7.65,7.65]:
 box('bogie_frame',(0,.48,z),(2.06,.3,2.65),'bogie_steel',.07)
 for dz in [-.95,.95]:
  beam('axle',(-.9,.43,z+dz),(.9,.43,z+dz),.09,'bogie_steel')
  for side in [-1,1]:
   cyl('wheel',(side*.8,.43,z+dz),.43,.16,'bogie_steel');cyl('wheel_hub',(side*.90,.43,z+dz),.18,.075,'rubber')
   cyl('suspension',(side*1.08,.67,z+dz),.15,.24,'rubber',axis='y')
for z in [-3.4,3.4]:
 box('HVAC_module',(0,3.86,z),(2.04,.32,2.7),'brushed_aluminium',.09)
 for zz in [-.72,0,.72]:box('roof_grille',(0,4.025,z+zz),(1.7,.012,.30),'bogie_steel',.01)
# Compact raised pantograph, all under 4.9m overall.
box('pantograph_base',(0,3.93,7.7),(1.2,.15,1.3),'bogie_steel',.04)
for side in [-1,1]:
 beam('pantograph_lower',(side*.36,4,7.4),(side*.36,4.44,8.25),.025,'bogie_steel')
 beam('pantograph_upper',(side*.36,4.44,8.25),(side*.36,4.84,7.6),.02,'bogie_steel')
beam('contact_shoe',(-.85,4.85,7.6),(.85,4.85,7.6),.025,'bogie_steel')
for z in [10.8]:box('gangway',(0,2.21,z+.45),(1.30,2.2,.50),'rubber',.09)
# Camera-local cab: keep clear forward vision. Coordinate origin is the driver's eye.
box('dashboard',(0,-1.09,-1.25),(3.05,.31,1.04),'cab_graphite',.10,'cab')
box('dashboard_lip',(0,-.91,-1.60),(3.02,.10,.20),'cab_slate',.04,'cab')
for x in [-1.38,1.38]:
 beam('windscreen_pillar',(x,-1.05,-1.77),(x*.88,1.15,-1.8),.06,'cab_graphite','cab')
box('cab_header',(0,1.18,-1.81),(2.6,.14,.15),'cab_graphite',.04,'cab')
for x in [-.60,.40]:
 box('instrument_bezel',(x,-.88,-1.12),(.66,.085,.38),'rubber',.035,'cab')
 box('instrument_screen',(x,-.832,-1.13),(.54,.012,.27),'screen',.016,'cab')
 for z in [-1.22,-1.13,-1.04]:box('screen_line',(x,-.821,z),(.42,.004,.007),'ceramic_white',0,'cab')
for x in [.89,1.06,1.23]:cyl('desk_button',(x,-.865,-1.04),.035,.04,'green_led' if x<1 else 'safety_yellow',axis='y',group='cab')
box('controller_mount',(-1.06,-.85,-1.04),(.24,.1,.27),'rubber',.035,'cab')
beam('controller_lever',(-1.06,-.83,-1.04),(-1.06,-.60,-1.11),.022,'bogie_steel','cab')
box('controller_grip',(-1.06,-.60,-1.11),(.18,.065,.075),'cab_graphite',.025,'cab')
beam('resting_wiper',(.58,-.82,-1.85),(.93,-.42,-1.85),.007,'rubber','cab')
# Lift the desk into the lower 20 percent of a 60-degree vertical field of view.
for obj in bpy.context.scene.objects:
 if obj.get('group')=='cab' and obj.name.split('.')[0] not in ['windscreen_pillar','cab_header','resting_wiper']:obj.location.z+=.28
# Join by material for static meshes; each articulated leaf keeps a stable root.
bpy.ops.object.select_all(action='DESELECT')
allmeshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];groups={}
for o in allmeshes:
 g=o.get('group')
 if o.name.split('.')[0] in ['nose_fascia','lower_nose','windscreen_gasket','windscreen','destination_housing','lamp_recess','lamp_lens','windscreen_wiper']:g='nose'
 key=(g,o.data.materials[0].name) if g in ['car','cab','nose','trailer'] else (g,'leaf')
 groups.setdefault(key,[]).append(o)
for (g,m),objs in groups.items():
 bpy.ops.object.select_all(action='DESELECT')
 for o in objs:o.select_set(True)
 bpy.context.view_layer.objects.active=objs[0];bpy.ops.object.join();o=bpy.context.object;o.name=f'{g}_{m}';o['group']=g
 # Door pivot remains local in metre units; translations animate along Three Z.
 bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR');bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
# Separate collection for editable cabinet and car.
for name in ['Exterior','Driver cab']:
 col=bpy.data.collections.new(name);bpy.context.scene.collection.children.link(col)
for o in list(bpy.context.scene.objects):
 target=bpy.data.collections['Driver cab' if o.get('group')=='cab' else 'Exterior']
 for c in list(o.users_collection):c.objects.unlink(o)
 target.objects.link(o)
for kind,path in [('car','melbourne-commuter.glb'),('cab','driver-cab.glb')]:
 bpy.ops.object.select_all(action='DESELECT')
 for o in bpy.context.scene.objects:o.select_set((o.get('group')=='cab')==(kind=='cab'))
 bpy.ops.export_scene.gltf(filepath=os.path.join(ROOT,'public/models',path),export_format='GLB',use_selection=True,export_yup=True,export_animations=False,export_cameras=False,export_lights=False,export_extras=True)
# Product render: source .blend has studio camera/lights, excluded from GLBs.
for o in bpy.data.collections['Driver cab'].objects:o.hide_render=True
for o in bpy.data.collections['Exterior'].objects:
 if o.get('group')=='trailer':o.hide_render=True
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.03));ground=bpy.context.object;ground.name='Studio ground';ground.data.materials.append(M['cab_graphite'])
world=bpy.context.scene.world or bpy.data.worlds.new('Studio');bpy.context.scene.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.19,.24,.3,1);world.node_tree.nodes['Background'].inputs[1].default_value=.6
for loc,power,size in [((7,14,15),2400,9),((-9,5,10),1900,8),((0,-12,13),2600,7)]:
 bpy.ops.object.light_add(type='AREA',location=loc);bpy.context.object.data.energy=power;bpy.context.object.data.shape='DISK';bpy.context.object.data.size=size;bpy.context.object.rotation_euler=(Vector((0,0,1.8))-bpy.context.object.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(23,30,9));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,1.8))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=30;bpy.context.scene.camera=cam
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=24;scene.render.resolution_x=1600;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.filepath=os.path.join(ROOT,'artifacts/train-studio.png')
scene.view_settings.view_transform='AgX';bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,'assets/source/melbourne-commuter.blend'));bpy.ops.render.render(write_still=True)
print('TRAIN_ASSETS_COMPLETE')
