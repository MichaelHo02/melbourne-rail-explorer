"""Prepare unsaved precinct elevation diagnostic from retained municipal records."""
import json
from pathlib import Path
R=Path(__file__).resolve().parents[1];raw=json.loads(Path('/Users/holeminhthach/Developer/train-simulator/public/data/buildings-raw.json').read_text());selected={'806667','816359','812338','805928','809180','816815'};records={str(v['objectid']):v for v in raw if str(v['structure_id']) in selected};prepared=json.loads((R/'public/data/buildings.json').read_text())['buildings'];out=[]
for b in prepared:
 if str(b['id']) in records:
  r=records[str(b['id'])];out.append({'id':str(b['id']),'structure_id':str(r['structure_id']),'offset':r['structure_min_elevation']-4.1,'ring':[(x,-y) for x,y in b['ring']],'base':b['base'],'height':b['height']})
Path('/tmp/federation-datum-sections.json').write_text(json.dumps(out))
