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
