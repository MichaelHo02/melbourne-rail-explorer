# City Loop environment rebuild

Active goal: coherent, realistic buildings, ground and vegetation throughout the visible City Loop environment, using Victorian open data, Blender and generated visual assets. Whole corridor; viaduct first. Work is isolated on `codex/city-loop-environment`.

## First implementation checkpoint

The original surveyed viaduct building pair was already present at baseline commit `87956da`; it is not new work in this checkpoint. The current implementation adds:

- `scripts/prepare-loop-landscape.py` reproducibly queries two non-overlapping northern/eastern rectangles using the existing source API/clip contracts. The southern corridor source is unchanged. It fetched 1,353 road segments, 174 rail segments, 6,405 trees and 39 open-space features into `src/data/loop-landscape-source.json` (1,740,889 bytes). Source URLs, queries, licences, field caveats and retrieval date are bundled. Truncation and payload limits fail the build step rather than silently dropping data.
- Rendering combines the two inventories, resolves species indices and deduplicates shared tree IDs against the southern dataset. Known named parks get lawn; promenades/squares get paving. Open-space designation alone does not imply turf. Parcels remain flat at the existing authored ground datum; these are not a terrain survey.
- `scripts/blender/build_urban_trees.py` creates editable plane, gum, elm and palm prototypes with branching trunks and full three-dimensional leaves/fronds. Each prototype uses one vertex-colour material for efficient instancing. Source `.blend` and runtime `.glb` are retained. Prototype sizes and species-class approximations are artistic; original mapped tree coordinates remain unchanged. The previous undocumented conversion of trunk diameter to centimetres is removed.
- Near trees use the Blender models; distant trees retain inexpensive foliage cards in 200 m cells. Surface railway clearance uses route-wide samples rather than only the viaduct. Asset load is included in scene readiness.
- Generated turf is used as an authored base-colour texture on mapped lawn parcels, with repeat wrapping and mipmaps. It is not an aerial photograph.

Sources: [City Urban Forest](https://data.melbourne.vic.gov.au/explore/dataset/trees-with-species-and-dimensions-urban-forest/information/), [Vicmap Transport](https://discover.data.vic.gov.au/dataset/vicmap-transport), [VEAC Open Space Inventory](https://discover.data.vic.gov.au/dataset/veac-metropolitan-melbourne-open-space-inventory). CC BY 4.0. Geometry processing and artistic dimensions are disclosed in the source manifests and existing game credits.

## Visual direction and generated assets

Built-in image generation was used, not the CLI/API fallback.

`docs/assets/urban-vegetation-direction.png`: original modelling reference. Prompt: “Use case: stylized-concept. Asset type: Blender environment modelling reference sheet for a realistic Melbourne City Loop train simulator. Create a refined landscape-format 3D production design sheet showing four separate vegetation assets on a neutral light grey studio background: a mature London plane tree with strong mottled pale trunk, branching limbs and irregular broad green canopy; a river red gum with pale grey branching trunk and airy hanging narrow-leaf grey-green foliage; a rounded dense elm with visible buttressed base and branching; a Canary Island date palm with thick textured trunk and gracefully arching feathery fronds. Each tree entirely visible with no overlap, at consistent scale with physically believable branches and natural crown variation. Lower strip shows small close-up material studies of Melbourne bluestone retaining wall, dry green riverbank turf with sparse leaf litter, and pale exposed-aggregate promenade. Realistic game-ready PBR visual target, soft neutral daylight, restrained natural greens, no cartoon blobs or low-poly faceted spheres. This is an artistic modelling guide, not surveyed geometry or evidence of real tree locations. No text, no labels, no logos, no people.”

`public/textures/surfaces/riverbank-turf.png`: runtime turf. Prompt: “Use case: photorealistic-natural. Asset type: seamless square albedo texture for Melbourne riverside park turf in a realistic 3D train game. Orthographic straight-down macro-to-medium view of a 4 metre square patch of slightly dry early-spring urban park lawn. Fine interwoven muted olive and sage green grass blades, subtle pale straw thatch and tiny occasional brown leaf fragments, small irregular sparse dry patches, natural organic scale variation. Flat diffuse illumination suitable as PBR base color, absolutely no directional lighting, no cast shadows, no ambient-occlusion shading, no perspective, no horizon, no objects, no labels, no borders. Texture should tile seamlessly on all four edges and contain no large distinctive central mark. Natural restrained colours, no saturated emerald green. Grass fills entire image edge to edge; make the microtexture detailed but the large-scale colour variation subtle.”

## Verification and remaining work

Initial visual review at the viaduct and northbank rejected sparse first-generation crowns; crown coverage was increased and leaf orientations corrected. A subsequent performance sample at the northbank was 22.22 ms/frame, 743 draw calls, 3.26 million triangles, WebGPU ready, no logged browser errors. Leaf geometry was then halved; this sample is therefore not a final performance claim.

129 tests passed before the final leaf optimization and turf integration. Production build passed with the expanded geography; Vite reported its existing large-bundle warning. Final checkpoint validation is recorded below.

The full goal remains active. Remaining audits/work include: prominent building identity and facade coherence beyond the existing pair; Southern Cross approach ground/rail joins; park/path edge and foreground ground detail; tree silhouette/LOD transition refinement; aerial-mesh/ground overlap and floating fragments; all-route cab and exterior visual checks; final performance and gameplay verification. Data coverage and a passing build alone do not establish environment realism.

Final checkpoint validation: production build passed after turf integration and leaf optimization; all three dedicated source/asset tests passed. The earlier complete regression run passed 129 tests. Southern Cross platform and northbank scenes were opened in the in-app WebGPU browser. The full-route visual and final performance audits remain outstanding.
