"""Retain official open-space inventory parcels for the surveyed preview extent."""
import json,urllib.request,urllib.parse,datetime,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
base='https://opendata.maps.vic.gov.au/geoserver/wfs'
bounds=[144.9671-2000/87939,-37.8183-800/111320,144.9671+1250/87939,-37.8183+1750/111320]
query={'service':'WFS','version':'1.0.0','request':'GetFeature','typeName':'open-data-platform:veac_metro_open_space','outputFormat':'application/json','srsName':'EPSG:4326','bbox':','.join(map(str,bounds))+',EPSG:4326','maxFeatures':1000}
with urllib.request.urlopen(base+'?'+urllib.parse.urlencode(query),timeout=45) as response:raw=response.read();data=json.loads(raw)
assert data['features'] and len(data['features'])<1000
assert len({f['properties']['veac_id'] for f in data['features']})==len(data['features'])
source={'url':base,'catalogueUrl':'https://discover.data.vic.gov.au/dataset/veac-metropolitan-melbourne-open-space-inventory','license':'CC BY 4.0','attribution':'State of Victoria, VEAC Metropolitan Melbourne Open Space Inventory','query':query}
r={'sources':{'openSpaces':source},'layers':{'openSpaces':data},'bounds':bounds,'fetchedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sourceSha256':hashlib.sha256(raw).hexdigest()}
(ROOT/'assets/source/environment/city-parks-expanded.json').write_text(json.dumps(r,separators=(',',':'))+'\n');print('Retained expanded open-space parcels:',len(data['features']))
