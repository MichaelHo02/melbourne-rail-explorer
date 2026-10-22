"""Trace prominent pale bridge pixels to saved objects before repairs."""
import bpy,json
from pathlib import Path
from mathutils import Vector
r=Path(bpy.data.filepath).resolve().parents[3];s=bpy.context.scene;s.camera=bpy.data.objects['02 Flinders precinct'];s.render.resolution_x=1500;s.render.resolution_y=1100;s.render.resolution_percentage=100;cam=s.camera;frame=cam.data.view_frame(scene=s);out=[]
for px,py in [(780,720),(780,760),(660,875),(635,870),(800,635),(790,695),(755,785)]:
 u=px/1500;v=1-py/1100;bottom=frame[2].lerp(frame[1],u);top=frame[3].lerp(frame[0],u);q=bottom.lerp(top,v);origin=cam.matrix_world@Vector((q.x,q.y,0));direction=cam.rotation_euler.to_quaternion()@Vector((0,0,-1));hit,p,n,index,o,_=s.ray_cast(bpy.context.evaluated_depsgraph_get(),origin,direction)
 if hit:
  face=o.data.polygons[index] if o.type=='MESH' and index<len(o.data.polygons) else None;out.append({'pixel':[px,py],'object':o.name,'point':list(p),'face':index,'material':o.data.materials[face.material_index].name if face and o.data.materials else None})
(r/'docs/bridge-aerial-surface-diagnostic.json').write_text(json.dumps({'camera':cam.name,'hits':out,'limits':'Geometric nearest-hit diagnostic; transparent faces can be returned. Render confirms optical appearance separately.'},indent=2)+'\n');print(json.dumps(out,indent=2),flush=True)
