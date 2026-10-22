"""Authored sloping upper shell and windows from municipal exterior reference."""
import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(bpy.data.filepath).resolve().parents[3];d=json.loads((R/'assets/source/environment/westin-authored-mansard.json').read_text());name='Westin authored sloping crown';col=bpy.data.collections.get(name)
if col:
 for o in list(col.objects):bpy.data.objects.remove(o,do_unlink=True)
else:col=bpy.data.collections.new(name);bpy.context.scene.collection.children.link(col)
metal=bpy.data.materials['Westin authored silver blue mansard metal'];glass=bpy.data.materials['Westin authored vertical bay glazing'];frame=bpy.data.materials['Westin authored bay frame']
def obj(name,v,f,m):
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(v,[],f);mesh.materials.append(m);mesh.update();o=bpy.data.objects.new(name,mesh);col.objects.link(o);return o
roof=obj(name+' shell',[(x,y,z+.02) for x,y,z in d['vertices']],d['faces'],metal);assert all(p.normal.z>0 for p in roof.data.polygons)
ring=d['ring'][:-1];signed=sum(ring[i-1][0]*ring[i][1]-ring[i][0]*ring[i-1][1] for i in range(len(ring)));gv=[];gf=[];fv=[];ff=[];count=0
low=d['base']+.02;high=d['top']+.02
def quad(v,f,points):
 k=len(v);v.extend(tuple(p) for p in points);f.append([k,k+1,k+2,k+3])
for i,(x,y) in enumerate(ring):
 a=Vector((x,y,0));b=Vector((*ring[(i+1)%len(ring)],0));delta=b-a;length=delta.length
 if length<7:continue
 t=delta/length;normal=Vector((t.y,-t.x,0))*(1 if signed>0 else -1);bays=int(length/4.2)
 def point(center,z,extra=.04):return center+normal*(2*(high-z)/(high-low)+extra)+Vector((0,0,z))
 for floor in range(4):
  bottom=low+1+floor*3.6;top=min(high-.6,bottom+2.4)
  for bay in range(bays):
   c=a+t*((bay+.5)*length/bays);half=min(1.1,length/bays*.26);left=c-t*half;right=c+t*half
   quad(gv,gf,[point(left,bottom),point(right,bottom),point(right,top),point(left,top)]);count+=1
   for q in [[point(left-t*.055,bottom-.055,.055),point(right+t*.055,bottom-.055,.055),point(right+t*.055,bottom,.055),point(left-t*.055,bottom,.055)],[point(left-t*.055,top,.055),point(right+t*.055,top,.055),point(right+t*.055,top+.055,.055),point(left-t*.055,top+.055,.055)],[point(left-t*.055,bottom,.055),point(left,bottom,.055),point(left,top,.055),point(left-t*.055,top,.055)],[point(right,bottom,.055),point(right+t*.055,bottom,.055),point(right+t*.055,top,.055),point(right,top,.055)]]:quad(fv,ff,q)
obj(name+' authored sloped glazing',gv,gf,glass);obj(name+' authored window frames',fv,ff,frame);col['reference']=d['reference'];col['limits']=d['limits']+' Original generic upper windows remain retained behind the outward shell and are occluded; new flat glazing follows authored slope, not real dormer/bay projections or measured count.';col['window_quads']=count
print('VERIFIED Westin sloping shell',len(d['faces']),'roof triangles',count,'sloped window quads',len(ff),'frame strips',flush=True)
