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
