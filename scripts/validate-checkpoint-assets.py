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
        if name == 'parkour_checkpoint':
            assert model['display']['fixed']['rotation'] == [0,180,0], 'Plaque front must face the billboard viewer'
            assert 'parent' not in model, 'Plaque must use actual thick geometry'
            assert all(e['to'][2]-e['from'][2] >= 1 for e in model['elements'])
            bars=model['elements'][-18:]
            assert len(bars)==18
            for i in range(9):
                left,right=bars[i],bars[i+9]
                assert abs((left['from'][0]+left['to'][0]+right['from'][0]+right['to'][0])/2-16)<1e-6
        if count is not None: assert len(model['elements']) == count
        boxes=model['elements']
        for i,a in enumerate(boxes):
            for b in boxes[i+1:]:
                overlap=[min(a['to'][axis],b['to'][axis])-max(a['from'][axis],b['from'][axis]) for axis in range(3)]
                assert not all(value>1e-6 for value in overlap), (name,'overlapping geometry')
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
    assert set(sign.getchannel('A').getdata()) == {0,255}, 'No translucent fringe'
print('PASS: solid plaque depth, symmetric 3D bars, non-overlapping edges, clean alpha and atlas registration')
