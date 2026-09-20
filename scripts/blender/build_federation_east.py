"""Survey structure 816359 with an authored opening for the training railway.
Run after node scripts/export-blender-route.mjs.
The footprint is measured; cladding and the rail opening are interpretations.
"""
import bpy, bmesh, importlib.util, json, math, hashlib, sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('frontage',Path(__file__).with_name('build_viaduct_frontage.py'))
f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f)
f.reset_scene()
# Optional source structure lets the same surveyed-envelope treatment repair
# adjacent sections without maintaining divergent cladding/clearance logic.
structure_id=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else '816359'
source_sections={'816359':['16221','16222','16223'],'806667':['4607'],'805928':['37331','37332'],'805929':['17198','17199']}
ids=source_sections[structure_id];f.STRUCTURES[structure_id]={'objectIds':ids}
asset_name='federation-east' if structure_id=='816359' else 'federation-'+structure_id
source=ROOT/'public/data/buildings.json'
buildings=json.loads(source.read_text())['buildings']
# The shard footprint contains a sub-decimetre out-and-back survey spike.
# Remove consecutive near-duplicates before tessellation, preserving metre-scale geometry.
for section in buildings:
 if section['id'] not in ids:continue
 clean=[]
 for point in section['ring']:
  if not clean or math.dist(point,clean[-1])>.2:clean.append(point)
 if len(clean)>1 and math.dist(clean[0],clean[-1])<.2:clean.pop()
 section['ring']=clean
stone=f.material('sandstone',(.48,.40,.30),.91)
concrete=f.material('rail opening concrete',(.25,.26,.25),.96)
roof=f.material('zinc roof',(.28,.30,.30),.78,.12)
envelope,sections=f.union_sections(buildings,structure_id,(stone,concrete,roof))
route=json.loads(Path('/tmp/city-loop-clearance-route.json').read_text())
bounds=[p for section in sections for p in section['ring']]
x_min=min(p[0] for p in bounds)-20;x_max=max(p[0] for p in bounds)+20
z_min=min(p[1] for p in bounds)-20;z_max=max(p[1] for p in bounds)+20
# Keep a contiguous ribbon extending beyond the entire source building. Wide
# shoulders preserve adjacent railway context as well as the playable track.
route=[p for p in route if 5050<=p['distance']<=5520]
verts=[]
for i,p in enumerate(route):
 a=route[max(0,i-1)];b=route[min(len(route)-1,i+1)]
 dx=b['x']-a['x'];dz=b['z']-a['z'];length=math.hypot(dx,dz)
 nx=-dz/length;nz=dx/length
 for y in [-35,p['y']+7]:
  for side in [-1,1]:verts.append(f.game_to_blender(p['x']+nx*12*side,y,p['z']+nz*12*side))
faces=[(0,2,3,1)]
for i in range(len(route)-1):
 a=i*4;b=a+4
 faces.extend([(a,b,b+1,a+1),(a+2,a+3,b+3,b+2),(a,a+2,b+2,b),(a+1,b+1,b+3,a+3)])
