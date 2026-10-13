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
            return expand(jar.read(path).decode(), seen)
        return re.sub(r"#moj_import\s+<([^>]+)>", include, source)
    for filename, extension in [("rendertype_text.vsh", "vert"), ("rendertype_text.fsh", "frag")]:
        (output / f"text.{extension}").write_text("#version 330\n" + expand((shader_dir / filename).read_text(), set()))
result = subprocess.run([str(compiler), "-l", str(output / "text.vert"), str(output / "text.frag")], capture_output=True, text=True)
if result.returncode: raise SystemExit(result.stdout + result.stderr)

assets = root / "overlay/assets/viksstuff"
for font, expected_advance in [("parkour_timer_digits", 7), ("parkour_timer_small", 6)]:
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
assert panel.size == (200, 17) and panel.getpixel((100, 12))[3] == 255
assert panel.getpixel((100, 2))[3] == 180
assert panel.getpixel((0, 1)) == (255, 0, 255, 255)
assert panel.getpixel((5, 14)) == (1, 0, 254, 255)
assert panel.getpixel((194, 14)) == (254, 0, 254, 255)
print("PARKOUR TIMER SHADERS PASS: linked vertex/fragment stages using native 1.21.11 includes; 49 fixed-width glyphs; translucent inline strip; server-driven countdown progress mask.")
