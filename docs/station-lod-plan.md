# Station approach performance

User requested LOD while the environment is being rebuilt. Reference:
https://developers.openai.com/blog/how-to-build-games-with-astra

Apply its coarse-to-fine continuity, stable refinement and measured frame-time
principles to the railway. This is implementation direction, not a claim that
station LOD is complete or that current performance meets 60 fps.

## Initial inspection (before the LOD changes below)

- Trees switch between coarse and detailed cells at 330 m; disappear at 1000 m.
  The detailed switch currently lacks hysteresis.
- Viaduct uses Three LOD with 190 m detail and 1500 m visibility thresholds,
  with hysteresis.
- Stations become visible as entire groups within 620 m. There is no station
  architectural proxy/detail hierarchy yet.
- City chunks and aerial tiles use distance visibility, not geometric LOD.
- Assets load at startup. Shader compilation currently covers entry views;
  it does not prove every upcoming station material is warmed.

## Required work alongside environment refinement

1. Establish moving approach profiles for each station: median/p95/p99/max
   frame interval, draw calls, triangles, and active detail counts. Report
   hardware/backend and keep screenshots outside the timed interval.
2. Retain station silhouettes and roofs at distance; separate small fittings,
   platform furniture, structural repetition and facade detail into nearer
   tiers. Keep tracks, signals, platform edge and stop cues reliable.
3. Add hysteresis so marginal camera movement does not repeatedly switch tiers.
   Retain coarse coverage until detailed resources are ready.
4. Prepare upcoming station materials incrementally ahead of the train rather
   than compiling or uploading everything at one visibility boundary.
5. Budget nearby detail across stations, trees and city together. Verify both
   approach and departure, plus portal transitions and stopped door-checks.
6. Compare the same driving path before/after, inspect for popping or gaps, and
   complete the rendered-service audit. Do not infer a frame-rate win merely
   from lower polygon counts.

The POV harness now records timing percentiles and samples render counters
before asynchronous PNG encoding. Its static samples locate problems but do
not measure moving approach stutter; a moving profile remains required.

## First implementation and measured diagnosis

Station decorative fittings now have a 360 m entry / 400 m exit tier. The
structural platform, coping, roof, stop marker and signals stay in the core
representation. Whole-station visibility has a 620/660 m hysteresis band;
tree detail has 330/370 m. Geometry batching keeps core/detail materials apart.
This is an initial detail tier, not a completed multi-resolution station asset.

`/scripts/station-profile.html` now replays three 260 m approaches at a fixed
20 m/s simulation rate, then repeats them in the same loaded scene. Each pass
collects 780 frame intervals after 60 settling frames. No screenshot encoding
occurs in the timed interval. These are browser frame intervals at 1280×720 on
the current Mac's IAB WebGPU backend, not GPU timestamp measurements or actual
manual driving. Build/test processes were idle during the final two-pass run.

| Station | First-use mean / p99 / max ms | Warm mean / p99 / max ms | Peak draws / triangles |
| --- | --- | --- | --- |
| Southern Cross | 20.98 / 101.0 / 201.0 | 17.57 / 33.5 / 34.3 | 700 / 3,566,694 |
| Flagstaff | 18.65 / 133.3 / 216.4 | 18.46 / 133.3 / 134.0 | 467 / 1,082,189 |
| Flinders Street | 21.22 / 99.9 / 100.6 | 21.50 / 100.0 / 116.5 | 974 / 4,321,208 |

These results do NOT prove a performance improvement from the initial LOD tier.
The earlier comparison overlapped a build and was discarded as a timing
comparison. First-use preparation appears significant at Southern Cross;
Flagstaff and Flinders retain repeatable expensive frames after warm-up.
Investigate changing light sets and passenger batches before adding more LOD
complexity. Stable global light identities may avoid rebuilding lighting shader
variants, but this is a hypothesis requiring an isolated comparison.

A screenshot after the final pass confirms the Flinders platform, rails,
station signs and nearby fittings remain present. Full service and visual
transition validation remain outstanding for the overall environment goal.

## Stable lighting and loading-time preparation

The previous world changed active PointLight objects at station boundaries.
The replacement keeps one ten-light pool registered for the entire service,
moves it to the nearest underground station's original warped lamp positions,
and changes intensity between 0 and the existing 55. Light count and identities
stay stable, while colour, attenuation and authored positions remain unchanged.
Platform lamp meshes remain in their existing geometry tiers.

Loading now compiles each station's local visible assets with mesh frustum
culling temporarily disabled, then restores culling and the initial game state
before declaring ready. This deliberately moves preparation into the loading
screen. It does not stream new network assets during driving.

