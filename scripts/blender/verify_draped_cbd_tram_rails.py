import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
r=Path(bpy.data.filepath).resolve().parents[3];o=bpy.data.objects['Retained Vicmap tram rails - authored road-draped gauge'];p=r/'docs/cbd-draped-tram-rails-audit.json';a=json.loads(p.read_text());assert len(o.data.polygons)==a['rail_segments'];assert a['source_sha256']==hashlib.sha256((r/'assets/source/environment/city-rails-expanded.json').read_bytes()).hexdigest();dg=bpy.context.evaluated_depsgraph_get();supports=[]
for name in a['support_objects']:
 q=bpy.data.objects[name];assert not q.hide_render
 if name.startswith('Municipal Swanston'):assert q['type'] in ('RoadCarriageway','RoadTramFormation')
 supports.append((q,BVHTree.FromObject(q,dg)))
errors=[]
for i in range(0,len(o.data.vertices),max(1,len(o.data.vertices)//300)):
 c=o.data.vertices[i].co;hs=[]
 for q,bv in supports:
  hit,n,ix,dist=bv.ray_cast(q.matrix_world.inverted()@Vector((c.x,c.y,100)),Vector((0,0,-1)),200)
  if hit is not None and n.z>.75:hs.append((q.matrix_world@hit).z)
 assert hs;errors.append(abs(c.z-max(hs)-.008))
assert max(errors)<.00005;assert all(p.normal.z>0 for p in o.data.polygons);assert bpy.context.scene.camera.name=='37 CBD aerial review';a['saved_verification']={'rail_segments':len(o.data.polygons),'sampled_road_clearance_checks':len(errors),'max_clearance_error_m':max(errors),'support_types_valid':True};p.write_text(json.dumps(a,indent=2)+'\n');print('VERIFIED_SAVED_TRAM_RAILS',len(errors),flush=True)
s=(r/'scripts/blender/render_swanston_approach_detail.py').read_text().replace('Vector((52,18,6))','Vector((38,35,6))').replace('ortho_scale=210','ortho_scale=95').replace('observatory-swanston-approach-detail.png','observatory-cbd-draped-tram-rails.png');exec(compile(s,'render','exec'))
