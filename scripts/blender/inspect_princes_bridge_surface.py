import bpy,json
from pathlib import Path
from mathutils import Vector
r=Path(bpy.data.filepath).resolve().parents[3];s=bpy.context.scene;s.camera=bpy.data.objects['02 Flinders precinct'];s.render.resolution_x=1400;s.render.resolution_y=1000;s.render.resolution_percentage=100;cam=s.camera;frame=cam.data.view_frame(scene=s);out=[]
for px,py in [(710,655),(710,675),(703,695),(700,715)]:
 u=px/1400;v=1-py/1000;q=frame[2].lerp(frame[1],u).lerp(frame[3].lerp(frame[0],u),v);origin=cam.matrix_world@Vector((q.x,q.y,0));direction=cam.rotation_euler.to_quaternion()@Vector((0,0,-1));hit,p,n,i,o,m=s.ray_cast(s.evaluated_depsgraph_get() if hasattr(s,'evaluated_depsgraph_get') else bpy.context.evaluated_depsgraph_get(),origin,direction)
 if hit:out.append({'pixel':[px,py],'point':list(p),'object':o.name,'face':i,'material':o.data.materials[o.data.polygons[i].material_index].name if o.type=='MESH' and i<len(o.data.polygons) else None})
(r/'docs/princes-bridge-surface-audit.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out),flush=True)
