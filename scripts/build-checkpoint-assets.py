from pathlib import Path
import json
from PIL import Image
from collections import deque

root = Path(__file__).resolve().parents[1]
source = root / 'source-art/parkour/checkpoint-gold.png'
overlay = root / 'overlay/assets/viksstuff'
def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')
image = Image.open(source).convert('RGBA')
assert image.getextrema()[3][0] == 0, 'Sign must retain transparency'
image.thumbnail((512, 512), Image.Resampling.NEAREST)
texture = overlay / 'textures/item/parkour_checkpoint_gold.png'
texture.parent.mkdir(parents=True, exist_ok=True)
canvas = Image.new('RGBA', (512,512))
canvas.paste(image, ((512-image.width)//2,(512-image.height)//2))
# Remove partial-alpha fringe and detached specks before building solid geometry.
mask = canvas.getchannel('A').point(lambda value: 255 if value >= 160 else 0)
pending = set((x,y) for y in range(512) for x in range(512) if mask.getpixel((x,y)))
components = []
while pending:
    first = pending.pop()
    group = [first]
    queue = deque([first])
    while queue:
        x,y = queue.popleft()
        for neighbor in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]:
            if neighbor in pending:
                pending.remove(neighbor); group.append(neighbor); queue.append(neighbor)
    components.append(group)
keep = set(p for group in sorted(components,key=len,reverse=True)[:2] for p in group)
for y in range(512):
    for x in range(512):
        if (x,y) in keep:
            r,g,b,a = canvas.getpixel((x,y)); canvas.putpixel((x,y),(r,g,b,255))
        else: canvas.putpixel((x,y),(255,213,0,0))
canvas.save(texture)
Image.new('RGBA',(16,16),(255,213,0,255)).save(overlay / 'textures/item/parkour_checkpoint_edge.png')
# Register model sprites explicitly in both model atlases used by supported clients.
for atlas in ['blocks','items']:
    atlas_path = overlay.parent / ('minecraft/atlases/' + atlas + '.json')
    definition = json.loads(atlas_path.read_text(encoding='utf-8'))
    for sprite in ['viksstuff:item/parkour_checkpoint_gold','viksstuff:item/parkour_outline','viksstuff:item/parkour_checkpoint_edge']:
        if not any(entry.get('resource') == sprite for entry in definition['sources']):
            definition['sources'].append({'type':'minecraft:single','resource':sprite,'sprite':sprite})
    write(atlas_path,definition)
# Merge silhouette runs into disjoint extruded cuboids. Solid sides are visible from above.
grid = canvas.getchannel('A').resize((64,64),Image.Resampling.NEAREST)
active = {}
rectangles = []
for y in range(65):
    runs = []
    if y < 64:
        x = 0
        while x < 64:
            if not grid.getpixel((x,y)): x += 1; continue
            start = x
            while x < 64 and grid.getpixel((x,y)): x += 1
            runs.append((start,x))
    for run in list(active):
        if run not in runs:
            rectangles.append((*run,active.pop(run),y))
    for run in runs: active.setdefault(run,y)
plaque = []
for x0,x1,y0,y1 in rectangles:
    uv = [x0/4,y0/4,x1/4,y1/4]
    plaque.append({'from':[x0/4,16-y1/4,7.5],'to':[x1/4,16-y0/4,8.5],
        'faces':{'south':{'texture':'#front','uv':uv},
                 'north':{'texture':'#front','uv':[x1/4,y0/4,x0/4,y1/4]},
                 **{face:{'texture':'#edge'} for face in ['east','west','up','down']}}})
# Keep the plaque silhouette clean: the former 18 detached side-dot cuboids
# have been removed. The sign itself retains its depth and original artwork.
write(overlay / 'models/item/parkour_checkpoint.json', {'textures':{'front':'viksstuff:item/parkour_checkpoint_gold','edge':'viksstuff:item/parkour_checkpoint_edge','particle':'viksstuff:item/parkour_checkpoint_edge'},'elements':plaque,'display':{'fixed':{'rotation':[0,180,0],'translation':[0,0,0],'scale':[1,1,1]}}})
for name in ['parkour_checkpoint','parkour_outline_top','parkour_outline_full']:
    write(overlay / ('items/' + name + '.json'), {'model':{'type':'minecraft:model','model':'viksstuff:item/' + name}})
Image.new('RGBA', (16,16), (255,245,230,255)).save(overlay / 'textures/item/parkour_outline.png')
for full in [False, True]:
    elements = []
    def rod(a,b):
        elements.append({'from':a,'to':b,'faces':{face:{'texture':'#all'} for face in ['north','south','east','west','up','down']}})
    lo,hi,t = -.65,16.65,.5
    for y in ([lo,hi-t] if full else [hi-t]):
        for z in [lo,hi-t]: rod([lo,y,z],[hi,y+t,z+t])
        for x in [lo,hi-t]: rod([x,y,lo+t],[x+t,y+t,hi-t])
    if full:
        for x in [lo,hi-t]:
            for z in [lo,hi-t]: rod([x,lo+t,z],[x+t,hi-t,z+t])
    write(overlay / ('models/item/parkour_outline_' + ('full' if full else 'top') + '.json'), {'textures':{'all':'viksstuff:item/parkour_outline','particle':'viksstuff:item/parkour_outline'},'elements':elements,'display':{'fixed':{'rotation':[0,0,0],'translation':[0,0,0],'scale':[1,1,1]}}})
write(overlay / 'items/parkour_outline_segment.json', {'model':{'type':'minecraft:model','model':'viksstuff:item/parkour_outline_segment'}})
write(overlay / 'models/item/parkour_outline_segment.json', {
    'textures':{'all':'viksstuff:item/parkour_outline','particle':'viksstuff:item/parkour_outline'},
    'elements':[{'from':[0,0,0],'to':[16,16,16],
        'faces':{face:{'texture':'#all'} for face in ['north','south','east','west','up','down']}}],
    'display':{'fixed':{'rotation':[0,0,0],'translation':[0,0,0],'scale':[1,1,1]}}})
print('Checkpoint plaque without side dots, legacy outline models and one outline segment built:', image.size)
