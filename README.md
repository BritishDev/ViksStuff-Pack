# ViksStuff Pack

Client resource pack for the standalone Viks Stuff recording server.

## Reproducible build

The tracked `base/ViksStuff-Pack.base.zip` is the preserved pack from before the
RPS integration. Files under `overlay/` are merged over that base in ordinal path
order. The builder writes each ZIP entry once with a fixed `1980-01-01T00:00:00Z`
timestamp, so repeat builds do not accumulate duplicate paths or local file times.

```powershell
.\scripts\build-pack.ps1
.\scripts\validate-pack.ps1
```

The validator checks pack format 75.0, every JSON file, case-sensitive and
case-insensitive ZIP uniqueness, and the 64x64 RGBA RPS textures. To regenerate
the icon derivatives, install Sharp 0.35.4 (`npm install --no-save sharp@0.35.4`),
run `node scripts/process-rps-icons.mjs`, then rebuild the ZIP.

The RPS item-model keys are:

- `viksstuff:rps_rock`
- `viksstuff:rps_paper`
- `viksstuff:rps_scissors`

Round selectors support every value from 1 through 25 through the item-model
keys `viksstuff:round_1` to `viksstuff:round_25`. Their generated source sheet,
exact prompt, hash, and nearest-neighbour processing notes are recorded in
`source-art/rounds/PROVENANCE.md`.

Source-art hashes, exact ImageGen prompts, processing details, and licensing
scope are recorded in `source-art/rps/PROVENANCE.md`. No asset from the supplied
unlicensed inspiration archive is included.

## Third-party assets

The wheel texture and geometry reference are adapted from
[Wheel of Wacky](https://github.com/HyperPigeon/WheelOfWacky), distributed
under the MIT License. See `LICENSE-WheelOfWacky`.
Resource pack assets for the standalone Viks Stuff recording server

## Parkour relay timer

The default `ribbon` layout follows the user's Minecraft pixel-badge reference: a crimson stepped bevel, recessed graphite timer face, and a matching live skin badge. Regular custom pixel numerals replace the previous desktop font. Position/rank is omitted from the overlay and remains available through standings. The server supplies the section time and visible disguise-safe player's head; sample data is never baked into runtime frames.

Editable art, the preserved reference and provenance are in `source-art/parkour/reference-badge/`. Reproduce it with `scripts/build-parkour-timer.py` and `scripts/parkour_badge_art.py`. The native atlas retains the 194-by-39 composition and existing scale/head contracts. `previews/parkour-reference-badge.png` shows detail and default-size views. The other design IDs remain available for compatibility.

A scoped Minecraft 1.21.11 text shader enlarges native skin-backed text heads
to 22 by 22 pixels. The WHITE boss-bar color is reserved as an invisible HUD
carrier; only its background and progress sprites are blanked. Other colors
keep vanilla sprites. The plugin's plain fallback uses BLUE.

The matching plugin defaults to 55% size and encodes the live scale in reserved
GUI colors. The shader scales the entire frame/text/portrait composition together
around the screen center and a fixed top margin; ordinary text is unaffected.
`/parkourtimer scale 50` sets 50%, while `scale smaller`, `scale bigger` and
`scale reset` provide quick adjustment. The saved range is 25%-125% in half-percent
steps, and changes need no pack download or restart. The scale comparison is
`previews/parkour-gold-scales.png`; its raster preview is not client proof.

Regenerate assets with `python scripts/build-parkour-timer.py`, then run the
normal reproducible pack build. `scripts/validate-parkour-timer.py` links both
shader stages against a 1.21.11 client JAR and checks bitmap advances. The
`previews/parkour-timer-states.png` image is an artwork preview, not client proof.

On the matching plugin build, `/parkourtimer preview` demonstrates the ten-second
start, two twenty-second legs, and a five-second handover. Manual controls
include `handover [next player]`, `runner <player>` during a countdown, and
`standings` for recorded results. Client appearance,
GUI scaling, stacked boss bars, and modded-client shader support need an in-game
playtest after deployment.
