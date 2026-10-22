"""Illustrative lane separation on selected Vicmap divided-single centrelines."""
import json,math
from pathlib import Path
from shapely import LineString,Polygon,box,union_all
R=Path(__file__).resolve().parents[1];source=json.loads((R/'assets/source/environment/city-roads-expanded.json').read_text());names={'KING STREET','QUEEN STREET','RUSSELL STREET','EXHIBITION STREET','LONSDALE STREET'}
vertices=[];faces=[];ufis=[];clip=box(-1800,0,800,1600)
for feature in source['features']:
 p=feature['properties']
 if p.get('ezi_road_name') not in names or p.get('div_rd')!='DS' or p.get('direction_code')!='B' or str(p.get('vehicular_access'))!='1':continue
 lines=[feature['geometry']['coordinates']] if feature['geometry']['type']=='LineString' else feature['geometry']['coordinates'];count=0
 for raw in lines:
  line=LineString([((a-144.9671)*87939,(b+37.8183)*111320) for a,b,*_ in raw])
  for side in [-3.2,3.2]:
   for distance in range(24,int(line.length)-25,12):
    a=line.interpolate(distance);b=line.interpolate(distance+3);dx=b.x-a.x;dy=b.y-a.y;length=math.hypot(dx,dy)
    if length<2.9:continue
    nx=-dy/length;ny=dx/length
    points=[(a.x+nx*(side-.05),a.y+ny*(side-.05)),(b.x+nx*(side-.05),b.y+ny*(side-.05)),(b.x+nx*(side+.05),b.y+ny*(side+.05)),(a.x+nx*(side+.05),a.y+ny*(side+.05))]
    if not clip.covers(Polygon(points)):continue
    start=len(vertices);vertices.extend([(x,y,.282) for x,y in points]);faces.append([start+i for i in range(4)]);count+=1
 if count:ufis.append(p['ufi'])
assert faces
out={'source':source['source'],'source_sha256':source['sourceSha256'],'license':source['license'],'ufis':ufis,'dash_count':len(faces),'vertices':vertices,'faces':faces,'reference':'https://www.vicroads.vic.gov.au/-/media/files/technical-documents-new/traffic-engineering-manual-v2/tem-vol-2-part-2-as17422-traffic-control-devices-for-general-use.ashx','limits':'Illustrative lane guides, not an as-built marking inventory. Selected five named streets, bidirectional divided-single representation. Two authored offsets +/-3.2 m; 100 mm width and 3 m dash/9 m gap based published VicRoads standard pattern. End setbacks 24 m; current lane counts, turning lanes, tram operations and controls unverified. No centre dividing line added.'}
(R/'assets/source/environment/cbd-authored-lane-guides.json').write_text(json.dumps(out,separators=(',',':'))+'\n');print(len(ufis),'features',len(faces),'dashes')
