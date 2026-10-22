"""Build compact attributed central-Melbourne scenery data from official APIs.
Usage: python3 scripts/prepare-corridor.py
Only queries a small corridor; it does not download statewide datasets.
"""
import concurrent.futures,datetime,json,pathlib,urllib.parse,urllib.request
ROOT=pathlib.Path(__file__).resolve().parents[1]
BOUNDS=[144.949,-37.8245,144.972,-37.814]
TRANSPORT='https://vicmap.land.vic.gov.au/agsgis/rest/services/vicmap/Vicmap_Transport/MapServer'
TREES='https://data.melbourne.vic.gov.au/api/explore/v2.1/catalog/datasets/trees-with-species-and-dimensions-urban-forest'
COMMON=['ufi','pfi','feature_type_code']
SPECS={
 'roads':(1,COMMON+['ezi_road_name','class_code','direction_code','structure_name','width_m','length_m','road_seal','div_rd','road_status','vehicular_access','physical_condition']),
 'rails':(3,COMMON+['name','tracks_number_of','structure_type','structure_name','rail_gauge','physical_condition']),
 'roadStructures':(0,COMMON+['name','rotation','length_m','width_m','structure_type','construction_material','height_limit']),
 'railStructures':(2,COMMON+['name','rotation','physical_condition']),
}

def get(url):
 with urllib.request.urlopen(url,timeout=45) as response:j=json.load(response)
 if isinstance(j,dict) and 'error' in j:raise RuntimeError(j['error'])
 return j

def query_url(base,query):return base+'?'+urllib.parse.urlencode(query)

def clip_segment(a,b):
 dx=b[0]-a[0];dy=b[1]-a[1];start=0.;end=1.
 for p,q in [(-dx,a[0]-BOUNDS[0]),(dx,BOUNDS[2]-a[0]),(-dy,a[1]-BOUNDS[1]),(dy,BOUNDS[3]-a[1])]:
  if abs(p)<1e-16:
   if q<0:return None
  elif p<0:start=max(start,q/p)
  else:end=min(end,q/p)
  if start>end:return None
 return [[round(a[0]+t*dx,8),round(a[1]+t*dy,8)] for t in [start,end]]

def clip_geometry(g):
 if g['type']=='Point':
  x,y=g['coordinates'][:2]
  return {'type':'Point','coordinates':[round(x,8),round(y,8)]} if BOUNDS[0]<=x<=BOUNDS[2] and BOUNDS[1]<=y<=BOUNDS[3] else None
 lines=[g['coordinates']] if g['type']=='LineString' else g['coordinates'] if g['type']=='MultiLineString' else None
 if lines is None:raise RuntimeError('Unexpected geometry '+g['type'])
 segments=[]
 for line in lines:
  current=[]
  for a,b in zip(line,line[1:]):
   clipped=clip_segment(a,b)
   if clipped and clipped[0]!=clipped[1]:
    if current and current[-1]==clipped[0]:current.append(clipped[1])
    else:
     if len(current)>1:segments.append(current)
     current=clipped
   elif current:
    if len(current)>1:segments.append(current)
    current=[]
  if len(current)>1:segments.append(current)
 if not segments:return None
 return {'type':'LineString','coordinates':segments[0]} if len(segments)==1 else {'type':'MultiLineString','coordinates':segments}

