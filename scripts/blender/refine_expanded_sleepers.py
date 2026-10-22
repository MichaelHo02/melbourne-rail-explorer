"""Illustrative sleeper rhythm on additional ordinary Vicmap alignments."""
import bpy,json,math
from pathlib import Path
root=globals().get('root') or Path(bpy.data.filepath).resolve().parents[3];name='Expanded ordinary railway authored sleepers'
if not bpy.data.objects.get(name):
 d=json.loads((root/'assets/source/environment/city-trackbeds-expanded-additions.json').read_text());v=[];f=[];count=0
 for line in d['alignments']:
  for a,b in zip(line,line[1:]):
   dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy)
   if length<.65 or not all(-2000<=p[0]<=1250 and -800<=p[1]<=1750 for p in [a,b]):continue
   tx,ty=dx/length,dy/length;nx,ny=-ty,tx
   for i in range(int(length/.65)):
    x,y=a[0]+tx*(i*.65+.325),a[1]+ty*(i*.65+.325);start=len(v)
    for z in [.405,.445]:
     for along,across in [(-.12,-1.22),(.12,-1.22),(.12,1.22),(-.12,1.22)]:v.append((x+tx*along+nx*across,y+ty*along+ny*across,z))
    f.extend(tuple(start+j for j in face) for face in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]);count+=1
 m=bpy.data.meshes.new(name);m.from_pydata(v,[],f);m.materials.append(bpy.data.materials['Authored sleeper concrete']);m.update();o=bpy.data.objects.new(name,m);bpy.data.collections['GROUND - official horizontal geography, authored levels'].objects.link(o);o['sleeper_count']=count;o['limits']='Authored concrete appearance, .65 m spacing, 2.44 m length, .24 m width and flat .405-.445 m level on additional ordinary source lines; actual sleeper specification, track multiplicity and elevation unverified.';print('VERIFIED expanded authored sleepers',count,flush=True)
