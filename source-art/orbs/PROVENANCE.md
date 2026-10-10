# Original orb materials and geometry

The orb geometry, circuit textures, projection sigils, LabPBR material maps, material shader and three synthesized sounds were authored for this project. They do not derive from a third-party asset or from the AI concept illustrations.

`scripts/build-orb-assets.mjs` builds 14 custom item/model keys, six albedo textures, corresponding normal/specular maps, synchronized 16-frame circuit animations, and three namespaced Vorbis sounds using Sharp and FFmpeg. `scripts/validate-orb-assets.mjs` checks references, legal bounds, emission values, synchronized dimensions and LabPBR alpha encoding. `scripts/validate-orb-shaders.py` uses the installed Minecraft 1.21.11 JAR for shader include definitions and Khronos glslang to link nine pipeline variants.

The original orb shader include is `assets/viksstuff/shaders/include/orb_material.glsl`. The existing combined pack's entity shader integration is extended, retaining its player/mannequin logic and bringing the general per-face lighting interface into line with 1.21.11. Only tagged orb materials enter the new shading branch. Player skin dimensions are explicitly excluded. The standard source include contents are used for validation only and are not copied into this repository.

The alpha tag is 249/255 with a narrow white/red chroma check. LabPBR specular alpha intentionally stays below 255: 255 means no emission in LabPBR 1.3. These are resource-pack material effects; they do not implement screen-wide bloom or guarantee shader-mod compatibility.
