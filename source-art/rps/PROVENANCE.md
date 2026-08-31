# Rock-paper-scissors icon provenance

These three original RGBA PNGs were generated specifically for ViksStuff-Pack with
OpenAI ImageGen. They were not copied, traced, or extracted from the supplied
inspiration archive.

## Source files

| Icon | Repository source | Original generated filename | SHA-256 |
| --- | --- | --- | --- |
| Rock | `rps-rock-imagegen-original.png` | `exec-b339ded5-ba89-4607-b3cd-e5f8223d6599.png` | `31792f0bafd8fa971bda79623929c1e73f2475c7e8f88894b659e6d4ea422049` |
| Paper | `rps-paper-imagegen-original.png` | `exec-86fd88cc-82b3-4290-bb97-0932678afc48.png` | `bbaf7292905aafc2d0eeb870e0d1f21b6022c028f247fe4d83db69eb8a100143` |
| Scissors | `rps-scissors-imagegen-original.png` | `exec-e811568d-0bf3-4dd4-ba89-8435af9e2bbc.png` | `31b9cec8396b7c6050b7d52d901e39db8c41e155da485e523f1d65e79eb3a06b` |

## Prompts

### Rock

```text
Use case: stylized-concept
Asset type: Minecraft Java resource-pack game UI icon
Primary request: an original rock hand-symbol icon representing ROCK for a rock-paper-scissors selector
Subject: compact clenched stone fist silhouette, unmistakably rock, no human skin
Style/medium: polished Minecraft-inspired pixel art, chunky 16-bit game UI sprite, crisp hard pixel clusters, subtle dark outline
Composition/framing: one centered square icon with generous transparent padding, readable when reduced to 32x32
Color palette: charcoal slate, warm gray highlights, tiny muted gold accent
Constraints: genuinely transparent background; no text; no letters; no border tile; no shadow outside silhouette; no logos; no watermark; single object only
Avoid: photorealism, smooth vector gradients, scenery, checkerboard background
```

### Paper

```text
Use case: stylized-concept
Asset type: Minecraft Java resource-pack game UI icon
Primary request: an original folded paper hand-symbol icon representing PAPER for a rock-paper-scissors selector
Subject: compact angular sheet of parchment shaped like an open hand, unmistakably paper
Style/medium: polished Minecraft-inspired pixel art, chunky 16-bit game UI sprite, crisp hard pixel clusters, subtle dark outline
Composition/framing: one centered square icon with generous transparent padding, readable when reduced to 32x32
Color palette: warm ivory parchment, pale gray shade, tiny muted gold accent
Constraints: genuinely transparent background; no text; no letters; no border tile; no shadow outside silhouette; no logos; no watermark; single object only
Avoid: photorealism, smooth vector gradients, scenery, checkerboard background
```

### Scissors

```text
Use case: stylized-concept
Asset type: Minecraft Java resource-pack game UI icon
Primary request: an original crossed shears hand-symbol icon representing SCISSORS for a rock-paper-scissors selector
Subject: compact open metal shears forming a clear V silhouette, unmistakably scissors
Style/medium: polished Minecraft-inspired pixel art, chunky 16-bit game UI sprite, crisp hard pixel clusters, subtle dark outline
Composition/framing: one centered square icon with generous transparent padding, readable when reduced to 32x32
Color palette: steel gray blades, deep muted crimson handles, tiny muted gold accent
Constraints: genuinely transparent background; no text; no letters; no border tile; no shadow outside silhouette; no logos; no watermark; single object only
Avoid: photorealism, smooth vector gradients, scenery, checkerboard background
```

## Processing

`scripts/process-rps-icons.mjs` trims fully transparent bounds, fits the visible
art into a 56x56 box using nearest-neighbour resampling, adds four transparent
pixels on every side, and writes deterministic 64x64 RGBA PNGs into the overlay.
The checked-in textures were processed with Node.js 24.19.0 and Sharp 0.35.4.

The generated RPS art is original project material. The separate
`LICENSE-WheelOfWacky` applies only to the pre-existing Wheel of Wacky-derived
assets identified in the base pack and README.
