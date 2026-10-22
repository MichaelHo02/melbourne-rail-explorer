"""Select simple low-rise recorded gables and prepare illustrative pitch geometry."""
import json,math,hashlib,collections
from pathlib import Path
from shapely.geometry import Polygon,LineString
from shapely.ops import split,triangulate
root=Path(__file__).resolve().parents[1];rawpath=Path('/Users/holeminhthach/Developer/train-simulator/public/data/buildings-raw.json');raw=json.loads(rawpath.read_text());lookup={r['objectid']:r for r in raw};data=json.loads((root/'public/data/buildings.json').read_text());groups=json.loads((root/'assets/source/environment/city-facade-groups.json').read_text())['groups'];counts=collections.Counter(groups[b['id']]['structure_id'] for b in data['buildings'] if b['id'] in groups);rows=[]
for b in data['buildings']:
 r=lookup.get(b['id']);g=groups.get(b['id'])
 if not r or not g or r['roof_type']!='Gable' or counts[g['structure_id']]!=1 or not (3<=b['height']<=20) or b['base']>1:continue
 p=Polygon([(x,-y) for x,y in b['ring']])
 if not p.is_valid or not (25<p.area<1200):continue
 rect=p.minimum_rotated_rectangle
 if p.area/rect.area<.94:continue
 coords=list(rect.exterior.coords);a,c=max(zip(coords,coords[1:]),key=lambda e:math.dist(*e));dx,dy=c[0]-a[0],c[1]-a[1];l=math.hypot(dx,dy);u=(dx/l,dy/l);n=(-u[1],u[0]);ts=[x*n[0]+y*n[1] for x,y in p.exterior.coords];mid=(min(ts)+max(ts))/2;half=(max(ts)-min(ts))/2
 if half<1.5:continue
 top=b['base']+b['height'];drop=min(3,half*.35,b['height']-2);center=p.centroid;off=mid-center.x*n[0]-center.y*n[1];cx,cy=center.x+n[0]*off,center.y+n[1]*off;pieces=split(p,LineString([(cx-u[0]*200,cy-u[1]*200),(cx+u[0]*200,cy+u[1]*200)]));faces=[]
 for piece in pieces.geoms:
  for t in triangulate(piece):
   if piece.covers(t):faces.append([[x,y,top-drop*abs(x*n[0]+y*n[1]-mid)/half] for x,y in list(t.exterior.coords)[:-1]])
 rows.append({'id':b['id'],'structure_id':g['structure_id'],'recorded_roof_type':'Gable','capture_date':r['date_captured'],'ring':[(x,-y) for x,y in b['ring']],'normal':n,'mid':mid,'half':half,'top':top,'drop':drop,'faces':faces})
out={'source':data['url'],'source_raw_sha256':hashlib.sha256(rawpath.read_bytes()).hexdigest(),'rows':rows,'limits':'Roof type is recorded; ridge direction inferred from simple footprint long axis. Pitch/eave height authored within retained maximum. Single-section low-rise rectangles only; excludes complex landmarks and overlapping sections. Capture dates retained, current roof materials unverified.'};(root/'assets/source/environment/city-survey-gables.json').write_text(json.dumps(out,indent=2)+'\n');print('VERIFIED selected recorded gables',len(rows))