def transport_layer(item):
 name,(number,fields)=item;base=f'{TRANSPORT}/{number}'
 metadata=get(base+'?f=pjson')
 where="feature_type_code IN ('bridge','tunnel','level_crossing')" if name=='roadStructures' else "feature_type_code IN ('bridge_rail_o','tunnel_rail_o','rail_station')" if name=='railStructures' else '1=1'
 query={'where':where,'geometry':','.join(map(str,BOUNDS)),'geometryType':'esriGeometryEnvelope','inSR':'4326','spatialRel':'esriSpatialRelIntersects','outFields':','.join(fields),'outSR':'4326','returnGeometry':'true','f':'geojson','resultRecordCount':2000}
 raw=get(query_url(base+'/query',query))
 if raw.get('exceededTransferLimit') or len(raw.get('features',[]))>=2000:raise RuntimeError('Pagination required; do not silently truncate.')
 features=[]
 for feature in raw['features']:
  geometry=clip_geometry(feature['geometry'])
  if geometry:features.append({'type':'Feature','geometry':geometry,'properties':{k:v for k,v in feature['properties'].items() if k in fields and v is not None}})
 features.sort(key=lambda f:str(f['properties'].get('ufi','')))
 return name,{'type':'FeatureCollection','features':features}, {'url':base,'catalogueUrl':'https://discover.data.vic.gov.au/dataset/vicmap-transport-road-line' if name=='roads' else 'https://discover.data.vic.gov.au/dataset/vicmap-transport','license':'CC BY 4.0','licenseUrl':'https://creativecommons.org/licenses/by/4.0/','attribution':'© State of Victoria (Department of Transport and Planning), Vicmap Transport. Clipped and selected attributes.','query':query,'fields':[{k:f[k] for k in ['name','type','alias'] if k in f} for f in metadata['fields'] if f['name'] in fields]}

def tree_layer():
 metadata=get(TREES)
 query={'where':f'longitude >= {BOUNDS[0]} AND longitude <= {BOUNDS[2]} AND latitude >= {BOUNDS[1]} AND latitude <= {BOUNDS[3]}','select':'com_id,common_name,scientific_name,diameter_breast_height,located_in,longitude,latitude'}
 raw=get(query_url(TREES+'/exports/json',query));species=sorted(set((b.get('common_name') or '',b.get('scientific_name') or '') for b in raw));species_index={s:i for i,s in enumerate(species)}
 features=[]
 for b in raw:
  properties={'com_id':b['com_id'],'species':species_index[(b.get('common_name') or '',b.get('scientific_name') or '')]}
  if b.get('diameter_breast_height') is not None:properties['diameter_breast_height']=b['diameter_breast_height']
  if b.get('located_in'):properties['located_in']=b['located_in']
  features.append({'type':'Feature','geometry':{'type':'Point','coordinates':[round(b['longitude'],8),round(b['latitude'],8)]},'properties':properties})
 features.sort(key=lambda f:str(f['properties']['com_id']))
 provenance={'url':TREES,'catalogueUrl':'https://data.melbourne.vic.gov.au/explore/dataset/trees-with-species-and-dimensions-urban-forest/information/','license':'CC BY 4.0','licenseUrl':metadata['metas']['default']['license_url'],'attribution':'City of Melbourne, Trees with species and dimensions (Urban Forest). Filtered to corridor; species strings dictionary encoded.','dataProcessed':metadata['metas']['default'].get('data_processed'),'query':query,'fields':[{k:f[k] for k in ['name','type','description'] if k in f} for f in metadata['fields'] if f['name'] in query['select'].split(',')],'treeSizeCaveat':'No tree height/crown dimension supplied. DBH unit is unspecified in returned field metadata; retain as raw source attribute, do not treat as metres.'}
 return {'type':'FeatureCollection','features':features},[{'common_name':a,'scientific_name':b} for a,b in species],provenance

def clip_ring(ring):
 points=[p[:2] for p in ring[:-1]]
 for axis,bound,greater in [(0,BOUNDS[0],True),(0,BOUNDS[2],False),(1,BOUNDS[1],True),(1,BOUNDS[3],False)]:
  if not points:return []
  output=[]
  for a,b in zip(points[-1:]+points[:-1],points):
   inside_a=a[axis]>=bound if greater else a[axis]<=bound
   inside_b=b[axis]>=bound if greater else b[axis]<=bound
   if inside_a!=inside_b:
    t=(bound-a[axis])/(b[axis]-a[axis]);point=[a[k]+(b[k]-a[k])*t for k in [0,1]];point[axis]=bound;output.append(point)
   if inside_b:output.append(b)
  points=output
 points=[[round(v,8) for v in p] for p in points]
 return points+[points[0]] if len(points)>=3 else []

