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

## Seven selectable sets and textured final scores

Design 1 preserves the selected Crimson Classic HUD and result artwork. Designs 2-7 are original code-native vector designs, rasterized into PNG bitmap-font assets by scripts/build-training-designs.mjs. These are not additional ImageGen outputs. Themes: Obsidian Edge, Royal Gold, Arctic Glass, Emerald Circuit, Violet Orbit, Pearl Studio. All seven contain scores 0/10 through 10/10, plus BELOW AVERAGE, AVERAGE, and ABOVE AVERAGE plaques. Labels are fixed score bands (0-4, 5, 6-10), not empirical server averages.

Preview commands: /training mode design preview <1-7> [0-10]. The eight-second private preview cycles success, failure, then final score with a spectator action-bar sample. /training mode design set <1-7> explicitly saves the choice. Default remains 1. Active sessions block preview/selection; preview is cleaned up on entry to training, disconnect, or plugin disable. Run node scripts/process-training.mjs before node scripts/build-training-designs.mjs, then scripts/build-pack.ps1. The preview gallery is previews/training/index.html; seven-designs.png is the contact sheet.

## Structural layouts correction

The final build-training-layouts.mjs pass replaces layouts 2-7 with genuinely different arrangements: Segmented Meter, Two-Row Scoreboard, Arc of Diamonds, Split Wings, Hanging Pennants, Ticket Strip. All use the original shared success/failed textures through training_result, regardless of selected mode. Classic Medallions remains design 1.

Each alternative uses one background and ten independently placed bitmap overlays, not a recolored row. Font-space advances cancel the measured glyph width after each layer. /training mode design <1-7> saves and applies the mode immediately; idle players also see its preview. The standard builder invokes this final pass automatically. Older theme names above describe the superseded revision.

## Aim countdown and selection artwork

Built-in ImageGen, using the original SUCCESS/FAILED atlas as a style reference. Source files: aim-countdown.png and select-aim.png. The glyphs are packaged by build-aim-art.mjs using Lanczos reduction. Five through one and GO render at 14 GUI pixels before title scaling; the menu banner renders at 16 GUI pixels. The existing countdown timing and sounds are retained.

Countdown prompt:
Use the supplied SUCCESS and FAILED plaque artwork as a STYLE reference only. Make a new 1536x1024 sprite sheet containing SIX isolated game HUD plaques in a strict 3-column by 2-row grid of equal 512x512 cells. Top row exact text '5', '4', '3'. Bottom row exact text '2', '1', 'GO!'. Each plaque centered within its cell, maximum width 400 pixels and height 200 pixels, generous black padding. Same chunky beveled Minecraft-inspired glossy letters, thin dark metallic panel and jewel-like border. Countdown numbers use vivid cyan to blue gradient instead of red; GO! emerald green. Smooth clean silhouettes, polished rendered edges, not deliberately low-resolution pixelation. Flat black outside plaques, no external glow, no additional text. The digits must be very readable, matching the reference family with a slight fresh cyan variation.

Selection prompt:
Create ONE wide Minecraft game UI plaque matching the beveled SUCCESS/FAILED artwork in the reference. Exact text: SELECT AIM TRAINER. All words on ONE line. Chunky bold beveled letters, vivid cyan-to-blue gradient, black metallic backing and thin cyan beveled border with small blue jewel accents at ends. Smooth polished finish while keeping the original chunky lettering style. Center the plaque in a 1536x1024 image; plaque spans x80 to1456 and y380 to640 approximately, horizontal very wide and short. Flat black background, no external glow, no extra words, no watermark. Text must read exactly SELECT AIM TRAINER, perfectly legible.

The selection plaque text was changed to GOOD LUCK! at the user's request. Built-in ImageGen edit prompt: Change the exact lettering from SELECT AIM TRAINER to GOOD LUCK! including the exclamation mark. Keep the same cyan-to-blue beveled chunky lettering, dark metallic plaque, thin blue border and jewel accents. Keep the image 1536x1024 and the plaque within the same approximate x8..1528 y350..610 bounding area so it remains compatible with the existing crop. Center GOOD LUCK! and use appropriately spaced bold letters. Flat black background, no extra text.
Final source: good-luck.png. Existing glyph identifier is retained for compatibility.
