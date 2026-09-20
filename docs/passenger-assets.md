# Blender commuter assets

Six clothed commuter variants replace the former capsule people at all five stations. They use MakeHuman's **hm08 basemesh**, skeleton and weights, graphical core assets explicitly released under CC0. See the [official asset licensing explanation](https://static.makehumancommunity.org/about/license.html) and retained `assets/source/passengers/CC0-MakeHuman.md`. The OBJ records the September 2020 CC0 release and credits Data Collection AB, Joel Palmius and Jonas Hauquier. This project includes graphical data, not MakeHuman or MPFB program code.

`scripts/blender/build_passengers.py` creates original clothing, hair, shoes, shoulder bags, a phone, colour variations and commuter poses around the anatomical mesh. Blender applies the supplied bone weights offline. It exports editable `assets/source/passengers/commuters.blend` and `public/models/passengers/commuters.glb`. No Blender addon is needed.

The second pose revision addresses the MakeHuman rest forearms pointing forward: both forearms and upper arms are posed so non-phone hands rest beside the thighs, with bent finger joints instead of splayed hands. Shoulder bags replace the disconnected briefcase/tote handles. Loose torso profiles remove the inflated anatomy beneath clothing; a continuous knit collar covers the neck seam. The phone pose includes an actual phone. These remain original stylised models rather than scanned people.

Rebuild and deduplicate with:

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --threads 4 --python scripts/blender/build_passengers.py
npx --yes @gltf-transform/cli@4.5.0 dedup public/models/passengers/commuters.glb /tmp/commuters-dedup.glb
cp /tmp/commuters-dedup.glb public/models/passengers/commuters.glb
```

The GLB is approximately 8.3 MB and the complete set is approximately 142,000 triangles. Six full variants and six reduced meshes share five materials. Heights range from 1.65 to 1.85 metres; feet are at Y=0 and front is +Z in glTF. Nodes are `commuter_01` through `commuter_06`, with `_low` equivalents. The runtime instances each variant/material, uses full detail within 40 metres, reduced geometry from 40–150 metres, and hides distant people. There are 24 placements per unique station.

## Restrained idle motion

Each near mesh exports three genuine glTF morph targets: `look_left`, `look_right` and `breathe`. The head turns at most eight degrees around the skull base with a blended neck; the upper chest expands by two millimetres. The pelvis, legs, feet and placement matrices do not move. `passenger-idle.ts` samples eased glance/hold/return events and breathing from simulation time with different phases and periods for each placement. Pausing or replaying the same service time produces exactly the same weights. This is local anatomical deformation, not body bobbing, walking or boarding.

The WebGPU renderer uses `InstancedMesh.setMorphAt()` and one weight texture per existing near batch. In the installed Three r180 implementation, `MorphNode.setup()` selects the instance-texture path only when `mesh.count > 1`. Morph batches therefore allocate the full texture before rendering and keep a minimum count of two, using a zero-scale second instance for singleton draws. Hidden batches keep that contract too; their visibility is false. This avoids switching shader paths when the crowd culls to one person. Far meshes remain static; at more than 40 metres the small head turn has little screen-space impact.

One additional instanced transparent plane batch provides two small soft footprint contact cues, visible within 75 metres. They are authored grounding cues, not physically calculated light shadows. Near people retain ordinary dynamic shadow casting.

## Verification and limits

`tests/passenger-assets.test.ts` reads the shipped GLB, verifies all twelve roots and three near morph targets, enforces the material/payload budget, and checks that every exported target keeps lower-leg and sole vertices fixed. `tests/passenger-idle.test.ts` checks deterministic pause/replay poses, bounded weights, independent timing and non-overlapping left/right glances. Browser pause verification uses the canvas passenger metrics (`animated`, `simulationTime`, `idleWeightSum`) alongside visual checks.

The Blender lineup is rendered to `/tmp/passengers-lineup.png`; denoising is disabled because the installed OpenImageDenoise path was very slow during review. Visual review is required after regenerating poses. Faces and outfits are still stylised and repetitive at close range. There is no facial animation, walking, passenger interaction or boarding simulation; the service dwell timer does not imply animated boarding.
