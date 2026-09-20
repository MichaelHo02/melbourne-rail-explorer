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

### Shared yard formation and restored nearby tracks

The 1800m view showed a largely empty strip beside the training line despite
available Vicmap railway centrelines. The former fixed 26m rejection removed
narrow safe track beds. Clearance now measures each candidate segment against
the sampled route polyline, subtracts half its length for a conservative whole-
segment bound, and reserves 8m beyond the complete track-bed/shoulder footprint.
Beds without at least a 4m shoulder are omitted; four-track widths remain wider.

An initial comparison (`yard-track-clearance`) exposed artificial raised pads:
Southern Cross context rails were hardcoded to elevation 3m. Both yards now use
the same nearest-route gradient, clamped to nonnegative height. Shared gravel
formation rises to 6cm below the rails, blends down over its outer 12m and fades
away beside the running line. Existing road, park, water and shallow-trench
exclusions remain. This is authored terrain adaptation to the training gradient,
not an elevation survey or an operational railway reconstruction.

The matched `yard-connected/01800.png` confirms visible neighbouring rails and
connected gravel rather than isolated tall embankments. Its 44-frame sample
measured 16.675ms mean, 17.7ms maximum, 459 draws and 1,651,661 triangles;
`federation-corridor/01800.png` measured 16.670ms mean, 17.4ms maximum, 461 draws
and 1,610,753 triangles. These short static samples are a smoke check, not a
controlled performance comparison. Production build and all 138 tests pass.

`yard-formation-route` completed all 24 captures; contact sheet and 1600m/5200m
full-size views were inspected. The 1600m view exposed overlapping formation
and approach triangles, so the ground blend now begins outside the existing
18m approach shoulder and reaches full height at 28m. The final
`yard-formation-join/01600.png` confirms the reduced overlap. Some coarse
embankment transitions and mixed photographic/procedural facades remain;
this pass is not a claim of finished whole-route fidelity.

After the join adjustment, production build and 138 tests passed again. The
rendered service served all six stops, exercised both cab and door-check views,
visited 57 100m cells across 1,241 frames, and reported errors `[]`. Final frame:
913 draws / 3,139,832 triangles, WebGPU. No gameplay logic was changed.

### Vegetation colour and silhouette consistency

The matched 600m and 5200m views showed pale sparse canopies beside the darker
city. `build_urban_trees.py` now gives plane/elm leaf cards fuller silhouettes
using the same number of leaves, and adjusts linear-space foliage tints for the
existing daylight. The Blender source previously used the leaf texture alone,
whereas the exported live model also multiplied vertex colours. The source
shader now multiplies the same vertex tint before baking distant impostors.
All four impostor PNGs were regenerated from the editable source. Prototype
triangles remain 8,252 in total. Inventory positions, species selection, runtime
scales and running-line exclusions are unchanged; crown proportions and colour
remain artistic approximations, not measured seasonal canopy observations.

Placement provenance remains the City of Melbourne Urban Forest inventory:
https://data.melbourne.vic.gov.au/explore/dataset/trees-with-species-and-dimensions-urban-forest/
The separate 2021 canopy polygon dataset exists, but was not imported or used
to claim measured crown dimensions in this pass.

`canopy-materials/00600.png` and `canopy-materials-east/05200.png` were compared
against the previous yard survey at matching camera positions. The near plane
canopy is fuller, gum colour is less pale, and the eastern tree line is darker.
Short 44-frame captures: 600m mean 18.94ms/max26.10ms, 605 draws/3,076,293
triangles; 5200m mean17.99ms/max25.60ms, 814 draws/3,427,201 triangles. These
are smoke measurements rather than a controlled LOD performance comparison.
Production build passes. Runtime TypeScript/gameplay code did not change.

Post-asset-change rendered service: six stops served, 1,241 frames, 57 visited
100m cells, cab and door-check views exercised, errors `[]`, no browser warnings.
Final frame remains 913 draws / 3,139,832 triangles on WebGPU. Coarse photographic
building remnants and generic facade fidelity are still open goal requirements.

