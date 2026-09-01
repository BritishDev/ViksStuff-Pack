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
