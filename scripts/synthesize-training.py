import math, wave, struct, subprocess, json, zipfile
from pathlib import Path
root=Path(__file__).resolve().parents[1]
out=root/'overlay/assets/viksstuff/sounds/training'
out.mkdir(parents=True,exist_ok=True)
source=root/'source-art/training'
rate=44100
for name,notes in [('success',[523.25,659.25,783.99]),('failed',[220,164.81,110])]:
    duration=.48 if name=='success' else .36
    samples=[]
    for i in range(int(rate*duration)):
        t=i/rate
        value=0
        for j,freq in enumerate(notes):
            age=t-j*.085
            if age>=0:
                envelope=min(1,age/.008)*math.exp(-age*13)
                value+=.20*envelope*(math.sin(2*math.pi*freq*age)+.18*math.sin(4*math.pi*freq*age))
        value*=min(1,(duration-t)/.025)
        samples.append(struct.pack('<h',int(max(-1,min(1,value))*32767)))
    wav=source/(name+'.wav')
    with wave.open(str(wav),'wb') as audio:
        audio.setnchannels(1);audio.setsampwidth(2);audio.setframerate(rate);audio.writeframes(b''.join(samples))
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(wav),'-c:a','libvorbis','-q:a','5',str(out/(name+'.ogg'))],check=True)
path=root/'overlay/assets/viksstuff/sounds.json'
if path.exists(): data=json.loads(path.read_text())
else:
    with zipfile.ZipFile(root/'base/ViksStuff-Pack.base.zip') as z:
        key='assets/viksstuff/sounds.json'
        data=json.loads(z.read(key)) if key in z.namelist() else {}
for name in ['success','failed']:
    data['training.'+name]={'sounds':[{'name':'viksstuff:training/'+name,'stream':False}]}
path.write_text(json.dumps(data,indent=2))
