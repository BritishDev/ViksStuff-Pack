# Training HUD artwork

Generated with the built-in ImageGen tool on 2026-09-15.

Exact prompt:
Create a Minecraft resource pack HUD sprite atlas on a genuinely transparent background. Three isolated horizontal plaques in three equal-height rows, centered, no overlap. Top plaque exact text "Clutch" in bold beautiful continuous bright red to deep dark red gradient letters, compact dark beveled backing and thin crimson border. Middle plaque exact text "FAILED" in bold coral red with dark red backing. Bottom plaque exact text "SUCCESS" in bold emerald green with dark green backing. Pixel-art influenced crisp game UI, clean readable lettering, no extra words, no scenery, no watermark. Each plaque is wide and short with generous transparent padding; atlas 1536x1024. These will be cropped as individual bitmap font glyphs for boss bar and title rendering.

The selected source is atlas.png. The generator retained a dark backdrop; no alpha transparency is claimed. process-training.mjs extracts each plaque and scales to 256 pixels wide with nearest-neighbour sampling. Fonts render the heading at 18 GUI pixels and result glyphs at 24 (before vanilla title scaling). No shader override or replacement of unrelated vanilla boss bars is required. The image itself contains the bold red gradient; glyph components remain white to preserve artwork colors.

Rebuild: node scripts/process-training.mjs, then scripts/build-pack.ps1.

## Compact attempt HUD revision

Built-in ImageGen prompt for attempts.png:
A game UI sprite sheet, 1536x1024. Exactly three square icon tiles aligned horizontally in equal 512-pixel columns, centered vertically at y=512. Each icon fits inside a 400x400 area. Left: empty dark round medallion with crimson beveled rim, no symbol. Middle: same round medallion with bright emerald green check mark. Right: same round medallion with bold red X cross. Minecraft pixel art style, crisp bevels, dark nearly black backplates, ruby red rims, matching a bold red gradient Clutch game HUD. Flat black background. No text, no letters, no other decoration. Symmetric and identical size.

The HUD now uses ten 12-pixel icons with ascent -3, moving the top edge below the screen margin. Result glyph height is 8 pixels (32 pixels in vanilla titles; 8 pixels in spectator action bars). The purple vanilla boss-bar background/progress sprites are transparent and purple is reserved for this HUD; future purple bars would also have their strip hidden. Other boss-bar colors are preserved.

Custom audio is original mathematical synthesis, not downloaded material: success is a 480ms ascending C/E/G chime, failed is a 360ms descending A/E/A chime. synthesize-training.py generates mono 44.1kHz WAV sources and encodes Ogg Vorbis using FFmpeg. All sounds have short attack/release envelopes and play privately to the contestant and eligible spectators.

## Smooth framed HUD revision

Built-in ImageGen prompt for attempts-smooth.png:
Create a smooth polished game HUD icon atlas 1536x1024. Three identical sized circular medallions in horizontal row, centers exactly x256 x768 x1280 and y512. Each diameter 440 pixels. Left empty charcoal circle with elegant thin ruby red metallic rim. Middle identical circle with emerald green check. Right identical circle with red X. Smooth antialiased circular edges, modern glossy game interface, NOT pixel art, no stair-step edges, restrained red gradient bevel. Pure black background no glow outside the circles. No text or additional objects.

The derivatives now use 128x128 textures and Lanczos sampling instead of 32x32 nearest-neighbour textures. A code-native 138x18 GUI-pixel dark frame with a red gradient border surrounds the ten icons. The frame is generated at 4x resolution. Font spacing overlays the icons with four pixels of horizontal padding. Minecraft GUI scaling still limits final screen sharpness; verify in the client.
