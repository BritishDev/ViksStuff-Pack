from pathlib import Path
import json, shutil, subprocess, numpy as np, hashlib
from PIL import Image,ImageDraw
root=Path('ViksStuff-Pack');o=root/'overlay/assets/viksstuff'
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
# Colored, opaque, full-bright geometry: no glowing-outline framebuffer pass.
faces=['north','south','east','west','up','down']
for name,color in [('red','#FF396B'),('green','#39FF88'),('gold','#FFD500'),('cyan','#29E7FF'),('blue','#3388FF'),('violet','#CC66FF'),('white','#FFFFFF')]:
 Image.new('RGBA',(16,16),color).save(o/f'textures/item/parkour_line_{name}.png')
 write(o/f'items/parkour_line_{name}.json',{'model':{'type':'minecraft:model','model':f'viksstuff:item/parkour_line_{name}'}})
 write(o/f'models/item/parkour_line_{name}.json',{'textures':{'all':f'viksstuff:item/parkour_line_{name}'},'elements':[{'from':[0,0,0],'to':[16,16,16],'shade':False,'faces':{f:{'texture':'#all'} for f in faces}}],'display':{'fixed':{'scale':[1,1,1]}}})
# Solid cuboid trophies, with wide bowl, handles, neck, and stepped base. Handheld at a natural scale.
for place,color in [(1,'#FFD34A'),(2,'#CFDCE8'),(3,'#CB8550')]:
 name=f'parkour_trophy_{place}';Image.new('RGBA',(16,16),color).save(o/f'textures/item/{name}.png')
 elements=[]
 for lo,hi in [([3,0,4],[13,2,12]),([5,2,5],[11,3,11]),([7,3,7],[9,8,9]),([4,8,5],[12,13,11]),([3,13,4],[13,15,12]),([1,10,6],[3,14,10]),([13,10,6],[15,14,10]),([2,8,6],[5,10,10]),([11,8,6],[14,10,10])]:elements.append({'from':lo,'to':hi,'faces':{f:{'texture':'#all'} for f in faces}})
 write(o/f'items/{name}.json',{'model':{'type':'minecraft:model','model':f'viksstuff:item/{name}'}})
 write(o/f'models/item/{name}.json',{'textures':{'all':f'viksstuff:item/{name}'},'elements':elements,'display':{'thirdperson_righthand':{'rotation':[0,0,0],'translation':[0,3,1],'scale':[.65,.65,.65]},'gui':{'rotation':[25,35,0],'scale':[.8,.8,.8]}}})
# Finish plaque and checkpoint/chat glyphs extend the existing integer pixel design.
patterns={
'F':['11111','10000','10000','11110','10000','10000','10000'],
'I':['111','010','010','010','010','010','111'],
'N':['10001','11001','11001','10101','10011','10011','10001'],
'S':['01111','10000','10000','01110','00001','00001','11110'],
'H':['10001','10001','10001','11111','10001','10001','10001']}
im=Image.new('RGBA',(128,32));d=ImageDraw.Draw(im);d.polygon([(1,6),(7,1),(120,1),(126,7),(126,25),(120,30),(7,30),(1,24)],fill='#082B1B',outline='#39FF88',width=2)
x=44
# Checkered flag, readable even when seen at distance.
for cy in range(3):
 for cx in range(4):d.rectangle((21+cx*4,7+cy*4,24+cx*4,10+cy*4),fill='#FFF5E6' if (cx+cy)%2==0 else '#0E3824')
d.rectangle((21,7,22,25),fill='#39FF88')
for ch in 'FINISH':
 p=patterns[ch]
 for y,row in enumerate(p):
  for col,v in enumerate(row):
   if v=='1':d.rectangle((x+col*2,8+y*2,x+col*2+1,8+y*2+1),fill='#FFF5E6')
 x+=(len(p[0])+1)*2
