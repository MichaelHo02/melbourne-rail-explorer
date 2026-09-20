# Station circulation, riverbank and driving feedback — 20 September 2026

## Changes and evidence

This pass adds station end walls and staff access gates, recessed Flagstaff/Parliament entrances, underground suspended information displays, and a second-road opening at Melbourne Central. Platform views were reviewed for all five stations. The entrance review caught ceiling geometry crossing the vestibules and floating station labels; both were corrected. The platform/track arrangement remains authored rather than a surveyed station model.

Along the viaduct, seven foreground buildings now retain their complete survey-derived procedural structures rather than alternating between partial photographic storeys and replacement facades. Bounded clipping removes the remaining seam chips and aerial tree sheets above the two official Batman/Enterprise Park parcels. Five source photographic GLBs remain unchanged. The northbank review shows continuous buildings and mapped trees without the previous floating park crowns; distant aerial roof artifacts remain visible.

The Yarra now occupies an opening in the ground mesh, with its authored water level below the park. Low stone bank faces, physically scaled paving, parcel grass variation and three benches improve the northbank. Browser review caught a mixed indexed/non-indexed geometry batch that prevented the bank from rendering; the revetment now uses compatible indexed geometry. These are authored surface/elevation details placed using official plan geometry, not a riverbank elevation survey.

The Blender commuter export adds distinct jackets, a coat, hoodie, knitwear, shirt, hairstyles and bags while retaining shared materials and restrained idle morphs. It contains six near and six distant variants, 147,742 triangles and 8,378,836 bytes. The final lineup and in-game passengers were visually reviewed. Close-up faces remain stylised, and passengers do not walk or board.

The training stop guide now uses the same motion equations, acceleration ramp and upcoming authored gradients as driving. Original controller, door and brake cues follow accepted simulation transitions. Door movement uses service time, freezing on pause and closing explicitly on service completion. The final-stop closure defect found during review has a regression test. Cab-reference documentation distinguishes the user's VLocity photographs from the game's HCMT-inspired controls; the photographs are not republished.

## Automated validation

- `npm test`: **71 tests pass across 12 files**, including predictive braking against actual simulation, final-stop door closure, pause timing, mechanical audio transitions, source commuter morphs and photographic clearance boundaries.
- `npm run build`: strict TypeScript, production Vite build and native-WebGPU-only guard pass. The photographic worker is 51.99 KB; the application chunk is 2,344.94 KB before gzip (330.56 KB gzip), excluding the separate Three.js chunk and external assets. The existing large-chunk warning remains.
- Final read-only review found no material correctness regressions in motion, guide integration, door timing, audio transition/cleanup or river geometry/material readiness. `git diff --check` passes.

## Codex in-app browser

Desktop review covered the five station platform views, Flagstaff/Parliament entrances and the viaduct/northbank. At 1280×720, the stopping guide remained clear of the driving controls; at 600×850, compact controls fit with document width equal to the viewport's 600 pixels. The temporary viewport override was reset.

During a real-controller Flagstaff approach, brake two predicted a stop approximately 107 m short, and the train stopped 107 m short. The aligned-marker state was separately inspected using the stopped Melbourne Central development fixture. This is not a claim of a manually driven perfect stop or complete circuit. Opening doors hid the guide; closing after boarding advanced the next station. Sound startup changed the control to Mute without errors. This verifies startup and transition integration, not an audible mix review or a clean voiced-announcement library.

Two paused Melbourne Central observations retained exactly 81.933333 seconds of passenger simulation time and idle-weight sum 7.038381. The northbank sample reported WebGPU, 647 draw calls, 1,574,620 triangles and an 18.89 ms recent average frame interval. These are local samples with other tabs present, not controlled performance guarantees.

The production build was reviewed on port 5181, isolated from the user's port-5180 saved service. Actual controls verified open-door traction interlock, closed-door departure, acceleration to 46 km/h, rejection of opening doors while moving, emergency braking to zero, exterior camera and pause. Reloading and continuing retained the stopped position, 1.19 km to Southern Cross, and emergency state. Final development and production warning/error logs were empty. Screenshots and geometry audits remain locally under ignored `artifacts/`.

