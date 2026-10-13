"""Derive the live Minecraft HUD from the selected Championship Gold source artwork.
Requires Pillow and NumPy. The original is retained; frame and glyph atlas derivatives
remove sample values so the server can supply real ranks, times and player portraits.
"""
from pathlib import Path
import hashlib, json
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source-art/parkour/championship-gold.png"
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == "4f65714ef1047060fca1af928d342c299b6fb9e5c892ac093a5e13c2a26719d8"
ART = Image.open(SOURCE).convert("RGBA")
TEXTURES = ROOT / "overlay/assets/viksstuff/textures/parkour"
FONTS = ROOT / "overlay/assets/viksstuff/font"
TEXTURES.mkdir(parents=True, exist_ok=True)
FONTS.mkdir(parents=True, exist_ok=True)
WIDTH, HEIGHT = 194, 39
CHARACTERS = "0123456789:.s#-?+"

# Original alpha-supported frame bounds. Derivatives use double-resolution
# bitmap textures, with each glyph below the client's 256x256 atlas allocation.
FRAMES = [
    ("rank", (120,164,573,544), 0,46, "\uE600"),
    ("time", (589,164,1590,544), 48,102, "\uE601"),
    ("head", (1604,164,2028,544), 151,43, "\uE602"),
]
clean = np.array(ART).copy()
def clear_sample(x0,y0,x1,y1,left,right):
    # Reconstruct only sample-data holes from clean scanline strips within
    # this same recessed face; never regenerate the selected frame/bevel/icon.
    for y in range(y0,y1):
        l = clean[y,left[0]:left[1],:3].mean(axis=0)
        r = clean[y,right[0]:right[1],:3].mean(axis=0)
        t = np.linspace(0,1,x1-x0)[:,None]
        clean[y,x0:x1,:3] = np.rint(l*(1-t)+r*t).astype(np.uint8)
        clean[y,x0:x1,3] = 255

clear_sample(216,260,491,465,(195,211),(494,510))
clear_sample(906,276,1530,461,(891,905),(1530,1538))
clear_sample(1700,236,1938,484,(1675,1695),(1941,1954))
# Head background remains smoked graphite while the live skin is rendered over it.
clean[236:484,1700:1938,:3] = np.maximum(clean[236:484,1700:1938,:3], 27)
clean[:,:,3] = np.where(clean[:,:,3] >= 128,255,0).astype(np.uint8)
clean_art = Image.fromarray(clean)
providers = []
panel = Image.new("RGBA",(WIDTH*2,HEIGHT*2))
for name,bounds,left,width,char in FRAMES:
    image = clean_art.crop(bounds).resize((width*2,HEIGHT*2),Image.Resampling.LANCZOS)
    # Low-alpha measuring pixel is invisible in the text shader, but fixes advance.
    image.putpixel((image.width-1,image.height-1),(255,255,255,1))
    image.save(TEXTURES / f"timer_{name}_frame.png")
    panel.alpha_composite(image,(left*2,0))
    providers.append({"type":"bitmap","file":f"viksstuff:parkour/timer_{name}_frame.png",
                      "height":HEIGHT,"ascent":6,"chars":[char]})
providers.append({"type":"space","advances":{chr(0xE800+n+195):n for n in range(-195,196)}})
(FONTS/"parkour_timer.json").write_text(json.dumps({"providers":providers},indent=2)+"\n")
panel.save(TEXTURES/"timer_panel.png") # Composite preview/validation source; not a single atlas glyph.

# White letter bodies and gold suffix from the original concept. Font shadows
# are baked into each glyph, avoiding Minecraft's thin/default text rendering.
BOUNDS = {"#":(229,301,340,435), "1":(365,268,454,439),
          "4":(918,283,1029,437),"2":(1041,283,1141,437),
          ".":(1160,397,1188,437),"7":(1199,283,1296,437),
          "3":(1314,283,1414,437),"s":(1435,332,1508,437)}
