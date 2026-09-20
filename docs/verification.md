# Background pause audio — 20 September 2026

Window blur and document visibility loss paused and saved the service but deferred audio suspension until the next animation frame. A hidden tab may receive no further frame, allowing its audio clock and Parliament recording to continue while the train remained paused. The shared pause helper now synchronizes audio immediately, preserving the active recording's playback position through pause and resume.

The regression invokes the real application blur and visibility callbacks without delivering another frame. Before the fix it failed with `expected 'running' to be 'suspended'`; afterward it verifies a frozen audio clock and resume without stopping or replaying the recording. The focused audio suite passes all 11 tests; `npm test` passes **105 tests across 16 files**. `npm run build` passes strict TypeScript, production bundling and the native-WebGPU-only guard; the existing large-chunk warning remains. `git diff --check` passes. Independent review found no actionable issues in the bounded change.

This regression uses a mocked AudioContext with the real application lifecycle and audio implementation. It does not establish audible continuity or actual browser background-tab behavior; no new listening check was performed.

---

# Wraparound cab, free camera and station feedback — 20 September 2026

## Changes and evidence

The supplied cab references now inform the left annunciator/horn/sound console and the right radio-style service display, retaining the accepted centre desk. Lamps use accepted simulation state; the service display reports the real target stop, distance and emergency/door status. Its route, guide and camera keys are functional. The generated logo remains in the header, joined by five individually generated transparent button illustrations for route, cab, exterior, sound and guide. Their exact prompts and asset paths are recorded in `docs/brand-assets.md`; clear HTML labels remain alongside the images. The header replaces unlabelled icons with City Loop Route map, Cab, Outside, Centre, Sound, Guide and Pause. The station progress line also opens the map.

At the user's direction, all compact layout variants were removed. There is one 1280 × 720 composition, uniformly scaled and centred to fit the browser. At a 1190 × 850 production viewport, browser layout diagnostics reported stage bounds x=0, y=90.3125, width=1190, height=669.375 and scale=0.9296875. A 600 × 850 visual check also retained the complete wide desk with letterboxing. No controls rearrange or disappear in a compact mode.

Scene dragging now rotates the seated view, the exterior orbit and development inspection viewpoints. Double-click or Centre resets the view; selecting Cab or Outside exits a fixed inspection viewpoint. Drag distances use the transformed canvas bounds. Opening map/help, pausing, pointer loss and window blur gate/cancel dragging. Cab structure remains train-aligned while looking around. Surface exterior allows a full orbit; the underground outside view uses an authored front-quarter clearance envelope rather than placing the camera behind tunnel walls. This is not general collision detection against station props or buildings.

Underground passengers now receive station-local diffuse fill from the existing hemisphere light, approximating reflection from pale walls and tiles. A curved, height-bounded chamber volume preserves the original exterior and running-tunnel light. Flagstaff, Melbourne Central and Parliament were visually inspected; faces and clothing read more clearly without changing skin materials, exposure or adding extra lights/shadow maps. Surface and dark tunnel views were checked in the same pass.

Service captions clear at passed/missed stops, distinguish an accepted final stop from a missed one, and expire after completion even when simulation time is frozen. Restoring a service baselines audio while still paused before resuming, clearing pending tones without replaying an old arrival or Parliament field recording. An independent review caught the previous resume ordering issue, and its regression invokes the actual application HUD callback. Clean voiced station announcements remain an unfilled asset requirement; no voice asset was generated in this pass.

## Validation

- `npm test`: **104 tests pass across 16 files**, including camera limits/scaled pointer input, tunnel envelope samples, station lighting, announcement lifecycle and the real saved-service callback.
- `npm run build`: strict TypeScript, Vite production build and native-WebGPU-only guard pass. Main application chunk: 2,368.69 KB before gzip, 338.23 KB gzip; stylesheet: 28.71 KB before gzip, 7.78 KB gzip. Existing large-chunk warning remains.
- `git diff --check` passes. Bounded independent review found no further concrete defects in pointer dispatch, camera gating, control wiring, state indicators or save integrity.
- The optional automated Chrome harness was updated for the single scaled layout but was not run. All interactive checks used the Codex in-app browser.

## Browser checks

At 1280 × 720, the centre desk and both side consoles fit without overlap; opening doors illuminated the correct lamps and changed the service display. Horn and sound controls were exercised, with topbar/desk sound state synchronized; this establishes control startup/wiring, not a new audible mix review. The side Route and Guide keys opened their intended panels. The final illustrated header was visually checked; clicking directly on the generated route image opened the map. Final development warning/error logs were empty.

Dragging Melbourne Central's boarding view produced yaw=0.368, pitch=-0.085 with no simulation change. Centre restored zero angles; dragging while its route map was open retained zero and reported camera input disabled. Tunnel cab drag reached yaw=0.724, pitch=-0.113. The tunnel outside view reached yaw=-1.09, pitch=0.353 with the camera visibly inside the bore facing the train. Double-click reset to yaw=-0.55, pitch=0.24; pause disabled camera input. The tunnel remained dark away from headlamps and fixtures.

