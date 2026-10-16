"""Original, integer-grid blue badge art for Copy the Build.

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
BLUE, LIGHT, DARK = '#39A0FF', '#E9F4FF', '#131A20'
CHARACTERS = '0123456789.s'
panel = Image.new('RGBA', (194, 39))
draw = ImageDraw.Draw(panel)


def polygon(points, color):
    draw.polygon(points, fill=color)


def rectangle(box, color):
    x1, y1, x2, y2 = box
    polygon([(x1, y1), (x2 + 1, y1), (x2 + 1, y2 + 1), (x1, y2 + 1)], color)


def badge(x, width):
    polygon(outline(x + 1, 3, width - 1, 36, 7), '#061019')
    polygon(outline(x, 1, width - 1, 36, 7), '#102539')
    polygon(outline(x + 1, 2, width - 3, 34, 6), '#20598D')
    polygon(outline(x + 2, 3, width - 5, 32, 5), '#4490D6')
    # Distinct top, bevel, lip and inset planes: all colors meet on whole pixels.
    rectangle((x + 7, 2, x + width - 9, 3), '#94CCFF')
    rectangle((x + 5, 4, x + width - 7, 4), '#74B7F5')
    rectangle((x + 3, 7, x + 4, 28), '#89BFF1')
    rectangle((x + 7, 33, x + width - 9, 34), '#24517B')
    rectangle((x + width - 5, 8, x + width - 4, 28), '#234E75')
    polygon(outline(x + 5, 6, width - 11, 26, 4), '#070D12')
    polygon(outline(x + 6, 7, width - 13, 24, 3), '#1C2329')
    rectangle((x + 10, 8, x + width - 12, 12), '#242A30')
    rectangle((x + 8, 27, x + width - 10, 29), '#161E25')
    rectangle((x + 11, 3, x + 18, 3), '#B5DBFF')


badge(0, 39)
badge(43, 151)
# The left badge is deliberately empty: live unfinished-player count is rendered by Java.

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
# Preserve the bevel; let the dark inner face transmit the world below.
for y in range(panel.height):
    for x in range(panel.width):
        r,g,b,a=panel.getpixel((x,y))
        if a and max(r,g,b)<65:panel.putpixel((x,y),(r,g,b,205))
panel = panel.resize((388, 78), Image.Resampling.NEAREST)
panel.save(TEXTURES / 'timer_panel.png')
(SOURCE / 'blue-timer.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 194 39" shape-rendering="crispEdges">' + ''.join(pixel_svg) + '</svg>\n')
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
    for color, offset in [('#0A1015', 2), (BLUE if character == 's' else LIGHT, 0)]:
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
        d.polygon([(4, 0), (8, 2), (8, 6), (4, 8), (0, 6), (0, 2)], fill='#153049')
        d.polygon([(4, 1), (7, 2), (4, 4), (1, 2)], fill='#9CCFFF')
        d.polygon([(1, 3), (3, 5), (3, 7), (1, 6)], fill='#4894DB')
        d.polygon([(5, 5), (7, 3), (7, 6), (5, 7)], fill='#23619B')
    elif index == 1:
        d.rectangle((3, 0, 5, 1), fill='#96CDFF')
        d.polygon([(2, 2), (6, 2), (8, 4), (8, 6), (6, 8), (2, 8), (0, 6), (0, 4)], fill='#408ACE')
        d.rectangle((2, 3, 6, 6), fill=LIGHT)
        d.line([(4, 3), (4, 5), (6, 5)], fill='#233648')
    elif index == 2:
        d.rectangle((1, 0, 2, 7), fill='#95CCFF')
        d.polygon([(3, 1), (8, 1), (7, 3), (8, 4), (3, 4)], fill='#3A90DF')
        d.rectangle((0, 8, 4, 8), fill='#2F6AA1')
    else:
        d.rectangle((0, 1, 8, 4), fill='#2B6AA5')
        d.rectangle((1, 2, 7, 3), fill='#141D25')
        d.polygon([(2, 0), (6, 0), (6, 4), (5, 5), (3, 5), (2, 4)], fill='#91CAFF')
        d.rectangle((3, 6, 5, 7), fill='#4090D9')
        d.rectangle((1, 8, 7, 8), fill='#6BAAE5')
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
    remaining='10'
    count_x=((39-sum(advance(c) for c in remaining))//2)*2
    for character in remaining:
        result.alpha_composite(letters[character],(count_x,24));count_x+=advance(character)*2
    width = sum(advance(character) for character in value)
    x = (43 + (151 - width) // 2) * 2
    for character in value:
        result.alpha_composite(letters[character], (x, 24))
        x += advance(character) * 2
    return result


sample('42.73s').resize((1164, 234), Image.Resampling.NEAREST).save(PREVIEWS / 'copy-build-timer.png')
icon_preview = Image.new('RGBA', (60, 17), '#181F25')
for i in range(4):
    icon_preview.alpha_composite(icons.crop((i*9, 0, i*9+9, 9)), (3+i*15, 4))
icon_preview.resize((720, 204), Image.Resampling.NEAREST).save(PREVIEWS / 'copy-build-icons.png')
metrics = dict(width=195, artwork_width=194, height=39, scale=0.75, frame_advance=98,
               digits_advance=14, icon_advance=10, chars=CHARACTERS,
               source='Original integer-grid blue bevel, graphite recess, cream pixel numerals; no antialiasing.',
               validation='Native glyph packing and client visual acceptance are separate checks.')
(SOURCE / 'metrics.json').write_text(json.dumps(metrics, indent=2) + '\n')
print('COPY BUILD ASSETS: 2 frame glyphs, 12 numeric glyphs, 4 icons, 391 spaces. Existing pack content untouched.')

# Same native block face as Parkour, authored into a separate blue countdown font.
countdown=json.loads((FONTS/'parkour_countdown_block.json').read_text())
source_texture=ROOT/'overlay/assets/viksstuff/textures/parkour/text/countdown_block.png'
from colorsys import rgb_to_hsv,hsv_to_rgb
image=Image.open(source_texture).convert('RGBA')
for y in range(image.height):
    for x in range(image.width):
        r,g,b,a=image.getpixel((x,y));h,s,v=rgb_to_hsv(r/255,g/255,b/255)
        if a and s>.12:
            rr,gg,bb=hsv_to_rgb(.58,s,v);image.putpixel((x,y),(round(rr*255),round(gg*255),round(bb*255),a))
image.save(TEXTURES/'countdown.png')
for provider in countdown['providers']:
    if provider.get('type')=='bitmap':provider['file']='viksstuff:copy_build/countdown.png'
(FONTS/'copy_build_countdown.json').write_text(json.dumps(countdown,indent=2)+'\n')
Image.new('RGBA',(1,1),(255,255,255,255)).save(TEXTURES/'blackout.png')
(FONTS/'transition.json').write_text(json.dumps({'providers':[{'type':'bitmap','file':'viksstuff:copy_build/blackout.png','height':1,'ascent':1,'chars':['\ue7fe']}]},indent=2)+'\n')
