import { describe, expect, it } from 'vitest';
import source from '../data/corridor-source.json';
import { project } from '../data/route';
import riverSource from '../data/river-source.json';
import bridgeDecks from '../data/bridge-decks.json';
import { insideRing, riverCrossings, streetElevations, type StreetLine } from './corridor-geography';

type Position=number[];
type Feature={geometry:{type:string;coordinates:unknown};properties:Record<string,unknown>};
const layers=source.layers as unknown as Record<string,{features:Feature[]}>;
function positions(value:unknown):Position[]{
  if(!Array.isArray(value))throw new Error('Expected GeoJSON coordinates');
  if(typeof value[0]==='number')return [value as Position];
  return value.flatMap(positions);
}
const byName=(layer:string,name:string)=>layers[layer].features.filter(f=>f.properties.structure_name===name||f.properties.name===name);
const closestWorldPoint=(features:Feature[],x:number,z:number)=>Math.min(...features.flatMap(f=>positions(f.geometry.coordinates)).map(([lon,lat])=>{
  const p=project(lon,lat);return Math.hypot(p.x-x,p.z-z);
}));

describe('corridor geography contracts',()=>{
  it('retains finite horizontal WGS84 coordinates inside the declared clip and Melbourne world bounds',()=>{
    expect(source.coordinateSystem).toBe('EPSG:4326');
    const [west,south,east,north]=source.bounds;
    for(const [name,layer] of Object.entries(layers)){
      expect(layer.features.length,`${name} must not silently disappear`).toBeGreaterThan(0);
      const invalid=layer.features.find(feature=>positions(feature.geometry.coordinates).some(p=>{
        if(p.length!==2||!p.every(Number.isFinite))return true;
        const [lon,lat]=p,world=project(lon,lat);
        return lon<west-1e-7||lon>east+1e-7||lat<south-1e-7||lat>north+1e-7||
          world.x< -1700||world.x>500||world.z< -500||world.z>750||world.y!==0;
      }));
      expect(invalid,`Invalid or axis-swapped feature in ${name}`).toBeUndefined();
    }
  });

  it('keeps north towards negative Z and resolves known bridge endpoints near the railway origin',()=>{
    expect(project(144.9671,-37.8173).z).toBeLessThan(0);
    expect(project(144.9681,-37.8183).x).toBeGreaterThan(0);
    // Independent metre-scale anchors protect against lon/lat swaps, mirrored
    // latitude and projection-origin drift, without snapshotting all vertices.
    const sandridge=byName('roads','SANDRIDGE PEDESTRIAN BRIDGE');
    expect(sandridge.length).toBeGreaterThan(0);
    expect(sandridge.every(f=>f.properties.feature_type_code==='foot_bridge'&&f.properties.class_code===9)).toBe(true);
    expect(closestWorldPoint(sandridge,-357,199)).toBeLessThan(5);
    const queens=byName('roads','QUEENS BRIDGE');
    expect(queens.length).toBeGreaterThan(0);
    expect(queens.every(f=>f.properties.feature_type_code==='bridge')).toBe(true);
    expect(closestWorldPoint(queens,-502,240)).toBeLessThan(5);
  });

  it('preserves road semantics and usable line segments rather than reducing everything to roads',()=>{
    const kinds=new Set(layers.roads.features.map(f=>f.properties.feature_type_code));
    for(const kind of ['road','trail','bridge','foot_bridge','tunnel'])expect(kinds.has(kind)).toBe(true);
    for(const feature of [...layers.roads.features,...layers.rails.features]){
      expect(['LineString','MultiLineString']).toContain(feature.geometry.type);
      const parts=(feature.geometry.type==='LineString'?[feature.geometry.coordinates]:feature.geometry.coordinates) as number[][][];
      expect(parts.every(line=>line.length>=2&&line.some(p=>p[0]!==line[0][0]||p[1]!==line[0][1]))).toBe(true);
    }
    // These two-point bridge segments have no vertex in the river interior.
    // Keep them available for the segment-crossing geometry regression.
    for(const id of [62504807,62504838]){
      const feature=layers.roads.features.find(f=>f.properties.ufi===id);
      expect(feature?.properties.feature_type_code).toBe('foot_bridge');
      expect(feature?.properties.ezi_road_name).toBe('SOUTH WHARF PROMENADE');
    }
  });

  it('retains named park polygons and closed rings, separately from paved promenade parcels',()=>{
    const parks=byName('openSpaces','Batman Park and Enterprise Park');
    expect(parks.length).toBeGreaterThan(0);
    expect(byName('openSpaces','Alexandra Gardens').length).toBeGreaterThan(0);
    expect(byName('openSpaces','Southbank Promenade').length).toBeGreaterThan(0);
    for(const feature of layers.openSpaces.features){
      expect(['Polygon','MultiPolygon']).toContain(feature.geometry.type);
      const polygons=(feature.geometry.type==='Polygon'?[feature.geometry.coordinates]:feature.geometry.coordinates) as number[][][][];
      for(const rings of polygons)for(const ring of rings){
        expect(ring.length).toBeGreaterThanOrEqual(4);
        expect(ring.at(-1)).toEqual(ring[0]);
      }
    }
    // Batman Park lies west of Flinders Street on the northern riverbank.
    expect(parks.flatMap(f=>positions(f.geometry.coordinates)).every(([lon,lat])=>lon<144.963&&lat> -37.823)).toBe(true);
  });

  it('keeps tree species dictionary references valid and source identity intact',()=>{
    const trees=layers.trees.features;
    expect(new Set(trees.map(f=>String(f.properties.com_id))).size).toBe(trees.length);
    for(const tree of trees){
      expect(tree.geometry.type).toBe('Point');
      const species=tree.properties.species as number;
      expect(Number.isInteger(species)&&species>=0&&species<source.treeSpecies.length).toBe(true);
      expect(typeof source.treeSpecies[species].common_name).toBe('string');
    }
    // This file is geography, not a survey of rendered tree height or deck Y.
    expect(source.sources.trees.treeSizeCaveat).toContain('unit is unspecified');
  });
});