Remaining boundaries: nearby traffic is the fixed-date timetable, not live positions; station geometry/cab controls and river levels are authored; some distant photographic roofs are coarse; crowd walking/boarding and a station-specific voiced announcement bank are not implemented. The current changes improve the prototype without claiming photorealism or operational calibration.

---

# Scenery and passenger refinement — 20 September 2026

## Changes and evidence

The second pass corrects stretched platform surfaces, duplicated Flinders Street poles, generic floating light bars and incomplete photographic surfaces near the authored railway. Platform UVs now use the physical material dimensions before asynchronous texture loading; the original map-readiness check had stretched one texture across a 200 m platform. Canopy lights, gutters, Southern Cross roof ribs/supports, underground panel joints and light channels are tied to the station geometry. Dimensions and circulation remain authored approximations.

The photographic cleanup now runs triangle/volume subtraction in a dedicated worker, preserving interpolated atlas UVs and normals at each boundary. Building suppression also requires retained lower-facade evidence and rejects sections intersecting removed source faces. This preserves survey-derived support beneath incomplete photographic context. Source GLBs are unchanged; this is a local game presentation correction, not an update of the 2020 survey or a surveyed vertical alignment.

The Blender commuters now have relaxed forearms, curled fingers, clearer clothing, shoulder bags and an actual phone. Three local morphs provide independently timed head glances and restrained chest breathing; the feet and placement remain fixed. A final Blender lineup was inspected, and asset tests read the exported morph deltas to verify that lower legs and soles remain stationary. The optimized GLB is 8,290,776 bytes, with six near and six distant variants sharing five materials.

## Automated validation

- `npm test`: **57 tests pass across 11 files**, including the shipped commuter morph data, deterministic idle timing, photographic clipping/interpolation, Southern Cross low-context clearance and asynchronous platform UV regression.
- `npm run build`: strict TypeScript, production bundling and the native-WebGPU-only bundle guard pass. The new photographic worker is 45.86 KB; the main application chunk is 2,328.45 KB before gzip (323.83 KB gzip), excluding the separate Three.js chunk and external assets. The existing large-chunk warning remains.
- Read-only integration review checked worker failure/cleanup, tile-local versus world coordinates, source attribute layout, per-instance morph allocation and pause-clock behavior. No concrete defects remained in those paths.

## Interactive review

All review uses the Codex in-app browser. The development platform views for all five stations and the Yarra viaduct were inspected. Checks caught remaining low scan fragments at Southern Cross and redundant poles in the Flinders canopy; these prompted further corrections rather than treating the first screenshot as acceptance.

At Parliament, two separated paused observations reported identical commuter simulation time (9.766667 seconds) and total idle weight (12.933609). Unpaused samples changed their weights. This confirms simulation-clock integration; it does not establish walking, boarding, facial animation or realistic crowd behaviour. Screenshots and the Blender lineup are retained locally under ignored `artifacts/`.

The final Southern Cross platform view removed the visible suspended dark sheets and distant triangular shards; surrounding building facades remain continuous. Its sample reported WebGPU, 739 draw calls, 1.83 million triangles and a 24.17 ms recent average browser frame interval. This is one local observation with another game tab present, not a controlled GPU benchmark or a guaranteed frame rate.

The built game was tested at `127.0.0.1:5181` to avoid changing the existing saved service on port 5180. Native WebGPU initialized and Start became available. Actual controls verified power blocked with open doors, closing doors advancing the next stop, acceleration to 16 km/h, emergency braking to zero, camera switching and pause. The final browser warning/error log was empty.

Remaining visual limits are explicit: close-up people are stylised, station layouts/elevations are authored, and coarse aerial trees/jagged background context remain along parts of the viaduct. The Southern Cross cleanup deliberately replaces the mismatched low photographic surfaces with the existing survey-footprint buildings; it does not recover missing street-level photography. No new live train feed, walking/boarding simulation or voiced announcement bank is claimed by this pass.

