import fs from 'node:fs';

const buildings = JSON.parse(fs.readFileSync('public/data/buildings.json', 'utf8')).buildings;
const manifest = JSON.parse(fs.readFileSync('public/models/environment/viaduct-frontage.json', 'utf8'));
const runtime = fs.readFileSync('src/render/world.ts', 'utf8');
const glb = fs.readFileSync('public/models/environment/viaduct-frontage.glb');
const fail = message => { throw new Error(`Viaduct frontage check failed: ${message}`); };
const near = (a, b, tolerance = .02) => Math.abs(a - b) <= tolerance;

if (glb.toString('ascii', 0, 4) !== 'glTF' || glb.readUInt32LE(4) !== 2 || glb.readUInt32LE(8) !== glb.length) {
  fail('invalid GLB 2 header or byte length');
}
const jsonChunkLength = glb.readUInt32LE(12);
if (glb.readUInt32LE(16) !== 0x4e4f534a) fail('missing GLB JSON chunk');
const document = JSON.parse(glb.toString('utf8', 20, 20 + jsonChunkLength));
if (document.buffers?.some(buffer => buffer.uri)) fail('asset must not depend on external geometry or textures');

const replacementSet = new Set();
for (const [structureId, details] of Object.entries(manifest.structures)) {
  const wanted = new Set(details.objectIds);
  for (const id of wanted) {
    if (replacementSet.has(id)) fail(`duplicate replacement id ${id}`);
    replacementSet.add(id);
  }
  const sections = buildings.filter(building => wanted.has(String(building.id)));
  if (sections.length !== wanted.size) fail(`${structureId} source section count changed`);
  const coordinates = sections.flatMap(section => section.ring);
  const sourceBounds = [
    Math.min(...coordinates.map(point => point[0])),
    Math.min(...coordinates.map(point => point[1])),
    Math.max(...coordinates.map(point => point[0])),
    Math.max(...coordinates.map(point => point[1])),
  ].map(value => Math.round(value * 10) / 10);
  if (sourceBounds.some((value, index) => value !== details.surveyRingBoundsXZMetres[index])) {
    fail(`${structureId} manifest bounds do not match retained survey rings`);
  }
  const minY = Math.min(...sections.map(section => section.base));
  const maxY = Math.max(...sections.map(section => section.base + section.height));
  if (!near(details.verticalRangeMetres[0], minY) || !near(details.verticalRangeMetres[1], maxY)) {
    fail(`${structureId} vertical manifest does not match the prepared game datum`);
  }
  if (!details.verticalDatum?.includes('footprint_min_elevation - structure_min_elevation')) {
    fail(`${structureId} vertical datum is not documented`);
  }
  if (details.sectionVerticalIntervalsMetres.length !== sections.length || details.sectionVerticalIntervalsMetres.some(interval => {
    const source = sections.find(section => String(section.id) === interval.objectId);
    return !source || !near(interval.base, source.base) || !near(interval.top, source.base + source.height);
  })) fail(`${structureId} per-section vertical intervals do not match prepared source sections`);

  const node = document.nodes.find(candidate => candidate.name === `structure_${structureId}_clean_envelope`);
  if (!node) fail(`${structureId} clean envelope missing from GLB`);
  const extras = node.extras ?? {};
  const exportedIds = new Set(String(extras.source_object_ids ?? '').split(',').filter(Boolean));
  if (String(extras.source_structure_id) !== structureId || exportedIds.size !== wanted.size || [...wanted].some(id => !exportedIds.has(id))) {
    fail(`${structureId} GLB envelope extras do not identify every replaced survey section`);
  }
  const mesh = document.meshes[node.mesh];
  const accessors = mesh.primitives.map(primitive => document.accessors[primitive.attributes.POSITION]);
  const bounds = [
    Math.min(...accessors.map(accessor => accessor.min[0])),
    Math.min(...accessors.map(accessor => accessor.min[1])),
    Math.min(...accessors.map(accessor => accessor.min[2])),
    Math.max(...accessors.map(accessor => accessor.max[0])),
    Math.max(...accessors.map(accessor => accessor.max[1])),
    Math.max(...accessors.map(accessor => accessor.max[2])),
  ];
  const expected = [sourceBounds[0], minY, sourceBounds[1], sourceBounds[2], maxY, sourceBounds[3]];
  if (bounds.some((value, index) => !near(value, expected[index]))) {
    fail(`${structureId} exported envelope bounds differ from the surveyed extents: ${bounds.join(', ')}`);
  }
}

const runtimeIds = runtime.match(/const frontageObjectIds=new Set\(\[([\s\S]*?)\]\)/)?.[1]
  ?.matchAll(/'([^']+)'/g);
if (!runtimeIds) fail('runtime replacement set missing');
const runtimeSet = new Set(Array.from(runtimeIds, match => match[1]));
if (runtimeSet.size !== replacementSet.size || [...replacementSet].some(id => !runtimeSet.has(id))) {
  fail('runtime replacement set does not match the successfully built survey sections');
}
if (!runtime.includes('frontageLoaded&&frontageObjectIds.has(String(b.id))')) {
  fail('runtime must replace source sections only after the GLB loads');
}
if (!runtime.includes('complete.size!==Object.keys(expectedSections).length')) {
  fail('runtime must keep source geometry unless both complete survey envelopes are present');
}

console.log(`Verified two cleaned envelopes, ${replacementSet.size} survey sections, source bounds, self-contained GLB, and load-gated runtime replacement.`);
