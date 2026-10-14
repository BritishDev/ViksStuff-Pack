"""Hand-drawn pixel bevels from the user's Minecraft badge reference.

This draws new geometry; it does not recolor or trace the supplied bitmap.
All coordinates are native GUI pixels. No antialiasing or glow is used.
"""
from PIL import Image, ImageDraw

PATTERNS = {
    '0': ['01110','10001','10001','10001','10001','10001','01110'],
    '1': ['00100','01100','00100','00100','00100','00100','01110'],
    '2': ['01110','10001','00001','00110','01000','10000','11111'],
    '3': ['11110','00001','00001','01110','00001','00001','11110'],
    '4': ['00010','00110','01010','10010','11111','00010','00010'],
    '5': ['11111','10000','10000','11110','00001','00001','11110'],
    '6': ['01110','10000','10000','11110','10001','10001','01110'],
    '7': ['11111','00001','00010','00100','00100','00100','00100'],
    '8': ['01110','10001','10001','01110','10001','10001','01110'],
    '9': ['01110','10001','10001','01111','00001','00001','01110'],
    's': ['0000','0000','0111','1000','0110','0001','1110'],
    '.': ['0','0','0','0','0','0','1'],
    ':': ['0','0','1','0','1','0','0'],
    '#': ['01010','11111','01010','01010','11111','01010','00000'],
    '-': ['00000','00000','00000','11111','00000','00000','00000'],
    '?': ['01110','10001','00001','00010','00100','00000','00100'],
    '+': ['00000','00100','00100','11111','00100','00100','00000'],
}


def outline(x, y, width, height, cut):
    """Stair-step chamfer, with one-pixel horizontal/vertical landings."""
    right, bottom = x + width - 1, y + height - 1
    return [(x+cut,y),(right-cut,y),(right-cut,y+1),(right-cut+2,y+1),
            (right-cut+2,y+3),(right-2,y+3),(right-2,y+cut),(right,y+cut),
            (right,bottom-cut),(right-2,bottom-cut),(right-2,bottom-3),
            (right-cut+2,bottom-3),(right-cut+2,bottom-1),(right-cut,bottom-1),
            (right-cut,bottom),(x+cut,bottom),(x+cut,bottom-1),
            (x+cut-2,bottom-1),(x+cut-2,bottom-3),(x+2,bottom-3),
            (x+2,bottom-cut),(x,bottom-cut),(x,y+cut),(x+2,y+cut),
            (x+2,y+3),(x+cut-2,y+3),(x+cut-2,y+1),(x+cut,y+1)]


def artwork():
    image = Image.new('RGBA', (194, 39))
    draw = ImageDraw.Draw(image)

    def badge(x, width):
        # Back extrusion, dark cut silhouette, crimson metal, recessed face.
        draw.polygon(outline(x+1,3,width-1,36,7),fill='#17090E')
        draw.polygon(outline(x,1,width-1,36,7),fill='#380E19')
        draw.polygon(outline(x+1,2,width-3,34,6),fill='#C5243D')
        outer = outline(x+2,3,width-5,32,5)
        draw.polygon(outer,fill='#E9334D')
        # Raised top and left planes catch the same upper-left light as the ref.
        draw.line(outer[:9],fill='#F85666',width=1)
        draw.line([outer[-1],outer[0],outer[1]],fill='#FF6575',width=2)
        draw.line(outer[9:23],fill='#A61C37',width=2)
        draw.line(outer[22:]+[outer[0]],fill='#F45966',width=1)
        # Inner dark lip gives the graphite a visible recess.
        face = outline(x+5,6,width-11,26,4)
        draw.polygon(face,fill='#0C0C10')
        inner = outline(x+6,7,width-13,24,3)
        mask = Image.new('L', image.size)
        ImageDraw.Draw(mask).polygon(inner,fill=255)
        graphite = Image.new('RGBA', image.size)
        for py in range(7,31):
            for px in range(x+6,x+width-7):
                # Restrained three-dimensional face shading, built on pixel grid.
                edge = min(px-(x+6),x+width-8-px,py-7,30-py)
                shade = 24 + min(9,max(0,edge)*2) + (1 if (px//4+py//4)%3==0 else 0)
                graphite.putpixel((px,py),(shade,shade,shade+2,255))
        image.paste(graphite,(0,0),mask)
        draw.line([inner[0],inner[1]],fill='#15151B',width=1)
        draw.line(inner[11:18],fill='#414047',width=1)
        # Small square specular highlights, never glow/particles.
        draw.rectangle((x+8,3,x+18,4),fill='#FF8A90')
        draw.rectangle((x+9,3,x+11,3),fill='#FFC1B7')
        draw.rectangle((x+4,6,x+5,7),fill='#FF8A8F')
        draw.rectangle((x+width-9,31,x+width-7,31),fill='#B7233E')

    badge(0,147)
    badge(151,43)
    return image.resize((388,78),Image.Resampling.NEAREST)


def letter(char, name, cell, height, advance):
    image = Image.new('RGBA',(cell,height))
    draw = ImageDraw.Draw(image)
    step = 2 if name=='small' else 4
    pattern = PATTERNS[char]
    # Narrow lowercase suffix respects the existing native kerning.
    if char=='s' and name!='small': step=3
    y0 = 28-7*step if char=='s' and name!='small' else 0
    shadow = 1 if name=='small' else 2
    for color, offset in [('#09080D',shadow), ('#F5F1E7' if char!='s' else '#EE8089',0)]:
        for y,row in enumerate(pattern):
            for x,bit in enumerate(row):
                if bit=='1':
                    px,py=x*step+offset,y*step+y0+offset
                    draw.rectangle((px,py,px+step-1,py+step-1),fill=color)
    # Low-alpha measuring pixel retains the exact native bitmap advance.
    image.putpixel(((advance-1)*2-1,height-1),(255,255,255,1))
    return image
