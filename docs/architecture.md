# Architecture and City Loop development direction

Reference: [Building games with Astra](https://developers.openai.com/blog/how-to-build-games-with-astra), Thomas Ricouard, September 4, 2026; [Void Explorer showcase](https://developers.openai.com/showcase/void-explorer).

## Experience

The player operates a train, looking out from its cab into a geographically recognisable Melbourne. The first loop is close doors → accelerate → coast → brake → stop accurately → open doors → board → depart. Failure is recoverable: an overrun records a missed station; the player can continue or restart. The initial target is a desktop browser with accessible keyboard and clickable controls.

## What we adopt from Void Explorer

| Article principle | This implementation |
|---|---|
| TypeScript + Vite + Three.js | A plain TypeScript runtime with a small DOM interface |
| Simulation independent of renderer | Serializable train state, pure route sampling, fixed 60 Hz updates |
| Consistent coordinates and time | Metres, seconds, m/s, local projected geography, one simulation clock |
| Geometry work away from input thread | A worker triangulates measured building footprints into 250 m city chunks |
| Load only useful detail | Merged city chunks, distance culling, instanced sleepers, merged rails and tunnel meshes; multi-LOD asset streaming is a next milestone |
| Screenshot and state inspection | Named departure, approach, and tunnel scenarios, renderer counters, browser screenshots, keyboard tests |
| Preserve gameplay while evolving graphics | The renderer is an adapter around train state; route, station service, and save files do not own Three.js objects |

The article began with WebGL2 and later moved to WebGPU. This prototype starts with **WebGL2**, which is the tested renderer here. A future `three/webgpu` adapter can use TSL and richer atmosphere/materials without replacing train simulation. WebGPU support is not claimed in this build.

## Module ownership

```text
src/data/route.ts       Geographic projection, continuous path sampling, station markers
src/game/simulation.ts Fixed-step train dynamics, controls, dwell, stop results, save validation
src/game/audio.ts      Optional synthesized traction/rail ambience and horn
src/render/renderer.ts Renderer lifecycle, cameras, quality, metrics
src/render/world.ts    Track, tunnel, station and city scene adapters
src/render/city.worker.ts Building triangulation/merging off the main thread
src/render/materials.ts  Generated material textures and station signs
src/render/train.ts    Exterior rolling stock and physical cab framing
src/ui/                DOM HUD, route map, menus, help, styles
src/main.ts            Input mapping, fixed timestep, save lifecycle, composition
```

One route-distance value is authoritative for train position. Camera and each carriage sample the same continuous path. Physics uses acceleration, braking, rolling drag, gravity along the authored grade, and a bounded acceleration-change rate. A train constrained to a single track does not need a general rigid-body engine. Add Rapier only when meaningful free-motion collision physics is introduced; it should not replace the route-distance model.

## Rendering and performance

- City vertices use metre coordinates close to Melbourne CBD. This compact route does not require Void Explorer's astronomical integer-cell coordinate system.
- Buildings are extruded in a worker from source polygons, merged by 250 m cells, and transferred as typed arrays. Current city data is fetched once; this is chunked generation and visibility culling, not a finished network streaming or LOD system.
- Sleepers use instancing. Rails, tunnel lining, viaducts, and furniture geometry are merged where practical.
- Nearby platform lights only; a train headlamp lights tunnels. A movable directional shadow volume follows the train.
- Device pixel ratio is capped. A pause-menu quality switch disables shadows and reduces pixel ratio.
- Tab blur and visibility changes pause simulation. Lost WebGL context pauses and saves; the UI asks for reload rather than pretending recovery succeeded.
- Debug metrics distinguish draw calls, triangles, resources, and observed frame timings. Browser timings must not be described as measured GPU execution times.

## Realism milestones

1. **Playable foundation (this build):** operator controls, one complete official-shape-derived training circuit, real building outlines/heights, surface/tunnel transitions, station service, local save, and reproducible tests.
2. **Track accuracy:** two official DTP route shapes and platform points are integrated; next, use dedicated track/geographic data and validate a named service and direction. Resolve physical railway topology, gradients, broad-gauge alignment, platform markers and clearances against references. Keep source metadata and version the route.
3. **Detailed stations and rolling stock:** a photo-based seven-car HCMT with animated doors, gameplay cab and Blender-authored Flinders Street landmark are integrated, with a characteristic Southern Cross roof. Next refine underground station interiors, verified cab proportions, platform fittings and recorded/licensed audio. Do not infer station interiors from building footprints.
4. **City photogrammetry:** evaluate the City of Melbourne 2018 photomesh. Crop only corridor-visible tiles, transform MGA55/AHD coordinates into the local frame, convert OBJ/MTL/JPG to GLB, create LODs and KTX2 textures, and stream ahead of the train. Keep nearby authored railway assets detailed and distant city assets inexpensive. Validate licensing and retain attribution per asset.
5. **Operational simulation:** choose a Melbourne fleet and route era, then calibrate traction/braking, signals, blocks, speed boards, traffic and timetables. Introduce optional live data only after simulated operation is coherent.

## Why live API data is not required yet

Player-controlled movement immediately diverges from a real vehicle feed. The game owns the player train's state. GTFS Schedule is the eventual service/network input; GTFS Realtime can provide background traffic or seeded scenarios through a cached server adapter. Secrets must stay server-side. A stable bundled route allows play while paused, offline, or without an API key.
