"""Retain structure identifiers to keep authored facade decisions consistent."""
import argparse,json,hashlib
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--raw',type=Path,required=True);args=p.parse_args();root=Path(__file__).resolve().parents[1]
raw=json.loads(args.raw.read_text());selected={str(b['id']) for b in json.loads((root/'public/data/buildings.json').read_text())['buildings']};groups={}
for b in raw:
 if str(b['objectid']) in selected:groups[str(b['objectid'])]={'structure_id':str(b['structure_id']),'structure_height':b['structure_max_elevation']-b['structure_min_elevation']}
assert selected<=groups.keys()
(root/'assets/source/environment/city-facade-groups.json').write_text(json.dumps({'source_url':'https://data.melbourne.vic.gov.au/explore/dataset/2023-building-footprints/','raw_sha256':hashlib.sha256(args.raw.read_bytes()).hexdigest(),'groups':groups},separators=(',',':'))+'\n');print('VERIFIED structure grouping for',len(groups),'retained sections')