describe('river crossing and bridge approach geometry',()=>{
  const rectangle=[{x:0,z:-5},{x:10,z:-5},{x:10,z:5},{x:0,z:5},{x:0,z:-5}];

  it('clips a crossing to both banks even when both source endpoints are on land',()=>{
    const road=[{x:-5,z:0},{x:15,z:0}];
    expect(road.every(p=>!insideRing(p,rectangle))).toBe(true);
    expect(riverCrossings(road,rectangle)).toEqual([{a:{x:0,z:0},b:{x:10,z:0}}]);
    expect(riverCrossings([...road].reverse(),rectangle)).toEqual([{a:{x:10,z:0},b:{x:0,z:0}}]);
    expect(riverCrossings([{x:-5,z:10},{x:15,z:10}],rectangle)).toEqual([]);
    expect(riverCrossings([{x:5,z:0},{x:5,z:0}],rectangle)).toEqual([]);
  });

  it('separates multiple water intervals across a concave bank instead of bridging the intervening land',()=>{
    const bank=[{x:0,z:-2},{x:10,z:-2},{x:10,z:2},{x:7,z:2},{x:7,z:-1},{x:3,z:-1},{x:3,z:2},{x:0,z:2},{x:0,z:-2}];
    expect(riverCrossings([{x:-1,z:0},{x:11,z:0}],bank)).toEqual([
      {a:{x:0,z:0},b:{x:3,z:0}},
      {a:{x:7,z:0},b:{x:10,z:0}},
    ]);
  });

  it('detects the real two-point South Wharf footbridges missed by vertex-only water tests',()=>{
    const bank=riverSource.geometry.coordinates[0].map(([lon,lat])=>project(lon,lat));
    for(const id of [62504807,62504838]){
      const feature=layers.roads.features.find(f=>f.properties.ufi===id)!;
      const road=positions(feature.geometry.coordinates).map(([lon,lat])=>project(lon,lat));
      expect(road.every(p=>!insideRing(p,bank))).toBe(true);
      const spans=riverCrossings(road,bank);
      expect(spans.length).toBeGreaterThan(0);
      for(const {a,b} of spans){
        expect(Math.hypot(b.x-a.x,b.z-a.z)).toBeGreaterThan(1);
        expect(insideRing({x:(a.x+b.x)/2,z:(a.z+b.z)/2},bank)).toBe(true);
      }
    }
  });

  it('keeps a bent bridge component level and joins its connected approaches without steps',()=>{
    const lines:StreetLine[]=[
      {points:[{x:0,z:0},{x:5,z:0},{x:5,z:5}],walking:false,bridge:true,deck:5.5},
      {points:[{x:5,z:5},{x:10,z:5}],walking:false,bridge:true},
      {points:Array.from({length:14},(_,i)=>({x:-i*5,z:0})),walking:false,bridge:false},
      {points:Array.from({length:14},(_,i)=>({x:10+i*5,z:5})),walking:false,bridge:false},
    ];
    const heights=streetElevations(lines);
    expect(heights[0]).toEqual([5.5,5.5,5.5]);
    expect(heights[1]).toEqual([5.5,5.5]);
    for(const approach of heights.slice(2)){
      expect(approach[0]).toBe(5.5);
      expect(approach[6]).toBeCloseTo(2.34,10);
      expect(approach[12]).toBeCloseTo(-.82,10);
      expect(approach[13]).toBeCloseTo(-.82,10);
      for(let i=1;i<approach.length;i++){
        expect(approach[i]).toBeLessThanOrEqual(approach[i-1]);
        expect(approach[i-1]-approach[i]).toBeLessThan(.8);
      }
    }
  });

  it('keeps an unconnected perpendicular crossing and a coincident footway below the road deck',()=>{
    const heights=streetElevations([
      {points:[{x:0,z:0},{x:10,z:0}],walking:false,bridge:true,deck:5.5},
      // Crosses geometrically, but has no shared source-network vertex.
      {points:[{x:5,z:-5},{x:5,z:5}],walking:false,bridge:false},
      // Same coordinates are not sufficient to connect different transport levels.
      {points:[{x:0,z:0},{x:10,z:0}],walking:true,bridge:false},
    ]);
    expect(heights).toEqual([[5.5,5.5],[-.82,-.82],[-.82,-.82]]);
  });

  it('avoids abrupt height drops on densified real bridge and approach lines',()=>{
    const bank=riverSource.geometry.coordinates[0].map(([lon,lat])=>project(lon,lat));
    const decks=bridgeDecks.map(d=>({top:d.top,ring:d.ring.map(([x,z])=>({x,z}))}));
    const streets:StreetLine[]=[];
    const identities:unknown[]=[];
    for(const feature of layers.roads.features){
      const kind=feature.properties.feature_type_code;
      if(kind==='tunnel')continue;
      const parts=(feature.geometry.type==='LineString'?[feature.geometry.coordinates]:feature.geometry.coordinates) as number[][][];
      for(const part of parts){
        const original=part.map(([lon,lat])=>project(lon,lat));
        const points=[original[0]];
        for(let i=1;i<original.length;i++){
          const a=original[i-1],b=original[i],steps=Math.ceil(Math.hypot(b.x-a.x,b.z-a.z)/5);
          for(let k=1;k<=steps;k++)points.push({x:a.x+(b.x-a.x)*k/steps,y:0,z:a.z+(b.z-a.z)*k/steps});
        }
        const bridge=kind==='bridge'||kind==='foot_bridge';
        const crossings=bridge?riverCrossings(original,bank):[];
        const measured=crossings.flatMap(({a,b})=>decks.filter(d=>insideRing({x:(a.x+b.x)/2,z:(a.z+b.z)/2},d.ring)).map(d=>d.top));
        streets.push({points,walking:kind==='trail'||kind==='foot_bridge'||Number(feature.properties.class_code)===9,bridge,
          deck:crossings.length?(measured.length?Math.max(...measured)+.03:3.3):undefined});
        identities.push(feature.properties.ufi);
      }
    }
    const heights=streetElevations(streets);
    for(let i=0;i<heights.length;i++){
      expect(heights[i].every(Number.isFinite)).toBe(true);
      for(let j=1;j<heights[i].length;j++){
        expect(Math.abs(heights[i][j]-heights[i][j-1]),`Abrupt drop on source UFI ${identities[i]}`).toBeLessThan(2);
      }
    }
    const formerlyBroken=identities.indexOf(56721397);
    expect(formerlyBroken).toBeGreaterThanOrEqual(0);
    expect(Math.max(...heights[formerlyBroken])-Math.min(...heights[formerlyBroken])).toBeLessThan(.01);
  });
});
