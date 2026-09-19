# Melbourne Rail Explorer — prompt playbook

Based on the [Void Explorer showcase](https://developers.openai.com/showcase/void-explorer) and [Building games with Astra](https://developers.openai.com/blog/how-to-build-games-with-astra), by Thomas Ricouard.

## What is actually published

These pages provide selected, edited prompts and a build narrative, not a complete conversation, repository, or hidden system prompt. The showcase outlines concept art, a first playable slice, controls, rendering, vehicle references, Blender modeling, interaction, and consistency passes. The article says the author described constraints and let Astra propose the architecture; it does not publish a full verbatim architecture prompt.

Two short verbatim excerpts from the article show the pattern:

> Everything I can see should be reachable.

> Generate clean views of this ship from several angles.

The first expresses an experience invariant. The second asks for reference views that make a modeling problem inspectable. For the ship, the author reviewed concepts and Blender renders before integrating the runtime model, then measured rendering cost. We apply the same sequence to a real-world vehicle, using actual reference photographs for factual shape and generated views only to explore uncertain art direction.

## Adapted prompts for this project

Everything below is newly written for Melbourne Rail Explorer, not quoted from OpenAI or the original author.

### 1. Establish the experience

> Build a desktop-browser train simulator where I operate a Melbourne commuter train through the City Loop. I want to see a recognisable Melbourne from the cab, pull away from a platform, enter the tunnels, brake smoothly, stop at the correct marker, open the doors, and run a complete service. Start with approachable throttle, brakes, and doors. Preserve a sense of real distance and train weight. Use real geography where available and clearly distinguish any authored approximation. Keep the driving view spacious; put maps and secondary controls behind buttons.

### 2. Propose the architecture around that experience

> Use TypeScript, Vite, and Three.js. Separate a fixed-step, serializable train simulation from the scene graph and DOM controls. Express the railway as a continuous route in metres. The train, every carriage, camera, rails, platforms, tunnel openings, and stop markers must sample that same path. Keep asset loading separate from gameplay and use workers for heavy geographic mesh generation. Add named scenarios and a development-only inspection API early, so you can test a station approach without driving the whole route each time. Start with a reliable renderer and preserve the simulation when improving graphics.

### 3. Ground the city in evidence

> Build the City Loop's Melbourne surroundings from public data. Record the source, license, capture date, projection, and every transformation. Use real building footprints and measured heights for the initial city, with convincing PBR surfaces and daylight. Investigate official photogrammetry for higher fidelity. Extract and optimize only the corridor-visible content; do not send a whole-city archive to the browser. Avoid claiming that generated façades, guessed gradients, or old scans are contemporary survey-accurate scenery.

### 4. Make a useful train reference brief

> Review photographs of Melbourne commuter trains and choose a coherent reference family. Prepare front, side, rear, roof, and driver-eye references with consistent proportions. Pay special attention to the yellow nose, blue and silver bodywork, windscreen shape, doors, bogies, pantograph, and cab sightlines. Keep reference facts separate from design guesses. The target is believable Melbourne rolling stock, not a collection of unrelated train details. Show the silhouette clearly before spending time on small fittings.

### 5. Build and ship the Blender assets

> Use the installed Blender to build an editable train and driver cab at metre scale. Keep the source organized, with semantic names and separate movable door parts. Review renders from the front three-quarter, side, and driver-eye views. Refine the silhouette and materials against the references. Export optimized GLB assets using shared material batches and deliberate mesh budgets, then load them in the existing Three.js train adapter. Keep the train's route-driven motion and cab camera intact. Check wheel gauge, carriage spacing, nose position, door travel, and sightlines in the actual game.

### 6. Fix what the player actually sees

> Play the departure, underground approach, platform arrival, and loop completion. Capture screenshots and inspect simulation state at each. Investigate visual defects at their source: a platform crossing the railway must be fixed in the shared route geometry, not hidden with a camera adjustment. Keep the tunnel opening, visible rail, and carriage movement coherent during surface transitions. The cab should feel like a physical train without blocking useful sightlines or covering the view with interface panels.

### 7. Measure before optimizing

> Record draw calls, triangles, geometry/texture counts, loading time, and frame intervals in the same repeatable scenes before and after asset changes. Identify whether a stall comes from CPU geometry generation, shader compilation, GPU upload, or too much visible detail. Merge static material-compatible geometry, instance repeated objects, and generate or stream scenery ahead of the train. Keep interface text sharp when reducing scene resolution. State the browser and hardware conditions; do not present software-renderer timings as native GPU performance.

### 8. Close the loop with evidence

> Verify the complete service with meaningful simulation tests and browser tests using real input. Cover traction with doors open, braking to rest, stop accuracy, boarding time, overruns, pause, save/reload, camera switching, and narrow-window layout. Review the actual city, cab, tunnel, and station screenshots. Keep sources and fidelity limitations up to date. Once implementation and checks are complete, commit on the dedicated feature branch and leave a playable local preview with clear controls.

## Current work breakdown

- **Integration:** runtime architecture, real city data, natural lighting, prompt/source documentation, browser verification.
- **Blender asset work:** authored train and cab, editable source, optimized GLB, runtime adapter and visual review.
- **Environment work:** curved platforms, tunnel portals, station architecture and visual coherence.
- **Simulation audit:** train/door behavior, complete circuit, pause/save validation and regressions.

These are cooperating subtasks in one project. They share the simulation and coordinate conventions rather than producing separate games.
