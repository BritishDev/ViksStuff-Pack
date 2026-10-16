"""Rebuild scoped translucent UI, and install the supplied library icons/block textures.

Extracted source PNGs carry invalid CRC/Adler checksums. Normalize container checksums
without changing their decoded pixels. No global font replacement is used.
"""
from pathlib import Path
from io import BytesIO
import json,struct,zlib,hashlib
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'overlay/assets'; T=ASSETS/'viksstuff/textures/parkour'; F=ASSETS/'viksstuff/font'
SOURCE=Path('C:/Users/navra/Desktop/Minecraft Pack Sound Library/Full Extracted Packs/MCC Island - f0cfc17835/assets')
PROVENANCE=[]
def source_png(name):
    raw=(SOURCE/name).read_bytes(); p=8; chunks=[]; compressed=b''
    while p<len(raw):
        size=int.from_bytes(raw[p:p+4],'big'); kind=raw[p+4:p+8]; data=raw[p+8:p+8+size];p+=12+size
        if kind==b'IDAT':compressed+=data
        else:chunks.append((kind,data))
    decoded=zlib.decompress(compressed[2:-4],-15)
    result=raw[:8]
    for kind,data in chunks:
        if kind==b'IEND':
            content=b'IDAT'+zlib.compress(decoded,9);result+=struct.pack('>I',len(content)-4)+content+struct.pack('>I',zlib.crc32(content)&0xffffffff)
        content=kind+data;result+=struct.pack('>I',len(data))+content+struct.pack('>I',zlib.crc32(content)&0xffffffff)
    image=Image.open(BytesIO(result)).convert('RGBA');image.load()
    PROVENANCE.append(dict(source=str(SOURCE/name),source_sha256=hashlib.sha256(raw).hexdigest(),decoded_size=image.size))
    return image

T.mkdir(parents=True,exist_ok=True)
providers=[]
for ch,name,file in [(0xE780,'checkpoint','mcc/textures/_fonts/icon/flag.png'),(0xE781,'finish','mcc/textures/_fonts/icon/trophy/yellow.png')]:
    im=source_png(file);im.putpixel((im.width-1,im.height-1),(255,255,255,1));im.save(T/f'ui_{name}.png')
    providers.append(dict(type='bitmap',file=f'viksstuff:parkour/ui_{name}.png',height=8,ascent=7,chars=[chr(ch)]))
for ch,name,w,h,ascent in [(0xE782,'action',190,12,9),(0xE783,'score',180,9,7),(0xE784,'heading',180,12,9)]:
    im=Image.new('RGBA',(w,h),(0,0,0,116));im.save(T/f'ui_{name}.png')
    providers.append(dict(type='bitmap',file=f'viksstuff:parkour/ui_{name}.png',height=h,ascent=ascent,chars=[chr(ch)]))
providers.append(dict(type='space',advances={chr(0xF000+n+512):n for n in range(-512,513)}))
providers.append(dict(type='reference',id='minecraft:default'))
(F/'parkour_ui.json').write_text(json.dumps(dict(providers=providers),indent=2)+'\n')
frames=[('rank',0,48),('time',48,103),('head',151,43)]
for i,design in enumerate(['ribbon','bracket','split','ticket','orbit']):
    art=Image.new('RGBA',(388,78));d=ImageDraw.Draw(art)
    # Clean black plates with breathing room. Slightly different corner cuts retain the five layouts.
    inset=8+i%3;cut=2+i
    d.polygon([(inset+cut,10),(294-cut,10),(294,10+cut),(294,68-cut),(294-cut,68),(inset+cut,68),(inset,68-cut),(inset,10+cut)],fill=(0,0,0,126))
    d.rounded_rectangle((310,10,382,68),radius=3+i,fill=(0,0,0,126))
    for name,left,width in frames:
        tile=art.crop((left*2,0,(left+width)*2,78));tile.putpixel((tile.width-1,77),(255,255,255,1));tile.save(T/f'timer_{design}_{name}_frame.png')
        if design=='ribbon':tile.save(T/f'timer_{name}_frame.png')
    art.save(T/f'timer_{design}_panel.png')
    if design=='ribbon':art.save(T/'timer_panel.png')

block=ASSETS/'minecraft/textures/block';block.mkdir(parents=True,exist_ok=True)
for name in ['water_still','water_flow']:
    im=source_png(f'minecraft/textures/block/{name}.png');im.save(block/f'{name}.png')
    (block/f'{name}.png.mcmeta').write_bytes((SOURCE/f'minecraft/textures/block/{name}.png.mcmeta').read_bytes())
for name in ['ice','packed_ice','blue_ice']:
    source_png('mcc/textures/block/f/packed_ice.png').save(block/f'{name}.png')
mud=ROOT/'source-art/parkour/packed-mud/option-1-source.png'
if mud.exists():
    Image.open(mud).convert('RGBA').resize((16,16),Image.Resampling.NEAREST).save(block/'packed_mud.png')
    PROVENANCE.append(dict(source='source-art/parkour/packed-mud/option-1-source.png',source_sha256=hashlib.sha256(mud.read_bytes()).hexdigest(),selected_by_user=1,export_size=[16,16]))
(ROOT/'docs/parkour-polish-assets.json').write_text(json.dumps(dict(source='User supplied full extracted pack library',assets=PROVENANCE,ui_alpha=126),indent=2)+'\n')
preview=Image.new('RGBA',(600,180),'#263D32')
for i,name in enumerate(['water_still','ice']):
    im=Image.open(block/f'{name}.png');w=im.width;preview.alpha_composite(im.crop((0,0,w,w)).resize((128,128),Image.Resampling.NEAREST),(i*150,20))
for i,name in enumerate(['checkpoint','finish']):preview.alpha_composite(Image.open(T/f'ui_{name}.png').resize((96,96),Image.Resampling.NEAREST),(320+i*120,30))
preview.save(ROOT/'previews/parkour-polish-library-assets.png')
print('CLEAN UI: five translucent frames, local icons and backings; animated water, ice and selected warm-clay packed mud.')
