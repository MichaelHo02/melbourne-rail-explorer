#!/usr/bin/env python3
"""Prepare the City Loop training corridor from DTP route shapes (CC BY 4.0).

First import: python3 scripts/prepare-route.py --lines lines.geojson --stops stops.geojson --metadata package.json
Rebuild from the small bundled raw extract: python3 scripts/prepare-route.py
No network access required; never imports replacement-bus shapes.
"""
import argparse,json,math,pathlib
ROOT=pathlib.Path(__file__).resolve().parent.parent
OUT=ROOT/'src/data/route-source.json'
IDS=['2-FKN-vpt-1.29.R','2-UFD-vpt-35.17.R']
STOP_IDS=['11217','22191','10921','12197','12199']
p=argparse.ArgumentParser();p.add_argument('--lines');p.add_argument('--stops');p.add_argument('--metadata');args=p.parse_args()
if args.lines:
    metadata=json.load(open(args.metadata))['result']
    assert metadata['license_id']=='cc-by' and '4.0' in metadata['license_title']
    lines=json.load(open(args.lines))['features'];stops=json.load(open(args.stops))['features']
    source={'attribution':'Department of Transport and Planning, Victoria','license':metadata['license_title'],'licenseUrl':metadata['license_url'],'datasetUrl':metadata['full_metadata_url'],'metadataModified':metadata['metadata_modified'],'retrieved':'2026-09-19','sourceLines':[next(f for f in lines if f['properties']['SHAPE_ID']==id and f['properties']['MODE']=='METRO TRAIN') for id in IDS],'sourceStops':[next(f for f in stops if f['properties']['STOP_ID']==id and f['properties']['MODE']=='METRO TRAIN') for id in STOP_IDS]}
else:source=json.load(open(OUT))
a=list(reversed(source['sourceLines'][0]['geometry']['coordinates']));b=source['sourceLines'][1]['geometry']['coordinates']
def distance(a,b):return math.hypot((a[0]-b[0])*87939,(a[1]-b[1])*111320)
assert distance(a[78],source['sourceStops'][2]['geometry']['coordinates'])<30, 'Source shape changed: review Flagstaff splice'
assert distance(b[33],source['sourceStops'][3]['geometry']['coordinates'])<30, 'Source shape changed: review Melbourne Central splice'
# Retain Frankston's western loop through Flagstaff; interpolate across the
# adjacent tunnel alignments over the long straight towards Melbourne Central.
# This splice is a fictional training connection, not an operational turnout.
original=a[:79]+b[33:]
anchors=[list(p) for p in original]
# Match the departure/arrival platform tracks over the final 300 m instead of
# adding a short perpendicular connector at Flinders Street.
offset=[anchors[0][i]-anchors[-1][i] for i in range(2)]
remaining=0
for i in range(len(anchors)-1,-1,-1):
    if i<len(anchors)-1:remaining+=distance(original[i],original[i+1])
    t=max(0,1-remaining/300);weight=t*t*(3-2*t)
    anchors[i]=[round(anchors[i][k]+offset[k]*weight,8) for k in range(2)]
anchors[-1]=anchors[0][:]
source['derivation']='Reverse Frankston shape from Flinders Street through Flagstaff; join Upfield shape towards Melbourne Central, Parliament and Flinders Street. Blend final 300 m to close platform tracks. Horizontal route shapes only; vertical profile is authored. Not a current service or surveyed railway.'
source['coordinates']=anchors
OUT.write_text(json.dumps(source,separators=(',',':'))+'\n')
print(f'Wrote {OUT.relative_to(ROOT)}: {len(anchors)} control points, {OUT.stat().st_size} bytes; {source["license"]}')
