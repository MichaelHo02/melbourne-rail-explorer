"""Triangulate retained open-space parcels with holes; surface finishes authored."""
import json
import argparse
from pathlib import Path
from shapely import Polygon, constrained_delaunay_triangles,box,set_precision
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--source',default='src/data/corridor-source.json');parser.add_argument('--output',default='assets/source/environment/city-park-surfaces.json');parser.add_argument('--clip-bounds',nargs=4,type=float);args=parser.parse_args()
s=json.loads((ROOT/args.source).read_text());parts=[]
for feature in s['layers']['openSpaces']['features']:
    p=feature['properties']
    if p.get('os_group')!='Parkland and garden':continue
    polygons=feature['geometry']['coordinates'] if feature['geometry']['type']=='MultiPolygon' else [feature['geometry']['coordinates']]
    for index,rings in enumerate(polygons):
        projected=[[( (lon-144.9671)*87939,(lat+37.8183)*111320) for lon,lat in ring] for ring in rings]
        shape=Polygon(projected[0],projected[1:]).buffer(0)
        if args.clip_bounds:shape=set_precision(shape.intersection(box(*args.clip_bounds)),.01)
        if shape.is_empty:continue
        vertices=[];faces=[];area=0
        for tri in constrained_delaunay_triangles(shape).geoms:
            coords=list(tri.exterior.coords)[:3];a,b,c=coords
            if (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])<0:coords.reverse()
            start=len(vertices);vertices.extend([(x,y,.32) for x,y in coords]);faces.append([start,start+1,start+2]);area+=tri.area
        assert abs(area-shape.area)<max(.01,shape.area*1e-8)
        name=p.get('name','NO DATA');finish=1 if 'Promenade' in name or 'Queensbridge Square' in name else 2 if name in ('NO DATA','Melbourne Aquarium','Yarra River Frontage - Melbourne') else 0
        parts.append({'id':p['veac_id'],'name':name,'index':index,'vertices':vertices,'faces':faces,'area':area,'hole_count':len(rings)-1,'finish':finish})
result={'revision':s.get('sourceSha256','retained-corridor'),'preview_clip_bounds':args.clip_bounds,'source':s['sources']['openSpaces']['url'],'license':s['sources']['openSpaces']['license'],'limits':'Inventory parcel boundaries with holes preserved. Named promenades and civic square use authored paving; unspecified parcels neutral; named parks illustrative grass, not measured land cover. Flat datum and present-day condition unverified.','parts':parts}
(ROOT/args.output).write_text(json.dumps(result,separators=(',',':'))+'\n')
print('Prepared',len(parts),'parcels; holes:',sum(p['hole_count'] for p in parts),'paved:',sum(p['finish']==1 for p in parts))
