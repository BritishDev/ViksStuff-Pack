from pathlib import Path
import json
from PIL import Image

root=Path(__file__).resolve().parents[1]
sheet=Image.open(root/'source-art/parkour/spectator-icons.png').convert('RGBA')
assets=root/'overlay/assets/viksstuff'
for i,name in enumerate(['runner','checkpoint','players']):
    tile=sheet.crop((sheet.width*i//3,0,sheet.width*(i+1)//3,sheet.height))
    alpha=tile.getchannel('A').point(lambda p:255 if p>=160 else 0)
    tile.putalpha(alpha);tile=tile.crop(alpha.getbbox());tile.thumbnail((60,60),Image.Resampling.NEAREST)
    canvas=Image.new('RGBA',(64,64));canvas.paste(tile,((64-tile.width)//2,(64-tile.height)//2))
    texture=assets/('textures/item/parkour_spec_'+name+'.png');texture.parent.mkdir(parents=True,exist_ok=True);canvas.save(texture)
    for folder,data in [('items',{'model':{'type':'minecraft:model','model':'viksstuff:item/parkour_spec_'+name}}),
                        ('models/item',{'parent':'minecraft:item/generated','textures':{'layer0':'viksstuff:item/parkour_spec_'+name}})]:
        path=assets/(folder+'/parkour_spec_'+name+'.json');path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    for atlas in ['blocks','items']:
        path=assets.parent/('minecraft/atlases/'+atlas+'.json');data=json.loads(path.read_text(encoding='utf-8'))
        sprite='viksstuff:item/parkour_spec_'+name
        if not any(s.get('resource')==sprite for s in data['sources']):data['sources'].append({'type':'minecraft:single','resource':sprite,'sprite':sprite})
        path.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
print('Three spectator hotbar models/icons packaged')
