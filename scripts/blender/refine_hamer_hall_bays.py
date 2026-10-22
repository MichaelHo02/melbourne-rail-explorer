"""Illustrative deep framed bays following retained Hamer Hall outline."""
import bpy,json,math
from pathlib import Path
root=globals().get('root') or Path(bpy.data.filepath).resolve().parents[3];name='Hamer Hall authored road-facing framed bays'
if not bpy.data.objects.get(name):
 b=next(b for b in json.loads((root/'public/data/buildings.json').read_text())['buildings'] if str(b['id'])=='3168');r=[(x,-y) for x,y in b['ring']];signed=sum(a[0]*c[1]-c[0]*a[1] for a,c in zip(r,r[1:]));lengths=[math.dist(a,c) for a,c in zip(r,r[1:])];total=sum(lengths);count=int(total/5);v=[];f=[];mi=[]
 def box(cx,cy,ux,uy,nx,ny,s,t,z,w,depth,h,mat):
  i=len(v)
  for zz in [z,z+h]:
   for ss,tt in [(-w/2,0),(w/2,0),(w/2,depth),(-w/2,depth)]:v.append((cx+ux*(s+ss)+nx*(t+tt),cy+uy*(s+ss)+ny*(t+tt),zz))
  for q in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]:f.append(tuple(i+j for j in q));mi.append(mat)
 for j in range(count):
  distance=(j+.5)*total/count;acc=0
  for a,c,L in zip(r,r[1:],lengths):
   if distance<=acc+L:
    ux,uy=(c[0]-a[0])/L,(c[1]-a[1])/L;nx,ny=(uy,-ux) if signed>0 else (-uy,ux);t=(distance-acc)/L;cx,cy=a[0]+(c[0]-a[0])*t,a[1]+(c[1]-a[1])*t
    if nx<=.3:break
    box(cx,cy,ux,uy,nx,ny,0,.08,8.5,2.8,.03,3.8,1)
    for side in [-1,1]:box(cx,cy,ux,uy,nx,ny,side*1.55,.06,8.2,.3,.45,4.4,0)
    for z in [8.2,12.3]:box(cx,cy,ux,uy,nx,ny,0,.06,z,3.4,.45,.3,0)
    break
   acc+=L
 m=bpy.data.meshes.new(name);m.from_pydata(v,[],f)
 for label in ['Authored Arts theatre bush hammered concrete','Authored Arts theatre horizontal glazing']:m.materials.append(bpy.data.materials[label])
 for p,i in zip(m.polygons,mi):p.material_index=i
 m.update();o=bpy.data.objects.new(name,m);bpy.data.collections['CITY - reference-authored landmarks'].objects.link(o);o['bay_count']=len(f)//30;o['limits']='Authored approximately 5m framed-bay rhythm, 3.4m width and 0.45m projecting reveals. Retained outline placement; exact original opening count, depths, balconies and current condition unmeasured.';o['reference']='https://www.heritage.vic.gov.au/__data/assets/pdf_file/0027/722547/2024.10.28-Updated-AMPA-HIS.pdf';print('VERIFIED Hamer road-facing bays:',len(f)//30,len(f))

old=bpy.data.objects.get('Hamer Hall authored deep framed bays')
if old:old.hide_render=True;old.hide_set(True);old['replacement']=name
