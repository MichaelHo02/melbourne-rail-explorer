# Survey buildings: authored facade presentation

`createBuildingMaterial()` uses one standard PBR material, a 2048 × 1024 colour atlas and a matching linear roughness atlas. No external texture files or additional materials are loaded.

The [City of Melbourne 2023 Building Footprints dataset](https://data.melbourne.vic.gov.au/explore/dataset/2023-building-footprints/) supplies the building geometry used by this project. It does **not** establish the generated facade colours, glass, window arrangement or material choices. Those are authored visual approximations selected deterministically from height, footprint area and section ID. No individual building's facade is claimed to be a photographic reconstruction.

## Appearance and geometry

Tall sections use cool or neutral curtain-wall glazing; medium sections use concrete piers and long vertical windows. Lower sections vary between pale masonry, muted brick, contemporary light cladding and broad industrial openings. Reflections have continuous gradients and restrained colours; there are no randomly glowing checkerboard windows. Each vertical atlas repeat represents eight four-metre storeys.

The worker preserves source ring positions, base and height. It splits wall surfaces at 24 × 32 metre atlas boundaries, assigning UVs within one selected family. This preserves window scale on both short walls and towers. Absolute vertical UV coordinates align floors across vertically stacked sections. Roofs and exposed undersides use a separate matte cell. Numerical roof slivers smaller than 0.0025 square metres are discarded to avoid Float32 winding flips on collinear survey points.

## Integration

In `World.loadCity`, use `const materials = [createBuildingMaterial()]`. The worker continues transferring `key`, `position`, `normal`, `uv` and `color` arrays. The atlas and worker changes must be used together.

## Verification

TypeScript passes. A browser-free execution of the worker across the prepared dataset checked finite attributes, bounded UVs, consistent triangle winding and that each triangle samples only one atlas cell. Output remains 126 chunks: 616,874 triangles and 81,427,368 bytes of transferred attributes, compared with 508,352 triangles and 67,102,464 bytes previously. Geometry increases about 21%; chunk/material draw-call structure is unchanged. Visual and GPU-performance verification belongs to the integrated browser pass; this task did not launch Chrome.

## Infrastructure semantics

The optional `kind` field preserves the survey `footprint_type`. Bridges and jetties use their source-derived top height and footprint, with an authored deck thickness of at most 0.6 metres (never more than the source extrusion). Their undersides are closed, but space below the deck is left open. Train platforms and tram stops keep their original base and height. All four infrastructure types sample only the matte atlas cell, avoiding artificial windows. Deck thickness is an authored simplification, and top elevation remains relative to the project’s approximate ground datum, not a verified absolute engineering elevation.
