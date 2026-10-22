import json
from pathlib import Path
from shapely import Polygon,union_all,constrained_delaunay_triangles
R=Path(__file__).resolve().parents[1];p=json.load(open(R/'assets/source/environment/city-parks-expanded.json'));f=next(f for f in p['layers']['openSpaces']['features'] if f['properties']['reference_p']=='M010918');coords=f['geometry']['coordinates'][0][0];outline=Polygon([((x-144.9671)*87939,(y+37.8183)*111320) for x,y in coords])
# Align plan Collins/Westin/Flinders Lane corners to retained parcel corners.
a=(-30.0,304.28);b=(-.7035,315.5922);c=(32.0118,224.8664)
def xy(u,v):
 t=(u-733)/913;s=(v-365)/297
 return (b[0]+t*(c[0]-b[0])+s*(a[0]-b[0]),b[1]+t*(c[1]-b[1])+s*(a[1]-b[1]))
def rect(x0,y0,x1,y1):return Polygon([xy(x0,y0),xy(x1,y0),xy(x1,y1),xy(x0,y1)]).intersection(outline)
ob=[]
for z in json.load(open(R/'public/data/buildings.json'))['buildings']:
 if z['base']<=.1:ob.append(Polygon([(x,-y) for x,y in z['ring']]).buffer(0))
obstacles=union_all(ob);beds=[rect(*q) for q in [(1072,436,1182,478),(1215,435,1323,478),(1355,435,1467,478),(1468,436,1546,474),(1547,437,1605,464),(1070,614,1183,655),(1216,614,1325,655),(1357,614,1465,655)]];garden=union_all(beds).difference(obstacles);event=rect(1046,497,1485,609).difference(garden).difference(obstacles);stone=outline.difference(garden).difference(event).difference(obstacles)
parts=[]
for finish,shape in [('garden',garden),('granite',event),('bluestone',stone)]:
 v=[];faces=[]
 for t in constrained_delaunay_triangles(shape).geoms:
  q=list(t.exterior.coords)[:3]
  if sum(q[i][0]*q[(i+1)%3][1]-q[(i+1)%3][0]*q[i][1] for i in range(3))<0:q.reverse()
  k=len(v);v.extend((x,y,.34) for x,y in q);faces.append([k,k+1,k+2])
 assert abs(sum(Polygon([v[i][:2] for i in face]).area for face in faces)-shape.area)<.01
 parts.append({'finish':finish,'area_m2':shape.area,'vertices':v,'faces':faces})
out={'garden_rings':[list(g.exterior.coords)[:-1] for g in garden.geoms], 'parts':parts,'source_parcel':f,'reference':'https://bigbuild.vic.gov.au/__data/assets/pdf_file/0015/1016043/Appendix-D_CBD-South-Precinct-Development-Plan_Rev-L.pdf','limits':'Authored approximate surface zones from visually inspected hardscape sheet 01; affine alignment to older unnamed M010918 parcel is not georeferenced as-built geometry. Granite event space and garden-bed arrangement interpreted from plan. Exact colours, joints, levels and planting authored. Ground buildings excluded; station entrance, ancillary structures and cultural artworks remain unmodelled; bed walls and planting are separate authored passes.'};(R/'assets/source/environment/city-square-authored-surfaces.json').write_text(json.dumps(out,separators=(',',':'))+'\n');print([(p['finish'],round(p['area_m2']),len(p['faces'])) for p in parts])
