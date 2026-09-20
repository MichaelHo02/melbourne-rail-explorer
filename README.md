# Melbourne Rail Explorer

A desktop-browser train-driving prototype through Melbourne's City Loop. Take the driver's seat, work the throttle and brakes, stop at platforms, board passengers, and complete a circuit.

![Blender-authored Melbourne HCMT game model](docs/images/hcmt-preview.png)

*Original Blender asset based on Melbourne HCMT photographic reference. This is a game recreation, not manufacturer CAD.*

```sh
npm install
npm run dev
```

Open the local URL printed by Vite. A WebGPU-capable browser and GPU are required. `npm run build` creates a static site in `dist/`.

## Graphics

The renderer uses Three.js's native WebGPU backend, with TSL height-aware haze and animated Yarra water normals. Shadows, antialiasing and the current high-quality lighting are always enabled. The train simulation, controls and saves remain independent of the renderer. Start stays disabled until graphics, assets and initial material compilation finish. If WebGPU cannot initialize, the game shows an error and leaves the service unavailable.

There is no WebGL rendering path or reduced-quality mode. The production build rejects inclusion of Three.js's WebGL fallback backend. Development builds expose the backend and frame statistics on the canvas dataset; `/?view=river&scene=departure` selects a water inspection camera. The Flinders Street–Southern Cross corridor combines official map geometry, selected City of Melbourne 2020 photographic mesh, mapped vegetation, PBR surfaces and an instanced Blender viaduct with distance-based detail. All five stations have reference-based fittings and Blender-built commuters. Platforms use metre-scaled surface textures; station lights follow the canopies and underground soffits. Nearby commuters have varied coats, jackets, hair and bags, planted feet, subtle breathing and independent head glances driven by the simulation clock. Underground platforms have framed tunnel mouths, end gates and recessed circulation openings. The northbank uses mapped park lawns and a low stone edge; foreground viaduct buildings retain complete surveyed facades where coarse aerial fragments conflicted with the playable scene.

## Controls

| Input | Action |
|---|---|
| W / Up | Move controller toward power |
| S / Down | Move controller toward braking |
| D | Open / close doors |
| Space | Emergency brake |
| C | Cab / exterior camera |
| M | Route map |
| H | Horn (enable sound first) |
| Escape | Pause / resume |

The controller has four brake notches, coast, and four power notches. Stop within eight metres of the station marker to open doors. Boarding takes eight seconds. Doors lock out traction. Within 650 metres of the next stop, a training guide estimates the stopping point using the same physics and gradients as the train; it shows when to begin braking and whether the current brake setting stops short or beyond the marker. Pausing or leaving the tab saves progress locally; a new visit offers Continue saved service. No account or API key is needed for the included offline dataset.

## What is geographically grounded

- Five cropped photographic city patches (36 MB) from City of Melbourne’s May 2020 aerial survey, with source hashes and worker-based triangle clipping around the playable railway, stations and riverbanks. The source files remain unchanged.
- 8,533 measured building sections from City of Melbourne's **2023 Building Footprints** dataset, cropped to the CBD. The source contains capture dates including 2018; the dataset name is not a guarantee of contemporary scenery.
- Projected local metre coordinates anchored near Flinders Street, with measured building footprints, vertical offsets, and extrusion heights.
- Official Transport Victoria route shape legs and station coordinates, assembled into a continuous five-station training circuit.
- The Yarra's variable-width water boundary from Victoria's Vicmap Hydro dataset, including the central-city banks.
- 804 official Vicmap road/path/bridge segments and 188 rail/tram segments in the western corridor, with surface tram alignments rendered.
- 3,100 City of Melbourne tree locations and 40 official open-space parcels; selected park parcels provide grass areas. Tree shapes and road widths are authored, not measured.

## Prototype boundaries

The horizontal railway is derived from **official Transport Victoria route shapes**, joined into a training circuit; elevations, junction transition and closure are authored. It is not surveyed track. The single playable training circuit is Flinders Street → Southern Cross → Flagstaff → Melbourne Central → Parliament → Flinders Street. It does not model all four actual City Loop tunnels or represent a particular current timetable.

The seven-car HCMT exterior is recreated in Blender from photographic reference, with animated doors and an editable source file. Flinders Street has an authored heritage façade; Southern Cross has its characteristic wave roof. The PT-inspired interface uses navy, blue and white wayfinding, with local system fonts.