The isolated production preview on port 5181 resumed the existing test save at zero speed, emergency brake applied and 1.38 km to Southern Cross. Exterior selection and drag produced yaw=0.432, pitch=0.353 in the surface scene. The user's separate port-5180 service was not loaded or overwritten. Screenshots remain under ignored `artifacts/`, including `wide-stage-scaled-600.png`, `tunnel-cab-free-look.png`, `tunnel-exterior-free-look.png`, `production-surface-orbit.png`, `flagstaff-indoor-fill.png` and `parliament-indoor-fill.png` and `illustrated-header-wide.png`.

The prototype still uses authored station geometry and handling, stylised commuters, fixed-date timetable traffic and incomplete spoken audio. These checks do not establish photorealism, operational railway accuracy or unrestricted camera collision avoidance.

---

# Walking passengers, cab desk and Southern Cross concourse — 20 September 2026

## Changes and evidence

The header now uses an original generated train, Flinders dome and loop emblem, with accessible live HTML naming alongside it. The built-in image generation prompt and original asset are recorded in `docs/brand-assets.md`. The supplied cab photograph informs a curved silver desk, charcoal fascia, physical left-hand controller, analogue speed/demand dials, illuminated blue door button and red emergency mushroom. These are simplified gameplay instruments rather than an HCMT equipment specification. The driving footer (view name, timetable date, formation and clock) is removed.

Six near and six distant Blender commuters now carry eight articulated stride poses. Distance-driven pose blending moves knees, ankles and arms, and individual sole contacts follow the stance foot. The shipped GLB is 13,833,876 bytes with 148,960 triangles and five shared materials. Four commuters per station walk short clear circuits; six potential boarders align with real door centres before entering, including the reversed rear carriage. Only the platform-side doors open. Behaviour derives from service time, preserving pause and saved-service determinism without adding save fields. Boarding is illustrative; there is no full station navigation or alighting simulation.

Southern Cross gains a raised concourse, glazed balustrades, three twin-flight stairways and a scenic lift. The geometry is authored using the user's photograph and official station/architect references, not surveyed dimensions. A stair-approach inspection confirms the tread, landing and concourse connections. The playable route remains an authored training alignment.

Platform coping now follows station-specific offsets, reducing the previous gap while allowing the long carriages to swing on curves. A refined geometry audit against the shipped front, trailer and reversed-rear train bodies finds minimum sampled clearance of 11.9–18.2 cm across the six visits. Regression tests sweep carriage bodies and open doors against the actual segmented coping, requiring at least 8 cm. These are rendered-geometry checks, not operational loading-gauge measurements.

## Browser checks

The Codex in-app browser shows the generated emblem and complete desk at 1280×720 and 600×850; the compact document has no horizontal overflow. Pointer dragging selects brake at the top and power at the bottom. Testing caught and fixed the focused native slider swallowing driving shortcuts: W/S, doors and emergency now remain available after a pointer interaction, while the range retains its native arrow-key behaviour. An actual Space input with the lever focused applied the emergency latch and showed 100% brake demand. Door interlock suppresses positive power demand; emergency and service-brake demand remain visible.

A real door-button action at Melbourne Central started six boarders. The captured frame shows a passenger entering the open doorway rather than the carriage wall. Pausing retained identical passenger service time (58.29999999999797 seconds), idle sum (7.576303) and gait phase sum (4.762636) across separate observations; resuming advances animation. Screenshots and geometry audit artifacts remain local under ignored `artifacts/`.

The Southern Cross stair-approach sample reported WebGPU, 1,080 draw calls, 2,290,383 triangles, three timetable trains and a 17.22 ms recent average frame interval. The Melbourne Central boarding view reported 611 draw calls, approximately 1.07 million triangles and 16.67 ms. These are local observations with other tabs present, not controlled performance guarantees.

Platform review covered all five stations. Final integration review found boarders crossing the previous waiting positions when stopping away from the exact marker. Waiting groups now occupy gaps between walking circuits. A sweep of all six visits, every 0.25 m stopping offset over ±8 m and every 50 ms of boarding found a minimum 1.05 m root separation from waiting passengers; the 180-second walking sweep found 3.62 m. This checks these authored paths, not general-purpose crowd avoidance.

The production check on port 5181 preserved the user's separate port-5180 service. With the lever focused, W selected power while open doors held speed and displayed demand at zero; D closed the doors and subsequent power accelerated to 26 km/h. A door action while moving kept them closed, then Space latched emergency braking and the train stopped. Pause/reload/Continue retained zero speed, emergency state and 1.38 km to Southern Cross. Sound startup switched to Mute, and camera switching showed the exterior. This is an audio-startup check, not a new audible mix review. Final development and production error/warning logs were empty.

## Automated validation

- `npm test`: **86 tests pass across 14 files**, including exported walk morphs, pause/save determinism, boarding paths through all station visits, waiting-person separation and actual train/platform clearance.
- `npm run build`: strict TypeScript, production Vite build and the native-WebGPU-only guard pass. Main application chunk: 2,354.40 KB before gzip, 334.34 KB gzip; separate Three.js chunk: 457.17 KB before gzip. The existing large-chunk warning remains.
- `git diff --check` passes. No real passenger photographs are published; the generated emblem and authored Blender source/export are included.

Remaining boundaries: station geometry and train handling are authored; commuters are stylised and follow limited paths; nearby trains use the fixed-date timetable rather than live positions; clean voiced station announcements remain an asset need; distant photographic building surfaces can be coarse. This pass does not claim photorealism or railway operational accuracy.

---

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
