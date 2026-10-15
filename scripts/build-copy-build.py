"""Original, integer-grid emerald badge art for Copy the Build.

No existing pack image is modified. The established 194px HUD contract and
shader marker are shared; every texture, font and editable master is additive.
"""
from pathlib import Path
import json
from PIL import Image, ImageDraw
from parkour_badge_art import PATTERNS, outline

ROOT = Path(__file__).resolve().parents[1]
TEXTURES = ROOT / 'overlay/assets/viksstuff/textures/copy_build'
FONTS = ROOT / 'overlay/assets/viksstuff/font'
SOURCE = ROOT / 'source-art/copy-build'
PREVIEWS = ROOT / 'previews'
for directory in (TEXTURES, FONTS, SOURCE, PREVIEWS):
    directory.mkdir(parents=True, exist_ok=True)
GREEN, LIGHT, DARK = '#39FF88', '#F1FFE9', '#132019'
CHARACTERS = '0123456789.s'
panel = Image.new('RGBA', (194, 39))
draw = ImageDraw.Draw(panel)


def polygon(points, color):
    draw.polygon(points, fill=color)


def rectangle(box, color):
    x1, y1, x2, y2 = box
    polygon([(x1, y1), (x2 + 1, y1), (x2 + 1, y2 + 1), (x1, y2 + 1)], color)


def badge(x, width):
    polygon(outline(x + 1, 3, width - 1, 36, 7), '#06190D')
    polygon(outline(x, 1, width - 1, 36, 7), '#103920')
    polygon(outline(x + 1, 2, width - 3, 34, 6), '#208D43')
    polygon(outline(x + 2, 3, width - 5, 32, 5), '#44D66A')
    # Distinct top, bevel, lip and inset planes: all colors meet on whole pixels.
    rectangle((x + 7, 2, x + width - 9, 3), '#BFFF94')
    rectangle((x + 5, 4, x + width - 7, 4), '#74F58D')
    rectangle((x + 3, 7, x + 4, 28), '#89F19A')
    rectangle((x + 7, 33, x + width - 9, 34), '#247B36')
    rectangle((x + width - 5, 8, x + width - 4, 28), '#237539')
    polygon(outline(x + 5, 6, width - 11, 26, 4), '#07120C')
    polygon(outline(x + 6, 7, width - 13, 24, 3), '#1C2923')
    rectangle((x + 10, 8, x + width - 12, 12), '#24302A')
    rectangle((x + 8, 27, x + width - 10, 29), '#16251C')
    rectangle((x + 11, 3, x + 18, 3), '#E5FFB5')


badge(0, 39)
badge(43, 151)
# Stop watch, drawn at the native GUI scale. Cream face remains clearly readable.
rectangle((16, 8, 21, 9), '#09331C')
rectangle((17, 7, 20, 8), '#AEFF96')
polygon([(14, 11), (23, 11), (27, 15), (27, 24), (23, 28), (14, 28), (10, 24), (10, 15)], '#0A130E')
polygon([(14, 12), (23, 12), (26, 15), (26, 24), (23, 27), (14, 27), (11, 24), (11, 15)], '#76DD75')
polygon([(15, 14), (22, 14), (24, 16), (24, 23), (22, 25), (15, 25), (13, 23), (13, 16)], LIGHT)
rectangle((18, 15, 19, 20), '#273429')
rectangle((19, 20, 22, 21), '#273429')
rectangle((12, 15, 12, 18), '#D8FFB8')

# Export exact pixel runs as editable SVG rectangles, avoiding polygon rasterizer
# edge differences between the preview and vector editors.
pixel_svg = []
for y in range(panel.height):
    x = 0
    while x < panel.width:
        color = panel.getpixel((x, y))
        right = x + 1
        while right < panel.width and panel.getpixel((right, y)) == color:
            right += 1
        if color[3]:
            pixel_svg.append(f'<rect x="{x}" y="{y}" width="{right-x}" height="1" fill="#{color[0]:02x}{color[1]:02x}{color[2]:02x}"/>')
        x = right
panel = panel.resize((388, 78), Image.Resampling.NEAREST)
panel.save(TEXTURES / 'timer_panel.png')
(SOURCE / 'emerald-timer.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 194 39" shape-rendering="crispEdges">' + ''.join(pixel_svg) + '</svg>\n')
providers = []
for index in range(2):
    tile = panel.crop((index * 194, 0, (index + 1) * 194, 78))
    tile.putpixel((193, 77), (255, 255, 255, 1))
    tile.save(TEXTURES / f'timer_frame_{index}.png')
    providers.append(dict(type='bitmap', file=f'viksstuff:copy_build/timer_frame_{index}.png',
                          height=39, ascent=6, chars=[chr(0xE600 + index)]))
providers.append(dict(type='space', advances={chr(0xE800 + amount + 195): amount for amount in range(-195, 196)}))
(FONTS / 'copy_build_timer.json').write_text(json.dumps(dict(providers=providers), indent=2) + '\n')