Building outlines, heights and river boundaries use real data, but this is **not yet a photorealistic recreation**. Outside the photographic patches, building façades remain authored. Station interiors, ground elevations, road widths, bridge approaches, tree sizes, river level and bank structures, gradients and cab controls remain approximations. Roads and mapped vegetation use official horizontal locations. Water reflects the sky environment; it does not yet mirror nearby buildings. Surrounding trains replay the official **19 September 2026** timetable, starting at 06:42. The surface corridor shows a visual subset on authored adjacent tracks with illustrative HCMT models; these are not observed live positions or verified fleet assignments. No accurate signalling, switches, operational safety systems, or collisions with other trains are claimed. Train braking and acceleration are deliberately approachable and are not fleet-calibrated.

Sound is opt-in. Southern Cross field ambience, Flinders/Swanston exterior traffic and a Parliament train departure are licensed historical recordings. Door mechanisms, controller detents and brake pressure cues are original synthesized effects. Service captions and a short cue are authored; there is no clean, dynamic spoken announcement bank. People have varied resting poses, local head/breathing animation and Blender walking cycles. Four commuters walk in clear platform lanes and six can board through nearby doors during a served stop. Movement pauses and restores with the service. This is authored ambient behaviour, not crowd navigation, alighting or facial animation.

See [architecture](docs/architecture.md) for the Void Explorer-inspired boundaries and the realistic-asset integration path, and [sources](docs/sources.md) for provenance and attribution.

## Validation

```sh
npm test              # Physics, interlocks, station service, save validation, route continuity
npm run test:browser  # Installed Google Chrome; launch, keyboard controls, save, screenshots
npm run build        # Strict TypeScript + production bundle
```

The automated browser harness is optional and uses installed Chrome. Final interactive visual verification is performed in the Codex in-app browser. Browser screenshots are written to ignored `artifacts/`; frame timings are environment-specific, not a hardware performance guarantee.

Development builds expose `window.__RAIL_EXPLORER__` with `state()`, `metrics()`, `scenario(name)`, and validated `restore(state)`. Named scenarios: `departure`, `viaduct`, `approach`, `tunnel`, `platform` (Melbourne Central), `flagstaff`, `parliament`, `southern-cross`. `&view=platform` selects a platform inspection camera; `&view=entrance` checks underground circulation recesses and `&view=northbank` checks the mapped Batman Park edge. Scenario runs do not overwrite saved services. `/?scene=viaduct&view=viaduct` reviews the railway from the river bank; `/?scene=viaduct` reviews the cab. Alternatively open `/?scene=tunnel` in the development server. Debug hooks and query-driven scenarios are not exposed in production.

## Refreshing building data

The runtime ships the compact, attributed `public/data/buildings.json` snapshot (approximately 2.8 MB). To regenerate it, download the official CBD export to `public/data/buildings-raw.json`, then run `node scripts/prepare-city.mjs`. Raw exports are excluded from Git and are not needed to play. The precise query and source are in `docs/sources.md`.

## Design and assets

- [Adapted prompts and article implementation approach](docs/prompt-playbook.md)
- [Blender HCMT source and export pipeline](docs/train-assets.md)
- [Blender viaduct kit, references and rebuild](docs/viaduct-assets.md)
- [Corridor geography and data refresh](docs/corridor-data.md)
- [Northbank references and authored elevation boundaries](docs/corridor-riverbank.md)
- [Cab reference controls and game simplifications](docs/cab-reference.md)
- [Environment fidelity review](docs/corridor-review.md)
- [Photographic city conversion and limitations](docs/photomesh.md)
- [Station photo references](docs/station-visual-references.md)
- [Blender commuter source and rebuild](docs/passenger-assets.md)
- [Timetable replay and live API requirements](docs/traffic-data.md)
- [Licensed Melbourne location audio](docs/audio-sources.md)
- [Ready-made Melbourne model research](docs/model-research.md)
- [Melbourne PT style references](docs/ui-brand-references.md)

Independent fan-made training simulator. Not affiliated with or endorsed by Metro Trains Melbourne, PTV or Transport Victoria. Source access does not grant rights to third-party marks; dataset and HDRI attribution is recorded in [sources](docs/sources.md).