### 700 Bourke Street foreground replacement

The 1600m cab rays identified retained upper scan fragments in tiles I3S289401
and I3S292532 around survey structure 810894. The City 2014 address record
identifies this site as Bourke Junction, 700–704 Bourke Street; its low historic
height/floor fields are not used for the replacement. All four 2023 sections
3663–3666 form the Blender union. `docs/bourke700-reference.json` preserves the
address cross-check and architect reference; the prepared 2023 relative heights
control the model silhouette. The architect's railway-facing photo was inspected
for dark glazing, pale triangular panels, narrow mullions, coloured return facets
and the pale podium. Panel positions/materials remain authored approximations.

The new editable source and GLB are built by `build_bourke700.py` (74,556
triangles). The complete source hull masks overlapping photographic geometry;
runtime source IDs are removed only after a valid replacement loads. Nearest
survey edge to the 2m-sampled training line is 64.699m at route1830m. No extra
apron or unmeasured plant structures extend this footprint.

`bourke700/01600.png` shows a continuous dark/triangular facade replacing the
mixed generic lower walls and torn upper mesh. `bourke700-passing/01800.png`
confirms the model passes behind the cab normally; adjacent buildings still
have coarse upper fragments and remain open work. The 1600m short sample is
14.77ms mean/17.50ms max, 539 draws/2,287,884 triangles. The earlier matched
capture was16.69ms mean/17.60ms max, 521 draws/2,140,991 triangles; no causal
performance gain is inferred from these brief samples. Build and138 tests pass.

Post-replacement rendered service: all six stops served, cab/door-check views,
57 visited100m cells, 1,241 frames, errors `[]`, no browser warnings. Final
frame922 draws/3,213,027 triangles, WebGPU; procedural sections8216, with the
four replaced sections represented by the verified Blender envelope instead.

### Stadium shell and source opening

At1800m, a cab ray at NDC(-.85,.83) hit I3S292532 at
[-1633.9088,53.5252,-260.1941]. The adjacent source structure808392 is the
stadium, not an office tower. Its16 source sections920–935 include a common
interior ring that was discarded by the generic prepared building extrusion.
`src/data/stadium-source.json` retains the original City2023 records, including
those rings, with CC BY4.0 attribution. The Blender generator unions the complete
prepared sections, then restores the central opening from source section920.
An overhead ray at its centre confirms the shell is open.

Engineer reference inspected:
https://www.aurecongroup.com/projects/property/marvel-stadium
The model adds authored dark concourse bands, pale horizontal edges/structural
bays and roof lattice silhouettes aligned to the source opening. These details
are visual approximations, not structural drawings. The envelope represents the
2023 survey with relative prepared heights; neither interior seating nor the
2024 redevelopment is reconstructed. The roof is shown open without animation.

The runtime validates all16 source IDs before suppressing procedural sections.
The whole source hull replaces overlapping scan fragments. The1800m comparison
shows a coherent stadium concourse instead of generic office windows and torn
roof strips. The neighbouring tower's upper scan is still coarse and remains an
open task. Production build and138 tests passed after integration.

The final shell contains57,450 triangles. `stadium-final/01800.png` confirms
structural bay detail, a continuous roofline and clear track. Its44-frame static
sample measured33.32ms mean/34.10ms maximum,486 draws/1,897,870 triangles.
This run was slower than earlier~16.7ms captures; no controlled attribution or
performance improvement is claimed. Overall playable performance remains a
separate goal gate, especially around station approaches.

The generator now fails if an overhead centre ray intersects the stadium shell,
preventing regression of the recorded opening. Complete rendered service passed:
six stops served,57 visited100m cells,1,241 frames, cab/door-check views, errors
`[]` and no browser warnings. Final frame928 draws/3,264,082 triangles on WebGPU;
8,200 procedural sections plus validated authored landmark replacements.

