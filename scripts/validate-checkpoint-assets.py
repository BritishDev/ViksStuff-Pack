from pathlib import Path
from zipfile import ZipFile
import json
from PIL import Image
from io import BytesIO

root = Path(__file__).resolve().parents[1]
with ZipFile(root / 'ViksStuff-Pack.zip') as pack:
    for name, count in [('parkour_checkpoint',None),('parkour_outline_top',4),('parkour_outline_full',12)]:
        item = json.loads(pack.read('assets/viksstuff/items/' + name + '.json'))
        assert item['model']['model'] == 'viksstuff:item/' + name
        model = json.loads(pack.read('assets/viksstuff/models/item/' + name + '.json'))
        if count is not None: assert len(model['elements']) == count
        for sprite in set(model['textures'].values()):
            assert sprite.startswith('viksstuff:item/')
            path = 'assets/viksstuff/textures/' + sprite.split(':')[1] + '.png'
            image = Image.open(BytesIO(pack.read(path)))
            assert image.width == image.height
            for atlas in ['blocks','items']:
                entries = json.loads(pack.read('assets/minecraft/atlases/' + atlas + '.json'))['sources']
                assert any(entry.get('resource') == sprite and entry.get('sprite') == sprite for entry in entries), (atlas,sprite)
    sign = Image.open(BytesIO(pack.read('assets/viksstuff/textures/item/parkour_checkpoint_gold.png')))
    assert sign.getextrema()[3][0] == 0 and sign.getextrema()[3][1] == 255
print('PASS: packed checkpoint models, hollow edge geometry, transparency and atlas registration')
