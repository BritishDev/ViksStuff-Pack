"""Hand-composed crimson HUD geometry and light glyphs; five editable SVG masters."""
from pathlib import Path
import json, zipfile
from io import BytesIO
from PIL import Image,ImageDraw,ImageFont
from parkour_badge_art import artwork as badge_artwork, letter as pixel_letter
R=Path(__file__).resolve().parents[1]; T=R/'overlay/assets/viksstuff/textures/parkour'; F=R/'overlay/assets/viksstuff/font'; S=R/'source-art/parkour/red-designs'; P=R/'previews'
for p in (T,F,S,P): p.mkdir(parents=True,exist_ok=True)
DESIGNS=['ribbon','bracket','split','ticket','orbit']; CHARS='0123456789:.s#-?+'
RED='#D52D45'; DARK='#211B22'; LIGHT='#F4E9E7'
def artwork(name):
 im=Image.new('RGBA',(1552,312)); d=ImageDraw.Draw(im); svg=[]
 def poly(pts,color):
  d.polygon([(int(x*8),int(y*8)) for x,y in pts],fill=color); svg.append('<polygon points="'+' '.join(f'{x},{y}' for x,y in pts)+f'" fill="{color}"/>')
 def box(x,y,w,h,c): poly([(x,y),(x+w,y),(x+w,y+h),(x,y+h)],c)
 def line(pts,c,w=1):
  d.line([(int(x*8),int(y*8)) for x,y in pts],fill=c,width=int(w*8)); svg.append('<polyline points="'+' '.join(f'{x},{y}' for x,y in pts)+f'" fill="none" stroke="{c}" stroke-width="{w}"/>')
 if name=='ribbon':
  return badge_artwork()
 elif name=='bracket':
  box(10,8,138,23,'#17171D'); line([(19,5),(6,5),(6,34),(19,34)],RED,1.5); line([(137,5),(150,5),(150,34),(137,34)],RED,1.5); line([(160,5),(190,5),(190,34),(160,34)],'#79313F'); box(155,8,3,23,RED)
 elif name=='split':
  box(3,5,145,29,DARK); box(3,5,4,29,RED); box(156,3,36,33,RED); box(159,6,30,27,DARK); line([(14,34),(143,34)],'#79313F',.7)
 elif name=='ticket':
  poly([(3,6),(148,6),(152,10),(188,10),(191,13),(191,30),(187,34),(3,34),(7,30),(7,10)],'#E9D5CF'); box(8,8,143,24,DARK); box(158,8,31,26,RED)
  for y in (7,12,17,22,27,32): box(153,y,1,2,RED)
  line([(15,10),(37,10)],RED)
 else:
  box(9,9,135,23,'#19171D'); line([(12,33),(137,33),(149,21)],RED,1.2); d.arc((1240,8,1544,304),25,335,fill=RED,width=12); svg.append(f'<path d="M189 28 A18 18 0 1 0 187 8" fill="none" stroke="{RED}" stroke-width="1.5"/>'); box(141,9,9,2,RED)
 (S/f'{name}.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 194 39">'+''.join(svg)+'</svg>\n'); return im.resize((388,78),Image.Resampling.LANCZOS)
frames=[('rank',0,48,'\uE600'),('time',48,103,'\uE601'),('head',151,43,'\uE602')]
for design in DESIGNS:
 art=artwork(design); providers=[]
 for name,left,width,char in frames:
  tile=art.crop((left*2,0,(left+width)*2,78)); tile.putpixel((tile.width-1,77),(255,255,255,1)); tile.save(T/f'timer_{design}_{name}_frame.png'); providers.append(dict(type='bitmap',file=f'viksstuff:parkour/timer_{design}_{name}_frame.png',height=39,ascent=6,chars=[char]))
 providers.append(dict(type='space',advances={chr(0xE800+n+195):n for n in range(-195,196)})); (F/f'parkour_timer_{design}.json').write_text(json.dumps(dict(providers=providers),indent=2)+'\n'); art.save(T/f'timer_{design}_panel.png')
 if design=='ribbon':
  (F/'parkour_timer.json').write_text(json.dumps(dict(providers=providers),indent=2)+'\n'); art.save(T/'timer_panel.png')
  for n,l,w,c in frames: Image.open(T/f'timer_{design}_{n}_frame.png').save(T/f'timer_{n}_frame.png')
