from pathlib import Path
from PIL import Image,ImageDraw
from io import BytesIO
import zipfile
r=Path(__file__).resolve().parents[1];t=r/'overlay/assets/viksstuff/textures/parkour';chars='0123456789:.hms#-?+'
sheet=Image.open(t/'timer_minecraft_digits.png').convert('RGBA')
with zipfile.ZipFile('C:/Users/navra/.gradle/caches/fabric-loom/1.21.11/minecraft-client.jar') as z:
 skin=Image.open(BytesIO(z.read('assets/minecraft/textures/entity/player/wide/steve.png'))).convert('RGBA')
head=skin.crop((8,8,16,16));head.alpha_composite(skin.crop((40,8,48,16)));head=head.resize((36,36),Image.Resampling.NEAREST)
out=Image.new('RGBA',(388,78*3+20),'#61705C')
for i,value in enumerate(['59s','1m0s','1h1m1s']):
 panel=Image.open(t/'timer_ribbon_panel.png').convert('RGBA');x=((153-len(value)*12)//2)*2
 for c in value:
  tile=sheet.crop((chars.index(c)*32,0,chars.index(c)*32+32,32));panel.alpha_composite(tile,(x,24));x+=24
 panel.alpha_composite(head,(328,21));out.alpha_composite(panel,(0,i*78+10))
out.resize((1164,762),Image.Resampling.NEAREST).save(r/'previews/parkour-minecraft-hud.png')
