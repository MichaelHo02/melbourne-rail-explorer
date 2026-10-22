"""Reference-informed authored facade relief projected onto captured station walls."""
import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(bpy.data.filepath).resolve().parents[3];scan=bpy.data.objects['Flinders station - municipal 2020 scan, authored colours'];bv=BVHTree.FromObject(scan,bpy.context.evaluated_depsgraph_get());colname='Flinders scan authored facade openings';col=bpy.data.collections.get(colname)
if col:
 for o in list(col.objects):bpy.data.objects.remove(o,do_unlink=True)
else:col=bpy.data.collections.new(colname);bpy.context.scene.collection.children.link(col)
ring=json.loads((R/'assets/source/environment/flinders-scan-material-zones.json').read_text())['zones'][0]['ring'];signed=sum(ring[i-1][0]*ring[i][1]-ring[i][0]*ring[i-1][1] for i in range(len(ring)));glassv=[];glassf=[];framev=[];framef=[];sillv=[];sillf=[];records=[];rejected=0

def mesh(name,v,f,mat):
 data=bpy.data.meshes.new(name);data.from_pydata(v,[],f);data.materials.append(mat);bm=bmesh.new();bm.from_mesh(data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(data);bm.free();data.update();o=bpy.data.objects.new(name,data);col.objects.link(o);return o

def box(v,f,c,t,n,width,depth,height):
 k=len(v)
 for z in [-height/2,height/2]:
  for x,y in [(-width/2,-depth/2),(width/2,-depth/2),(width/2,depth/2),(-width/2,depth/2)]:v.append(tuple(c+t*x+n*y+Vector((0,0,z))))
 f.extend([tuple(k+i for i in q) for q in [[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]])

def probe(c,t,n,points):
 depths=[]
 for x,z in points:
  origin=c+t*x+Vector((0,0,z))+n*4;hit,normal,index,distance=bv.ray_cast(origin,-n,8)
  if hit is None or normal.dot(n)<.25:return None
  depths.append((hit-c-Vector((0,0,z))-t*x).dot(n))
 if max(depths)-min(depths)>.75:return None
 return max(depths)+.075

for i,a in enumerate(ring[:-1]):
 b=ring[i+1];start=Vector((*a,0));delta=Vector((b[0]-a[0],b[1]-a[1],0));length=delta.length
 if length<7:continue
 t=delta/length;n=Vector((t.y,-t.x,0))*(1 if signed>0 else -1)
 if abs(n.y)<.65:continue
 bays=int(length/3.8)
 for bay in range(bays):
  c=start+t*((bay+.5)*length/bays);half=min(.88,length/bays*.25)
  for level,(bottom,height,arched) in enumerate([(3.5,2.7,False),(8.5,2.7,False),(14,3.4,True)]):
   top=bottom+height;points=[(-half,bottom),(half,bottom),(-half,top-half if arched else top),(half,top-half if arched else top),(0,top),(0,bottom+height/2)]
   offset=probe(c,t,n,points)
   if offset is None:rejected+=1;continue
   def point(x,z,extra=0):return c+t*x+n*(offset+extra)+Vector((0,0,z))
   outline=[(-half,bottom),(half,bottom)]
   if arched:
    outline.append((half,top-half))
    outline.extend([(half*math.cos(j*math.pi/12),top-half+half*math.sin(j*math.pi/12)) for j in range(1,13)])
   else:outline.extend([(half,top),(-half,top)])
   k=len(glassv);glassv.extend(tuple(point(x,z)) for x,z in outline);glassf.append(tuple(range(k,k+len(outline))))
   # Geometric surrounds, mullions and shallow projecting sills; no image textures.
   for aa,bb in zip(outline,outline[1:]+outline[:1]):
    ax,az=aa;bx,bz=bb;dv=Vector((bx-ax,bz-az));ln=dv.length
    if ln<.0001:continue
    d=Vector((-dv.y,dv.x)).normalized()*.045;q=len(framev)
    framev.extend(tuple(point(x,z,.04)) for x,z in [(ax+d.x,az+d.y),(bx+d.x,bz+d.y),(bx-d.x,bz-d.y),(ax-d.x,az-d.y)]);framef.append(tuple(range(q,q+4)))
   box(framev,framef,point(0,bottom+height*.5,.055),t,n,.055,.055,height-.12)
   box(framev,framef,point(0,bottom+height*.48,.055),t,n,half*2-.08,.055,.055)
   box(sillv,sillf,point(0,bottom-.09,.10),t,n,half*2+.22,.24,.15)
   records.append({'edge_index':i,'level':level,'bay':bay,'center_xy':[c.x,c.y],'bottom':bottom,'top':top,'arch':arched,'source_plane_offset':offset,'side':'north' if n.y>0 else 'south'})

def material(name,c,rough,metal=0):
 m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*c,1);s=m.node_tree.nodes.get('Principled BSDF');s.inputs['Base Color'].default_value=m.diffuse_color;s.inputs['Roughness'].default_value=rough;s.inputs['Metallic'].default_value=metal;return m
mesh('Scan Flinders authored projected window panes',glassv,glassf,material('Scan Flinders authored deep blue glass',(.035,.065,.075),.28,.25));mesh('Scan Flinders authored geometric pane surrounds and mullions',framev,framef,material('Scan Flinders authored dark painted window frames',(.055,.085,.07),.65));mesh('Scan Flinders authored projecting window sills',sillv,sillf,material('Scan Flinders authored warm stone sill finish',(.58,.40,.18),.82))
limits='Own glass/frame/sill geometry over retained scan; no photographic textures. Historical1905 front elevation and undated south-facade archival photo guide forms only. 3.8m target spacing, levels3.5/8.5/14m, dimensions and mullions authored, not surveyed current openings. Six support points per pane ray-tested against captured wall; gaps and excessive surface variation rejected. No actual facade cutting or measured bay count.'
col['limits']=limits;col['reference']='https://www.flindersstreetstation.com.au/';col['south_reference']='https://www.flindersstreetstation.com.au/south-facade.php'
assert records and all(n.type!='TEX_IMAGE' for o in col.objects for m in o.data.materials for n in m.node_tree.nodes)
(R/'docs/flinders-scan-facade-relief-audit.json').write_text(json.dumps({'placed_windows':len(records),'rejected_candidates':rejected,'north':sum(r['side']=='north' for r in records),'south':sum(r['side']=='south' for r in records),'placements':records,'limits':limits},indent=2)+'\n');print('VERIFIED projected facade windows',len(records),'rejected',rejected,flush=True)