specs={'digits':(28,38,19,-6,14),'rank':(32,40,20,-4,16),'small':(20,28,14,-9,11)}; glyphs={}
for name,(cell,height,display,ascent,advance) in specs.items():
 sheet=Image.new('RGBA',(cell*len(CHARS),height)); glyphs[name]={}
 for index,char in enumerate(CHARS):
  tile=pixel_letter(char,name,cell,height,advance); sheet.alpha_composite(tile,(index*cell,0)); glyphs[name][char]=tile
 sheet.save(T/f'timer_{name}.png'); (F/f'parkour_timer_{name}.json').write_text(json.dumps(dict(providers=[dict(type='bitmap',file=f'viksstuff:parkour/timer_{name}.png',height=display,ascent=ascent,chars=[CHARS])]),indent=2)+'\n')
def adv(c,small=False): return (3 if small else 4) if c in '.:' else (6 if small else 8) if c=='s' else (8 if small else 12)
def sample(design,value='42.73s'):
 art=Image.open(T/f'timer_{design}_panel.png'); small=sum(adv(c) for c in value)>124; f='small' if small else 'digits'; width=sum(adv(c,small) for c in value); x=(150-width)//2*2
 for c in value: art.alpha_composite(glyphs[f][c],(x,30 if small else 24)); x+=adv(c,small)*2
 with zipfile.ZipFile('C:/Users/navra/.gradle/caches/fabric-loom/1.21.11/minecraft-client.jar') as client:
  skin=Image.open(BytesIO(client.read('assets/minecraft/textures/entity/player/wide/steve.png'))).convert('RGBA')
  face=skin.crop((8,8,16,16)); face.alpha_composite(skin.crop((40,8,48,16)))
 art.alpha_composite(face.resize((44,44),Image.Resampling.NEAREST),(324,16)); return art

board=Image.new('RGBA',(1200,900),'#13171D'); bd=ImageDraw.Draw(board); title=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',26); label=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',18); bd.text((40,25),'PARKOUR / CRIMSON STUDIES',font=title,fill=LIGHT)
desc=['Folded ribbon / angled portrait end','Open brackets / fine technical frame','Separate blocks / offset portrait','Cut ticket / warm paper edge','Open orbit / underline and portrait seal']
for i,design in enumerate(DESIGNS):
 y=90+i*155; bd.text((40,y),f'{i+1:02d}   {design.upper()}',font=label,fill='#ED7180'); bd.text((40,y+29),desc[i],font=label,fill='#A59FA5'); board.alpha_composite(sample(design).resize((776,156),Image.Resampling.NEAREST),(390,y-18)); sample(design).save(P/f'parkour-red-{design}.png')
board.save(P/'parkour-red-five-designs.png'); metrics=dict(width=195,height=39,designs=DESIGNS,frames=[dict(name=n,left=l,width=w,advance=w+1,char=c) for n,l,w,c in frames],fonts={n:dict(native_advance=s[4],height=s[2],ascent=s[3]) for n,s in specs.items()},source='Default ribbon: reference-style hand-drawn crimson pixel bevel, recessed graphite face, original regular 5x7 numeral glyphs. Live head/time only.'); (S/'metrics.json').write_text(json.dumps(metrics,indent=2)+'\n'); (R/'source-art/parkour/metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')
bars=R/'overlay/assets/minecraft/textures/gui/sprites/boss_bar'; bars.mkdir(parents=True,exist_ok=True)
for n in ('white_background','white_progress'): Image.new('RGBA',(182,5)).save(bars/f'{n}.png')
print('REFERENCE BADGE HUD: crimson pixel bevel, recessed graphite, regular pixel glyphs, live head/time only.')
