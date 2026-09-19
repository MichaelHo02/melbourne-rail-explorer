import fs from 'node:fs';

// City of Melbourne 2023 Building Footprints (CC BY 4.0).
// Input is the official export; retain real footprints and measured vertical extents.
const records = JSON.parse(fs.readFileSync('public/data/buildings-raw.json', 'utf8'));
const origin = [144.9671, -37.8183];
const project = ([lon, lat]) => [Math.round((lon-origin[0])*87939*10)/10, Math.round(-(lat-origin[1])*111320*10)/10];
// Exact raw object IDs, identified from source polygon/route intersections.
// 3295/3296 are the station structure's broad base and gabled roof sections;
// replacing only these retains the separate neighbouring commercial towers.
const southernCrossRoof = new Set(['3295','3296']);
// Platform corridor sample at lateral +2/+4/+6/+8m identifies the following
// connected source stack. Its lower levels occupy the platform; the upper
// parts are retained here in the exclusion to avoid suspended building caps.
const southernCrossPlatformConflict = new Set(['3297','3298','3299','3300','3301','3302','3303']);
// The dataset represents an elevated bridge as an extrusion from relative
// ground, which creates a solid wall over the track instead of an underpass.
const southernCrossBridge = new Set(['4244']);
// This small commercial building overlaps the coarse public service shape
// for 30m immediately south of the station. Remove it for playable clearance;
// this is a game reconciliation, not a claim the real railway passes through it.
const approachShapeConflict = new Set(['28201','28202','28203','28204']);
const excludedCounts={southernCrossRoof:0,southernCrossPlatformConflict:0,southernCrossBridge:0,approachShapeConflict:0};
const buildings = [];
for (const b of records) {
  const {lat,lon} = b.geo_point_2d;
  if (lat < -37.825 || lat > -37.803 || lon < 144.945 || lon > 144.981) continue;
  // Replace the station's survey blocks with our detailed heritage facade.
  if (lon > 144.9634 && lon < 144.9680 && lat > -37.81885 && lat < -37.81745) continue;
  const id=String(b.objectid);
  if(southernCrossRoof.has(id)){excludedCounts.southernCrossRoof++;continue;}
  if(southernCrossPlatformConflict.has(id)){excludedCounts.southernCrossPlatformConflict++;continue;}
  if(southernCrossBridge.has(id)){excludedCounts.southernCrossBridge++;continue;}
  if(approachShapeConflict.has(id)){excludedCounts.approachShapeConflict++;continue;}
  const g = b.geo_shape.geometry;
  const polygons = g.type === 'MultiPolygon' ? g.coordinates : [g.coordinates];
  for (const rings of polygons) {
    const ring = rings[0].map(project);
    let area = 0;
    for (let i=1;i<ring.length;i++) area += ring[i-1][0]*ring[i][1]-ring[i][0]*ring[i-1][1];
    if (Math.abs(area)/2 < 35 || b.footprint_extrusion < 1) continue;
    const base = Math.max(0, b.footprint_min_elevation - b.structure_min_elevation);
    buildings.push({id:b.objectid, ring, base:Math.round(base*10)/10, height:b.footprint_extrusion});
  }
}
fs.writeFileSync('public/data/buildings.json', JSON.stringify({
  source:'City of Melbourne — 2023 Building Footprints',
  url:'https://data.melbourne.vic.gov.au/explore/dataset/2023-building-footprints/',
  license:'CC BY 4.0', origin,
  exclusions:{southernCrossRoof:[...southernCrossRoof],southernCrossPlatformConflict:[...southernCrossPlatformConflict],southernCrossBridge:[...southernCrossBridge],approachShapeConflict:[...approachShapeConflict]}, buildings
}));
console.log(`Prepared ${buildings.length} measured building sections; Southern Cross exclusions: ${JSON.stringify(excludedCounts)}.`);