### Forum Theatre on the eastern return

Cab rays at5200m hit the coarse Forum foreground in I3S90514, including
[228.6599,29.1737,-184.7726]. Structure806370 contains source sections20100–20103.
The official2014 address-bearing record identifies150–162 Flinders Street;
`docs/forum-reference.json` preserves that cross-check. The City's photograph
was inspected for the copper dome, clock, minarets and cream masonry:
https://whatson.melbourne.vic.gov.au/things-to-do/forum-melbourne

`build_forum.py` preserves the footprint and replaces the upper rectangular
clock-tower extrusion with an authored dome/finial within the original34.5m
prepared tower height. Arched recesses, cornices, clocks and minarets are visual
interpretations, not conservation drawings. An explicit footprint plinth joins
the main section's2m survey base to the flat game ground. No other source
building is suppressed by the runtime replacement loader.

`forum-landmark/05200.png` was compared against the matching eastern view:
the clock/dome silhouette replaces the coarse front tower. A separate adjoining
scan remains behind it; ray(.4,.18) now hits[187.0249,35.2238,-174.3443], outside
the Forum footprint. That adjoining source block still needs coherent repair;
its connected scan component spans multiple buildings and is not blindly cut.
The production build and138 tests passed after integration.

`forum-final/05300.png` inspects the final plinth and arches at a closer viewpoint.
It also exposes unfinished side-track bridge ends and ground joins beside the
Federation opening, between the usual200m samples. These are the next terrain
priority; a clear centre track does not prove that surrounding joins are finished.
The5200m and5300m44-frame captures measured33.33ms mean, maxima33.90/34.10ms.
This continues the recent~30fps observation; no frame-time improvement is claimed.

Post-Forum service validation: all six stops served,1,241 rendered frames,
57 visited100m cells, both cab and door-check views, errors`[]`, no browser
warnings. Final928 draws/3,263,958 triangles, WebGPU. The four source sections
are represented by the authored replacement; remaining procedural count8196.

### Federation covered railway continuity

The5300m gap was a source-type boundary: Vicmap surface features end where
`rail_uground_o` begins, for example Glen Waverley at(281,-125), Lilydale
at(279,-135), and Hurstbridge at(273,-149). Both scenery rails and the Blender
opening generator previously ignored that continuation. This was not evidence
of real buffer stops.

Connected Federation portal approaches now follow the original covered geometry
for up to240m, within the existing eastern-yard region and protected running-line
margin. Missing track counts inherit the connected surface feature; explicitly
single-track branches remain single. Covered segments use a thin deck without
surface earthwork. Gantry footing checks include the covered centrelines.
All four Federation envelopes now cut both mapped railway types; where a covered
source has no count, the opening reserves two tracks. These heights and openings
remain authored adaptations to the training alignment, not engineering surveys.
The source IDs, footprints and prepared building heights are unchanged.

`portal-continuity/05300.png` isolates the rail repair; `portal-openings/05300.png`
shows the repaired entrance bays. The final `covered-yard-route` survey completed
all24 standard captures and its contact sheet was inspected. The5400m view now
shows neighbouring tracks continuing beneath the deck. The remaining flat ground
joins and coarse neighbouring scans still need repair; this is not a whole-route
visual sign-off. Four rebuilt assets contain8720/298/1586/1093 triangles for
816359/806667/805928/805929 respectively. Blender's running-line clearance guard
passed for each.

Production build and138 tests passed. Full rendered service served all six stops,
1,241 frames/57 visited100m cells, cab and door-check views, errors[] and no browser
warnings. Final928 draws/3,294,919 triangles,8196 procedural sections, WebGPU.
Survey44-frame means ranged16.65–26.52ms, maximum individual frame34.20ms.
These uncontrolled static samples do not establish an optimization gain; no LOD
threshold or scenery-density reduction was made for this repair.