a=(len(route)-1)*4;faces.append((a,a+1,a+3,a+2))
cutter=f.make_mesh_object('rail_clearance',verts,faces,concrete,'24m wide authored rail opening')
bpy.context.view_layer.objects.active=envelope
mod=envelope.modifiers.new('training_railway_opening','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.data.objects.remove(cutter,do_unlink=True)
# Also preserve the mapped scenery railway, not just the playable centreline.
context_cuts=0
for filename in ['corridor-source.json','loop-landscape-source.json']:
 data=json.loads((ROOT/'src/data'/filename).read_text())
 for feature in data['layers']['rails']['features']:
  if feature['properties'].get('feature_type_code')!='railway':continue
  lines=feature['geometry']['coordinates']
  if feature['geometry']['type']=='LineString':lines=[lines]
  count=min(4,max(1,float(feature['properties'].get('tracks_number_of') or 1)))
  half=count*2.1+3
  for line in lines:
   points=[((lon-144.9671)*87939,-(lat+37.8183)*111320) for lon,lat,*_ in line]
   for a,b in zip(points,points[1:]):
    if max(a[0],b[0])<x_min or min(a[0],b[0])>x_max or max(a[1],b[1])<z_min or min(a[1],b[1])>z_max:continue
    dx=b[0]-a[0];dz=b[1]-a[1];length=math.hypot(dx,dz)
    if length<.01:continue
    nx=-dz/length*half;nz=dx/length*half
    ring=[[a[0]+nx,a[1]+nz],[b[0]+nx,b[1]+nz],[b[0]-nx,b[1]-nz],[a[0]-nx,a[1]-nz]]
    heights=[min(route,key=lambda p:(p['x']-x)**2+(p['z']-z)**2)['y'] for x,z in [a,b]]
    cutter=f.ring_mesh('mapped_rail_opening',ring,-35,max(0,*heights)+7)
    bpy.context.view_layer.objects.active=envelope
    mod=envelope.modifiers.new('mapped_rail_opening','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
    bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True)
    context_cuts+=1
print('Mapped railway clearance sections',context_cuts)
# Triangular cladding follows each surveyed vertical face. Subdivision retains
# the silhouette and limits panels to around 6m, with narrow exposed seams.
mesh=envelope.data
bm=bmesh.new();bm.from_mesh(mesh)
bmesh.ops.triangulate(bm,faces=list(bm.faces))
for _ in range(6):
 long=[e for e in bm.edges if e.calc_length()>8]
 if not long:break
 bmesh.ops.subdivide_edges(bm,edges=long,cuts=1,use_grid_fill=True)
 bmesh.ops.triangulate(bm,faces=list(bm.faces))
bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00001)
bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=.00001)
bm.normal_update();bm.to_mesh(mesh);bm.free();mesh.validate();mesh.update()
from mathutils.bvhtree import BVHTree
bm=bmesh.new();bm.from_mesh(mesh);tree=BVHTree.FromBMesh(bm)
for i,p in enumerate(route):
 a=route[max(0,i-1)];b=route[min(len(route)-1,i+1)]
 dx=b['x']-a['x'];dz=b['z']-a['z'];length=math.hypot(dx,dz)
 for offset in [-3,0,3]:
  origin=Vector(f.game_to_blender(p['x']-dz/length*offset,p['y']+.1,p['z']+dx/length*offset))
  hit=tree.ray_cast(origin,Vector((0,0,1)),6.8)
  if hit[0] is not None:raise RuntimeError('Rail clearance failed at '+str(p['distance']))
bm.free()
materials=[f.material('sandstone light',(.57,.48,.36),.94),f.material('sandstone warm',(.44,.35,.26),.92),f.material('zinc panels',(.32,.35,.35),.72,.18),f.material('dark glazing',(.075,.13,.15),.3,.25)]
batches=[([],[]) for _ in materials]
for poly in mesh.polygons:
 poly.material_index=2 if poly.normal.z>.5 else 1
 if abs(poly.normal.z)>.05:continue
 original=[mesh.vertices[v].co.copy() for v in poly.vertices];pts=[]
 for a,b in zip(original,original[1:]+original[:1]):
  if a.z>=12:pts.append(a)
  if (a.z>=12)!=(b.z>=12):pts.append(a.lerp(b,(12-a.z)/(b.z-a.z)))
 if len(pts)<3:continue
 center=sum(pts,Vector())/len(pts)
 # Deterministic broad material fields, with modest variation within stone.
 kind=2 if poly.normal.y<-.5 else (3 if poly.normal.x<-.8 else int(abs(center.x+center.z)*7)%2)
 vs,fs=batches[kind];start=len(vs)
 vs.extend(tuple(center+(p-center)*.985+poly.normal*.025) for p in pts)
 fs.append(tuple(range(start,start+len(pts))))
for i,(v,fs) in enumerate(batches):f.make_mesh_object('federation_east_panels_'+str(i),v,fs,materials[i],'Authored triangular sandstone zinc and glass reference palette')
envelope['clearance_half_width']=12;envelope['clearance_above_rail']=7
envelope['adaptation']='Survey envelope cut by training alignment; not an architectural reconstruction'
if not mesh.polygons:raise RuntimeError('Empty replacement envelope: '+structure_id)
output=ROOT/('public/models/environment/'+asset_name+'.glb')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/('assets/source/environment/'+asset_name+'.blend')))
bpy.ops.export_scene.gltf(filepath=str(output),export_format='GLB',export_yup=True,export_extras=True,export_animations=False)
manifest={'structureId':structure_id,'objectIds':ids,'geometrySource':f.SOURCE_URL,'license':'CC BY 4.0','reference':'https://fedsquare.com/history-design','sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'clearance':{'halfWidthMetres':12,'heightAboveTrainingRailMetres':7,'sampleSpacingMetres':2},'limitations':'Federation Square area survey structure; exact tenancy not established. Prepared relative survey heights preserved. Triangular cladding palette and railway opening are authored interpretations, not measured facade or engineering drawings. The training track elevation is approximate.','triangles':sum(len(o.data.loop_triangles) for o in bpy.data.objects if o.type=='MESH')}
(ROOT/('public/models/environment/'+asset_name+'.json')).write_text(json.dumps(manifest,indent=2)+'\n')
print('Exported',output,output.stat().st_size)