def open_spaces():
 base='https://opendata.maps.vic.gov.au/geoserver/wfs'
 query={'service':'WFS','version':'1.0.0','request':'GetFeature','typeName':'open-data-platform:veac_metro_open_space','outputFormat':'application/json','srsName':'EPSG:4326','bbox':','.join(map(str,BOUNDS))+',EPSG:4326','maxFeatures':100}
 raw=get(query_url(base,query))
 if len(raw['features'])>=100:raise RuntimeError('Open space query needs pagination.')
 fields=['veac_id','name','os_group','polygon_source'];features=[]
 for feature in raw['features']:
  g=feature['geometry'];polygons=[g['coordinates']] if g['type']=='Polygon' else g['coordinates'];clipped=[]
  for poly in polygons:
   outer=clip_ring(poly[0])
   if outer:clipped.append([outer]+[ring for hole in poly[1:] if (ring:=clip_ring(hole))])
  if clipped:features.append({'type':'Feature','properties':{k:feature['properties'][k] for k in fields},'geometry':{'type':'MultiPolygon','coordinates':clipped}})
 source={'url':base,'catalogueUrl':'https://discover.data.vic.gov.au/dataset/veac-metropolitan-melbourne-open-space-inventory','license':'CC BY 4.0','licenseUrl':'https://creativecommons.org/licenses/by/4.0/','attribution':'State of Victoria (Department of Energy, Environment and Climate Action), VEAC Metropolitan Melbourne Open Space Inventory. Clipped and selected attributes.','query':query,'fields':[{'name':key,'type':'string'} for key in fields],'caveat':'Public open-space parcels are not lawn cover. Civic squares, promenades, Aquarium and boat berths occur in this inventory. Select named parks deliberately.'}
 return {'type':'FeatureCollection','features':features},source

def road_class_table():
 url=TRANSPORT+'/24/query';query={'where':'1=1','outFields':'road_class_code,road_class','returnGeometry':'false','f':'json'}
 j=get(query_url(url,query));return {str(f['attributes']['road_class_code']):f['attributes']['road_class'] for f in j['features']},{'url':url,'query':query}

def main():
 result={'coordinateSystem':'EPSG:4326','bounds':BOUNDS,'fetchedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'description':'Flinders Street to Southern Cross visual scenery corridor. Real horizontal locations, no authored widths/heights baked into this source.','layers':{},'sources':{}}
 with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
  jobs=[pool.submit(transport_layer,item) for item in SPECS.items()];trees=pool.submit(tree_layer);parks=pool.submit(open_spaces);classes=pool.submit(road_class_table)
  for job in jobs:
   name,collection,source=job.result();result['layers'][name]=collection;result['sources'][name]=source
  collection,species,source=trees.result();result['layers']['trees']=collection;result['treeSpecies']=species;result['sources']['trees']=source
  collection,source=parks.result();result['layers']['openSpaces']=collection;result['sources']['openSpaces']=source
  result['roadClasses'],result['sources']['roadClasses']=classes.result()
 result['modifications']=['Line geometry clipped to rectangle with Liang-Barsky; split parts preserved.','Coordinates rounded to 8 decimal places.','Selected source fields retained; null attributes omitted.','Tree species strings stored once in treeSpecies and referenced by integer properties.species.','Open-space polygons clipped to rectangle, source classifications preserved; not interpreted as lawn cover.','No inferred road polygons, no inferred greenspace polygons, no invented tree coordinates.']
 path=ROOT/'src/data/corridor-source.json';encoded=json.dumps(result,separators=(',',':'))+'\n'
 if len(encoded.encode())>1_000_000:raise RuntimeError('Bundle exceeds 1MB; revise scope before publishing.')
 path.write_text(encoded);counts={k:len(v['features']) for k,v in result['layers'].items()};print(len(encoded.encode()), 'bytes;', counts)
if __name__=='__main__':main()