PATTERNS = {
 "0":["01110","10001","10001","10001","10001","10001","01110"],
 "5":["11111","10000","10000","11110","00001","00001","11110"],
 "6":["01111","10000","10000","11110","10001","10001","01110"],
 "8":["01110","10001","10001","01110","10001","10001","01110"],
 "9":["01110","10001","10001","01111","00001","00001","11110"],
 "-":["00000","00000","00000","11111","11111","00000","00000"],
 "?":["01110","11011","00011","00110","01100","00000","01100"],
 "+":["00000","01100","01100","11111","11111","01100","01100"],
 ":":["00000","01100","01100","00000","01100","01100","00000"],
}
original = np.array(ART)
def source_letter(char):
    x0,y0,x1,y1=BOUNDS[char]
    a=original[y0:y1,x0:x1].copy()
    if char=="s": mask=(a[:,:,0]>150)&(a[:,:,1]>90)&(a[:,:,2]<150)
    else: mask=(a[:,:,:3].min(axis=2)>140)&(a[:,:,:3].max(axis=2)-a[:,:,:3].min(axis=2)<45)
    a[:,:,3]=np.where(mask,255,0)
    return Image.fromarray(a)

def letter(char,rank=False):
    canvas=Image.new("RGBA",(32 if rank else 28,40 if rank else 38))
    factor=194/1908*2
    if char in BOUNDS:
        body=source_letter(char)
        if rank:
            cap=171
            top=round((439-BOUNDS[char][3])*factor)
            if char=="#": top=round((301-268)*factor)
            size=(round(body.width*factor),round(body.height*factor))
        else:
            # The timer shares a 154px cap height; its '1' derives from rank '1'.
            scale=factor*(154/171 if char=="1" else 1)
            size=(round(body.width*scale),round(body.height*scale))
            top=round((BOUNDS[char][1]-283)*factor) if char in (".","s") else 0
        body=body.resize(size,Image.Resampling.LANCZOS)
    else:
        raw=Image.new("L",(22,31))
        grid=Image.new("L",(5,7))
        for y,row in enumerate(PATTERNS[char]):
            for x,value in enumerate(row):
                if value=="1": grid.putpixel((x,y),255)
        raw=grid.resize((20,28),Image.Resampling.NEAREST)
        raw=raw.filter(ImageFilter.MaxFilter(3)).resize((22,31),Image.Resampling.NEAREST)
        if rank: raw=raw.resize((24,35),Image.Resampling.NEAREST)
        body=Image.new("RGBA",raw.size)
        for y in range(raw.height):
            shade=255-round(y/(raw.height-1)*13)
            for x in range(raw.width): body.putpixel((x,y),(shade,shade,shade,raw.getpixel((x,y))))
        top=0
    shadow=Image.new("RGBA",body.size,(14,14,13,0))
    shadow.putalpha(body.getchannel("A"))
    canvas.alpha_composite(shadow,(3,top+3))
    canvas.alpha_composite(body,(0,top))
    return canvas

specs={"digits":(28,38,19,-6,14), "rank":(32,40,20,-4,16), "small":(20,28,14,-9,11)}
glyphs={}
for name,(cell,height,display,ascent,advance) in specs.items():
    sheet=Image.new("RGBA",(cell*len(CHARACTERS),height))
    glyphs[name]={}
    for index,char in enumerate(CHARACTERS):
        tile=letter(char,name=="rank")
        if name=="small": tile=tile.resize((20,28),Image.Resampling.LANCZOS)
        # Native advances include shadow extents. Explicit HUD kerning restores
        # the reference's tighter spacing, with a narrow decimal and suffix.
        tile.putpixel(((advance-1)*2-1,height-1),(255,255,255,1))
        # Keep every glyph's measuring extent identical including sparse chars.
        sheet.alpha_composite(tile,(index*cell,0))
        glyphs[name][char]=tile
    sheet.save(TEXTURES/f"timer_{name}.png")
    (FONTS/f"parkour_timer_{name}.json").write_text(json.dumps({"providers":[{
        "type":"bitmap","file":f"viksstuff:parkour/timer_{name}.png",
        "height":display,"ascent":ascent,"chars":[CHARACTERS]
    }]},indent=2)+"\n")

