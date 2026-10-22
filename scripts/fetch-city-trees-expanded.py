"""Retain the public Urban Forest inventory across the survey preview extent."""
import json,urllib.request,urllib.parse,datetime,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
base='https://data.melbourne.vic.gov.au/api/explore/v2.1/catalog/datasets/trees-with-species-and-dimensions-urban-forest/exports/json'
bounds=[144.9671-2000/87939,-37.8183-800/111320,144.9671+1250/87939,-37.8183+1750/111320]
query={'where':f'longitude >= {bounds[0]} AND longitude <= {bounds[2]} AND latitude >= {bounds[1]} AND latitude <= {bounds[3]}','select':'com_id,common_name,scientific_name,diameter_breast_height,located_in,longitude,latitude'}
with urllib.request.urlopen(base+'?'+urllib.parse.urlencode(query),timeout=45) as response:raw=response.read();records=json.loads(raw)
assert isinstance(records,list) and records
assert len({str(r['com_id']) for r in records})==len(records)
result={'source':base,'catalogueUrl':'https://data.melbourne.vic.gov.au/explore/dataset/trees-with-species-and-dimensions-urban-forest/information/','license':'CC BY 4.0','attribution':'City of Melbourne, Trees with species and dimensions (Urban Forest)','fetchedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'query':query,'bounds':bounds,'sourceSha256':hashlib.sha256(raw).hexdigest(),'limits':'Public inventory point locations, not guaranteed current tree condition. Crown height and size remain authored; DBH units not inferred.','records':records}
(ROOT/'assets/source/environment/city-trees-expanded.json').write_text(json.dumps(result,separators=(',',':'))+'\n');print('Retained expanded public tree records:',len(records))
