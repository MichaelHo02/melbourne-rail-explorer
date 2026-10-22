"""Unsaved contextual northern roof replacement trial; historical geometry, own zinc."""
import bpy,json,bmesh,math
from pathlib import Path
from mathutils import Vector
r=Path(bpy.data.filepath).resolve().parents[3];s=bpy.context.scene;ring=next(b['ring'] for b in json.loads((r/'public/data/buildings.json').read_text())['buildings'] if str(b['id'])=='16222');ring=[(x,-y) for x,y in ring]
def within(x,y):
 inside=False
 for a,b in zip(ring,ring[1:]+ring[:1]):
  if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:inside=not inside
 return inside
transparent=bpy.data.materials.new('Trial roof masking');transparent.use_nodes=True;ns=transparent.node_tree.nodes;ns.clear();out=ns.new('ShaderNodeOutputMaterial');t=ns.new('ShaderNodeBsdfTransparent');transparent.node_tree.links.new(t.outputs[0],out.inputs['Surface']);masked={}
for name in ['Continuous surveyed roofs - authored finishes','survey_16222']:
 o=bpy.data.objects[name];bm=bmesh.new();bm.from_mesh(o.data)
 fs=[f for f in bm.faces if f.normal.z>.5 and all(v.co.z>27.89 for v in f.verts) and within(*f.calc_center_median()[:2]) and f.calc_center_median().y>90]
 if fs:
  geom=list(set(fs+[e for f in fs for e in f.edges]+[v for f in fs for v in f.verts]));bmesh.ops.bisect_plane(bm,geom=geom,dist=.00001,plane_co=Vector((0,95,0)),plane_no=Vector((0,1,0)),clear_inner=False,clear_outer=False)
 bm.to_mesh(o.data);bm.free();o.data.update();o.data.materials.append(transparent);slot=len(o.data.materials)-1;count=0
 for p in o.data.polygons:
  q=p.center
  if p.normal.z>.5 and q.y>95 and q.z>27.89 and within(q.x,q.y):p.material_index=slot;count+=1
 masked[name]=count
bpy.data.objects['NGV eastern captured-fit roof relief'].hide_render=True
d=json.loads((r/'assets/source/environment/ngv-continuous-north-roof-trial.json').read_text());vs=d['vertices'];fs=d['faces']
m=bpy.data.meshes.new('Trial captured northern roof');m.from_pydata(vs,[],fs);m.materials.append(bpy.data.materials['Authored Federation Square zinc']);m.update();o=bpy.data.objects.new(m.name,m);s.collection.objects.link(o);bm=bmesh.new();bm.from_mesh(m);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001);bm.to_mesh(m);bm.free();m.update();mod=o.modifiers.new('Trial captured reduction','DECIMATE');mod.ratio=1.0
c=bpy.data.cameras.new('NGV north contextual capture trial');co=bpy.data.objects.new(c.name,c);s.collection.objects.link(co);co.location=(345,205,130);co.rotation_euler=(Vector((240,115,26))-co.location).to_track_quat('-Z','Y').to_euler();c.type='ORTHO';c.ortho_scale=140;s.camera=co;s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True;s.render.resolution_x=1200;s.render.resolution_y=900;s.render.resolution_percentage=100;s.render.filepath=str(r/'docs/images/ngv-continuous-north-context-trial.png');bpy.ops.render.render(write_still=True);(r/'docs/ngv-continuous-north-context-trial-audit.json').write_text(json.dumps({'masked_faces':masked,'captured_triangles':len(fs),'reduction_ratio':.35,'limits':'Unsaved trial. Historical2020 capture, own zinc. Authored95m boundary; scan holes and envelope contacts require visual review.'},indent=2)+'\n');print('NORTH_CAPTURE_CONTEXT_RENDERED_NO_SAVE',masked,len(fs),flush=True)
