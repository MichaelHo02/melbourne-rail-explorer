"""Authored concrete identity on retained Hamer Hall survey sections."""
import bpy,json,math
from pathlib import Path
root=globals().get('root') or Path(bpy.data.filepath).resolve().parents[3];name='Hamer Hall authored upper glazing band'
if not bpy.data.objects.get(name):
 for id in ['3167','3168','3169']:
  o=bpy.data.objects.get('survey_'+id);assert o;o.data.materials.clear();o.data.materials.append(bpy.data.materials['Authored Arts theatre bush hammered concrete']);o['architectural_reference']='https://armarchitecture.com.au/projects/hamer-hall/';o['finish_limits']='Authored concrete palette and relief on retained 2023 envelope; precise panels, balconies, restaurant curtain and current museum works unresolved.'
 b=next(b for b in json.loads((root/'public/data/buildings.json').read_text())['buildings'] if str(b['id'])=='3168');r=[(x,-y) for x,y in b['ring']];area=sum(a[0]*c[1]-c[0]*a[1] for a,c in zip(r,r[1:]));v=[];f=[]
 for a,c in zip(r,r[1:]):
  dx,dy=c[0]-a[0],c[1]-a[1];length=math.hypot(dx,dy)
  if length<.1:continue
  nx,ny=(dy/length,-dx/length) if area>0 else (-dy/length,dx/length);i=len(v);v.extend([(a[0]+nx*.06,a[1]+ny*.06,13.8),(c[0]+nx*.06,c[1]+ny*.06,13.8),(c[0]+nx*.06,c[1]+ny*.06,15),(a[0]+nx*.06,a[1]+ny*.06,15)]);f.append((i,i+1,i+2,i+3))
 m=bpy.data.meshes.new(name);m.from_pydata(v,[],f);m.materials.append(bpy.data.materials['Authored Arts theatre horizontal glazing']);m.update();o=bpy.data.objects.new(name,m);bpy.data.collections['CITY - reference-authored landmarks'].objects.link(o);o['limits']='Illustrative upper glazing ribbon on retained section 3168; actual deep openings, balconies and current works unmeasured.';print('VERIFIED Hamer Hall concrete and glazing:',len(f),'quads')
