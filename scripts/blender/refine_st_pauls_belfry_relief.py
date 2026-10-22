"""Authored lancet relief on existing tower faces; retain silhouette and source bounds."""
import bpy,math,json,hashlib
from pathlib import Path
from mathutils import Vector
r=Path(bpy.data.filepath).resolve().parents[3];s=bpy.context.scene;name='St Pauls Cathedral - authored belfry lancet relief';source=bpy.data.objects['St Pauls Cathedral - authored three spires'];vs=[];fs=[];mi=[];bays=[]
def face(points,material):
 k=len(vs);vs.extend(tuple(q) for q in points);fs.append(tuple(range(k,k+len(points))));mi.append(material)
def strip(a,b,width,normal,material=0):
 delta=b-a;side=normal.cross(delta).normalized()*width/2;face([a-side,b-side,b+side,a+side],material)
for p in source.data.polygons:
 if abs(p.normal.z)>.05 or p.material_index!=0:continue
 cs=[source.matrix_world@source.data.vertices[i].co for i in p.vertices];bottom=min(q.z for q in cs);top=max(q.z for q in cs);low=sorted([q for q in cs if abs(q.z-bottom)<.001],key=lambda q:(q.x,q.y))
 if len(low)!=2 or top-bottom<5:continue
 a,b=low;length=(b-a).length
 if length<4:continue
 tangent=(b-a).normalized();normal=(source.matrix_world.to_3x3()@p.normal).normalized();count=2 if length<13 else 3;width=min(1.8,length/(count*2.4));height=min(9,(top-bottom)*.40);z0=top-height-min(2.4,(top-bottom)*.15)
 for j in range(count):
  centre=a+tangent*(length*(j+1)/(count+1));centre.z=z0;centre+=normal*.045
  pts=[centre-tangent*width/2,centre+tangent*width/2,centre+tangent*width/2+Vector((0,0,height*.72)),centre+Vector((0,0,height)),centre-tangent*width/2+Vector((0,0,height*.72))]
  # Dark blind/recessed relief; no measured glazing or opening location claimed.
  if (pts[1]-pts[0]).cross(pts[2]-pts[0]).dot(normal)<0:pts.reverse()
  face(pts,1)
  for aa,bb in zip(pts,pts[1:]+pts[:1]):strip(aa+normal*.025,bb+normal*.025,.16,normal)
  strip(centre+normal*.032,centre+Vector((0,0,height*.76))+normal*.032,.09,normal)
  bays.append({'tower_face':p.index,'width':width,'height':height,'base_z':z0})
 # Horizontal stone stringcourse adds shadow below authored belfry zone.
 c=a.copy();d=b.copy();c.z=d.z=z0-.4;strip(c+normal*.12,d+normal*.12,.22,normal)
assert bays
m=bpy.data.meshes.new(name);m.from_pydata(vs,[],fs);m.materials.append(bpy.data.materials['Authored St Pauls warm masonry']);dark=bpy.data.materials.get('Authored St Pauls belfry recess - assumed') or bpy.data.materials.new('Authored St Pauls belfry recess - assumed');dark.use_nodes=True;bs=dark.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.045,.055,.052,1);bs.inputs['Roughness'].default_value=.85;m.materials.append(dark)
for p,i in zip(m.polygons,mi):p.material_index=i
m.update();o=bpy.data.objects.new(name,m);source.users_collection[0].objects.link(o);limits='Authored pointed lancet blind/recess relief, stone surrounds, mullions and stringcourses on existing tower faces. Counts, placement, dimensions and recess finish approximate, not measured current openings. Source tower geometry and silhouette unchanged. No photographic textures.';o['limits']=limits;o['reference']='https://ausmed.arts.uwa.edu.au/items/show/752';o['source_ids']='27583,27587';fingerprint=hashlib.sha256(json.dumps({'vertices':[list(v.co) for v in source.data.vertices],'faces':[list(p.vertices) for p in source.data.polygons],'materials':[p.material_index for p in source.data.polygons]}).encode()).hexdigest();a={'source_geometry_sha256':fingerprint,'bays':bays,'faces':len(fs),'limits':limits,'reference':o['reference']};(r/'docs/st-pauls-belfry-relief-trial-audit.json').write_text(json.dumps(a,indent=2)+'\n');print('BELFRY_RELIEF',len(bays),len(fs),flush=True)
if globals().get('SAVE_BELFRY_PASS'):
 s['st_pauls_belfry_relief_revision']='authored-lancet-relief-v1';(r/'docs/st-pauls-belfry-relief-audit.json').write_text(json.dumps(a,indent=2)+'\n');bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
else:
 code=(r/'scripts/blender/render_st_pauls_study.py').read_text().replace('bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)','scene.render.engine="CYCLES";scene.cycles.samples=24;scene.cycles.use_denoising=True').replace('observatory-st-pauls-study.png','observatory-st-pauls-belfry-trial.png');exec(compile(code,'render','exec'))
