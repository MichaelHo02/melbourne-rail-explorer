# Viaduct frontage verification

Verified 2026-09-20 on `codex/melbourne-fidelity-pass-two`.

The authored GLB contains joined envelopes for 15–33 William Street and 452–470 Flinders Street, retaining 13 source sections in total. Its prepared survey ring bounds are X/Z `[-733.9, 57.3, -658.1, 159.7]` and `[-784.8, 85.2, -718.9, 178.1]` metres respectively; both game-relative envelope ranges are 0–89 m. The broader photomesh exclusion hulls remain unchanged and were not used to expand the geometry.

The final Codex in-app browser captures [corridor inspection](../artifacts/viaduct-frontage-inspection-final.png) and [cab view](../artifacts/viaduct-frontage-cab-final.png) show the blue glass and distinct facade framing in the intended location. The scene reported `cityReady`, with no browser warnings or errors. The change replaces anonymous atlas facades with recognizable, source-identified building forms; surrounding city buildings remain generic.

The final build and `scripts/check-viaduct-frontage.mjs` passed. The checker compares all 13 replacement IDs, section bounds and vertical intervals against the prepared survey, validates the exported envelope bounds and GLB metadata, and checks load-gated replacement. The 126-test full-suite result recorded for earlier camera/roof work was not rerun or counted for this asset batch.

One uncontrolled browser sample reported 801 draw calls, 2,123,222 triangles and an 18.52 ms average frame time. This is a single inspection sample, not a benchmark.

Reference photos were viewed for facade character only and are not redistributed. The generated study sheet is likewise a facade modelling aid, not a dimension or roof reference.