bars=ROOT/"overlay/assets/minecraft/textures/gui/sprites/boss_bar"
bars.mkdir(parents=True,exist_ok=True)
for name in ("white_background","white_progress"): Image.new("RGBA",(182,5)).save(bars/f"{name}.png")

def advance(char,font):
    if font=="rank": return 14 if char=="#" else 11
    if font=="small": return 9 if char=="#" else 3 if char in ".:" else 6 if char=="s" else 8
    return 4 if char in ".:" else 8 if char=="s" else 12
def width(text,font): return sum(advance(char,font) for char in text)
def rendered(rank,time,portrait=True):
    result=panel.copy()
    def write(text,left,font):
        top={"rank":10,"digits":12,"small":15}[font]*2
        cursor=left*2
        for char in text:
            result.alpha_composite(glyphs[font][char],(cursor,top))
            cursor+=advance(char,font)*2
    rank_font="rank" if width(rank,"rank")<=36 else "small"
    time_font="digits" if width(time,"digits")<=62 else "small"
    write(rank,(46-width(rank,rank_font))//2+1,rank_font)
    write(time,80+(62-width(time,time_font))//2,time_font)
    if portrait:
        # Original Steve sample is for the comparison only; runtime uses live skins.
        face=ART.crop((1711,243,1930,462)).resize((44,44),Image.Resampling.LANCZOS)
        result.alpha_composite(face,(162*2,8*2))
    return result

preview=Image.new("RGBA",(440,340),(24,29,35,255))
states=[("#1","42.73s"),("#-","10.00s"),("#1","05.00s"),("#2","18.24s")]
for index,(rank,time) in enumerate(states):
    image=rendered(rank,time).resize((388,78),Image.Resampling.NEAREST)
    preview.alpha_composite(image,(26,8+index*83))
preview.save(ROOT/"previews/parkour-timer-states.png")
comparison=Image.new("RGBA",(800,340),(24,29,35,255))
target=ART.crop((120,164,2028,544)).resize((776,155),Image.Resampling.LANCZOS)
comparison.alpha_composite(target,(12,8))
comparison.alpha_composite(rendered("#1","42.73s").resize((776,156),Image.Resampling.LANCZOS),(12,179))
comparison.save(ROOT/"previews/parkour-gold-reference-match.png")
scale_preview=Image.new("RGBA",(620,336),(24,29,35,255))
scale_draw=ImageDraw.Draw(scale_preview)
for factor,top,label in [(1.0,18,"100% reference size"),(0.55,170,"55% default"),(0.4,267,"40% example")]:
    sample=rendered("#1","42.73s")
    sample=sample.resize((round(194*3*factor),round(39*3*factor)),Image.Resampling.NEAREST)
    scale_draw.text((12,top-14),label,fill=(255,245,230,255))
    scale_preview.alpha_composite(sample,((620-sample.width)//2,top))
scale_preview.save(ROOT/"previews/parkour-gold-scales.png")
metrics={"width":195,"height":39,"frames":[{"name":n,"left":l,"width":w,"advance":w+1,"char":c} for n,b,l,w,c in FRAMES],
         "fonts":{n:{"native_advance":s[4],"height":s[2],"ascent":s[3]} for n,s in specs.items()},
         "source_sha256":hashlib.sha256(SOURCE.read_bytes()).hexdigest()}
(ROOT/"source-art/parkour/metrics.json").write_text(json.dumps(metrics,indent=2)+"\n")
print("REFERENCE GOLD HUD PASS: original three frames/stopwatch, extracted heavy letter bodies, 194x39 layout, 22px live head slot.")