sheet = Image.new('RGBA', (28 * len(CHARACTERS), 38))
letters = {}
for index, character in enumerate(CHARACTERS):
    tile = Image.new('RGBA', (28, 38))
    brush = ImageDraw.Draw(tile)
    step = 3 if character == 's' else 4
    y0 = 7 if character == 's' else 0
    for color, offset in [('#0A150E', 2), (GREEN if character == 's' else LIGHT, 0)]:
        for y, row in enumerate(PATTERNS[character]):
            for x, bit in enumerate(row):
                if bit == '1':
                    left, top = x * step + offset, y * step + y0 + offset
                    brush.rectangle((left, top, left + step - 1, top + step - 1), fill=color)
    tile.putpixel((25, 37), (255, 255, 255, 1))
    sheet.alpha_composite(tile, (index * 28, 0))
    letters[character] = tile
sheet.save(TEXTURES / 'timer_digits.png')
(FONTS / 'copy_build_digits.json').write_text(json.dumps(dict(providers=[dict(
    type='bitmap', file='viksstuff:copy_build/timer_digits.png', height=19, ascent=-6, chars=[CHARACTERS])]), indent=2) + '\n')

icons = Image.new('RGBA', (36, 9))
for index in range(4):
    tile = Image.new('RGBA', (9, 9))
    d = ImageDraw.Draw(tile)
    if index == 0:  # Block: three planes on an integer isometric grid.
        d.polygon([(4, 0), (8, 2), (8, 6), (4, 8), (0, 6), (0, 2)], fill='#15492C')
        d.polygon([(4, 1), (7, 2), (4, 4), (1, 2)], fill='#A2FF9C')
        d.polygon([(1, 3), (3, 5), (3, 7), (1, 6)], fill='#48DB74')
        d.polygon([(5, 5), (7, 3), (7, 6), (5, 7)], fill='#239B50')
    elif index == 1:
        d.rectangle((3, 0, 5, 1), fill='#AEFF96')
        d.polygon([(2, 2), (6, 2), (8, 4), (8, 6), (6, 8), (2, 8), (0, 6), (0, 4)], fill='#40CE70')
        d.rectangle((2, 3, 6, 6), fill=LIGHT)
        d.line([(4, 3), (4, 5), (6, 5)], fill='#23482E')
    elif index == 2:
        d.rectangle((1, 0, 2, 7), fill='#9AFF95')
        d.polygon([(3, 1), (8, 1), (7, 3), (8, 4), (3, 4)], fill='#3ADF75')
        d.rectangle((0, 8, 4, 8), fill='#2FA159')
    else:
        d.rectangle((0, 1, 8, 4), fill='#2BA55C')
        d.rectangle((1, 2, 7, 3), fill='#14251B')
        d.polygon([(2, 0), (6, 0), (6, 4), (5, 5), (3, 5), (2, 4)], fill='#A5FF91')
        d.rectangle((3, 6, 5, 7), fill='#40D970')
        d.rectangle((1, 8, 7, 8), fill='#6BE586')
    tile.putpixel((8, 8), (255, 255, 255, 1))
    icons.alpha_composite(tile, (index * 9, 0))
icons.save(TEXTURES / 'icons.png')
(FONTS / 'copy_build_icons.json').write_text(json.dumps(dict(providers=[dict(
    type='bitmap', file='viksstuff:copy_build/icons.png', height=9, ascent=8,
    chars=[''.join(chr(0xE700 + index) for index in range(4))])]), indent=2) + '\n')


def advance(character):
    return 4 if character == '.' else 8 if character == 's' else 12


def sample(value):
    result = panel.copy()
    width = sum(advance(character) for character in value)
    x = (43 + (151 - width) // 2) * 2
    for character in value:
        result.alpha_composite(letters[character], (x, 24))
        x += advance(character) * 2
    return result


sample('42.73s').resize((1164, 234), Image.Resampling.NEAREST).save(PREVIEWS / 'copy-build-timer.png')
icon_preview = Image.new('RGBA', (60, 17), '#18251D')
for i in range(4):
    icon_preview.alpha_composite(icons.crop((i*9, 0, i*9+9, 9)), (3+i*15, 4))
icon_preview.resize((720, 204), Image.Resampling.NEAREST).save(PREVIEWS / 'copy-build-icons.png')
metrics = dict(width=195, artwork_width=194, height=39, scale=0.75, frame_advance=98,
               digits_advance=14, icon_advance=10, chars=CHARACTERS,
               source='Original integer-grid emerald bevel, graphite recess, cream pixel numerals; no antialiasing.',
               validation='Native glyph packing and client visual acceptance are separate checks.')
(SOURCE / 'metrics.json').write_text(json.dumps(metrics, indent=2) + '\n')
print('COPY BUILD ASSETS: 2 frame glyphs, 12 numeric glyphs, 4 icons, 391 spaces. Existing pack content untouched.')
