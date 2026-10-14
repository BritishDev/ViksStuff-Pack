# Crimson parkour timer designs

Five original compositions drawn with explicit polygon/line geometry. Editable SVG masters are in this directory; raster exports are reproduced by scripts/build-parkour-timer.py. Colors: crimson #D52D45, graphite #211B22, warm white #F4E9E7. Glyphs are rasterized from the locally installed Segoe UI Light font; no font file is redistributed. Windows with that font and Pillow are required to regenerate.

The preview portrait is a deliberately synthetic demonstration face. Runtime artwork contains no portrait or time: the plugin supplies the disguise-safe visible skin and clock. There is no rank/position on either custom or plain overlays. Countdown and handover retain 5.00s formatting and the existing live-scale shader.

Design IDs: ribbon, bracket, split, ticket, orbit. Each uses different framing geometry while preserving the same live head slot and stable native text centering. Rank-named crop files are retained for atlas compatibility; they contain only artwork.

Validation on 2026-10-14: targeted ParkourTimerHudTest passed; target 1.21.11 shader stages linked; 51 numeric glyph advances validated; all five frame sets within 256px atlas limits; 2415 native Minecraft glyph/space checks and 36 GUI centering/scale combinations passed. Local raster review completed. In-game readability with actual client/shaders remains a separate playtest.
