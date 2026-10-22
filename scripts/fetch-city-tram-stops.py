"""Retain official spatial tram stop points, without inferring platform geometry."""
import json,urllib.request,datetime,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[1];metadata_url='https://opendata.transport.vic.gov.au/api/3/action/package_show?id=public-transport-lines-and-stops'
with urllib.request.urlopen(metadata_url,timeout=30) as response:meta=json.load(response)['result']
resource=next(r for r in meta['resources'] if r['name']=='Public Transport Stops')
with urllib.request.urlopen(resource['url'],timeout=45) as response:raw=response.read();data=json.loads(raw)
rows=[]
for f in data['features']:
 if f['properties'].get('MODE')!='METRO TRAM' or f['geometry']['type']!='Point':continue
 lon,lat=f['geometry']['coordinates'][:2];x=(lon-144.9671)*87939;y=(lat+37.8183)*111320
 if -2000<=x<=1250 and -800<=y<=1750:rows.append({'source_feature':f,'xy':[x,y]})
assert rows
out={'metadata_url':metadata_url,'source_url':resource['url'],'resource_metadata':resource,'dataset_modified':meta.get('metadata_modified'),'license_id':meta.get('license_id'),'fetched_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_sha256':hashlib.sha256(raw).hexdigest(),'records':rows,'limits':'Official stop points only; source update does not prove each physical stop is unchanged. Platform boundaries, pole locations, accessible boarding layout, current service and operational status unverified. No realtime API key required or used.'};(root/'assets/source/environment/city-tram-stops.json').write_text(json.dumps(out,indent=2)+'\n');print('VERIFIED retained tram stop points',len(rows),'dataset modified',out['dataset_modified'])
