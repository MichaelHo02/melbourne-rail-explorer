"""Map close-review roof pixels to authoritative scene geometry."""
import bpy,json
from pathlib import Path
from mathutils import Vector
r=Path(bpy.data.filepath).resolve().parents[3];s=bpy.context.scene
loc=Vector((180,-190,300));rot=(Vector((52,18,6))-loc).to_track_quat('-Z','Y').to_matrix();records=[]
for x,y in [(300,350),(350,450),(350,550),(300,650),(230,450),(440,500),(400,600),(340,250)]:
 origin=loc+rot@Vector(((x/1200-.5)*210,(.5-y/1000)*175,0));direction=rot@Vector((0,0,-1));ok,p,n,face,o,mat=s.ray_cast(bpy.context.evaluated_depsgraph_get(),origin,direction,distance=10000)
 records.append({'pixel':[x,y],'hit':ok,'point':list(p),'normal':list(n),'face':face,'object':o.name if o else None,'material':o.data.materials[o.data.polygons[face].material_index].name if o and o.type=='MESH' and face<len(o.data.polygons) else None})
(r/'docs/flinders-visible-roof-ray-audit.json').write_text(json.dumps(records,indent=2)+'\n');print(json.dumps(records),flush=True)
