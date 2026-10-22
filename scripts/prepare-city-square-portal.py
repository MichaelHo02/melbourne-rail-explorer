from pathlib import Path
import json
from shapely import Polygon,union_all,constrained_delaunay_triangles
R=Path(__file__).resolve().parents[1]
def xy(u,v):
 a=(-30,304.28);b=(-.7035,315.5922);c=(32.0118,224.8664);t=(u-733)/913;s=(v-365)/297
 return (b[0]+t*(c[0]-b[0])+s*(a[0]-b[0]),b[1]+t*(c[1]-b[1])+s*(a[1]-b[1]))
ring=[xy(u,v) for u,v in [(856,480),(967,480),(967,601),(856,601)]];hole=Polygon(ring)
base=Polygon([(-8400,-4800),(6300,-4800),(6300,7500),(-8400,7500)])
d=json.load(open(R/'assets/source/environment/city-square-authored-surfaces.json'));p=next(p for p in d['parts'] if p['finish']=='bluestone');stone=union_all([Polygon([p['vertices'][i][:2] for i in f]) for f in p['faces']]);parts=[]
for name,shape,z in [('base',base.difference(hole),-.4),('bluestone',stone.difference(hole),.34)]:
 v=[];f=[]
 for t in constrained_delaunay_triangles(shape).geoms:
  q=list(t.exterior.coords)[:3]
  if sum(q[i][0]*q[(i+1)%3][1]-q[(i+1)%3][0]*q[i][1] for i in range(3))<0:q.reverse()
  k=len(v);v.extend((x,y,z) for x,y in q);f.append([k,k+1,k+2])
 assert abs(sum(Polygon([v[i][:2] for i in face]).area for face in f)-shape.area)<.02
 parts.append({'name':name,'vertices':v,'faces':f,'area_m2':shape.area})
out={'ring':ring,'hole_area_m2':hole.area,'parts':parts,'base_world_bounds':[-8400,-4800,6300,7500],'limits':'Authored opening aligned approximately to retained parcel using visually inspected public hardscape plan; cutting flat scene ground does not establish surveyed station dimensions or levels. Base bounds verified from saved Blender mesh.'};(R/'assets/source/environment/city-square-authored-portal.json').write_text(json.dumps(out,separators=(',',':'))+'\n');print('VERIFIED portal cut',hole.area,[(p['name'],len(p['faces'])) for p in parts])
