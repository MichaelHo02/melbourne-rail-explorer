"""Diagnostic only: no scene save. Requires temporary captured OBJ and section map.
See walkthrough for prerequisites. Geometry filters and4.1m datum offset authored.
"""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
sections=json.loads(Path('/tmp/federation-datum-sections.json').read_text());byid={p['id']:p for p in sections};report={}
def inside(x,y,r):
 a=False
 for i,p in enumerate(r):
  q=r[i-1]
  if (p[1]>y)!=(q[1]>y) and x<(q[0]-p[0])*(y-p[1])/(q[1]-p[1])+p[0]:a=not a
 return a
def dist(x,y,r):
 best=1e9
 for i,a in enumerate(r):
  b=r[i-1];dx=b[0]-a[0];dy=b[1]-a[1];den=dx*dx+dy*dy;t=max(0,min(1,((x-a[0])*dx+(y-a[1])*dy)/den)) if den else 0;best=min(best,math.hypot(x-a[0]-t*dx,y-a[1]-t*dy))
 return best
for p in sections:
 o=bpy.data.objects.get('survey_'+p['id'])
 if o:o.location.z+=p['offset'];report[o.name]=len(o.data.vertices)
labels=['Authored grouped window bays - varied low rise','Authored low rise sill and lintel bands','Authored roof edge cornices','Authored rooftop equipment - illustrative','Continuous surveyed roofs - authored finishes','Authored short low-rise window bays','Federation Square - authored triangular cladding']
for name in labels:
 o=bpy.data.objects.get(name)
 if not o or o.type!='MESH':continue
 m=o.data;attrib=m.attributes.get('source_section');changes={};conflicts=set();selected_faces=set()
 for f in m.polygons:
  p=byid.get(str(attrib.data[f.index].value)) if attrib else None
  if not p:
   v=f.center
   if not 35<v.x<320 or not -60<v.y<155:continue
   choices=[p for p in sections if p['id']!='20246' and p['base']-2<v.z<p['base']+p['height']+2 and (inside(v.x,v.y,p['ring']) or dist(v.x,v.y,p['ring'])<.4)]
   if not choices:continue
   p=min(choices,key=lambda p:abs(v.z-(p['base']+p['height'])))
  selected_faces.add(f.index)
  for j in f.vertices:
   if j in changes and abs(changes[j]-p['offset'])>.01:conflicts.add(j)
   changes[j]=p['offset']
 assert not conflicts,(name,len(conflicts))
 # A selected vertex must not move any unselected face of this merged mesh.
 shared=[f.index for f in m.polygons if f.index not in selected_faces and any(j in changes for j in f.vertices)]
 assert not shared,(name,"selected vertices belong to unselected faces",len(shared))
 print("OWNERSHIP_CLOSED",name,len(selected_faces),len(changes),flush=True)
 for j,d in changes.items():m.vertices[j].co.z+=d
 m.update();report[name]=len(changes)
for name in ['Federation Square - authored gable roof profiles','Federation Square - authored gable edge trim','Federation Square - authored zinc seams']:
 o=bpy.data.objects.get(name)
 if o:o.location.z+=4;report[name]='whole object +4m'

# Remove flat authored plaza only in this unsaved trial.
flat=bpy.data.objects['Federation Square - authored approximate sandstone plaza'];flat.hide_render=True
before=set(bpy.data.objects);bpy.ops.wm.obj_import(filepath='/tmp/federation-photomesh-2020-trial.obj',forward_axis='Y',up_axis='Z');terrain=next(o for o in bpy.data.objects if o not in before);terrain.name='Temporary captured Federation ground'
import bmesh
bm=bmesh.new();bm.from_mesh(terrain.data);remove=[]
for f in bm.faces:
 c=f.calc_center_median()
 protected=any(inside(c.x,c.y,p['ring']) or dist(c.x,c.y,p['ring'])<.3 for p in sections)
 if protected or c.z>13 or c.z<0 or c.y>115 or c.x<50 or c.x>310:remove.append(f)
bmesh.ops.delete(bm,geom=remove,context='FACES');bm.to_mesh(terrain.data);bm.free();terrain.data.update();terrain.data.materials.clear();terrain.data.materials.append(flat.data.materials[0])
for f in terrain.data.polygons:f.use_smooth=True
# Retain geometry around the square; no image textures, no source save.
s=bpy.context.scene;c=bpy.data.objects['02 Flinders precinct'];c.location=(110,-60,70);c.rotation_euler=(Vector((110,70,8))-c.location).to_track_quat('-Z','Y').to_euler();c.data.ortho_scale=200;s.camera=c;s.render.resolution_x=1200;s.render.resolution_y=900;s.render.resolution_percentage=100;s.cycles.samples=24;s.render.filepath='/tmp/federation-hybrid-ground-trial.png';print('HYBRID_GROUND',len(terrain.data.polygons),flush=True);bpy.ops.render.render(write_still=True)
