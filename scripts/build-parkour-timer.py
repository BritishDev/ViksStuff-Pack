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

panel = Image.new("RGBA", (200, 17), (12, 16, 23, 180))
draw = ImageDraw.Draw(panel)
# The lower band masks this bar's native 182x5 sprite; the text area remains translucent.
draw.rectangle((0, 11, 199, 16), fill=(17, 22, 31, 255))
draw.line((0, 1, 0, 15), fill=(255, 0, 255, 255))
for index, x in enumerate(range(5, 195)):
    panel.putpixel((x, 14), (1 + round(index / 189 * 253), 0, 254, 255))
panel.save(TEXTURES / "timer_panel.png")
advances = {chr(0xE800 + n + 201): n for n in range(-201, 202)}
save_json("parkour_timer.json", [
    {"type": "bitmap", "file": "viksstuff:parkour/timer_panel.png", "height": 17, "ascent": 9, "chars": ["\uE600"]},
    {"type": "space", "advances": advances},
])

digit_chars = "0123456789:."
sheet = Image.new("RGBA", (6 * len(digit_chars), 8))
for index, char in enumerate(digit_chars):
    pixels(sheet, DIGITS[char], index * 6, 0)
    # Alpha 1 measures the full cell for monospaced advances; vanilla's alpha cutoff hides it.
    sheet.putpixel((index * 6 + 5, 7), (255, 255, 255, 1))
sheet.save(TEXTURES / "timer_digits.png")
save_json("parkour_timer_digits.json", [{"type": "bitmap", "file": "viksstuff:parkour/timer_digits.png", "height": 8, "ascent": 7, "chars": [digit_chars]}])

small_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789|"
small_sheet = Image.new("RGBA", (5 * len(small_chars), 7))
for index, char in enumerate(small_chars):
    pixels(small_sheet, SMALL[char], index * 5, 0)
    if small_sheet.getpixel((index * 5 + 4, 6))[3] == 0:
        small_sheet.putpixel((index * 5 + 4, 6), (255, 255, 255, 1))
small_sheet.save(TEXTURES / "timer_small.png")
save_json("parkour_timer_small.json", [
    {"type": "space", "advances": {" ": 6}},
    {"type": "bitmap", "file": "viksstuff:parkour/timer_small.png", "height": 7, "ascent": 7, "chars": [small_chars]},
])

preview = Image.new("RGBA", (224, 143), (35, 46, 60, 255))
states = [("RELAY STARTS IN", "00:10.00", (255, 213, 0, 255), 1),
          ("RELAY TIME | LEG 1", "00:18.42", (41, 231, 255, 255), 1),
          ("NEXT RUNNER IN", "00:03.00", (255, 213, 0, 255), .6),
          ("RELAY PAUSED", "00:42.73", (204, 102, 255, 255), 1),
          ("RELAY COMPLETE", "01:22.56", (57, 255, 136, 255), 1)]
for index, (label, time, accent, progress) in enumerate(states):
    rendered = panel.copy()
    for y in range(17):
        for x in range(200):
            r, g, b, a = rendered.getpixel((x, y))
            if (r, g, b) == (255, 0, 255): rendered.putpixel((x, y), accent)
            elif b == 254 and g == 0:
                rendered.putpixel((x, y), accent if (r - 1) / 253 <= progress else (56, 66, 82, 255))
    label_x = 10
    for i, char in enumerate(label):
        if char != " ": pixels(rendered, SMALL[char], label_x + i * 6, 2, (255, 245, 230, 255))
    time_x = 201 - 10 - len(time) * 7
    for i, char in enumerate(time): pixels(rendered, DIGITS[char], time_x + i * 7, 2, accent)
    preview.alpha_composite(rendered, (12, 10 + index * 26))
preview_path = ROOT / "previews/parkour-timer-states.png"
preview_path.parent.mkdir(parents=True, exist_ok=True)
preview.resize((896, 572), Image.Resampling.NEAREST).save(preview_path)
print(f"PARKOUR TIMER ART PASS: 3 fonts, inline fixed-width digits, 200x17 strip, countdown progress mask, preview {preview_path}")
