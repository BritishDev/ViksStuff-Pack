"""Solid, hand-composed Minecraft trophy plaques: opaque cuboids, no generated image decals."""
from pathlib import Path
import json
from PIL import Image
R=Path(__file__).resolve().parents[1]; O=R/'overlay/assets/viksstuff'
P={
'C':['01111','11000','10000','10000','10000','11000','01111'],
'H':['10001','10001','10001','11111','10001','10001','10001'],
'E':['11111','10000','10000','11110','10000','10000','11111'],
'K':['10001','10010','10100','11000','10100','10010','10001'],
'P':['11110','10001','10001','11110','10000','10000','10000'],
'O':['01110','11011','10001','10001','10001','11011','01110'],
'I':['111','010','010','010','010','010','111'],
'N':['10001','11001','11001','10101','10011','10011','10001'],
'T':['11111','00100','00100','00100','00100','00100','00100'],
'F':['11111','10000','10000','11110','10000','10000','10000'],
'S':['01111','10000','10000','01110','00001','00001','11110']}
colors={'rim_dark':'#13271D','finish':'#39E98A','finish_light':'#9BFFD0','finish_shadow':'#166640','checkpoint':'#FFD34A','checkpoint_light':'#FFF0A6','checkpoint_shadow':'#9A5B14','face':'#181D22','white':'#FFF2DD','ink_shadow':'#4D4437','black':'#18241E'}
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
for n,c in colors.items():Image.new('RGBA',(16,16),c).save(O/f'textures/item/parkour_solid_{n}.png')
for name,word,theme in [('parkour_finish','FINISH','finish')]:
 els=[]
 def box(a,b,mat):els.append({'from':[round(v,4) for v in a],'to':[round(v,4) for v in b],'faces':{f:{'texture':'#'+mat} for f in ['north','south','east','west','up','down']}})
 # 2.5-unit-deep charcoal body with stepped corners; bright proud front rim.
 box([.4,5.3,6.3],[15.6,10.7,8.5],'rim_dark');box([0,5.9,6.3],[16,10.1,8.5],'rim_dark')
 box([.7,5.65,8.5],[15.3,6.1,8.95],theme+'_shadow');box([.7,9.9,8.5],[15.3,10.35,9.15],theme+'_light')
 box([.35,6.1,8.5],[.85,9.9,9.0],theme+'_light');box([15.15,6.1,8.5],[15.65,9.9,9.0],theme+'_shadow')
 for x in [.5,15.0]:
  box([x,5.95,8.5],[x+.5,6.4,9.05],theme);box([x,9.6,8.5],[x+.5,10.05,9.05],theme)
 box([.85,6.1,8.5],[15.15,9.9,8.8],'face')
 width=sum(len(P[ch][0])+1 for ch in word)-1
 unit=min(.33,11.0/width);start=3.45+(11-width*unit)/2;bottom=8-7*unit/2
 # Group contiguous pixels into runs, keeping a deliberate raised shadow beneath each letter.
 for ch in word:
  for y,row in enumerate(P[ch]):
   x=0
   while x<len(row):
    if row[x]=='0':x+=1;continue
    left=x
    while x<len(row) and row[x]=='1':x+=1
    x0=start+left*unit;x1=start+x*unit;y0=bottom+(6-y)*unit
    box([x0+.06,y0-.07,8.8],[x1+.06,y0+unit-.07,9.13],'ink_shadow')
    box([x0,y0,9.12],[x1,y0+unit,9.48],'white')
  start+=(len(P[ch][0])+1)*unit
 # Flag/check icon is real raised geometry, not a front texture.
 if theme=='finish':
  for y in range(4):
   for x in range(4):box([1.25+x*.4,7.2+y*.4,8.85],[1.65+x*.4,7.6+y*.4,9.35],'white' if (x+y)%2==0 else 'black')
  box([1.17,6.65,8.9],[1.37,8.95,9.42],theme)
 else:
  for x,y in [(0,2),(1,1),(2,0),(3,1),(4,2),(5,3),(6,4)]:box([1.1+x*.26,7.35+y*.26,8.9],[1.42+x*.26,7.67+y*.26,9.42],theme)
 tex={n:f'viksstuff:item/parkour_solid_{n}' for n in colors}
 write(O/f'models/item/{name}.json',{'textures':tex,'elements':els,'display':{'fixed':{'rotation':[0,180,0],'scale':[1,1,1]},'gui':{'rotation':[16,30,0],'scale':[1,1,1]}}})
 write(O/f'items/{name}.json',{'model':{'type':'minecraft:model','model':f'viksstuff:item/{name}'}})
 print(name,len(els),'solid cuboids')
for atlas in ['blocks','items']:
 p=R/f'overlay/assets/minecraft/atlases/{atlas}.json';a=json.loads(p.read_text())
 for n in colors:
  ref=f'viksstuff:item/parkour_solid_{n}'
  if not any(s.get('resource')==ref for s in a['sources']):a['sources'].append({'type':'minecraft:single','resource':ref,'sprite':ref})
 write(p,a)
