"""Retain public Vicmap railways across the surveyed preview extent."""
import json,urllib.request,urllib.parse,datetime,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
base='https://vicmap.land.vic.gov.au/agsgis/rest/services/vicmap/Vicmap_Transport/MapServer/3/query'
bounds=[144.942,-37.827,144.984,-37.800]
query=dict(where="1=1",geometry=','.join(map(str,bounds)),geometryType='esriGeometryEnvelope',inSR=4326,spatialRel='esriSpatialRelIntersects',outFields='ufi,pfi,feature_type_code,name,tracks_number_of,structure_type,structure_name,rail_gauge,physical_condition',outSR=4326,returnGeometry='true',f='geojson',resultRecordCount=2000,orderByFields='ufi')
features=[];seen=set();digest=hashlib.sha256();pages=0
for page in range(20):
    page_query={**query,'resultOffset':page*2000}
    with urllib.request.urlopen(base+'?'+urllib.parse.urlencode(page_query),timeout=45) as response:raw=response.read();data=json.loads(raw)
    if 'error' in data:raise RuntimeError(data['error'])
    current=data.get('features',[])
    for feature in current:
        ufi=feature['properties']['ufi']
        if ufi in seen:raise RuntimeError('Duplicate rail UFI across API pages')
        seen.add(ufi);features.append(feature)
    digest.update(raw);pages+=1
    if not data.get('exceededTransferLimit') and len(current)<2000:break
else:raise RuntimeError('Rail paging exceeded bounded import limit')
assert features
r={'source':base,'license':'CC BY 4.0','attribution':'State of Victoria (Department of Transport and Planning), Vicmap Transport','fetchedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'bounds':bounds,'query':query,'sourceSha256':digest.hexdigest(),'page_count':pages,'features':features}
(ROOT/'assets/source/environment/city-rails-expanded.json').write_text(json.dumps(r,separators=(',',':'))+'\n');print('Retained expanded official railway features:',len(features))
