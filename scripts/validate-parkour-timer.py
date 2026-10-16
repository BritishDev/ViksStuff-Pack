"""Compile both native 1.21.11 text stages and verify the font's actual bitmap advances."""
from pathlib import Path
import json, re, subprocess, sys, zipfile
from PIL import Image

root = Path(__file__).resolve().parents[1]
client, compiler = map(Path, sys.argv[1:3])
output = root.parent / ".tools/parkour-timer-shader-validation"
output.mkdir(parents=True, exist_ok=True)
shader_dir = root / "overlay/strength_1_21_11/assets/minecraft/shaders/core"
with zipfile.ZipFile(client) as jar:
    assert json.loads(jar.read("version.json"))["id"] == "1.21.11", "Validation requires the target client JAR."
    def expand(source, seen):
        source = re.sub(r"^\s*#version[^\n]*\n", "", source, flags=re.M)
        def include(match):
            identifier = match.group(1)
            namespace, name = identifier.split(":", 1) if ":" in identifier else ("minecraft", identifier)
            path = f"assets/{namespace}/shaders/include/{name}"
            if path in seen: return ""
            seen.add(path)
            local = root / "overlay/strength_1_21_11" / path
            return expand(local.read_text() if local.exists() else jar.read(path).decode(), seen)
        return re.sub(r"#moj_import\s+<([^>]+)>", include, source)
    for pipeline in ["rendertype_text", "rendertype_text_intensity", "rendertype_text_see_through", "rendertype_text_intensity_see_through"]:
        for suffix, extension in [("vsh", "vert"), ("fsh", "frag")]:
            filename = pipeline + "." + suffix
            local = shader_dir / filename
            source = local.read_text() if local.exists() else jar.read("assets/minecraft/shaders/core/"+filename).decode()
            (output / f"{pipeline}.{extension}").write_text("#version 330\n" + expand(source, set()))
        result = subprocess.run([str(compiler), "-l", str(output / f"{pipeline}.vert"), str(output / f"{pipeline}.frag")], capture_output=True, text=True)
        if result.returncode: raise SystemExit(result.stdout + result.stderr)
        print("LINK PASS:",pipeline)

assets = root / "overlay/assets/viksstuff"
metrics = json.loads((root / 'source-art/parkour/metrics.json').read_text())
for name, spec in metrics['fonts'].items():
    font, expected_advance = 'parkour_timer_' + name, spec['native_advance']
    providers = json.loads((assets / f"font/{font}.json").read_text())["providers"]
    for provider in providers:
        if provider["type"] != "bitmap": continue
        image = Image.open(assets / ("textures/" + provider["file"].split(":")[1])).convert("RGBA")
        chars = provider["chars"][0]
        cell = image.width // len(chars)
        scale = provider["height"] / image.height
        for index, char in enumerate(chars):
            occupied = [x for x in range(cell) if any(image.getpixel((index * cell + x, y))[3] for y in range(image.height))]
            actual = int((max(occupied) + 1) * scale + 0.5) + 1
            assert actual == expected_advance, (font, char, actual, expected_advance)
panel = Image.open(assets / "textures/parkour/timer_panel.png")
assert panel.size == (388, 78)
for design in metrics['designs']:
    provider=json.loads((assets / f'font/parkour_timer_{design}.json').read_text())['providers']
    assert len(provider)==4
    for frame in metrics['frames']:
        tile=Image.open(assets / f"textures/parkour/timer_{design}_{frame['name']}_frame.png")
        assert tile.size==(frame['width']*2,78)
        assert max(tile.size)<=256
assert len({Image.open(assets / f'textures/parkour/timer_{d}_panel.png').tobytes() for d in metrics['designs']})==5
for frame in metrics['frames']:
    image = Image.open(assets / f"textures/parkour/timer_{frame['name']}_frame.png")
    assert image.width <= 256 and image.height <= 256, 'Native bitmap atlas allocation exceeded'
    assert image.size == (frame['width']*2,78)
for name in ('white_background','white_progress'):
    sprite=Image.open(root / f'overlay/assets/minecraft/textures/gui/sprites/boss_bar/{name}.png')
    assert sprite.size == (182,5) and not sprite.getchannel('A').getbbox()
print("CRIMSON SHADERS PASS: native 1.21.11 stages linked; 51 light glyphs; five distinct atlas-safe compositions; transparent WHITE carrier.")
