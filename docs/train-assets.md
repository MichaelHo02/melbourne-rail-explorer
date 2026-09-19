# HCMT rolling stock: Blender source and runtime assets

The playable train is a photo-based reconstruction of Melbourne's **High Capacity Metro Train (HCMT)**, targeting the user's second reference photograph at Flinders Street. It replaces the earlier generic commuter entirely. This is original Blender geometry delivered as GLB; the editable `.blend` is included. The user's interactive Blender session was preserved by using background Blender processes.

## Reference and fidelity

The source photograph is retained in `assets/source/hcmt-user-reference.png` for local modelling. It was supplied by the user on 19 September 2026; its original photographer and redistribution licence were not supplied. It is **excluded from Git and not shipped in `public/` or displayed by the game**. The first user reference appeared to be a concept rendition; the photograph is the shape/livery target.

Primary corroboration:

- [Evolution Rail: about the HCMT project](https://evolutionrail.com/hcmt-project/about-project/) identifies the train as a seven-car fleet, initially operating Cranbourne/Pakenham and subsequently the Metro Tunnel to Sunbury.
- [Transport Victoria: High Capacity Metro Trains project](https://www.vic.gov.au/high-capacity-metro-trains-project) confirms the actual fleet and service history. A City Loop run should be presented as a training/historical scenario, not a statement about the current 2026 service pattern.
- Evolution Rail's gallery returned HTTP 403 and its linked image assets could not be fetched during this task. No claim is made that inaccessible photographs were inspected.

Modelled identifying details include the tall raked cab and continuous curved nose, graphite front, yellow identification panel, large dark windscreen, low round headlights, white roof rim, blue geometric side wrap, narrow driver-side door/quarterlight, silver sidewalls, blue passenger doors, roof equipment and pantograph. Logo lettering is reconstructed geometry, not an official provided brand asset.

This is a **source-based game recreation, not engineering CAD or a fleet-perfect reproduction**. Car dimensions, exact livery triangles, bogies, roof apparatus and cabin instrumentation remain approximations. The gameplay cab follows the agreed approachable controls and is not a verified replica of the HCMT driver's workplace; the references show only the outside. There are no authentic signalling/control-system claims.

## Runtime contract

- `TrainVisual.ready` resolves only after both GLBs load and rejects on load failure.
- Car local origins are at rail level at their centre. Three.js is Y-up, forward is local −Z; Blender uses Z-up and the glTF exporter converts axes.
- Seven cars use 22.85m centre spacing, approximately 160m total. Shell length is approximately 22.3m, wheel-centre gauge 1.6m, shell width approximately 3m, pantograph height 4.85m.
- The leading car centre sits 11.2m behind the simulation's front position.
- All cars share GPU geometry/materials. Driving nose nodes are visible only at the front and rear (rear reversed); inner cars use the `trailer_*` extension and gangway nodes.
- Twelve `door_*_minus_leaf` / `door_*_plus_leaf` nodes per car slide in local Z. Stable names and independent nodes must survive optimization.
- The camera-local cab is a separate GLB. At the game's 60° vertical FOV, its desk occupies roughly the bottom fifth while leaving the forward sightline clear.
- Lighting is dynamic. No image textures, skeletons or collision meshes are embedded. The spline-constrained train simulation does not need carbody physics collisions. One mesh detail level is used for a bounded seven-car formation.
- `artifacts/train-studio.png` and `artifacts/train-cab.png` document Blender visual review. These establish asset shape and cab framing, not in-game lighting/performance; browser review is separately required.

## Rebuild

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup --python scripts/blender/build_train.py
sh scripts/blender/optimize.sh
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup --python scripts/blender/render_cab.py
```

Blender 5.2.2 and glTF Transform 4.5.0 were used. Optimization deduplicates, welds, conservatively simplifies, prunes and repackages. Scene flattening/joining/instancing are disabled to preserve door articulation. Geometry compression is disabled to avoid an additional runtime decoder. Materials are batched in Blender before export and shared across runtime clones.

## Optimized asset budget

public/models/melbourne-commuter.glb: 1,155,732 bytes; 27,760 triangles; 35 mesh nodes; 59 material primitives; 12 materials; 12 articulated door leaves.

public/models/driver-cab.glb: 91,084 bytes; 2,056 triangles; 8 mesh nodes; 8 material primitives; 8 materials; 0 articulated door leaves.

These are mesh/file measurements. Clones share buffers; fully visible cars still issue material draw calls individually. Shadow passes add work. Browser frame-rate claims require separate runtime measurements.
