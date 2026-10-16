"""Use Mojang's actual ASCII glyph pixels for the parkour clock, without font redesign."""
from pathlib import Path
from io import BytesIO
import json,zipfile
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];A=ROOT/'overlay/assets/viksstuff';chars='0123456789:.hms#-?+'
with zipfile.ZipFile('C:/Users/navra/.gradle/caches/fabric-loom/1.21.11/minecraft-client.jar') as jar:
    ascii=Image.open(BytesIO(jar.read('assets/minecraft/textures/font/ascii.png'))).convert('RGBA')
for name,cell,height,ascent,native in [('digits',32,16,-6,14),('small',24,12,-8,11)]:
    sheet=Image.new('RGBA',(cell*len(chars),cell))
    for i,c in enumerate(chars):
        n=ord(c);glyph=ascii.crop((n%16*8,n//16*8,n%16*8+8,n//16*8+8)).resize((cell,cell),Image.Resampling.NEAREST)
        # Half a display pixel vertically centers the original 7px-high ink in the plate.
        tile=Image.new('RGBA',(cell,cell));tile.alpha_composite(glyph,(1,1))
        if c in 'hms':
            tinted=Image.new('RGBA',tile.size,(255,82,108));tinted.putalpha(tile.getchannel('A'));tile=tinted
        metric=25 if name=='digits' else 19;tile.putpixel((metric,cell-1),(255,255,255,1))
        sheet.alpha_composite(tile,(i*cell,0))
    target=f'parkour/timer_minecraft_{name}.png';sheet.save(A/'textures'/target)
    (A/f'font/parkour_timer_{name}.json').write_text(json.dumps(dict(providers=[dict(type='bitmap',file='viksstuff:'+target,height=height,ascent=ascent,chars=[chars])]),indent=2)+'\n')
metrics=ROOT/'source-art/parkour/metrics.json';m=json.loads(metrics.read_text());m['fonts']['digits'].update(height=16,ascent=-6);m['fonts']['small'].update(height=12,ascent=-8);m['source']='Mojang Minecraft ASCII glyph pixels, red time units, translucent black plates and centered 18px head.';metrics.write_text(json.dumps(m,indent=2)+'\n')
# Icon font must also render ordinary inherited text; this prevents missing-letter squares.
p=A/'font/parkour_ui.json';m=json.loads(p.read_text());m['providers']=[v for v in m['providers'] if v.get('type')!='reference'];m['providers'].append(dict(type='reference',id='minecraft:default'));p.write_text(json.dumps(m,indent=2)+'\n')
print('MINECRAFT CLOCK: original vanilla glyphs, matching red units; icon font includes native-text fallback.')