im.save(o/'textures/item/parkour_finish.png')
write(o/'items/parkour_finish.json',{'model':{'type':'minecraft:model','model':'viksstuff:item/parkour_finish'}})
write(o/'models/item/parkour_finish.json',{'textures':{'all':'viksstuff:item/parkour_finish'},'elements':[{'from':[0,6,7.875],'to':[16,10,8.125],'shade':False,'faces':{'south':{'texture':'#all','uv':[0,0,16,16]},'north':{'texture':'#all','uv':[16,0,0,16]}}}],'display':{'fixed':{'rotation':[0,180,0],'scale':[1,1,1]}}})
im.resize((768,192),Image.Resampling.NEAREST).save(root/'previews/parkour-finish.png')
# Dedicated glyphs for checkpoint title/chat and finish title, with no copied server art.
icon=Image.new('RGBA',(16,16));di=ImageDraw.Draw(icon);di.line([(2,8),(6,12),(14,3)],fill='#FFD500',width=3);icon.save(o/'textures/item/parkour_checkpoint_icon.png')
write(o/'font/parkour_events.json',{'providers':[{'type':'bitmap','file':'viksstuff:item/parkour_checkpoint_icon.png','ascent':8,'height':9,'chars':['\ue710']},{'type':'bitmap','file':'viksstuff:item/parkour_finish.png','ascent':10,'height':16,'chars':['\ue711']}]})
# Register every new sprite in both atlas variants.
for atlas in ['blocks','items']:
 p=root/f'overlay/assets/minecraft/atlases/{atlas}.json';a=json.loads(p.read_text())
 for sprite in ['parkour_line_red','parkour_line_green','parkour_line_gold','parkour_line_cyan','parkour_line_blue','parkour_line_violet','parkour_line_white','parkour_trophy_1','parkour_trophy_2','parkour_trophy_3','parkour_finish','parkour_checkpoint_icon']:
  ref=f'viksstuff:item/{sprite}'
  if not any(s.get('resource')==ref for s in a['sources']):a['sources'].append({'type':'minecraft:single','resource':ref,'sprite':ref})
 write(p,a)
# Silence only block landing/footsteps, including locally predicted client sounds.
p=root/'overlay/assets/minecraft/sounds.json';reg=json.loads(p.read_text()) if p.exists() else {}
for cue in ['block.slime_block.fall','block.slime_block.step']:reg[cue]={'replace':True,'sounds':[]}
write(p,reg)
# Reduce the reserved HUD portrait from 22 to 18 pixels, retaining its center.
p=root/'overlay/strength_1_21_11/assets/minecraft/shaders/core/rendertype_text.vsh';s=p.read_text().replace('? -7.0 : 7.0','? -5.0 : 5.0');p.write_text(s)
# Measured +4dB audio target, with limiting rather than clipping.
ff=shutil.which('ffmpeg');manifest=root/'docs/parkour-sounds.json';m=json.loads(manifest.read_text());back=Path('artifacts/parkour-recording/audio-before');back.mkdir(exist_ok=True)
for cue,info in m['sounds'].items():
 p=o/f'sounds/parkour/{cue}.ogg';prior=back/p.name
 if not prior.exists():shutil.copy2(p,prior)
 subprocess.run([ff,'-v','error','-y','-i',str(prior),'-af','volume=4dB,alimiter=limit=0.82:attack=2:release=40:level=false:latency=true','-c:a','libvorbis','-q:a','7',str(p)],check=True)
 def decode(path):return np.frombuffer(subprocess.check_output([ff,'-v','error','-i',str(path),'-ac','1','-ar','48000','-f','f32le','-']),dtype='<f4')
 a=decode(p);old=decode(prior);info.update(sha256=hashlib.sha256(p.read_bytes()).hexdigest(),rms=round(float(np.sqrt(np.mean(a*a))),4),decoded_peak=round(float(max(abs(a))),4),gain_db_vs_previous=round(float(20*np.log10(np.sqrt(np.mean(a*a))/np.sqrt(np.mean(old*old)))),2))
 assert np.isfinite(a).all() and max(abs(a))<.95
m['version']=5;m['loudness_target_db_vs_previous']=4;write(manifest,m)
shutil.copy2(Path(r'C:/Users/navra/.codex/generated_images/01a141a7-0dda-7ab2-b9c8-7f62b9a1213d/exec-27b5922e-20b4-48d4-8bc7-fc45fd56e26d.png'),root/'previews/water-concept.png')
print('Assets, slime silence and measured louder audio built')

import runpy
runpy.run_path(str(root/'scripts/build-parkour-solid-signs.py'),run_name='__main__')