Controlled first-approach comparison (same 780-frame routes and resolution):

| Station | Previous p99 / max ms | Stable pool + preparation p99 / max ms |
| --- | --- | --- |
| Southern Cross | 101.0 / 201.0 | 33.5 / 83.3 |
| Flagstaff | 133.3 / 216.4 | 17.6 / 17.7 |
| Flinders Street | 99.9 / 100.6 | 34.2 / 34.3 |

Peak draw calls and triangle counts are unchanged. This supports pipeline
preparation as a cause of the earlier stalls; these browser timings do not
isolate individual shader or GPU commands. Flinders still averages 20.13 ms
with 74 frames over 33.34 ms, so the 60 fps target is not achieved. Southern
Cross still had one 83.3 ms frame. Future geometric/draw-call LOD should address
sustained cost without undoing the scene's fidelity.

Warm-pass p99 was 33.6 ms Southern Cross, 17.6 ms Flagstaff and 34.1 ms
Flinders. Resource preparation increases the work done before the loading
screen finishes; its startup time and memory cost have not yet been benchmarked.

Post-change full rendered service audit passed: 37,224 simulation ticks,
1,241 rendered frames, all six stops served, cab and door-check views exercised,
57 visited 100 m cells, maximum rendered travel gap 6.172 m, and no runtime
errors. This accelerated service audit verifies route/gameplay continuity,
not wall-clock driving performance. All 138 unit tests and production build
passed separately.

Matched 2600 m cab captures (`baseline-1280` and `pooled-station-lighting`)
were inspected at full resolution. The Flagstaff ceiling, tiled walls,
platform, passengers and light falloff retain their appearance. The repaired
track-bed floor is also visible; the baseline predates that separate repair.

## Baked tree silhouettes and tighter detail range

The existing editable Blender prototypes now also produce four transparent
256px distant-tree images. Each far tree uses two crossed quads (four triangles)
with geometry/UVs cropped to its actual prototype bounds. Positions, species
classes and authored dimensions remain shared with the detailed trees. Detail
enters at a cell-centre distance of 220m and leaves at 260m; the existing 1000m
outer range remains. This is cell LOD with hysteresis, not a continuous crossfade.
The former coarse leaf cards remain as a fallback if optional images fail.
The four small maps are explicitly uploaded during loading.

Bake command: Blender `--background assets/source/environment/urban-trees.blend
--python scripts/blender/bake_tree_impostors.py`. Baked assets and metadata are
in `public/textures/trees`. Lighting is baked and approximate; the crossed
images cannot reproduce every near-tree viewing angle. The nearby models,
track clearance and mapped tree locations are unchanged.

Fresh before/after profiles use the existing 780-frame station ranges,
1280x720 WebGPU, separate first and warm passes, without builds, test execution
or screenshot capture inside the timed interval. The first untrimmed LOD run
reduced peak Southern Cross triangles from 3,578,858 to 3,231,314 and Flinders
from 4,346,721 to 3,609,759. It did not establish an FPS improvement: warm
means changed 18.14→20.30ms and 21.45→22.91ms respectively, and one first-use
Flinders frame was 116.7ms at 5322m. Transparent margins were subsequently
trimmed and the four image uploads made explicit. A follow-up profile records
the final implementation below; that does not by itself establish the cause
of the earlier outlier.

Final cropped/preloaded run (mean / p99 / max milliseconds):

| Station | Before first | Final first | Before warm | Final warm |
| --- | --- | --- | --- | --- |
| Southern Cross | 24.17 / 34.3 / 49.9 | 19.42 / 33.8 / 34.2 | 18.14 / 33.4 / 33.9 | 17.65 / 33.4 / 33.7 |
| Flagstaff | 16.67 / 17.6 / 17.7 | 18.63 / 33.9 / 34.2 | 16.67 / 17.5 / 17.6 | 16.67 / 17.5 / 17.7 |
| Flinders Street | 20.79 / 34.3 / 50.1 | 21.88 / 33.8 / 100.1 | 21.45 / 34.1 / 34.3 | 21.28 / 33.9 / 37.5 |

Final peaks: Southern Cross 675 draws / 3,231,314 triangles; Flagstaff
467 / 1,082,189; Flinders 957 / 3,609,699. Geometry reduction is verified;
steady 60fps and removal of first-use stalls are not. The user subsequently
prioritized continuous landscape coverage over further fine-grained LOD work.
Keep this bounded improvement and resume the route's visible gaps before
spending more time tuning small frame-time differences.
