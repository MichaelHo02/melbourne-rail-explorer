"""Retain coherent survey facades for seven foreground viaduct structures.
Uses the locally cached official 2023 footprint export. No network/download.
"""
import hashlib, json, math, pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
SOURCE=ROOT/'public/data/buildings-raw.json'
STRUCTURES=['813984','801838','809141','817607','806929','807118','814208']
ORIGIN=[144.9671,-37.8183]
MARGIN=3
# I3S tile 141755 retains a facade patch 2.48m outside this structure's 3m
# envelope at (-726.40,43.43,116.88), measured from the inspection camera ray.
LOCAL_MARGINS={'817607':6}
# Disconnected remnants measured after the footprint/low-context cuts using
# the viaduct inspection camera. These bounded boxes have 10cm padding only;
# they do not enlarge the full-height photographic building envelopes.
RESIDUAL_FRAGMENTS=[
 {'sourceTile':'viaduct-context/I3S 146111','retainedTrianglesBeforeRepair':31,'measuredBounds':[-735.324826,40,110.048160,-733.165415,53.645716,111.126797],'exclusionBounds':[-735.425,39.9,109.948,-733.065,53.746,111.227]},
 {'sourceTile':'viaduct-context/I3S 141755','retainedTrianglesBeforeRepair':7,'measuredBounds':[-727.127637,40,117.435418,-726.584729,45.398772,119.106239],'exclusionBounds':[-727.228,39.9,117.335,-726.485,45.499,119.207]},
]

def hull(points):
 points=sorted(set(points))
 def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
 low=[];high=[]
 for p in points:
  while len(low)>1 and cross(low[-2],low[-1],p)<=0:low.pop()
  low.append(p)
 for p in reversed(points):
  while len(high)>1 and cross(high[-2],high[-1],p)<=0:high.pop()
  high.append(p)
 return low[:-1]+high[:-1]

def expand(ring,margin):
 # The hull is counter-clockwise. Shift every edge outward by exactly margin;
 # intersect neighbouring shifted lines to retain one convex envelope.
 lines=[]
 for i,a in enumerate(ring):
  b=ring[(i+1)%len(ring)];dx=b[0]-a[0];dz=b[1]-a[1];length=math.hypot(dx,dz)
  nx=dz/length;nz=-dx/length;lines.append((nx,nz,nx*a[0]+nz*a[1]+margin))
 out=[]
 for i,line in enumerate(lines):
  a,b,c=lines[i-1];d,e,f=line;det=a*e-b*d
  if abs(det)<1e-8:continue
  out.append([round((c*e-b*f)/det,3),round((a*f-c*d)/det,3)])
 return out

def main():
 payload=SOURCE.read_bytes();records=json.loads(payload);items=[]
 for structure_id in STRUCTURES:
  records_for_id=[r for r in records if str(r['structure_id'])==structure_id]
  if not records_for_id:raise RuntimeError('Missing surveyed structure '+structure_id)
  points=[]
  for record in records_for_id:
   geometry=record['geo_shape']['geometry'];polygons=geometry['coordinates'] if geometry['type']=='MultiPolygon' else [geometry['coordinates']]
   for rings in polygons:
    for lon,lat in rings[0]:points.append((round((lon-ORIGIN[0])*87939,3),round(-(lat-ORIGIN[1])*111320,3)))
  footprint=hull(points)
  margin=LOCAL_MARGINS.get(structure_id,MARGIN)
  items.append({'structureId':structure_id,'objectIds':sorted(str(r['objectid']) for r in records_for_id),'footprintHullXZ':footprint,'photographicExclusionXZ':expand(footprint,margin),'photographicMarginMetres':margin,'measuredStructureHeight':max(r['structure_extrusion'] for r in records_for_id)})
 document={'source':'City of Melbourne 2023 Building Footprints','url':'https://data.melbourne.vic.gov.au/explore/dataset/2023-building-footprints/','license':'CC BY 4.0','sourceSha256':hashlib.sha256(payload).hexdigest(),'origin':ORIGIN,'purpose':'Keep one coherent surveyed procedural facade for seven foreground viaduct structures instead of overlapping different photographic and procedural storeys. Distant photographic city remains.','selection':'Structure anchors 58–118 m on the city side of route distances 540–920 m, identified in the riverbank/viaduct inspection view.','modifications':'Convex envelope of all source footprint sections; photographic exclusion expands each envelope edge by 3 m, except a verified residual facade patch on structure 817607 requiring 6 m. Two remaining disconnected scan fragments use individually measured bounds with 10cm padding and finite height limits. Complete source object IDs are retained.','structures':items,'residualFragments':RESIDUAL_FRAGMENTS}
 (ROOT/'src/data/photomesh-foreground.json').write_text(json.dumps(document,separators=(',',':'))+'\n')
 print('Prepared',len(items),'foreground structures with',sum(len(i['objectIds']) for i in items),'source sections')
if __name__=='__main__':main()
