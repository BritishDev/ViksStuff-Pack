"""Five original thick pixel faces and matching crimson centre-countdown badges.

All drawing is integer-grid code-native art. Existing timer frames, shaders,
skins, legacy fonts and Copy the Build assets are left byte-for-byte untouched.
"""
from pathlib import Path
from io import BytesIO
import json
import zipfile
from PIL import Image, ImageDraw, ImageFilter
from parkour_badge_art import PATTERNS, outline

ROOT = Path(__file__).resolve().parents[1]
TEXTURES = ROOT / 'overlay/assets/viksstuff/textures/parkour/text'
FONTS = ROOT / 'overlay/assets/viksstuff/font'
SOURCE = ROOT / 'source-art/parkour/text-styles'
PREVIEWS = ROOT / 'previews'
for directory in (TEXTURES, FONTS, SOURCE, PREVIEWS):
    directory.mkdir(parents=True, exist_ok=True)
STYLES = ['classic', 'block', 'bevel', 'outline', 'stencil']
CHARS = '0123456789:.hms#-?+'
BLOCK = {
    '0': ['0111110','1111111','1100011','1100011','1100011','1100011','1100011','1111111','0111110'],
    '1': ['0011100','0111100','1111100','0011100','0011100','0011100','0011100','1111111','1111111'],
    '2': ['0111110','1111111','1100011','0000011','0001110','0011100','0110000','1111111','1111111'],
    '3': ['1111110','1111111','0000011','0000011','0011110','0000011','0000011','1111111','1111110'],
    '4': ['0001110','0011110','0110110','1100110','1100110','1111111','1111111','0000110','0000110'],
    '5': ['1111111','1111111','1100000','1100000','1111110','0000011','0000011','1111111','1111110'],
    '6': ['0011110','0111110','1100000','1100000','1111110','1100011','1100011','1111111','0111110'],
    '7': ['1111111','1111111','0000011','0000110','0001100','0011000','0011000','0011000','0011000'],
    '8': ['0111110','1111111','1100011','1100011','0111110','1100011','1100011','1111111','0111110'],
    '9': ['0111110','1111111','1100011','1100011','0111111','0000011','0000011','0111110','0111100'],
    'G': ['0111110','1111111','1100011','1100000','1101111','1100011','1100011','1111111','0111110'],
    'O': ['0111110','1111111','1100011','1100011','1100011','1100011','1100011','1111111','0111110'],
}
CLASSIC = dict(PATTERNS, h=['10000','10000','10110','11001','10001','10001','10001'], m=['00000','00000','11010','10101','10101','10101','10101'], G=['01111','11000','11000','11011','11001','11001','01111'], O=PATTERNS['0'])


def mask(style, char):
    """Return a tightly bounded face mask; every face has thicker strokes than v1."""
    if char not in BLOCK or style == 'classic':
        pattern = CLASSIC[char]
        step = 3 if char in 'hms' else 4
        face = Image.new('L', (28, 34))
        d = ImageDraw.Draw(face)
        for y, row in enumerate(pattern):
            for x, bit in enumerate(row):
                if bit == '1': d.rectangle((x*step, y*step, x*step+step, y*step+step-1), fill=255)
        # Punctuation is deliberately separate and thicker, without filling the
        # zero-width tracking cells that follow it at runtime.
        return face.crop(face.getbbox())
    step = 2 if style == 'outline' else 3
    pattern = BLOCK[char]
    face = Image.new('L', (28, 34))
    d = ImageDraw.Draw(face)
    for y, row in enumerate(pattern):
        for x, bit in enumerate(row):
            if bit == '1': d.rectangle((x*step, y*step, (x+1)*step-1, (y+1)*step-1), fill=255)
    face = face.crop(face.getbbox())
    if style == 'outline':
        padded = Image.new('L', (face.width+2, face.height+2))
        padded.paste(face, (1, 1))
        face = padded.filter(ImageFilter.MaxFilter(3))
    if style == 'stencil' and char not in '14':
        # Cut through broad upper/lower strokes, producing a real stencil face.
        d = ImageDraw.Draw(face)
        center = face.width//2
        d.rectangle((center, 0, center+1, 5), fill=0)
        d.rectangle((center, face.height-6, center+1, face.height-1), fill=0)
    return face


