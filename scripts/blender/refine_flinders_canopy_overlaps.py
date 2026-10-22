"""Reversibly hide captured faces covered by fitted roofs or repaired edge bands.
No vertices or faces deleted. Original face material slots are saved inside the
.blend as a JSON Text block and in the audit for restoration.
"""
import bpy,json,hashlib
from pathlib import Path
R=Path(bpy.data.filepath).resolve().parents[3];data=json.loads((R/'assets/source/environment/flinders-captured-canopy-panels.json').read_text());scan=bpy.data.objects['Flinders station - municipal 2020 scan, authored colours'];mesh=scan.data
textname='Flinders canopy overlap original material slots.json';name='Flinders canopy covered captured faces - reversible transparency'
def geometry_hash():return hashlib.sha256(repr(([tuple(v.co) for v in mesh.vertices],[tuple(p.vertices) for p in mesh.polygons])).encode()).hexdigest()
before=geometry_hash();original_count=len(mesh.polygons)
material=bpy.data.materials.get(name) or bpy.data.materials.new(name);material.use_nodes=True;material.diffuse_color=(0,0,0,0);material.node_tree.nodes.clear();out=material.node_tree.nodes.new('ShaderNodeOutputMaterial');transparent=material.node_tree.nodes.new('ShaderNodeBsdfTransparent');material.node_tree.links.new(transparent.outputs['BSDF'],out.inputs['Surface'])
if hasattr(material,'surface_render_method'):material.surface_render_method='DITHERED'
indices={m.name:i for i,m in enumerate(mesh.materials) if m};existing=indices.get(name)
previous=bpy.data.texts.get(textname)
if previous and existing is not None:
 recovery=json.loads(previous.as_string());assert recovery['vertices']==len(mesh.vertices) and recovery['faces']==len(mesh.polygons)
 for i,slot in recovery['original_materials']:
  if mesh.polygons[i].material_index==existing:mesh.polygons[i].material_index=slot
if existing is None:mesh.materials.append(material);existing=len(mesh.materials)-1
def inside(x,y,ring):
 result=False
 for i,(ax,ay,*_) in enumerate(ring):
  bx,by,*_=ring[i-1]
  if (ay>y)!=(by>y) and x<(bx-ax)*(y-ay)/(by-ay)+ax:result=not result
 return result
zones=[z['ring'] for z in json.loads((R/'assets/source/environment/flinders-scan-material-zones.json').read_text())['zones'] if z['source_id'] in ['1145','1146','1148']]
def edge_distance(x,y,ring):
 best=float('inf')
 for i,a in enumerate(ring):
  b=ring[i-1];dx=b[0]-a[0];dy=b[1]-a[1];den=dx*dx+dy*dy;t=max(0,min(1,((x-a[0])*dx+(y-a[1])*dy)/den)) if den else 0
  best=min(best,((x-a[0]-t*dx)**2+(y-a[1]-t*dy)**2)**.5)
 return best
def covered(v,p):
 c=p['plane_coefficients'];gap=c[0]*v.x+c[1]*v.y+c[2]+p['plane_lift_above_grid_m']-v.z
 return abs(gap)<.6 and inside(v.x,v.y,p['boundaries'][0]) and not any(inside(v.x,v.y,r) for r in p['boundaries'][1:])
def edge_band(v,p):
 c=p['plane_coefficients'];gap=c[0]*v.x+c[1]*v.y+c[2]+p['plane_lift_above_grid_m']-v.z
 return v.z>2.4 and -.8<gap<3.5 and not any(inside(v.x,v.y,r) for r in zones) and not any(inside(v.x,v.y,r) for r in p['boundaries'][1:]) and (inside(v.x,v.y,p['boundaries'][0]) or edge_distance(v.x,v.y,p['boundaries'][0])<1.5)
original=[];counts=[0]*len(data['panels']);areas=[0.]*len(counts);edge_counts=[0]*len(counts)
for face in mesh.polygons:
 points=[mesh.vertices[j].co for j in face.vertices]
 selected=None
 for i,p in enumerate(data['panels']):
  if covered(face.center,p) and all(covered(v,p) for v in points):selected=(i,False);break
 if selected is None:
  for i,p in enumerate(data['panels']):
   if edge_band(face.center,p) and all(edge_band(v,p) for v in points):selected=(i,True);break
 if selected is not None:
  i,is_edge=selected;original.append([face.index,face.material_index]);face.material_index=existing;counts[i]+=1;areas[i]+=face.area
  if is_edge:edge_counts[i]+=1
record={'vertices':len(mesh.vertices),'faces':len(mesh.polygons),'geometry_sha256':before,'original_materials':original}
text=bpy.data.texts.get(textname) or bpy.data.texts.new(textname);text.clear();text.write(json.dumps(record))
mesh.update();assert geometry_hash()==before and len(mesh.polygons)==original_count
scan['canopy_overlap_repair']='Covered roof faces and bounded damaged edge/underside bands hidden via transparent material. Main station zones protected from extra edge selection. Geometry retained. Restore slots from '+textname
report={'hidden_faces':len(original),'additional_edge_band_faces_per_panel':edge_counts,'faces_per_panel':counts,'hidden_surface_area_per_panel_m2':areas,'captured_vertices':len(mesh.vertices),'captured_faces':len(mesh.polygons),'captured_geometry_unchanged':geometry_hash()==before,'geometry_sha256':before,'recovery_text_block':textname,'selection':'All vertices either inside panel within0.6m of plane, or above local2.4m, between0.8m above and3.5m below plane and within1.5m of outer edge. Extra edge band excludes main station zones1145/1146/1148 and holes.','limits':'Author-selected presentation cleanup. Captured geometry retained; only surface material visibility changes. Edge repair extends at most1.5m beyond fitted footprint; lower and taller disconnected scan defects remain. No captured support layout is claimed.','recovery_sha256':hashlib.sha256(text.as_string().encode()).hexdigest()}
(R/'docs/flinders-canopy-overlap-cleanup-audit.json').write_text(json.dumps(report,indent=2)+'\n');print('OVERLAP_CLEANUP',json.dumps({k:v for k,v in report.items() if k!='original_materials'}),flush=True)
