"""Retain public Vicmap roads across the surveyed preview extent."""
import argparse
import json,urllib.request,urllib.parse,datetime,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--feature-type',choices=['road','trail'],default='road');parser.add_argument('--output',default='assets/source/environment/city-roads-expanded.json');args=parser.parse_args()
base='https://vicmap.land.vic.gov.au/agsgis/rest/services/vicmap/Vicmap_Transport/MapServer/1/query'
bounds=[144.942,-37.827,144.984,-37.800]
query=dict(where=f"feature_type_code = '{args.feature_type}' AND road_status = 'O'",geometry=','.join(map(str,bounds)),geometryType='esriGeometryEnvelope',inSR=4326,spatialRel='esriSpatialRelIntersects',outFields='ufi,feature_type_code,ezi_road_name,class_code,direction_code,vehicular_access,div_rd',outSR=4326,returnGeometry='true',f='geojson',resultRecordCount=2000,orderByFields='ufi')
features=[];seen=set();digest=hashlib.sha256();pages=0
for page in range(20):
    page_query={**query,'resultOffset':page*2000}
    with urllib.request.urlopen(base+'?'+urllib.parse.urlencode(page_query),timeout=45) as response:raw=response.read();data=json.loads(raw)
    if 'error' in data:raise RuntimeError(data['error'])
    current=data.get('features',[])
    for feature in current:
        ufi=feature['properties']['ufi']
        if ufi in seen:raise RuntimeError('Duplicate road UFI across API pages')
        seen.add(ufi);features.append(feature)
    digest.update(raw);pages+=1
    if not data.get('exceededTransferLimit') and len(current)<2000:break
else:raise RuntimeError('Road paging exceeded bounded import limit')
assert features
r={'source':base,'license':'CC BY 4.0','attribution':'State of Victoria (Department of Transport and Planning), Vicmap Transport','fetchedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'bounds':bounds,'query':query,'sourceSha256':digest.hexdigest(),'page_count':pages,'features':features}
(ROOT/args.output).write_text(json.dumps(r,separators=(',',':'))+'\n');print('Retained expanded official '+args.feature_type+' features:',len(features))