---

# Fidelity pass verification — 20 September 2026

## Automated and asset checks

- `npm test`: 42 tests pass across seven files, including official timetable selection/dwell/calendar rules, actual overlapping traffic services, announcement timing/interlocks, audio initialization retry and pause/mute lifecycle, existing driving/save/route/geography behaviour, and the native WebGPU guard.
- `npm run build`: strict TypeScript and production Vite build pass; no WebGL fallback module is bundled. The application chunk is about 2.32 MB before gzip (320 KB gzip), mainly including bundled geographic manifests and the fixed-date timetable. Vite reports a large-chunk warning. No streaming or payload-size improvement is claimed.
- All five photographic GLB SHA-256 hashes match the retained manifest. Preparation Python scripts parse successfully. Blender imports/renders checked source atlas orientation and the commuter lineup; the photographic source totals 267,736 triangles and 36,096,220 bytes. Review renders are excluded from shipped assets.

## Codex in-app browser

All browser work used the Codex in-app browser. Named development views were inspected for Flinders Street, Southern Cross, Flagstaff, Melbourne Central, Parliament and the viaduct. The review corrected aerial riverbank/viaduct overlap, retained authored playable station roofs where scan undersides were incomplete, adjusted Melbourne Central's ceiling profile, and fixed a zero endpoint bearing that collapsed passengers and rear carriages behind Flinders Street. A regression test verifies the 22.85 m rear-car spacing. Southern Cross still shows coarse or partial aerial context beyond the playable hall; this pass does not establish street-level scan quality.

The Sound control successfully loaded/decoded all three recordings and changed to Mute; toggling back and pausing produced the expected visible states without browser errors. This verifies browser startup/control integration, not listening quality, intelligibility of PA speech or an accurate dynamic announcement bank. Audio clock suspension and retry are additionally covered with mocked AudioContext tests.

The rebuilt production preview at `http://127.0.0.1:5180/` initialized with the canvas reporting WebGPU. Real UI/keyboard input verified power blocked with open doors, door closure advancing the next stop, acceleration to 22 km/h, emergency braking to zero, camera switching and pause. The final browser error/warning log was empty. The service was left paused for inspection.

A final Flinders development sample reported native WebGPU, 658 draw calls, about 2.05 million triangles, 7,558 procedural building sections after duplicate suppression, and two visible timetable trains. Its recent average browser frame interval was 16.67 ms. This is a single local observation, not a controlled benchmark or a GPU-time/performance guarantee.

## Remaining accuracy limits

The aerial capture is May 2020 and includes occluded facades, baked shadows and coarse close detail. Authored platform layouts, railway elevation, clearances and cab instruments are not operational surveys. Passengers have static varied poses with anatomical proportions; they do not walk or board. Traffic is a visual subset of the 19 September 2026 timetable on authored surface tracks with illustrative HCMT models, not live positions, actual fleet assignments or neighbouring underground circuits. Live access still needs a provisioned server-side Transport Victoria key. The included sound comprises historic field recordings plus original cues; clean voiced service announcements and appropriate Flagstaff/Melbourne Central recordings remain unfilled asset needs.

---

# Verification — 19 September 2026

## Automated checks

- `npm test`: 19 tests pass, including all six station visits in a complete service, stopping/boarding interlocks, emergency braking, pause behaviour, save validation, route continuity, official station anchors, Yarra geography and WebGPU failure handling. The latter uses real Three.js renderer initialization with mocked browser API/adapter/device failures, asserting that no alternate graphics context is requested.
- `npm run build`: strict TypeScript, production Vite build and the no-WebGL-backend bundle guard pass. Native WebGPU and application JS total approximately 783 KB before gzip (225 KB gzip), excluding the worker, versus 944 KB (269 KB gzip) for the previous dual-backend build. This is a payload measurement, not a frame-rate benchmark.
- The optional browser harness now requires WebGPU; the compatibility test and WebGL launch flags were removed. It was not rerun in Chrome, following the user's request for Codex browser verification.

