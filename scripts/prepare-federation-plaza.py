"""Reference-informed approximate Main Square paving, not a surveyed boundary."""
import json
from pathlib import Path
from shapely import Polygon,union_all,constrained_delaunay_triangles
root=Path(__file__).resolve().parents[1];buildings=json.loads((root/'public/data/buildings.json').read_text())['buildings'];roads=json.loads((root/'assets/source/environment/city-road-surfaces-expanded.json').read_text())['asphalt']
outline=[[35,35],[52,76],[86,65],[117,56],[148,60],[176,42],[172,17],[146,3],[104,4],[73,11],[43,15]];poly=Polygon(outline)
occupied=union_all([Polygon([(x,-y) for x,y in b['ring']]).buffer(1) for b in buildings if b['base']==0 and Polygon([(x,-y) for x,y in b['ring']]).intersects(poly)])
roadparts=[Polygon([roads['vertices'][i] for i in f]) for f in roads['faces']];poly=poly.difference(occupied).difference(union_all([p for p in roadparts if p.intersects(poly)]))
from shapely.affinity import scale
uncut=Polygon(outline);roadcut=union_all([p for p in roadparts if p.intersects(uncut)]);low,high=.7,1.0
for _ in range(35):
 factor=(low+high)/2;candidate=scale(uncut,xfact=factor,yfact=factor,origin='centroid').difference(occupied).difference(roadcut)
 if candidate.area<5000:low=factor
 else:high=factor
poly=candidate
vertices=[];faces=[]
for tri in constrained_delaunay_triangles(poly).geoms:
 points=list(tri.exterior.coords)[:3];start=len(vertices)
 if (points[1][0]-points[0][0])*(points[2][1]-points[0][1])-(points[1][1]-points[0][1])*(points[2][0]-points[0][0])<0:points.reverse()
 vertices.extend([[x,y,.32] for x,y in points]);faces.append([start,start+1,start+2])
assert abs(sum(Polygon([(vertices[i][0],vertices[i][1]) for i in f]).area for f in faces)-poly.area)<.01
out={'outline':outline,'vertices':vertices,'faces':faces,'area_m2':poly.area,'reference':'https://assets.heritagecouncil.vic.gov.au/assets/Determination-Federation-Square-FINAL.pdf','reference_page':57,'material_reference':'https://fedsquare.com/venues/main-square','limits':'Authored approximate Main Square boundary informed by 2019 precinct diagram, clipped around retained ground-level building envelopes with 1 m margin and road surfaces. Area calibrated to the official 5000 m2 venue figure; boundary still not georegistered or surveyed. Flat .32 m preview level; documented eastward rise of approximately 6 m not yet reconciled with local building datums. Paver sizes, joints and palette authored; artwork not reproduced.'}
(root/'assets/source/environment/federation-authored-plaza.json').write_text(json.dumps(out,indent=2)+'\n');print('VERIFIED plaza preparation',poly.area,len(faces))
