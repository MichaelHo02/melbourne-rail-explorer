# Driver POV environment survey

The development-only page `/scripts/pov-survey.html?run=UNIQUE-NAME`
loads the normal WebGPU world and captures the seated cab camera every 200 m,
plus endpoints, over Flinders Street–Southern Cross–Flagstaff and
Parliament–Flinders Street. It currently produces 24 views at 1280 × 720.

Each position settles for 60 rendered frames. Time, camera and resolution are
fixed for comparison. PNGs and JSON camera/render metrics are written under
`artifacts/pov-survey/UNIQUE-NAME/`. Use a new name for each run: existing files
are deliberately not overwritten. The capture endpoint only runs in Vite dev,
accepts same-origin loopback requests and writes to this fixed artifact root.

Generate an overview with:

```sh
python3 scripts/pov-contact-sheet.py artifacts/pov-survey/UNIQUE-NAME
```

This is a scene inspection harness, not a driving test. Teleporting between
views does not validate intermediate geometry, collisions or gameplay. Sampled
frame times are diagnostic, not a controlled performance benchmark. Use the
continuous rendered route audit separately.

## 20 September 2026 inspection

`baseline-1280`: all 24 captures completed. This baseline already includes the
initial surveyed-building running-line clearance and lowered-approach tree
filter; it is not a before-image for those changes.

Observed priorities:

- 600–1000 m: relatively continuous viaduct environment; generic facades and
  canopy material still need refinement.
- 1200 m: floating photographic fragments beside Southern Cross approach.
- 1600–1800 m: bare rail-yard surfaces and abrupt terrain boundaries.
- 2000 m and 5000 m: sky visible beside the narrow ballast at tunnel mouths.
- 5200–5400 m: eastern approach needs better bridge/ground connections and
  photographic mesh cleanup.

The first repair adds a continuous concrete bed below ballast through lowered
sections. Surveyed building volumes are now tested against a 6 m-wide running
corridor with vertical clearance, preserving buildings over deep tunnels and
bridges above the train. Trees close to low approaches are excluded before
instancing. These changes do not establish that every decorative mesh is clear;
Blender and aerial meshes require visual and geometric follow-up.

`track-bed-repair`: all 24 matching captures completed. Full-size inspection at
2000 m and 5000 m confirms the sky strips beside the ballast are closed.
Validation: 136 tests across 18 files passed for the clearance changes;
TypeScript and production build passed after the floor repair. The full service
was not rerun for this checkpoint. Floating aerial fragments and unfinished
landscape remain open work under the environment goal.

## Southern Cross fragment repair

The 1200 m capture probe at normalized screen (-0.4, 0.7) identified retained
face 1962 of I3S 158179 at [-1183.1035, 17.7384, 268.0956]. Replaying the runtime
clipper and welding vertices at 1 cm found a detached 163-triangle component.
Its measured bounds are recorded in the foreground preparation script, with
only 10 cm removal padding. `sxs-fragment-repair/01200.png` verifies removal of
the large floating wedge above the left-hand approach, preserving the towers.
Other facade fragments remain visible and still require work.

Use `&at=1200` for a single-position inspection. JSON now includes fixed surface
probes and timing percentiles. The latest counter-timing correction passes the
build but its fresh runtime sample remains unverified: the test tab entered a
connection-error page during a Vite configuration reload. The server was
subsequently confirmed listening on port 5174; no server restart was performed.

Counter follow-up: `counter-verification/01200.json` now reports 615 draw calls
and 2,793,569 triangles, with 44 static timing samples (mean 16.675 ms, p99
17.2 ms). The earlier zero counters were captured after an asynchronous frame
reset; this verification supersedes that pending check. Moving approach
measurements are recorded separately in station-lod-plan.md.

## 21 September: mapped yard earthworks

Scenery rail shoulders now grade at roughly 1:3 to the existing terrain,
limited to 14 m outside the track bed. The playable alignment retains its
26 m centreline exclusion; at the maximum four-track context width this leaves
at least 3.6 m between the shoulder footprint and the sampled running line.
Full-width road proximity suppresses earthwork fill around crossings and nearby
streets. Segment ends are capped below the rails to close exposed undersides.
These are authored terrain connections along Vicmap centrelines, not surveyed
vertical earthwork profiles or operational pointwork.

`yard-shoulders/01800.png` was compared with the original 1800 m capture:
steep/open end silhouettes on the left yard are replaced by continuous grounded
slopes. The track ahead is clear. Bare areas outside these shoulders and aerial
facade fragments remain outstanding. Production build and 11 corridor tests
pass; this local change is not a full environment completion claim.

`eastern-yard-shoulders/05200.png` also confirms connected broad shoulders on
both sides of the eastern running line, with the former exposed olive ground
strips reduced. The elevated foreground building/bridge representation and
coarse nearby photographic facades are still conspicuous and are the next
visual priority.

### Eastern survey structure 816359 — supported rail opening

The 5200m cab ray identified the generic upper storeys of City of Melbourne structure 816359 (sections 16221/16222/16223). Whole-section railway rejection removed its lower envelope, leaving the upper storeys unsupported. A Blender union now retains the three measured footprints and prepared heights, cuts a 24m-wide opening with 7m clearance above the authored rail alignment, and retains walls beside the opening. Eight nearby Vicmap railway segments are also used as clearance cutters. The generated mesh is validated with upward rays at 2m intervals and lateral offsets -3/0/+3m; no intersection occurs in the train clearance volume sampled by those rays. This is not a general collision proof for every object in the world.

