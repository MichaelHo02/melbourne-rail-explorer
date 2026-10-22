"""Build reversible scan-fitted canopy panels, eaves and geometric seams."""
import bpy,bmesh,json
from pathlib import Path
from mathutils import Vector
R=Path(bpy.data.filepath).resolve().parents[3];data=json.loads((R/'assets/source/environment/flinders-captured-canopy-panels.json').read_text());scan=bpy.data.objects['Flinders station - municipal 2020 scan, authored colours'];base=bpy.data.objects['Flinders captured canopy fitted metal skins']
def inside(x,y,ring):
 value=False
 for i,(ax,ay,*_) in enumerate(ring):
  bx,by,*_=ring[i-1]
  if (ay>y)!=(by>y) and x<(bx-ax)*(y-ay)/(by-ay)+ax:value=not value
 return value
def covered(x,y):return any(inside(x,y,p['original_ring']) and not any(inside(x,y,r) for r in p['original_holes']) for p in data['panels'])
# Remove only the earlier authored grid faces replaced by these clean panels.
# Raw captured station faces remain unchanged.
bm=bmesh.new();bm.from_mesh(base.data);remove=[f for f in bm.faces if covered(*f.calc_center_median()[:2])];bmesh.ops.delete(bm,geom=remove,context='FACES');bm.to_mesh(base.data);bm.free();base.data.update()
name='Flinders scan-fitted clean canopy panels and eaves';old=bpy.data.objects.get(name)
if old:bpy.data.objects.remove(old,do_unlink=True)
vertices=[];faces=[];slots=[];roof_count=eave_count=seam_count=0
for p in data['panels']:
 for triangle in p['triangles']:
  triangle=[Vector(v) for v in triangle]
  if (triangle[1]-triangle[0]).cross(triangle[2]-triangle[0]).z<0:triangle.reverse()
  start=len(vertices);vertices.extend(triangle);faces.append(tuple(range(start,start+3)));slots.append(0);roof_count+=1
 for boundary in p['boundaries']:
  for a,b in zip(boundary,boundary[1:]+boundary[:1]):
   a=Vector(a);b=Vector(b);start=len(vertices);vertices.extend([a,b,b-Vector((0,0,data['assumptions']['fascia_depth_m'])),a-Vector((0,0,data['assumptions']['fascia_depth_m']))]);faces.append(tuple(range(start,start+4)));slots.append(1);eave_count+=1
 for seam in p['seams']:
  for a,b in zip(seam,seam[1:]):
   a=Vector(a);b=Vector(b);d=b-a;n=Vector((-d.y,d.x,0)).normalized()*.009;start=len(vertices);vertices.extend([a+n,a-n,b-n,b+n]);faces.append(tuple(range(start,start+4)));slots.append(2);seam_count+=1
roof=bpy.data.materials['Flinders canopy authored charcoal zinc']
def mat(name,color):
 m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*color,1);s=m.node_tree.nodes.get('Principled BSDF');s.inputs['Base Color'].default_value=m.diffuse_color;s.inputs['Metallic'].default_value=.5;s.inputs['Roughness'].default_value=.45;return m
mats=[roof,mat('Flinders canopy authored folded zinc fascia',(.105,.14,.135)),mat('Flinders canopy authored raised zinc seams',(.23,.26,.245))]
mesh=bpy.data.meshes.new(name);mesh.from_pydata(vertices,[],faces);mesh.update()
for m in mats:mesh.materials.append(m)
for face,slot in zip(mesh.polygons,slots):face.material_index=slot;face.use_smooth=False
obj=bpy.data.objects.new(name,mesh);scan.users_collection[0].objects.link(obj);obj.matrix_world=scan.matrix_world.copy();obj['source']=data['source'];obj['limits']=data['limits'];obj['assumptions']=json.dumps(data['assumptions']);assert all(p.area>1e-9 for p in mesh.polygons)
report={'captured_scan_vertices':len(scan.data.vertices),'captured_scan_faces':len(scan.data.polygons),'panels':len(data['panels']),'roof_triangles':roof_count,'eave_quads':eave_count,'seam_quads':seam_count,'total_faces':len(mesh.polygons),'removed_previous_authored_grid_faces':len(remove),'panel_area_m2':sum(p['panel_area_m2'] for p in data['panels']),'filled_projected_area_m2':sum(p['filled_projected_area_m2'] for p in data['panels']),'trimmed_projected_area_m2':sum(p['trimmed_projected_area_m2'] for p in data['panels']),'limits':obj['limits'],'assumptions':data['assumptions'],'support_rmse_m':[p['support_rmse_m'] for p in data['panels']]}
(R/'docs/flinders-canopy-panel-repair-audit.json').write_text(json.dumps(report,indent=2)+'\n');print('CANOPY_PANELS',json.dumps(report),flush=True)
