"""Original pixel artwork and fixed-width font assets for the 1.21.11 relay timer."""
from pathlib import Path
import json
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "overlay/assets/viksstuff"
TEXTURES = ASSETS / "textures/parkour"
FONTS = ASSETS / "font"
TEXTURES.mkdir(parents=True, exist_ok=True)
FONTS.mkdir(parents=True, exist_ok=True)

DIGITS = {
    "0": ["01110", "10001", "10011", "10101", "11001", "10001", "01110"],
    "1": ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
    "2": ["01110", "10001", "00001", "00010", "00100", "01000", "11111"],
    "3": ["11110", "00001", "00001", "01110", "00001", "00001", "11110"],
    "4": ["00010", "00110", "01010", "10010", "11111", "00010", "00010"],
    "5": ["11111", "10000", "10000", "11110", "00001", "00001", "11110"],
    "6": ["01110", "10000", "10000", "11110", "10001", "10001", "01110"],
    "7": ["11111", "00001", "00010", "00100", "01000", "01000", "01000"],
    "8": ["01110", "10001", "10001", "01110", "10001", "10001", "01110"],
    "9": ["01110", "10001", "10001", "01111", "00001", "00001", "01110"],
    ":": ["00000", "00100", "00100", "00000", "00100", "00100", "00000"],
    ".": ["00000", "00000", "00000", "00000", "00000", "00100", "00100"],
}
SMALL = {char: value.split() for char, value in {
    "A": "01110 10001 10001 11111 10001 10001 10001",
    "B": "11110 10001 10001 11110 10001 10001 11110",
    "C": "01111 10000 10000 10000 10000 10000 01111",
    "D": "11110 10001 10001 10001 10001 10001 11110",
    "E": "11111 10000 10000 11110 10000 10000 11111",
    "F": "11111 10000 10000 11110 10000 10000 10000",
    "G": "01111 10000 10000 10111 10001 10001 01111",
    "H": "10001 10001 10001 11111 10001 10001 10001",
    "I": "01110 00100 00100 00100 00100 00100 01110",
    "J": "00001 00001 00001 00001 10001 10001 01110",
    "K": "10001 10010 10100 11000 10100 10010 10001",
    "L": "10000 10000 10000 10000 10000 10000 11111",
    "M": "10001 11011 10101 10101 10001 10001 10001",
    "N": "10001 11001 11001 10101 10011 10011 10001",
    "O": "01110 10001 10001 10001 10001 10001 01110",
    "P": "11110 10001 10001 11110 10000 10000 10000",
    "Q": "01110 10001 10001 10001 10101 10010 01101",
    "R": "11110 10001 10001 11110 10100 10010 10001",
    "S": "01111 10000 10000 01110 00001 00001 11110",
    "T": "11111 00100 00100 00100 00100 00100 00100",
    "U": "10001 10001 10001 10001 10001 10001 01110",
    "V": "10001 10001 10001 10001 10001 01010 00100",
    "W": "10001 10001 10001 10101 10101 11011 10001",
    "X": "10001 10001 01010 00100 01010 10001 10001",
    "Y": "10001 10001 01010 00100 00100 00100 00100",
    "Z": "11111 00001 00010 00100 01000 10000 11111",
    "|": "00100 00100 00100 00100 00100 00100 00100",
}.items()}
SMALL.update({char: DIGITS[char] for char in "0123456789"})

def pixels(image, rows, x, y, color=(255, 255, 255, 255)):
    for dy, row in enumerate(rows):
        for dx, value in enumerate(row):
            if value == "1": image.putpixel((x + dx, y + dy), color)

