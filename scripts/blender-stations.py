"""Reference-authored Flinders Street main station landmark.
Blender -b --python scripts/blender-stations.py
Coordinates are game metres: x east, y height, z toward platforms/south.
"""
import bpy, math, os
from mathutils import Vector
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bpy.context.preferences.filepaths.save_version=0
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
colors={'brick':(.43,.19,.12,1),'ochre':(.78,.59,.28,1),'lightstone':(.88,.74,.43,1),'copper':(.20,.34,.29,1),'glass':(.055,.095,.088,1),'iron':(.18,.23,.21,1),'clock':(.87,.84,.70,1),'roof':(.29,.32,.30,1)}
# Material factors are linear; reference paint swatches above are sRGB.
colors={k:tuple((c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4) for c in rgba[:3])+(1,) for k,rgba in colors.items()}
batches={k:[[],[]] for k in colors}
def mesh(kind,verts,faces):
 v,f=batches[kind];offset=len(v);v.extend([(x,-z,y) for x,y,z in verts]);f.extend([tuple(offset+i for i in face) for face in faces])
def box(kind,x,y,z,w,h,d):
 verts=[(x+sx*w/2,y+sy*h/2,z+sz*d/2) for sx,sy,sz in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
 mesh(kind,verts,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(3,7,6,2),(0,4,7,3),(1,2,6,5)])
def ring(kind,x,y,z,r0,r1,depth,steps=24,start=0,end=math.tau):
 verts=[]
 for zz in [-depth/2,depth/2]:
  for i in range(steps+1):
   a=start+(end-start)*i/steps
   for r in [r0,r1]:verts.append((x+r*math.cos(a),y+r*math.sin(a),z+zz))
 faces=[];offset=(steps+1)*2
 for i in range(steps):
  q=i*2;faces.extend([(q,q+1,q+3,q+2),(q+offset+2,q+offset+3,q+offset+1,q+offset),(q,q+2,q+offset+2,q+offset),(q+1,q+offset+1,q+offset+3,q+3)])
 mesh(kind,verts,faces)
def arch_window(x,y,z,width,height):
 # Sills, recessed glazing, tall arched render heads and fine mullions.
 r=width/2;box('ochre',x,y-.1,z,width+.55,height+.2,.25);box('glass',x,y,z+.18,width,height,.12)
 ring('lightstone',x,y+height/2-r,z+.3,r,r+.22,.20,12,0,math.pi)
 box('ochre',x,y+height/2,z+.29,width,.24,.3)
 box('iron',x,y,z+.30,.07,height,.06);box('iron',x,y,z+.30,width,.07,.06)
 box('lightstone',x,y-height/2-.16,z+.38,width+.5,.21,.52)
def dome(x,y,z,r,height):
 verts=[];steps=48;rows=16
 for j in range(rows+1):
  a=j/rows*math.pi/2
  rr=r*math.cos(a)*(1+.06*math.sin(a*2))
  for i in range(steps):
   phi=i/steps*math.tau;verts.append((x+rr*math.cos(phi),y+height*math.sin(a),z+rr*math.sin(phi)))
 faces=[]
 for j in range(rows):
  for i in range(steps):faces.append((j*steps+i,j*steps+(i+1)%steps,(j+1)*steps+(i+1)%steps,(j+1)*steps+i))
 mesh('copper',verts,faces)
 # Copper seams remain visible from elevated exterior camera.
 for i in range(16):
  phi=i/16*math.tau
  for j in range(12):
   a=(j+.5)/12*math.pi/2;rr=r*math.cos(a);box('iron',x+rr*math.cos(phi),y+height*math.sin(a),z+rr*math.sin(phi),.07,.25,.07)
def cylinder(kind,x,y,z,r,h,n=24):
 verts=[(x+r*math.cos(i/n*math.tau),y+yy*h/2,z+r*math.sin(i/n*math.tau)) for yy in [-1,1] for i in range(n)]
 faces=[tuple(range(n-1,-1,-1)),tuple(range(n,n*2))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)];mesh(kind,verts,faces)
def clock(x,y,z,r):
 ring('ochre',x,y,z,r,r+.3,.22,40);ring('clock',x,y,z,0,r,.08,40)
 for i in range(12):
  a=i/12*math.tau;box('iron',x+math.sin(a)*r*.83,y+math.cos(a)*r*.83,z+.08,.10,.24,.07)
 box('iron',x,y+r*.31,z+.14,.12,r*.62,.08);box('iron',x+r*.25,y,z+.15,r*.50,.10,.08)

# Long four-level redbrick elevation, repeated render pilasters and cornices.
box('brick',-147,13,0,294,26,25)
box('ochre',-147,3.5,0,295,7,25.4)
for y,h,projection in [(7,.65,.9),(8,.25,.5),(14,.40,.7),(20.9,.42,.7),(25,.8,1.1),(26,.3,1.4)]:
 for side in [-1,1]:box('ochre',-147,y,side*(12.5+projection/2),295,h,projection)
