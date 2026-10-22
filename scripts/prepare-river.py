"""Fetch and clip authoritative Vicmap Hydro Yarra water geometry (CC BY 4.0).
Run: python3 scripts/prepare-river.py
No credentials or GIS Python packages are required.
"""
import datetime,json,pathlib,urllib.parse,urllib.request
ROOT=pathlib.Path(__file__).resolve().parents[1]
SERVICE='https://vicmap.land.vic.gov.au/agsgis/rest/services/vicmap/Vicmap_Hydro/MapServer/1'
BOUNDS=[144.935,-37.826,144.987,-37.814]
QUERY={'where':"NAME LIKE '%YARRA%'",'geometry':','.join(map(str,BOUNDS)),'geometryType':'esriGeometryEnvelope','inSR':'4326','spatialRel':'esriSpatialRelIntersects','outFields':'*','outSR':'4326','returnGeometry':'true','f':'geojson'}

def clip_ring(ring):
    points=[p[:2] for p in ring[:-1]]
    # Sutherland-Hodgman rectangular clipping. This central-city water reach is
    # connected within this rectangle. Retain detailed bank vertices, no smoothing.
    for axis,bound,greater in [(0,BOUNDS[0],True),(0,BOUNDS[2],False),(1,BOUNDS[1],True),(1,BOUNDS[3],False)]:
        if not points:return []
        output=[]
        for a,b in zip(points[-1:]+points[:-1],points):
            inside_a=a[axis]>=bound if greater else a[axis]<=bound
            inside_b=b[axis]>=bound if greater else b[axis]<=bound
            if inside_a!=inside_b:
                t=(bound-a[axis])/(b[axis]-a[axis]);p=[a[k]+(b[k]-a[k])*t for k in [0,1]];p[axis]=bound;output.append(p)
            if inside_b:output.append(b)
        points=output
    rounded=[]
    for p in points:
        p=[round(v,8) for v in p]
        if not rounded or p!=rounded[-1]:rounded.append(p)
    return rounded+[rounded[0]] if len(rounded)>=3 else []

def main():
    url=SERVICE+'/query?'+urllib.parse.urlencode(QUERY)
    with urllib.request.urlopen(url,timeout=45) as response:data=json.load(response)
    if 'error' in data:raise RuntimeError(data['error'])
    features=[f for f in data['features'] if f['properties'].get('name')=='YARRA RIVER']
    if len(features)!=1 or features[0]['geometry']['type']!='Polygon':raise RuntimeError('Source geometry changed; inspect rather than silently choosing a feature.')
    feature=features[0];rings=[clipped for ring in feature['geometry']['coordinates'] if (clipped:=clip_ring(ring))]
    if len(rings)!=1:raise RuntimeError('Expected one central-city outer ring. Review clipping and holes.')
    result={
      'source':'Vicmap Hydro — Water Area (HY_WATER_AREA_POLYGON)',
      'sourceUrl':SERVICE,
      'catalogueUrl':'https://discover.data.vic.gov.au/dataset/vicmap-hydro-water-polygon',
      'license':'CC BY 4.0','licenseUrl':'https://creativecommons.org/licenses/by/4.0/',
      'attribution':'© State of Victoria (Department of Transport and Planning). Vicmap Hydro, CC BY 4.0. Clipped to central Melbourne for this game.',
      'fetchedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),
      'coordinateSystem':'EPSG:4326','clipBounds':BOUNDS,'query':QUERY,
      'sourceFeature':feature['properties'],
      'geometry':{'type':'Polygon','coordinates':rings},
      'modifications':'Clipped to bounding rectangle; rounded to 8 decimal places. No bank smoothing. Render height is authored separately.'
    }
    path=ROOT/'src/data/river-source.json';path.write_text(json.dumps(result,separators=(',',':'))+'\n')
    print(f'Wrote {path.relative_to(ROOT)}: {len(rings[0])} bank vertices, {path.stat().st_size} bytes.')
if __name__=='__main__':main()
