"""Source-bounded gable interpretation for Town Hall upper section27720."""
from pathlib import Path
import json,math
from shapely.geometry import Polygon,LineString
from shapely.ops import split,unary_union
from shapely import constrained_delaunay_triangles
R=Path(__file__).resolve().parents[1];d=json.loads((R/'assets/source/environment/town-hall-source-reference.json').read_text());r=next(x for x in d['records'] if x['objectid']=='27720');p=Polygon([((x-144.9671)*87939,(y+37.8183)*111320) for x,y in r['geo_shape']['geometry']['coordinates'][0]]);q=list(p.minimum_rotated_rectangle.exterior.coords)[:-1];a,b=max([(q[i],q[(i+1)%4]) for i in range(4)],key=lambda ab:math.dist(*ab));length=math.dist(a,b);ux,uy=(b[0]-a[0])/length,(b[1]-a[1])/length;nx,ny=-uy,ux;cx,cy=p.minimum_rotated_rectangle.centroid.coords[0];half=max(abs((x-cx)*nx+(y-cy)*ny) for x,y in q);bottom=r['footprint_min_elevation']-r['structure_min_elevation'];top=r['footprint_max_elevation']-r['structure_min_elevation'];ridge=LineString([(cx-ux*100,cy-uy*100),(cx+ux*100,cy+uy*100)]);parts=split(p,ridge);v=[];f=[];mi=[];tris=[]
def z(x,y):return bottom+(top-bottom)*max(0,1-abs((x-cx)*nx+(y-cy)*ny)/half)
for part in parts.geoms:
 for t in constrained_delaunay_triangles(part).geoms:
  coords=list(t.exterior.coords)[:-1]
  if (coords[1][0]-coords[0][0])*(coords[2][1]-coords[0][1])-(coords[1][1]-coords[0][1])*(coords[2][0]-coords[0][0])<0:coords.reverse()
  start=len(v);v.extend([[x,y,z(x,y)] for x,y in coords]);f.append([start,start+1,start+2]);mi.append(0);tris.append(t)
 for aa,bb in zip(list(part.exterior.coords),list(part.exterior.coords)[1:]):
  edge=LineString([aa,bb])
  if p.boundary.distance(edge.interpolate(.5,normalized=True))>.001:continue
  start=len(v);v.extend([[aa[0],aa[1],bottom],[bb[0],bb[1],bottom],[bb[0],bb[1],z(*bb)],[aa[0],aa[1],z(*aa)]]);f.append([start,start+1,start+2,start+3]);mi.append(1)
assert unary_union(tris).symmetric_difference(p).area<.00001
out={'source_id':'27720','roof_type':r['roof_type'],'vertices':v,'faces':f,'materials':mi,'outline':list(p.exterior.coords),'top':top,'area_m2':p.area,'limits':'Recorded Gable classification, footprint, relative base24.4m and top29.9m retained. Ridge follows longer minimum-rectangle axis; profile symmetric and roof finish authored. Near-square footprint makes direction uncertain; exact main-hall form, finish and current roof works unverified.','conservation_reference':'https://www.lovellchen.com.au/projects/melbourne-town-hall/'};(R/'assets/source/environment/town-hall-authored-gable.json').write_text(json.dumps(out,indent=2)+'\n');print('VERIFIED gable plan',p.area,'faces',len(f))
