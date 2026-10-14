from pathlib import Path
import json
from PIL import Image

root = Path(__file__).resolve().parents[1]
source = root / 'source-art/parkour/checkpoint-gold.png'
overlay = root / 'overlay/assets/viksstuff'
def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')
image = Image.open(source).convert('RGBA')
assert image.getextrema()[3][0] == 0, 'Sign must retain transparency'
image.thumbnail((512, 512), Image.Resampling.NEAREST)
texture = overlay / 'textures/parkour/checkpoint_gold.png'
texture.parent.mkdir(parents=True, exist_ok=True)
canvas = Image.new('RGBA', (512,512))
canvas.paste(image, ((512-image.width)//2,(512-image.height)//2))
canvas.save(texture)
write(overlay / 'models/item/parkour_checkpoint.json', {'parent':'minecraft:item/generated','textures':{'layer0':'viksstuff:parkour/checkpoint_gold'},'display':{'fixed':{'rotation':[0,0,0],'translation':[0,0,0],'scale':[1,1,1]}}})
for name in ['parkour_checkpoint','parkour_outline_top','parkour_outline_full']:
    write(overlay / ('items/' + name + '.json'), {'model':{'type':'minecraft:model','model':'viksstuff:item/' + name}})
Image.new('RGBA', (16,16), (255,245,230,255)).save(overlay / 'textures/parkour/outline.png')
for full in [False, True]:
    elements = []
    def rod(a,b):
        elements.append({'from':a,'to':b,'faces':{face:{'texture':'#all'} for face in ['north','south','east','west','up','down']}})
    lo,hi,t = -.08,16.08,.35
    for y in ([lo,hi-t] if full else [hi-t]):
        for z in [lo,hi-t]: rod([lo,y,z],[hi,y+t,z+t])
        for x in [lo,hi-t]: rod([x,y,lo],[x+t,y+t,hi])
    if full:
        for x in [lo,hi-t]:
            for z in [lo,hi-t]: rod([x,lo,z],[x+t,hi,z+t])
    write(overlay / ('models/item/parkour_outline_' + ('full' if full else 'top') + '.json'), {'textures':{'all':'viksstuff:parkour/outline','particle':'viksstuff:parkour/outline'},'elements':elements,'display':{'fixed':{'rotation':[0,0,0],'translation':[0,0,0],'scale':[1,1,1]}}})
print('Checkpoint transparent texture and three item models built:', image.size)
