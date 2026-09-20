# Station approach performance

User requested LOD while the environment is being rebuilt. Reference:
https://developers.openai.com/blog/how-to-build-games-with-astra

Apply its coarse-to-fine continuity, stable refinement and measured frame-time
principles to the railway. This is implementation direction, not a claim that
station LOD is complete or that current performance meets 60 fps.

## Current implementation inspection

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