def save_json(name, providers):
    (FONTS / name).write_text(json.dumps({"providers": providers}, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")

# Code-native Championship Gold artwork, recreated from the selected concept.
DIGITS.update({
    "#": ["01010", "01010", "11111", "01010", "11111", "01010", "01010"],
    "-": ["00000", "00000", "00000", "11111", "00000", "00000", "00000"],
    "?": ["01110", "10001", "00001", "00010", "00100", "00000", "00100"],
    "+": ["00000", "00100", "00100", "11111", "00100", "00100", "00000"],
    "s": ["00000", "00000", "01111", "10000", "01110", "00001", "11110"],
})

def outline(x, y, w, h, cut):
    return [(x+cut,y),(x+w-1-cut,y),(x+w-1,y+cut),(x+w-1,y+h-1-cut),
            (x+w-1-cut,y+h-1),(x+cut,y+h-1),(x,y+h-1-cut),(x,y+cut)]

panel = Image.new("RGBA", (186, 20))
draw = ImageDraw.Draw(panel)
for left, width in [(0, 36), (41, 112), (158, 28)]:
    draw.polygon(outline(left, 0, width, 20, 4), fill=(47,32,12,255))
    draw.polygon(outline(left+1, 1, width-2, 18, 3), fill=(169,111,27,255))
    draw.polygon(outline(left+2, 2, width-4, 16, 2), fill=(244,187,57,255))
    draw.line((left+5,1,left+width-6,1), fill=(255,232,142,255))
    draw.line((left+5,2,left+width-6,2), fill=(255,216,91,255))
    draw.line((left+4,18,left+width-5,18), fill=(112,70,19,255))
    draw.polygon(outline(left+3,3,width-6,14,1), fill=(95,65,24,255))
    draw.polygon(outline(left+4,4,width-8,12,1), fill=(35,35,38,255))
    draw.line((left+5,4,left+width-6,4), fill=(61,60,58,255))
# Gold stopwatch in the timer badge, independently of all live values.
draw.rectangle((52,3,56,4), fill=(255,216,91,255))
draw.rectangle((53,4,55,5), fill=(169,111,27,255))
draw.ellipse((47,5,60,17), fill=(123,77,18,255))
draw.ellipse((48,5,59,16), fill=(255,216,91,255))
draw.ellipse((50,7,57,14), fill=(255,245,219,255))
draw.line((54,8,54,11), fill=(43,38,30,255))
draw.line((54,11,56,11), fill=(43,38,30,255))
panel.save(TEXTURES / "timer_panel.png")

advances = {chr(0xE800+n+187): n for n in range(-187,188)}
save_json("parkour_timer.json", [
    {"type":"bitmap","file":"viksstuff:parkour/timer_panel.png","height":20,"ascent":9,"chars":["\uE600"]},
    {"type":"space","advances":advances},
])
characters = "0123456789:.s#-?+"
for name, cell, height, display_height, ascent in [
    ("digits",8,10,14,4), ("small",6,8,8,2)
]:
    sheet = Image.new("RGBA", (cell*len(characters),height))
    for index, char in enumerate(characters):
        pixels(sheet,DIGITS[char],index*cell,0)
        sheet.putpixel((index*cell+cell-1,height-1),(255,255,255,1))
    sheet.save(TEXTURES / f"timer_{name}.png")
    save_json(f"parkour_timer_{name}.json",[{
        "type":"bitmap","file":f"viksstuff:parkour/timer_{name}.png",
        "height":display_height,"ascent":ascent,"chars":[characters]
    }])

# The WHITE boss-bar color is reserved for the custom carrier. Other colors keep vanilla sprites.
native_bars = ROOT / "overlay/assets/minecraft/textures/gui/sprites/boss_bar"
native_bars.mkdir(parents=True, exist_ok=True)
for name in ("white_background","white_progress"):
    Image.new("RGBA",(182,5)).save(native_bars / f"{name}.png")

# Deterministic render preview only; the plugin supplies the real player skin at runtime.
face = [
    ["h"]*8, ["h"]*8, ["h","t","t","t","t","t","t","h"], ["t"]*8,
    ["t","w","b","t","t","b","w","t"], ["t","t","t","n","n","t","t","t"],
    ["t","t","d","d","d","d","t","t"], ["t","t","d","n","n","d","t","t"],
]
colors = {"h":(65,40,20,255),"t":(187,133,97,255),"w":(242,234,214,255),
          "b":(76,75,156,255),"n":(143,79,53,255),"d":(76,43,27,255)}
avatar = Image.new("RGBA",(8,8))
for y,row in enumerate(face):
    for x,value in enumerate(row): avatar.putpixel((x,y),colors[value])

preview = Image.new("RGBA",(214,148),(25,33,45,255))
states = [("#-","10.00s"),("#1","42.73s"),("#2","05.00s"),("#2","42.73s"),("#1","18.24s")]
for index,(rank,time) in enumerate(states):
    rendered = panel.copy()
    def write(text,left,top,scale,color):
        for i,char in enumerate(text):
            raw = Image.new("RGBA",(8,10))
            pixels(raw,DIGITS[char],0,0,color)
            scaled = raw.resize((round(8*scale),round(10*scale)),Image.Resampling.NEAREST)
            rendered.alpha_composite(scaled,(left+i*12,top))
    rank_width=len(rank)*12
    write(rank,(36-rank_width)//2,5,1.4,(255,245,230,255))
    time_width=len(time)*12
    write(time[:-1],65+(82-time_width)//2,5,1.4,(255,245,230,255))
    write("s",65+(82-time_width)//2+(len(time)-1)*12,5,1.4,(255,216,91,255))
    rendered.alpha_composite(avatar.resize((16,16),Image.Resampling.NEAREST),(164,2))
    preview.alpha_composite(rendered,(14,10+index*27))
preview_path=ROOT/"previews/parkour-timer-states.png"
preview_path.parent.mkdir(parents=True,exist_ok=True)
preview.resize((856,592),Image.Resampling.NEAREST).save(preview_path)
print(f"GOLD PARKOUR HUD ART PASS: three badges, 186x20, dynamic text/head slots, preview {preview_path}")
