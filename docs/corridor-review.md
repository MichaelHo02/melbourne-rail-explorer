# Flinders Street–Southern Cross environment pass

The western surface corridor now combines official horizontal geography with an authored railway structure and close-view materials. This follows the [Void Explorer build approach](https://developers.openai.com/blog/how-to-build-games-with-astra): keep simulation independent, prepare world geometry separately, author distinctive assets in Blender, and inspect named scenes through the real game renderer.

## What changed

- Replaced the approximate street grid with Vicmap road, path and bridge alignments. Distinct paved footways, asphalt, markings and mapped tram rails provide street context. Divided dual-line roads use a per-carriageway visual width.
- Bridge spans use exact segment/polygon intersection, including two-point features whose endpoints are both on land. Decks align with retained survey bridge tops where available. A graph of connected source streets gives approaches a smooth 60m elevation transition; geometrically crossing riverside paths retain their separate level. These elevations and widths are authored presentation, not engineering survey data.
- Added 3,100 mapped trees with species-aware palm/deciduous presentation, instanced in 200m cells. Tree sizes are inferred. Inferred crowns under the approximate viaduct are shortened for clearance; tree coordinates stay unchanged.
- Added selected official park parcels, Yarra bank walls and paved walks. Open-space records describing promenades and the Aquarium are not automatically painted as grass.
- Added the original [Blender viaduct kit](viaduct-assets.md): riveted girders, ornamental fascia and crossed-loop railings, bluestone supports and eastern masonry vaults. Six-track context, gantries and overhead wires surround the playable line. Track count/spacing, structure placement and vertical datum are authored.
- Replaced one conflicting survey footprint, object `19385`, with the viaduct. This long bank-side bridge polygon does not cross the Yarra; its source top otherwise creates a slab through the cab sightline. Nearby structures and river crossings remain.
- Replaced identical checkerboard facades with physically scaled glass, masonry, concrete and industrial families. Real building footprints and relative heights remain; generated facades are not observations of each building. Survey bridges/jetties now form thin matte decks instead of window-covered solid extrusions.
- Added bundled CC0 diffuse/normal/roughness maps for ballast, asphalt and paving. Reduced ambient fill to give surfaces more directional shading. Sunlit platforms keep visible lamp fittings while their redundant point lights are omitted; enclosed stations retain local illumination. The Yarra retains its official outline and WebGPU water material.

## Asset and rendering boundaries

The viaduct GLB is 1,351,588 bytes, with three shared materials. Geometry is instanced in 96m cells; ornamental spans render nearby, with a 348-triangle span beyond 190m and a distant cutoff. Internal fascia and railings are removed from parallel strips, keeping the driven track clear. Supports stretch below their fixed bearing datum to meet the approximate ground. Native WebGPU, shadows and the existing high-quality lighting remain mandatory.

All surface maps and required landmarks load before shader compilation and Start becomes available. Asset failures report a startup error. The corridor is an offline snapshot; it needs no live API key and cannot be affected by an API outage while driving. Sources, transformations and licences are in [corridor data](corridor-data.md), [facade materials](building-materials.md) and [attribution](sources.md).

## Verification

- `npm test`: 30 tests pass, including source-coordinate/axis contracts, source-specific missed river crossings, bent bridges, connected approaches, underpasses, and the existing driving/interlock/save tests.
- Production preview verified ready with WebGPU, enabled Start, and no new console errors or warnings. Existing saved-service entry remains available.
- `npm run build`: strict TypeScript and production bundling pass; the existing guard rejects Three.js WebGL fallback code.
- Blender asset was exported, optimized, re-imported and visually inspected. Original reference photographs are not redistributed.
- Interactive review in the Codex in-app browser confirmed departure, the door traction interlock, acceleration, braking to a stop, and cab/exterior camera switching. Named development scenes isolate departure, viaduct cab, viaduct riverside, river crossings, Southern Cross approach and tunnel. Scenario runs are ephemeral and do not overwrite saved services.
- The integrated viaduct bank view reported WebGPU, 571 draw calls, approximately 1.37 million triangles and a 13.5ms recent average frame interval on this session's browser. The cab view was about 1.39 million triangles. After removing redundant daylight point lights, the Flinders Street river view reported 950 draw calls, 1.72 million triangles and 15.2ms (previously roughly 42–47ms). Southern Cross approach reported 13.2ms and the tunnel 8.3ms. These are observed local samples, not a benchmark or hardware guarantee; screenshots and graphics appearance were inspected separately from build success.

## Remaining fidelity limits

The streets, tree locations, river banks and building envelopes are geographic data; most appearances and all terrain gradients are still authored. The masonry module represents vault structure, not Banana Alley's enclosed modern shopfronts. Parallel context tracks are decorative and do not introduce operational junctions. River-crossing bridge superstructures, individual landmark facades, street furniture and station interiors need more dedicated assets. Water reflects the sky environment rather than nearby buildings.

The official 2020 City of Melbourne photomesh has accessible I3S streaming metadata, documented in the data notes. No photomesh geometry or imagery is included in this pass. A bounded conversion of selected corridor tiles is the clearest next step toward photographic building detail.