def ink(style, char):
    face = mask(style, char)
    if style == 'outline' and char in BLOCK:
        face_with_border = Image.new('L', (face.width+4, face.height+4))
        face_with_border.paste(face, (2, 2))
        border = face_with_border.filter(ImageFilter.MaxFilter(5))
        image = Image.new('RGBA', (face.width+6, face.height+6))
        image.paste('#100A10', (2, 2), border)
        image.paste('#DE445C', (0, 0), border)
        image.paste('#FFF4E9', (2, 2), face)
        return image
    image = Image.new('RGBA', (face.width+2, face.height+2))
    image.paste('#100A10', (2, 2), face)
    fill = '#FF526C' if char in 'hms' else '#F5F0E7'
    if style == 'bevel' and char in BLOCK:
        colored = Image.new('RGBA', face.size)
        for y in range(face.height):
            for x in range(face.width):
                if not face.getpixel((x,y)): continue
                top = y == 0 or not face.getpixel((x,y-1))
                left = x == 0 or not face.getpixel((x-1,y))
                bottom = y+1 == face.height or not face.getpixel((x,y+1))
                right = x+1 == face.width or not face.getpixel((x+1,y))
                color = '#FFFFFF' if top or left else '#B68F91' if bottom or right else '#F0DBD3'
                colored.putpixel((x,y), (*tuple(int(color[i:i+2],16) for i in (1,3,5)),255))
        image.alpha_composite(colored)
    else:
        image.paste(fill, (0, 0), face)
    return image


def letter(style, character, compact=False):
    image = Image.new('RGBA', (20, 28) if compact else (28, 38))
    face = ink(style, character)
    # Keep the visible period at the baseline and the lowercase suffix modest.
    if compact:
        maximum = 5 if character in '.:' else 10 if character in 'hms' else 15
        factor = min(maximum/face.width, 20/face.height)
        face = face.resize((max(1,round(face.width*factor)),max(1,round(face.height*factor))), Image.Resampling.NEAREST)
        y = max(0, 21-face.height)
    else:
        y = max(0, 29-face.height)
    image.alpha_composite(face, (0, y))
    # Minecraft counts every alpha > 0 in its metric scan; its shader discards
    # this measuring pixel, preserving the shared live-text spacing contract.
    image.putpixel((19 if compact else 25, image.height-1), (255,255,255,1))
    return image


def badge(width):
    image = Image.new('RGBA', (64, 40))
    d = ImageDraw.Draw(image)
    x = (64-width)//2
    for dx,y,w,h,cut,color in [(1,3,width-1,36,7,'#17090E'),(0,1,width-1,36,7,'#380E19'),
                               (1,2,width-3,34,6,'#C5243D'),(2,3,width-5,32,5,'#E9334D'),
                               (5,6,width-11,26,4,'#0C0C10'),(6,7,width-13,24,3,'#202025')]:
        d.polygon(outline(x+dx,y,w,h,cut), fill=color)
    d.rectangle((x+8,3,x+width-10,4),fill='#FF8A90')
    d.rectangle((x+9,3,x+13,3),fill='#FFC1B7')
    d.rectangle((x+5,7,x+5,28),fill='#F45966')
    return image


def countdown(style, value):
    value = str(value)
    image = badge(38 if len(value) == 1 else 62)
    sprites = [ink(style,c) for c in value]
    # Center-card inner face is 24px high. Fit thick glyphs into it without
    # touching the recessed lip; numerals remain much larger than ordinary text.
    sprites = [sprite.resize((max(1,round(sprite.width*22/sprite.height)),22),Image.Resampling.NEAREST) for sprite in sprites]
    width = sum(sprite.width for sprite in sprites) + 3*(len(sprites)-1)
    assert width <= 48, (style,value,width)
    x = (64-width)//2
    for sprite in sprites:
        image.alpha_composite(sprite,(x,9)); x += sprite.width+3
    image.putpixel((63,39),(255,255,255,1))
    return image


def svg_pixels(image):
    rectangles = []
    for y in range(image.height):
        x = 0
        while x < image.width:
            color = image.getpixel((x,y)); right = x+1
            while right < image.width and image.getpixel((right,y)) == color: right += 1
            if color[3] > 1:
                rectangles.append(f'<rect x="{x}" y="{y}" width="{right-x}" height="1" fill="#{color[0]:02x}{color[1]:02x}{color[2]:02x}"/>')
            x = right
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {image.width} {image.height}" shape-rendering="crispEdges">'+''.join(rectangles)+'</svg>\n'


