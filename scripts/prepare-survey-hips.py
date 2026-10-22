"""Select simple low-rise recorded gables and prepare illustrative pitch geometry."""
import json,math,hashlib,collections
from pathlib import Path
from shapely.geometry import Polygon,LineString
from shapely.ops import split,triangulate
root=Path(__file__).resolve().parents[1];rawpath=Path('/Users/holeminhthach/Developer/train-simulator/public/data/buildings-raw.json');raw=json.loads(rawpath.read_text());lookup={r['objectid']:r for r in raw};data=json.loads((root/'public/data/buildings.json').read_text());groups=json.loads((root/'assets/source/environment/city-facade-groups.json').read_text())['groups'];counts=collections.Counter(groups[b['id']]['structure_id'] for b in data['buildings'] if b['id'] in groups);rows=[]
for b in data['buildings']:
 r=lookup.get(b['id']);g=groups.get(b['id'])
 if not r or not g or r['roof_type']!='Hip' or counts[g['structure_id']]!=1 or not (3<=b['height']<=20) or b['base']>1:continue
 p=Polygon([(x,-y) for x,y in b['ring']])
 if not p.is_valid or not (25<p.area<1200):continue
 rect=p.minimum_rotated_rectangle
 if p.area/rect.area<.94:continue
 coords=list(rect.exterior.coords);a,c=max(zip(coords,coords[1:]),key=lambda e:math.dist(*e));dx,dy=c[0]-a[0],c[1]-a[1];l=math.hypot(dx,dy);u=(dx/l,dy/l);n=(-u[1],u[0]);ts=[x*n[0]+y*n[1] for x,y in p.exterior.coords];mid=(min(ts)+max(ts))/2;half=(max(ts)-min(ts))/2
 if half<1.5:continue
 top=b['base']+b['height'];drop=min(3,half*.35,b['height']-2)
 vals=[(x*u[0]+y*u[1],x*n[0]+y*n[1]) for x,y in p.exterior.coords];xlo=min(x for x,y in vals);xhi=max(x for x,y in vals);ylo=min(y for x,y in vals);yhi=max(y for x,y in vals);ymid=(ylo+yhi)/2;left=xlo+half;right=xhi-half
 def world(x,y):return (x*u[0]+y*n[0],x*u[1]+y*n[1])
 patches=[[(xlo,ylo),(xhi,ylo),(right,ymid),(left,ymid)],[(xhi,yhi),(xlo,yhi),(left,ymid),(right,ymid)],[(xlo,yhi),(xlo,ylo),(left,ymid)],[(xhi,ylo),(xhi,yhi),(right,ymid)]];faces=[]
 for patch in patches:
  piece=p.intersection(Polygon([world(x,y) for x,y in patch]))
  for t in triangulate(piece):
   if piece.covers(t):
    face=[]
    for x,y in list(t.exterior.coords)[:-1]:
     lx=x*u[0]+y*u[1];ly=x*n[0]+y*n[1];rise=max(0,min(half,lx-xlo,xhi-lx,ly-ylo,yhi-ly));face.append([x,y,top-drop+drop*rise/half])
    faces.append(face)
 rows.append({'id':b['id'],'structure_id':g['structure_id'],'recorded_roof_type':'Hip','capture_date':r['date_captured'],'ring':[(x,-y) for x,y in b['ring']],'normal':n,'mid':mid,'half':half,'top':top,'drop':drop,'faces':faces})
out={'source':data['url'],'source_raw_sha256':hashlib.sha256(rawpath.read_bytes()).hexdigest(),'rows':rows,'limits':'Hipped roof type is recorded; ridge direction inferred from simple footprint long axis. Pitch/eave height authored within retained maximum. Single-section low-rise rectangles only; excludes complex landmarks and overlapping sections. Capture dates retained, current roof materials unverified.'};(root/'assets/source/environment/city-survey-hips.json').write_text(json.dumps(out,indent=2)+'\n');print('VERIFIED selected recorded hips',len(rows))
