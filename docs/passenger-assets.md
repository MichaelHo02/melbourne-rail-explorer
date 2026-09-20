# Blender commuter assets

Six clothed commuter variants replace the former capsule people at all five stations. They use MakeHuman's **hm08 basemesh**, skeleton and weights, graphical core assets explicitly released under CC0. See the [official asset licensing explanation](https://static.makehumancommunity.org/about/license.html) and retained `assets/source/passengers/CC0-MakeHuman.md`. The OBJ records the September 2020 CC0 release and credits Data Collection AB, Joel Palmius and Jonas Hauquier. This project includes graphical data, not MakeHuman or MPFB program code.

`scripts/blender/build_passengers.py` creates original clothing, hair, shoes, shoulder bags, a phone, colour variations and commuter poses around the anatomical mesh. Blender applies the supplied bone weights offline. It exports editable `assets/source/passengers/commuters.blend` and `public/models/passengers/commuters.glb`. No Blender addon is needed.

The second pose revision addresses the MakeHuman rest forearms pointing forward: both forearms and upper arms are posed so non-phone hands rest beside the thighs, with bent finger joints instead of splayed hands. Shoulder bags replace the disconnected briefcase/tote handles. Loose torso profiles remove the inflated anatomy beneath clothing; a continuous knit collar covers the neck seam. The phone pose includes an actual phone. These remain original stylised models rather than scanned people.

The outfit pass adds a navy open jacket with a contrasting shirt, two longer open coats, a green hoodie with a dropped hood and pocket seams, a plain knit top, and a blue shirt with collar points. Continuous hem bands overlap the trousers instead of exposing serrated waist edges, and wrist cuffs keep the hands visibly uncovered. The six hairlines now include short cropped hair, a tied bun, longer side/back hair, a shorter bob, and a higher greying hairline. Shoulder bags, backpacks and the phone remain separate readable props.

Rebuild and deduplicate with:

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --threads 4 --python scripts/blender/build_passengers.py
npx --yes @gltf-transform/cli@4.5.0 dedup public/models/passengers/commuters.glb /tmp/commuters-dedup.glb
cp /tmp/commuters-dedup.glb public/models/passengers/commuters.glb
```

The GLB is approximately 13.8 MB and the complete set is approximately 149,000 triangles. Six full variants and six reduced meshes share five materials. Heights range from 1.65 to 1.85 metres; feet are at Y=0 and front is +Z in glTF. Nodes are `commuter_01` through `commuter_06`, with `_low` equivalents. The runtime instances each variant/material, uses full detail within 40 metres, reduced geometry from 40–150 metres, and hides distant people. There are 24 placements per unique station.

## Restrained idle motion

Each near mesh exports three genuine glTF morph targets: `look_left`, `look_right` and `breathe`. The head turns at most eight degrees around the skull base with a blended neck; the upper chest expands by two millimetres. The pelvis, legs, feet and placement matrices do not move. `passenger-idle.ts` samples eased glance/hold/return events and breathing from simulation time with different phases and periods for each placement. Pausing or replaying the same service time produces exactly the same weights. These three idle targets keep the feet planted. Walking uses its own separately authored deformation targets below.

The WebGPU renderer uses `InstancedMesh.setMorphAt()` and one weight texture per animated material batch. In the installed Three r180 implementation, `MorphNode.setup()` selects the instance-texture path only when `mesh.count > 1`. Morph batches therefore allocate the full texture before rendering and keep a minimum count of two, using a zero-scale second instance for singleton draws. Hidden batches keep that contract too; their visibility is false. This avoids switching shader paths when the crowd culls to one person. Far meshes omit these small idle head/chest deformations, but include the complete walking cycle to avoid sliding legs when a moving commuter crosses the 40 metre detail boundary.

One additional instanced transparent plane batch provides two small soft footprint contact cues, visible within 75 metres. They are authored grounding cues, not physically calculated light shadows. Near people retain ordinary dynamic shadow casting.

## Walking poses

Both near and far meshes export eight additional `walk_0` through `walk_7` morph targets. They contain a full left/right cycle sampled at eighth-cycle intervals. The near target order is `look_left`, `look_right`, `breathe`, then `walk_0` through `walk_7`; the far target order contains only the eight walking targets. The runtime must address targets by name, blend adjacent walking poses cyclically, and use travelled distance divided by **1.1 metres** as phase. Weight one is the complete gait pose; ramping that weight over the beginning/end of a walk blends back into the standing pose.

The offline builder retains MakeHuman's anatomical vertex weights through garment solidification and mesh reduction. Jacket shoulders close into the neckline; sock cuffs overlap the trouser hem and blend from foot to shin so the raised ankle remains covered. A two-bone inverse kinematics solution bends each leg to a moving ankle target. Shoes and socks follow the foot; sleeves, hands, cuffs and the phone follow their arm. The phone arm swings less. The hips lower 5–7 cm into the stride, with only a 2 cm peak-to-peak vertical variation. This is combined with actual leg articulation and alternating foot lift, rather than moving an entire rigid person up and down. Shoulder bags and backpacks follow the torso.

For the left foot, let `p = phase % 1`; the right foot uses `(phase + 0.5) % 1`. During stance (`p < 0.6`), its local forward displacement is `0.33 - 1.1 * p` metres and its vertical lift is zero. That backwards sole motion cancels a root travelling 1.1 metres per cycle. During swing, let `u = (p - 0.6) / 0.4`: forward displacement is `-0.33 + 0.66 * u² * (3 - 2u)` and lift is `0.09 * sin(πu)` metres. These offsets are added to each variant's authored foot positions. Linear interpolation between the eight exported samples approximates this curve; contact cues should use the same sampled/interpolated phase. A full gait cycle takes one second at 1.1 m/s. Forward is **+Z in glTF**, equivalent to **-Y in Blender**.

Walking morphs export position deltas, with shared base vertex normals. This bounds payload and avoids increasing material/draw batches; very close views are still stylised, particularly around flexed joints. There is no skinning skeleton or animation mixer running per person. Root placement, heading, stopping, door association and visibility remain simulation/runtime responsibilities; the asset alone does not implement pathfinding or boarding.

## Verification and limits

`tests/passenger-assets.test.ts` reads the shipped GLB, verifies all twelve roots, three near idle targets and eight walking targets on both detail levels, enforces the five-material / 16 MB payload budget, and checks that idle targets keep lower-leg and sole vertices fixed. Initial exported morph weights are all zero. Walking checks confirm nonzero finite deltas and alternating raised/planted feet in both detail levels. `tests/passenger-idle.test.ts` checks deterministic pause/replay poses, bounded weights, independent timing and non-overlapping left/right glances. Browser pause verification uses the canvas passenger metrics (`animated`, `simulationTime`, `idleWeightSum`) alongside visual checks.

The Blender lineup is rendered to `/tmp/passengers-lineup.png`; denoising is disabled because the installed OpenImageDenoise path was very slow during review. Visual review is required after regenerating poses. Faces and outfits are still stylised and repetitive at close range. There is no facial animation, skeletal runtime rig or general crowd collision/pathfinding system. The exported gait is a restrained platform walk, with flat-foot contact and eight-pose interpolation; it is not a motion-captured or physically simulated human.
