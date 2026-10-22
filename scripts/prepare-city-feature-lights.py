"""Retain a conservative subset of mapped pole-mounted lighting assets."""
import json,hashlib,datetime,argparse
from pathlib import Path
from shapely import Polygon,Point,union_all
parser=argparse.ArgumentParser();parser.add_argument('--raw',required=True,help='Saved JSON export from the official feature-lighting dataset');args=parser.parse_args()
root=Path(__file__).resolve().parents[1];raw=Path(args.raw);rows=json.loads(raw.read_text());buildings=json.loads((root/'public/data/buildings.json').read_text())['buildings'];occupied=union_all([Polygon([(x,-y) for x,y in b['ring']]).buffer(0) for b in buildings if b['base']==0]);selected=[];excluded=0
for a in rows:
 p=a.get('geo_point_2d')
 if not p:continue
 x=(p['lon']-144.9671)*87939;y=(p['lat']+37.8183)*111320
 if not (-2000<=x<=1250 and -800<=y<=1750):continue
 if a['lightmounting'] not in ['Pole','Pole: Multiple Fixed']:continue
 if a['lightmounting']!='Pole' and a['featuredescription'] not in ['Flood','Flood Light (Upward Facing)','Down Light']:continue
 if occupied.covers(Point(x,y)):excluded+=1;continue
 selected.append({'assetid':a['assetid'],'x':x,'y':y,'lon':p['lon'],'lat':p['lat'],'description':a['description'],'mounting':a['lightmounting'],'feature':a['featuredescription'],'evaluationdate':a['evaluationdate']})
out={'source':'https://data.melbourne.vic.gov.au/api/explore/v2.1/catalog/datasets/feature-lighting-including-light-type-wattage-and-location/exports/json','license':'CC BY','fetched_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'raw_sha256':hashlib.sha256(raw.read_bytes()).hexdigest(),'raw_count':len(rows),'excluded_inside_ground_buildings':excluded,'assets':selected,'limits':'Mapped lighting assets selected by explicit pole mounting and Flood/Down Light classification, plus generic Pole. Up Light, ambiguous Feature and other mountings omitted. Ground-building overlaps omitted. Authored 4.5 m pole height, fixture design/orientation and ground datum; locations are asset points, not proof of independent poles or present-day operation. No lux sample positions used as assets.'}
(root/'assets/source/environment/city-authored-feature-lights.json').write_text(json.dumps(out,indent=2)+'\n');print('VERIFIED feature light preparation',len(selected),'inside-building exclusions',excluded)
