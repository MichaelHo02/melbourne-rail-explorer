"""Bounded official road import and dated parking fallback; no vehicle tracks inferred."""
import json, pathlib, urllib.request, urllib.parse, datetime, hashlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
BOUNDS=[144.949,-37.825,144.981,-37.805]
base='https://vicmap.land.vic.gov.au/agsgis/rest/services/vicmap/Vicmap_Transport/MapServer/1/query'
query=dict(where="feature_type_code = 'road' AND road_status = 'O'",geometry=','.join(map(str,BOUNDS)),geometryType='esriGeometryEnvelope',inSR=4326,spatialRel='esriSpatialRelIntersects',outFields='ufi,ezi_road_name,class_code,direction_code,vehicular_access,div_rd',outSR=4326,returnGeometry='true',f='geojson',resultRecordCount=2000)
with urllib.request.urlopen(base+'?'+urllib.parse.urlencode(query),timeout=45) as r: roads=json.load(r)
if 'error' in roads or roads.get('exceededTransferLimit') or len(roads.get('features',[]))>=2000: raise RuntimeError('Incomplete road response')
url='https://data.melbourne.vic.gov.au/api/explore/v2.1/catalog/datasets/on-street-parking-bay-sensors/exports/json'
with urllib.request.urlopen(url,timeout=45) as r: raw=r.read(); parking=json.loads(raw)
parking=[b for b in parking if b.get('location') and BOUNDS[0]<=b['location']['lon']<=BOUNDS[2] and BOUNDS[1]<=b['location']['lat']<=BOUNDS[3]]
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
(ROOT/'src/data/observatory-roads.json').write_text(json.dumps(dict(source=base,license='CC BY 4.0',attribution='State of Victoria (Department of Transport and Planning), Vicmap Transport',fetchedAt=now,bounds=BOUNDS,query=query,features=roads['features']),separators=(',',':'))+'\n')
(ROOT/'public/data/parking-snapshot.json').write_text(json.dumps(dict(source=url,license='CC BY 4.0',attribution='City of Melbourne, On-street Parking Bay Sensors',fetchedAt=now,sourceSha256=hashlib.sha256(raw).hexdigest(),mode='snapshot',results=parking),separators=(',',':'))+'\n')
print('Imported roads:',len(roads['features']),'parking bays:',len(parking))
