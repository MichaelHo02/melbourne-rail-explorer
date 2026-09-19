# Verification — 19 September 2026

## Automated checks

- `npm test`: 14 tests pass, including all six station visits in a complete service, stopping/boarding interlocks, emergency braking, pause behaviour, save validation, route continuity and official station anchors.
- `npm run build`: strict TypeScript and production Vite build pass. Three.js's engine chunk remains about 573 KB before gzip; this produces a size advisory, not a build failure.
- Earlier automated browser checks passed before the final asset/style changes. They are retained as an optional harness, but were not rerun in Chrome after the user requested Codex browser verification.

## Codex in-app browser

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