for x in range(-290,-10,6):
 for side in [-1,1]:
  z=side*12.8;box('ochre',x,16,z,.62,19,.65)
  for yy in [10.5,16.7,22.5]:
   # Window details face outward on both the street and platform elevations.
   if side==1:arch_window(x+3,yy,13,1.8,3.4)
   else:
    before={k:len(v[0]) for k,v in batches.items()};arch_window(x+3,yy,13,1.8,3.4)
    for k,(verts,faces) in batches.items():
     for i in range(before[k],len(verts)):
      bx,by,bz=verts[i];verts[i]=(bx,-by,bz)
  box('lightstone',x,25.8,side*13.2,1.05,.6,.9)
  box('glass',x+3,4.5,side*12.78,3,5,.13)
  if side==1:ring('ochre',x+3,6.5,13.1,1.5,1.85,.4,16,0,math.pi)
# Low parapet, dark pitched roof and brick chimney pots.
box('roof',-147,26.4,0,291,.35,24)
for x in range(-283,-20,24):
 box('brick',x,28.2,0,1.8,4,1.9);box('ochre',x,30.1,0,2.1,.3,2.2)
 for dx in [-.45,.45]:cylinder('ochre',x+dx,30.8,0,.23,1.1,8)
# Elizabeth Street clock tower and entry pavilion.
box('ochre',-166,16,0,16,32,29)
for side in [-1,1]:
 for xx in [-171,-161]:box('brick',xx,16,side*14.65,2,18,.25)
 for y in [8,22,30]:box('lightstone',-166,y,side*14.8,17,.6,1)
box('ochre',-166,35,0,11,12,12)
for x in [-171,-161]:
 for z in [-5,5]:box('lightstone',x,35,z,1,13,1)
clock(-166,35,6.14,3.0);clock(-166,35,-6.14,3.0)
box('lightstone',-166,41.3,0,13,1,14);dome(-166,42,0,6.5,5);cylinder('copper',-166,48,0,.9,3,16)
# Main eastern dome pavilion; more ornate render than the long brick wing.
box('ochre',-1,14,0,30,28,28)
for side in [-1,1]:
 box('lightstone',-1,27.8,side*14.2,31,1.2,1)
 for x in [-13,-9,7,11]:box('lightstone',x,16,side*14.3,1,21,.6)
 for x in [-6,0,6]:
  if side==1:arch_window(x,22,14.3,3.2,5)
  else:box('glass',x,22,-14.3,3.2,5,.1)
box('glass',-1,8,14.4,13,13,.2);ring('lightstone',-1,10.5,14.7,6.5,7.2,.65,24,0,math.pi)
for x in [-8.5,6.5]:box('lightstone',x,7,14.6,1.2,14,1)
for i in range(9):clock(-7.4+i*1.6,11.5,15.2,.56)
cylinder('ochre',-1,29.4,0,12,3.4,48);dome(-1,31,0,12.2,10.8)
cylinder('copper',-1,44,0,1.3,4,20);dome(-1,46,0,1.6,1.1);cylinder('iron',-1,48,0,.10,4,8)
# Finial cupolas flank the main entry.
for x in [-14,12]:
 cylinder('ochre',x,29,13,1.8,4,16);dome(x,31,13,2,2.1);cylinder('iron',x,34,13,.10,2,8)
# Platform-side corrugated verandah, ochre scalloped valance and cast-iron posts.
box('roof',-145,13.5,20,288,.18,14)
for x in range(-288,-5,4):
 box('lightstone',x,13.26,27,4,.6,.15)
 for dx in [i*.35 for i in range(12)]:ring('lightstone',x-2+dx,12.9,27,.06,.17,.13,6,math.pi,math.tau)
for x in range(-284,-5,12):
 cylinder('iron',x,10.5,25.8,.13,6,8);box('ochre',x,12.5,25.8,.5,.4,.5)
 box('iron',x,13,20,.12,.15,13)
# Material groups become only eight meshes/draw calls.
for kind,(verts,faces) in batches.items():
 data=bpy.data.meshes.new(kind);data.from_pydata(verts,[],faces);data.update();obj=bpy.data.objects.new('FSS_'+kind,data);bpy.context.collection.objects.link(obj)
 mat=bpy.data.materials.new(kind);mat.diffuse_color=colors[kind];mat.use_nodes=True;p=mat.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=colors[kind];p.inputs['Roughness'].default_value=.72 if kind not in ['copper','glass','iron'] else .38;p.inputs['Metallic'].default_value=.45 if kind in ['copper','iron'] else .08;data.materials.append(mat)
 # Smooth dome/curved elements while retaining hard architectural edges.
 for poly in data.polygons:poly.use_smooth=kind=='copper'
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,'assets/source/stations/flinders-street.blend'))
bpy.ops.export_scene.gltf(filepath=os.path.join(ROOT,'public/models/stations-flinders.glb'),export_format='GLB',export_apply=True,export_cameras=False,export_lights=False)
# Repeatable real-geometry review image, independent of the game renderer.
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32
scene.world.color=(.35,.35,.35)
bpy.ops.object.light_add(type='AREA',location=(-130,-100,140));bpy.context.object.data.energy=1800000;bpy.context.object.data.shape='DISK';bpy.context.object.data.size=200
bpy.ops.object.camera_add(location=(50,-230,105));camera=bpy.context.object;target=Vector((-100,0,18));camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=360;scene.camera=camera
scene.render.resolution_x=1800;scene.render.resolution_y=1000;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.filepath=os.path.join(ROOT,'assets/source/stations/flinders-review.png');bpy.ops.render.render(write_still=True)
