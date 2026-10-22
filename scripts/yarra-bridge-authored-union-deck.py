"""One Kings deck on retained footprint union; retained5m datum explicitly assumed."""
from pathlib import Path
import json
from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely import constrained_delaunay_triangles
ROOT=Path(__file__).resolve().parents[1]
bs=json.loads((ROOT/'public/data/buildings.json').read_text())['buildings'];ids=['39116','39117'];source=[next(b for b in bs if b['id']==sid) for sid in ids]
p=unary_union([Polygon([(x,-y) for x,y in b['ring']]) for b in source]);vertices=[];faces=[]
for tri in constrained_delaunay_triangles(p).geoms:
    xy=list(tri.exterior.coords)[:3]
    if (xy[1][0]-xy[0][0])*(xy[2][1]-xy[0][1])-(xy[1][1]-xy[0][1])*(xy[2][0]-xy[0][0])<0:xy.reverse()
    k=len(vertices);vertices.extend((x,y,5.) for x,y in xy);faces.append([k,k+1,k+2])
part={'name':'Kings','ids':ids,'source_polygons':[b['ring'] for b in source],'old_tops':[5.,11.],'vertices':vertices,'faces':faces,'plane_coefficients':[0.,0.,5.],'datum_basis':'Retained lower5m authored envelope; inferred coherent single deck, not captured elevation.'}
roads=json.loads((ROOT/'assets/source/environment/city-bridge-surfaces.json').read_text())['parts']
road=unary_union([Polygon([q['vertices'][i][:2] for i in f]) for q in roads if q['survey_id'] in ids for f in q['faces']]).intersection(p)
rv=[];rf=[]
for tri in constrained_delaunay_triangles(road).geoms:
    xy=list(tri.exterior.coords)[:3]
    if (xy[1][0]-xy[0][0])*(xy[2][1]-xy[0][1])-(xy[1][1]-xy[0][1])*(xy[2][0]-xy[0][0])<0:xy.reverse()
    k=len(rv);rv.extend((x,y,5.03) for x,y in xy);rf.append([k,k+1,k+2])
part['road_vertices']=rv;part['road_faces']=rf
(ROOT/'assets/source/environment/yarra-bridge-authored-union-deck.json').write_text(json.dumps({'parts':[part],'source':'https://data.melbourne.vic.gov.au/explore/dataset/2023-building-footprints/','capture':'2023 footprint planform only','limits':'Confirmed same Kings Bridge identity/sharedVicmapUFIs; retained source footprint union represented once. Flat5m chosen from retained lower authored layer. Elevation, slab600mm and merged southern approach inferred, not surveyed or current measured. Original layers recoverable.'})+'\n')
