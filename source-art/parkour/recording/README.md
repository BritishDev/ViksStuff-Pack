# Parkour recording assets

The solid FINISH sign is hand-composed Minecraft cuboid geometry with a recessed charcoal face, stepped green frame and raised pixel lettering. `scripts/build-parkour-solid-signs.py` is its authoritative editable source. The existing gold CHECKPOINT model is preserved.

`parkour-solid-signs.blend` is an editable Blender reconstruction of the exact cuboids, rendered in an isolated Blender 5.2.1 background process. The preview is `previews/parkour-solid-signs-3d.png`; it is an angled model render, not Minecraft client proof.

The separate `previews/water-concept.png` was generated with the built-in image tool using: "Create a seamless tileable Minecraft-style water texture concept. Square 512x512 image, deliberately chunky low-resolution pixel art, exactly a 32 by 32 logical pixel grid enlarged with hard nearest-neighbor edges. Muted clean cyan-blue water, subtle stepped horizontal wave clusters and restrained pale blue highlights, no foam, no objects, no text, no border, no photorealism, no gradients or blur. Pattern should tile seamlessly on all four edges. This is a texture preview for a lush green parkour map, readable and calm with low visual noise." It is preview-only; no vanilla water textures are overridden.

Audio revision 5 derives from the existing nine masters (the slime recording remains the user-supplied remix). A +4 dB gain stage and peak limiter increase RMS without clipping; actual measured gains and hashes are in `docs/parkour-sounds.json`. Only vanilla block slime step/fall events are silenced. Original creative provenance remains recorded for each cue.
