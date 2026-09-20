"""Extend existing official scenery coverage to the north/east City Loop.
Nonoverlapping rectangles retain the original viaduct dataset unchanged.
Uses the same checked source APIs, field selection and clipping as prepare-corridor.
"""
import importlib.util, json, datetime, concurrent.futures
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('corridor',ROOT/'scripts/prepare-corridor.py')
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
regions=[[144.949,-37.814,144.980,-37.8055],[144.972,-37.8245,144.980,-37.814]]
result={'coordinateSystem':'EPSG:4326','bounds':regions,'fetchedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'layers':{},'treeSpecies':[],'sources':[],'description':'Official north/east City Loop surface context. Positions are source data; dimensions and visual surfaces remain authored.'}
for bounds in regions:
 c.BOUNDS=bounds
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
  jobs=[pool.submit(c.transport_layer,(name,c.SPECS[name])) for name in ['roads','rails']]
  trees=pool.submit(c.tree_layer);parks=pool.submit(c.open_spaces)
  for job in jobs:
   name,collection,source=job.result();result['layers'].setdefault(name,{'type':'FeatureCollection','features':[]})['features'].extend(collection['features']);result['sources'].append(source)
  collection,species,source=trees.result();offset=len(result['treeSpecies']);result['treeSpecies'].extend(species)
  for f in collection['features']:f['properties']['species']+=offset
  result['layers'].setdefault('trees',{'type':'FeatureCollection','features':[]})['features'].extend(collection['features']);result['sources'].append(source)
  collection,source=parks.result();result['layers'].setdefault('openSpaces',{'type':'FeatureCollection','features':[]})['features'].extend(collection['features']);result['sources'].append(source)
encoded=json.dumps(result,separators=(',',':'))+'\n'
if len(encoded)>4_000_000:raise RuntimeError('Extension exceeds 4 MB review budget')
(ROOT/'src/data/loop-landscape-source.json').write_text(encoded)
print(len(encoded),'bytes',{k:len(v['features']) for k,v in result['layers'].items()})
