# Present-day Melbourne corridor workspace

Target: Melbourne as at 5 October 2026. This is an authoring target, not a claim that historical survey assets depict current conditions.

`assets/source/environment/corridor-layout.blend` is the editable Flinders Street–Southern Cross workspace. It contains complete survey sections intersecting local X [-1850, 200], Z [-550, 350] metres, plus the existing detailed William Street / Flinders Street frontage. The reference shells retain IDs, source URL, licence and currency caveats. They are hidden from render and excluded from web export. This first migration publishes the existing detailed frontage from the shared workspace; it does not yet publish the whole city or change railway topology.

## Rebuild and edit

From repository root:

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup --python scripts/blender/build_corridor_layout.py
```

This regenerates the workspace from bundled data and replaces manual edits. For an edited workspace, export without rebuilding:

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background assets/source/environment/corridor-layout.blend --python scripts/blender/build_corridor_layout.py -- --export-only
node scripts/check-viaduct-frontage.mjs
```

Only `PUBLISH - verified frontage` exports to `public/models/environment/corridor-frontage.glb`. Keep complete source envelopes and metadata together when editing. The runtime validates all thirteen source section IDs before removing their procedural counterparts; a failed load retains the survey fallback. Existing foreground masks remain unchanged. Wider city publication needs chunking, clearance validation and current visual evidence before moving reference objects into publish collections.

## Evidence and coordinates

- City of Melbourne [2023 Building Footprints](https://data.melbourne.vic.gov.au/explore/dataset/2023-building-footprints/information/), CC BY 4.0. Official catalogue checked 5 October 2026: May 2023 capture, stacked wall/podium sections, AHD source. Retained project records may contain older capture dates; dataset title alone does not establish individual section currency.
- Existing detailed frontage references and measured section intervals: `docs/viaduct-frontage-assets.md` and `public/models/environment/viaduct-frontage.json`. Facade articulation remains photo-derived and authored; current condition is unverified.
- Existing [2020 photomesh](https://data.melbourne.vic.gov.au/explore/dataset/city-of-melbourne-3d-textured-mesh-photomesh-2020/information/) is historical appearance evidence, not a 2026 observation. It remains loaded through its existing runtime pipeline.
- Origin longitude 144.9671, latitude -37.8183. Blender X east / Y north / Z up; GLB and game X east / Y up / Z south. Units: metres. Elevations retain the prepared relative game datum, not absolute AHD or surveyed rail levels.
- Scene records SHA-256 of the exact prepared survey input. No new geographic measurements, textures or photographs are invented by this importer.

Next evidence work: identify corridor changes since capture; attach dated current photographs or official project records to each replacement; resolve rail elevation/topology from applicable railway evidence. Source-backed approximations must remain labelled until verified.

## Validation on 5 October 2026

Saved Blender scene re-opened: 2,076 reference sections with source ID/licence metadata, five publish objects, metre units. Both fresh build and export-only paths pass the frontage checker (13 sections, bounds, metadata and self-contained GLB). All 126 unit tests and production build pass. Browser narrow-window test passes; city-menu screenshot inspected. Driving browser test fails at the existing door-check camera input flag (`enabled` versus expected `disabled`); identical failure reproduced on unchanged main. No complete driving-browser pass is claimed.