The cladding uses an authored sandstone/zinc/glass triangular palette based on [Fed Square's architecture description](https://fedsquare.com/history-design). Exact tenancy and facade dimensions are not established. This asset is an interpretation of a surveyed envelope, not an architectural reconstruction. The runtime checks source IDs and geometry before suppressing procedural fallback sections. The photographic exclusion uses the complete source hull.

Build with `node scripts/export-blender-route.mjs`, then Blender `--background --factory-startup --python scripts/blender/build_federation_east.py`. Source: `assets/source/environment/federation-east.blend`; provenance: `public/models/environment/federation-east.json`. Final GLB is 289,760 bytes and 8,337 triangles. Cladding tessellation was reduced from the initial 881,672-byte / 27,590-triangle version.

Matched 5200m comparison: `eastern-yard-shoulders/05200.png` versus `federation-east/05200.png`. The first replacement adds supporting mass and a visible opening instead of a floating windowed bar. `federation-east-final/05320.png` checks the closer approach; `federation-east-lean/05320.png` checks the optimized cladding. The first, denser version measured 800 draw calls / 4,805,714 triangles versus 788 / 4,753,859 in the prior 5200m scene, including shadow passes. These are scene complexity counts, not a claimed timing improvement. Final approach timings and full-service performance remain part of the wider goal. Build and 16 photographic clipping tests pass.

## Coverage-first landscape pass

Following the user's priority correction, detailed scenery coverage takes
precedence over small LOD timing improvements. The broad urban base now uses
the existing metre-scaled paving PBR material. Mapped open spaces, streets,
water and the existing approach trenches retain their separate geometry.

Rail-yard spaces near Southern Cross, the eastern return and Flinders throat
receive merged gravel ground within 34m of official Vicmap railway centrelines.
This uses 8m cells with deterministic colour variation. Cells avoid roads,
mapped open-space polygons, water and the shallow running trench; no claim is
made that the 34m buffer is a surveyed railway property boundary.

Authored lattice electrification frames follow the training alignment through
the sparse surface approaches where both anchors can be kept clear of mapped
roads, rail widths and the Southern Cross hall. Maintenance ledges sit outside
the six-metre running corridor and have solid support into the graded shoulders.
These are visual context, not a reconstruction of surveyed operating equipment.

`continuous-yard-ground` and `yard-context-final` each completed all 24 matched
views. The contact sheet and full-size 1800m/5200m views confirm the former bare
base patches now connect into gravel shoulders; the 1800m view also shows the
new yard frame and maintenance edges. The 2000m/5000m portal views remain clear.
`yard-supported-ledges/05200.png` checks the final solid ledge support adjustment.
The final contact sheet still shows conspicuous aerial facade remnants and
incomplete building fidelity; these remain open work, not accepted completion.

The tree LOD pass uses baked images from the same Blender prototypes, retains
the detailed near trees and their source positions, and cuts approach geometry.
See station-lod-plan.md for measured tradeoffs and the unresolved first-use
stall. Production build and the existing 138-test suite pass; screenshot timing
is not used as a performance benchmark.

Post-change rendered full service: all six stops served, 37,224 simulation
steps / 1,241 rendered frames, 57 visited 100m cells, maximum rendered travel
gap 6.172m, cab and door-check views exercised, errors `[]`. Final frame:
895 draws / 3,092,431 triangles, WebGPU. This accelerated audit proves service
and rendering continuity; it does not prove a wall-clock frame-rate target.


### Connected Federation foreground repair

The 5400m cab view exposed hanging photographic walls in the Federation Square
precinct. Offline replay of the runtime clipper identified the visible patch in
`flinders-street-context/I3S91823` at `[107.3533,18.4236,-96.9509]`.
Its welded connected component spans multiple source features, so its whole
bounding box is not used as a deletion mask.

Three adjacent official survey structures (806667, 805928, 805929; five source
sections) now have complete Blender envelopes using the existing Federation
east pipeline. Footprint-based photographic masks replace mixed scan/procedural
storeys with coherent geometry. Survey heights are retained as prepared relative
heights; cladding and rail openings are interpretations. Exact tenancies are not
claimed. The source shard contains a sub-decimetre duplicate spike; consecutive
points within 20cm are collapsed before tessellation. Empty exports now fail.

Reproduce with `node scripts/export-blender-route.mjs`, then Blender background
`--python scripts/blender/build_federation_east.py -- STRUCTURE_ID` for each of
the three IDs. Every export checks upward clearance at 2m intervals across the
six-metre running corridor. The authored opening extends 12m to either side and
7m above the training rails; nearby mapped railway lines receive separate cuts.
Successful asset loads replace only their own verified source sections.

`federation-group/05400.png` shows continuous building walls and clear track
through the repaired group. The wider survey remains necessary: this local
repair does not establish whole-route visual completion. Source height datums
still differ between aerial mesh and the flat/relative-height training world;
that needs a systematic terrain solution, not a global guessed vertical shift.

`scripts/inspect-photomesh.mjs` accepts a saved capture JSON and NDC ray pairs.
It reports clipped source faces and connected components without a browser.
These rays inspect photographic geometry only and must be checked against the
image because authored buildings can occlude their hits.

Validation: `federation-corridor` completed all 24 cab captures; contact sheet
inspected. The 5400m opening remains clear and the photographed floating patch
is replaced by continuous walls. Broad Southern Cross–Flagstaff yard context
remains visibly sparse and is the next coverage priority. Production build and
138 tests pass. The rendered full-service audit served all six stops in 1,241
frames, visited 57 100m cells, exercised cab/door-check views, and reported no
errors or browser warnings. Final frame: 913 draws / 3,095,732 triangles on
WebGPU. This is functional validation, not a new frame-time benchmark.
