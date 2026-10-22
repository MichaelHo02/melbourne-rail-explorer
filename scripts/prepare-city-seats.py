"""Retain explicit wooden-batten seat assets, excluding ground building interiors."""
import json,hashlib,argparse,datetime
from pathlib import Path
from shapely.geometry import Polygon,Point
from shapely.strtree import STRtree
p=argparse.ArgumentParser();p.add_argument('--raw',required=True);a=p.parse_args();raw=Path(a.raw);root=Path(__file__).resolve().parents[1];polys=[]
for b in json.loads((root/'public/data/buildings.json').read_text())['buildings']:
 if b['base']<=.1:
  poly=Polygon([(x,-y) for x,y in b['ring']])
  if poly.is_valid:polys.append(poly)
tree=STRtree(polys);selected=[];excluded=[]
for r in json.loads(raw.read_text()):
 if r['type']!='Seat' or r['modeldescription']!='Seat - Straight Seat - Wooden Battens - Type 2':continue
 xy=((float(r['longitude'])-144.9671)*87939,(float(r['latitude'])+37.8183)*111320)
 if not (-2000<xy[0]<1250 and -800<xy[1]<1750):continue
 pt=Point(xy)
 if any(polys[i].covers(pt) for i in tree.query(pt)):excluded.append(r['assetid']);continue
 selected.append({**r,'preview_xy':xy})
out={'source':'https://data.melbourne.vic.gov.au/api/explore/v2.1/catalog/datasets/street-furniture-including-bollards-bicycle-rails-bins-drinking-fountains-horse-/exports/json','license':'CC BY','fetched_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'raw_sha256':hashlib.sha256(raw.read_bytes()).hexdigest(),'records':selected,'excluded_inside_buildings':excluded,'limits':'Explicit wooden-batten Type 2 seat inventory points. Authored bench dimensions, supports, orientation and flat ground datum; actual appearance, access clearance and current existence not independently verified.'};(root/'assets/source/environment/city-authored-seats.json').write_text(json.dumps(out,indent=2)+'\n');print('VERIFIED seats retained:',len(selected),'excluded:',len(excluded))