for style in STYLES:
    for compact in (False, True):
        cell, height, display, ascent = (20,28,14,-9) if compact else (28,38,19,-6)
        suffix = '_small' if compact else ''
        sheet = Image.new('RGBA',(cell*len(CHARS),height))
        for index, char in enumerate(CHARS): sheet.alpha_composite(letter(style,char,compact),(index*cell,0))
        file = f'text_{style}{suffix}.png'; sheet.save(TEXTURES/file)
        (FONTS/f'parkour_timer_text_{style}{suffix}.json').write_text(json.dumps(dict(providers=[dict(
            type='bitmap',file=f'viksstuff:parkour/text/{file}',height=display,ascent=ascent,chars=[CHARS])]),indent=2)+'\n')
    sheet = Image.new('RGBA',(64*12,40))
    for index,value in enumerate([*range(11),'GO']): sheet.alpha_composite(countdown(style,value),(index*64,0))
    file=f'countdown_{style}.png'; sheet.save(TEXTURES/file)
    (FONTS/f'parkour_countdown_{style}.json').write_text(json.dumps(dict(providers=[dict(
        type='bitmap',file=f'viksstuff:parkour/text/{file}',height=20,ascent=17,
        chars=[''.join(chr(0xE720+i) for i in range(12))]),dict(type='space',advances={'\uE7FF':-1})]),indent=2)+'\n')
    (SOURCE/f'{style}-digits.svg').write_text(svg_pixels(Image.open(TEXTURES/f'text_{style}.png')))
    (SOURCE/f'{style}-countdown.svg').write_text(svg_pixels(sheet))

CLIENT=Path('C:/Users/navra/.gradle/caches/fabric-loom/1.21.11/minecraft-client.jar')
with zipfile.ZipFile(CLIENT) as client:
    vanilla = Image.open(BytesIO(client.read('assets/minecraft/textures/font/ascii.png'))).convert('RGBA')
    skin = Image.open(BytesIO(client.read('assets/minecraft/textures/entity/player/wide/steve.png'))).convert('RGBA')
face=skin.crop((8,8,16,16)); face.alpha_composite(skin.crop((40,8,48,16)))


def caption(image,x,y,value,color='#F5F0E7'):
    for char in value:
        if char == ' ': x += 4; continue
        code=ord(char); tile=vanilla.crop(((code%16)*8,(code//16)*8,(code%16)*8+8,(code//16)*8+8))
        alpha=tile.getchannel('A'); bounds=alpha.getbbox()
        inked=Image.new('RGBA',(8,8),color);inked.putalpha(alpha);image.alpha_composite(inked,(x,y))
        x += (bounds[2]+1) if bounds else 1


def timer_sample(style,value='1h1m1s'):
    panel=Image.open(ROOT/'overlay/assets/viksstuff/textures/parkour/timer_ribbon_panel.png').convert('RGBA')
    adv=lambda c: 4 if c in '.:' else 8 if c in 'hms' else 12
    x=(150-sum(adv(c) for c in value))//2*2
    for c in value:
        panel.alpha_composite(letter(style,c),(x,24));x+=adv(c)*2
    panel.alpha_composite(face.resize((44,44),Image.Resampling.NEAREST),(324,16))
    return panel


board=Image.new('RGBA',(600,456),'#17191F')
caption(board,14,12,'PARKOUR / FIVE PIXEL TEXT STYLES','#FF8A90')
for index,style in enumerate(STYLES):
    y=40+index*81
    caption(board,14,y,style.upper(),'#FF8A90')
    timer=timer_sample(style);board.alpha_composite(timer,(14,y+11))
    for i,value in enumerate(['5','GO']): board.alpha_composite(countdown(style,value).resize((80,50),Image.Resampling.NEAREST),(416+i*86,y+15))
    timer.resize((1164,234),Image.Resampling.NEAREST).save(PREVIEWS/f'parkour-text-{style}.png')
    countdown(style,'10').resize((512,320),Image.Resampling.NEAREST).save(PREVIEWS/f'parkour-countdown-{style}.png')
board.resize((1200,912),Image.Resampling.NEAREST).save(PREVIEWS/'parkour-text-five-styles.png')
sequence=Image.new('RGBA',(64*7,50),'#17191F')
for index,value in enumerate(['10','5','4','3','2','1','GO']):sequence.alpha_composite(countdown('block',value),(index*64,5))
sequence.resize((1344,150),Image.Resampling.NEAREST).save(PREVIEWS/'parkour-countdown-sequence.png')
(SOURCE/'metrics.json').write_text(json.dumps(dict(styles=STYLES,default='block',chars=CHARS,
    fonts={'large':dict(cell=28,texture_height=38,height=19,ascent=-6,advance=14),
           'small':dict(cell=20,texture_height=28,height=14,ascent=-9,advance=11),
           'countdown':dict(cell=64,texture_height=40,height=20,ascent=17,advance=33,kerning=-1)},
    title_geometry=dict(top=-10,bottom=10,title_y=-10,title_scale=4,gui_top=-80,gui_bottom=0,
                        subtitle_y=5,subtitle_scale=2,subtitle_gui_top=10),
    description='Original thick Minecraft pixel masks, block strokes, bevel, crimson outline and stencil cuts; existing frames unchanged.'),indent=2)+'\n')
(SOURCE/'pixel-masks.json').write_text(json.dumps(dict(classic=CLASSIC,block=BLOCK),indent=2)+'\n')
print('PARKOUR TEXT: five real large/compact pixel faces, 60 center countdown badges, editable SVGs and sample previews.')
