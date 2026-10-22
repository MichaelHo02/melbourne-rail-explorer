"""Prepare a bounded northbank vegetation clearance from cached official data.

No scan vertices, hand-picked fragments or downloaded resources are changed.
"""
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'src/data/corridor-source.json'
ORIGIN = [144.9671, -37.8183]
PARCEL_IDS = {'P383229', 'P361466'}
CANOPY_MARGIN = 8


def project(coordinate):
    lon, lat = coordinate
    return [round((lon - ORIGIN[0]) * 87939, 3),
            round(-(lat - ORIGIN[1]) * 111320, 3)]


def inside(point, ring):
    x, z = point
    hit = False
    for i, a in enumerate(ring):
        b = ring[i - 1]
        if (a[1] > z) != (b[1] > z) and x < (b[0] - a[0]) * (z - a[1]) / (b[1] - a[1]) + a[0]:
            hit = not hit
    return hit


def boundary_distance(point, ring):
    result = math.inf
    for i, a in enumerate(ring):
        b = ring[i - 1]
        dx, dz = b[0] - a[0], b[1] - a[1]
        t = max(0, min(1, ((point[0] - a[0]) * dx + (point[1] - a[1]) * dz) / (dx * dx + dz * dz or 1)))
        result = min(result, math.hypot(point[0] - a[0] - dx * t, point[1] - a[1] - dz * t))
    return result


def main():
    payload = SOURCE.read_bytes()
    source = json.loads(payload)
    parcels = []
    for feature in source['layers']['openSpaces']['features']:
        if feature['properties']['veac_id'] not in PARCEL_IDS:
            continue
        geometry = feature['geometry']
        polygons = geometry['coordinates'] if geometry['type'] == 'MultiPolygon' else [geometry['coordinates']]
        parcels.append({'veacId': feature['properties']['veac_id'],
                        'name': feature['properties']['name'],
                        'polygonsXZ': [[list(map(project, ring)) for ring in polygon] for polygon in polygons]})
    if {parcel['veacId'] for parcel in parcels} != PARCEL_IDS:
        raise RuntimeError('The expected northbank parcels are missing from the official cached export.')
    polygons = [polygon for parcel in parcels for polygon in parcel['polygonsXZ']]
    trees = []
    for feature in source['layers']['trees']['features']:
        point = project(feature['geometry']['coordinates'])
        if any((inside(point, rings[0]) or boundary_distance(point, rings[0]) <= CANOPY_MARGIN)
               and not any(inside(point, hole) for hole in rings[1:]) for rings in polygons):
            trees.append({'comId': feature['properties']['com_id'], 'positionXZ': point})
    sources = [{key: source['sources'][name][key] for key in ['catalogueUrl', 'license', 'attribution']}
               for name in ['openSpaces', 'trees']]
    result = {'purpose': 'Remove the low aerial vegetation crowns above the two Batman/Enterprise northbank parcels while retaining their mapped authored trees and lawns.',
              'sourceFile': 'src/data/corridor-source.json', 'sourceSha256': hashlib.sha256(payload).hexdigest(),
              'sources': sources, 'origin': ORIGIN, 'canopyMarginMetres': CANOPY_MARGIN, 'maxHeight': 45,
              'modifications': 'Original projected parcel rings, with an authored 8 m outer-edge canopy buffer and finite 45 m game-height ceiling. Mapped tree IDs/centres document the affected vegetation area; tree heights/crowns are not a survey. No city-wide or full-height building exclusion.',
              'parcels': parcels, 'mappedTrees': sorted(trees, key=lambda t: t['comId'])}
    target = ROOT / 'src/data/photomesh-northbank.json'
    target.write_text(json.dumps(result, separators=(',', ':')) + '\n')
    print(f'Prepared {len(parcels)} northbank parcels and {len(trees)} mapped tree centres; {target.stat().st_size} bytes')


if __name__ == '__main__':
    main()
