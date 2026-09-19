# Melbourne Rail Explorer

A desktop-browser train-driving prototype through Melbourne's City Loop. Take the driver's seat, work the throttle and brakes, stop at platforms, board passengers, and complete a circuit.

![Blender-authored Melbourne HCMT game model](docs/images/hcmt-preview.png)

*Original Blender asset based on Melbourne HCMT photographic reference. This is a game recreation, not manufacturer CAD.*

```sh
npm install
npm run dev
```

Open the local URL printed by Vite. Requires WebGL2. `npm run build` creates a static site in `dist/`.

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

The controller has four brake notches, coast, and four power notches. Stop within eight metres of the station marker to open doors. Boarding takes eight seconds. Doors lock out traction. Pausing or leaving the tab saves progress locally; a new visit offers Continue saved service. No account or API key is needed for the included offline dataset.

## What is geographically grounded

- 8,534 measured building sections from City of Melbourne's **2023 Building Footprints** dataset, cropped to the CBD. The source contains capture dates including 2018; the dataset name is not a guarantee of contemporary scenery.
- Projected local metre coordinates anchored near Flinders Street, with measured building footprints, vertical offsets, and extrusion heights.
- Official Transport Victoria route shape legs and station coordinates, assembled into a continuous five-station training circuit.

## Prototype boundaries

The horizontal railway is derived from **official Transport Victoria route shapes**, joined into a training circuit; elevations, junction transition and closure are authored. It is not surveyed track. The single playable training circuit is Flinders Street → Southern Cross → Flagstaff → Melbourne Central → Parliament → Flinders Street. It does not model all four actual City Loop tunnels or represent a particular current timetable.

The seven-car HCMT exterior is recreated in Blender from photographic reference, with animated doors and an editable source file. Flinders Street has an authored heritage façade; Southern Cross has its characteristic wave roof. The PT-inspired interface uses navy, blue and white wayfinding, with local system fonts.

Building outlines and heights are real, but this is **not yet a photorealistic recreation**. Building façades, station interiors, ground, roads, river, gradients and cab controls remain approximations. No accurate signalling, switches, operational safety systems, live trains, or collisions with other trains are claimed. Train braking and acceleration are deliberately approachable and are not fleet-calibrated.

See [architecture](docs/architecture.md) for the Void Explorer-inspired boundaries and the realistic-asset integration path, and [sources](docs/sources.md) for provenance and attribution.

## Validation

```sh
npm test              # Physics, interlocks, station service, save validation, route continuity
npm run test:browser  # Installed Google Chrome; launch, keyboard controls, save, screenshots
npm run build        # Strict TypeScript + production bundle
```

The automated browser harness is optional and uses installed Chrome. Final interactive visual verification is performed in the Codex in-app browser. Browser screenshots are written to ignored `artifacts/`; frame timings are environment-specific, not a hardware performance guarantee.

Development builds expose `window.__RAIL_EXPLORER__` with `state()`, `metrics()`, `scenario(name)`, and validated `restore(state)`. Named scenarios: `departure`, `approach`, `tunnel`, `platform`. Alternatively open `/?scene=tunnel` in the development server. Debug hooks and query-driven scenarios are not exposed in production.

## Refreshing building data

The runtime ships the compact, attributed `public/data/buildings.json` snapshot (approximately 2.7 MB). To regenerate it, download the official CBD export to `public/data/buildings-raw.json`, then run `node scripts/prepare-city.mjs`. Raw exports are excluded from Git and are not needed to play. The precise query and source are in `docs/sources.md`.

## Design and assets

- [Adapted prompts and article implementation approach](docs/prompt-playbook.md)
- [Blender HCMT source and export pipeline](docs/train-assets.md)
- [Ready-made Melbourne model research](docs/model-research.md)
- [Melbourne PT style references](docs/ui-brand-references.md)

Independent fan-made training simulator. Not affiliated with or endorsed by Metro Trains Melbourne, PTV or Transport Victoria. Source access does not grant rights to third-party marks; dataset and HDRI attribution is recorded in [sources](docs/sources.md).
