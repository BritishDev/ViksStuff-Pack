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