## Native-only renderer: Codex in-app browser

- Production preview initializes as WebGPU, enables Start, and renders the sky, city, water and HCMT.
- Development build initializes with the shared source modules. Real door/controller input accelerates the train from Flinders Street toward Southern Cross; cab lighting and scenery render correctly.
- The pause menu retains resume/restart and has no quality switch. Shadows and the existing high-quality settings are always enabled.
- No new graphics errors or warnings after the final server restart. A stale development server initially mixed old prebuilt shaders with the new source renderer; restarting Vite with the updated aliases resolved it. The production build was unaffected.
- Unavailable API, adapter and device cases were tested at renderer level with mocked browser capabilities, not by disabling WebGPU in the user's browser.

## Historical dual-backend migration: Codex in-app browser

These checks describe commit `4a5bd55`. The compatibility backend and quality switch described here have since been removed.

- Confirmed native `WebGPU` and explicitly forced `WebGL2` via the renderer's actual backend, exposed on the canvas dataset after initialization.
- Reviewed the menu, HCMT/cab, city exterior, tunnel and underground platform; checked door interlock, departure acceleration, camera switching and platform boarding with real input.
- Inspected the Yarra close-up on both backends. The initial shader warm-up produced black sky and water reflections; generating PMREM before `compileAsync` corrected both. Final screenshots show the sky, water ripples and Flinders Street on both backends, with no graphics errors or warnings logged.
- Corrected the old river centreline, which was approximately 137 m south of the official river centre at longitude 144.965. The new polygon follows Vicmap Hydro banks. Water level and riverside structures remain approximate.
- Switched off high-quality lighting on the WebGL2 backend and confirmed the scene still renders. Inspected at 1280×720, then restored the normal viewport.
- Final production-preview startup and native backend were checked at `http://127.0.0.1:5180/`.

Frame statistics now report per-frame draw calls and unclamped browser frame intervals. The observations are not a controlled performance comparison, and no frame-rate improvement is claimed. Automatic fallback when native WebGPU is unavailable, total initialization failure and device-loss recovery messaging are implemented but were not induced in this browser pass; the compatibility backend was exercised explicitly with `?renderer=webgl`.

## Earlier foundation verification: Codex in-app browser

The final interactive pass uses the production preview at `http://127.0.0.1:5180/`, and the development server's named scenes for targeted visual inspection. These checks were performed through visible UI and real keyboard input:

- Start service; open doors prevent movement under power.
- Close doors and increase power; speed rises and Southern Cross becomes the next stop.
- Attempt doors while moving; the interlock keeps them closed with an explanatory message.
- Apply emergency brake; speed reaches zero.
- Pause, reload and continue saved service; stopped position and next station are preserved.
- Switch cab/exterior cameras; inspect the HCMT, Flinders Street facade and railway precinct.
- Melbourne Central platform: open doors, attempt an early close (rejected while boarding), then close after dwell and advance to Parliament.
- Inspect tunnel, platform-to-tunnel opening, route map, PT-styled menu and controls.
- Inspect 1280×720 desktop layout and 600×850 compact controls. Compact document width equals viewport width; viewport override restored afterwards.
- No page errors recorded in the integrated browser log.

Visual review found and corrected mirrored Flinders platform signs and an exterior camera position obstructed by the facade. Southern Cross survey-roof/platform overlap was corrected by excluding exact conflicting source sections. A final Codex browser screenshot confirmed clear track and platform beneath the wave roof.

## Boundaries

The complete circuit is verified at simulation level, not a claim that every metre was manually driven and visually inspected. Building footprints/heights and selected route coordinates are real source data; facade textures, scenery ground, stations, rail topology, elevations, people and cab instrumentation remain approximations. The game is a playable, recognisably Melbourne first build, not a photorealistic digital twin or operational training system.
