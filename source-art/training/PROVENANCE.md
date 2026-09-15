# Training HUD artwork

Generated with the built-in ImageGen tool on 2026-09-15.

Exact prompt:
Create a Minecraft resource pack HUD sprite atlas on a genuinely transparent background. Three isolated horizontal plaques in three equal-height rows, centered, no overlap. Top plaque exact text "Clutch" in bold beautiful continuous bright red to deep dark red gradient letters, compact dark beveled backing and thin crimson border. Middle plaque exact text "FAILED" in bold coral red with dark red backing. Bottom plaque exact text "SUCCESS" in bold emerald green with dark green backing. Pixel-art influenced crisp game UI, clean readable lettering, no extra words, no scenery, no watermark. Each plaque is wide and short with generous transparent padding; atlas 1536x1024. These will be cropped as individual bitmap font glyphs for boss bar and title rendering.

The selected source is atlas.png. The generator retained a dark backdrop; no alpha transparency is claimed. process-training.mjs extracts each plaque and scales to 256 pixels wide with nearest-neighbour sampling. Fonts render the heading at 18 GUI pixels and result glyphs at 24 (before vanilla title scaling). No shader override or replacement of unrelated vanilla boss bars is required. The image itself contains the bold red gradient; glyph components remain white to preserve artwork colors.

Rebuild: node scripts/process-training.mjs, then scripts/build-pack.ps1.
