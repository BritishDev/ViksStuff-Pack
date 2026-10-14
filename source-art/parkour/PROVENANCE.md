# Championship Gold HUD

The user selected design 2 from this task's ImageGen exploration, then requested
a direct visual match after rejecting the first simplified implementation.
`championship-gold.png` is the original generated image, preserved unchanged.
SHA-256: `4f65714ef1047060fca1af928d342c299b6fb9e5c892ac093a5e13c2a26719d8`.

The generation brief specified three equally tall badges: `#1`, a stopwatch and
`42.73s`, and a Minecraft Steve face. The selected direction was smoked graphite
interiors, stepped gold rims, pale-gold upper bevels, broad chamfered corners,
dark inset channels and white numbers, with no fantasy ornaments or branding.

`scripts/build-parkour-timer.py` derives the original frame edges and stopwatch
directly from this image. Only sample rank/time/portrait holes are reconstructed
from nearby clean scanlines. The available letter bodies are extracted into
custom bitmap font atlases; additional numeric characters extend the same heavy
block style. Shadows are baked into the glyphs. Double-resolution background
textures are split into three glyphs so each fits Minecraft's native font atlas.
Explicit kerning preserves tabular numeral spacing and a narrow decimal point.

The live plugin supplies real ranks, section times and sanitized current-player
skins. The sample Steve face appears only in the artwork comparison preview;
it is never baked into the runtime backgrounds. `metrics.json` records native
layout and font geometry. `previews/parkour-gold-reference-match.png` compares
the original artwork (top) with the assembled atlas preview (bottom).

The plugin's live scale does not change these source textures or font metrics.
Reserved GUI colors communicate a 25%-125% affine scale to the text shader;
frames, letter bodies and the live portrait all share the same transform.
The default is 55%. `previews/parkour-gold-scales.png` compares selected sizes.

## CHECKPOINT plaque
Generated with the built-in Codex image generator on 2026-10-14 and approved by the user. Reference: championship-gold.png. Prompt: one front-facing transparent CHECKPOINT plaque matching the gold stepped bevel frame, charcoal inset and white pixel text; small downward gold chevron, subtle frame thickness, no other text or scene. Source retained as checkpoint-gold.png. scripts/build-checkpoint-assets.py packages the transparent art into a 512-square atlas and a thin extruded item model, plus hollow block-edge models.

