import fs from 'node:fs/promises';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
import sharp from 'sharp';
const pack=path.resolve('ViksStuff-Pack'),root=path.join(pack,'overlay/assets/viksstuff');
const write=async(p,x)=>{await fs.mkdir(path.dirname(p),{recursive:true});await fs.writeFile(p,JSON.stringify(x,null,2)+'\n');};
const box=(a,b,t='gold')=>({from:a,to:b,shade:t!=='gem',light_emission:t==='gem'?15:0,faces:Object.fromEntries(['up','down','north','south','east','west'].map(f=>[f,{texture:'#'+t,uv:[0,0,16,16]}]))});
for(const [id,rgb] of [['gold',[235,183,57]],['steel',[44,49,58]],['gem',[199,12,37]]]) {
 const data=Buffer.alloc(32*32*4);for(let y=0;y<32;y++)for(let x=0;x<32;x++){let k=(y*32+x)*4,g=.72+.25*Math.sin((x+y)*.24)+.035*Math.cos(y*7+x*3);for(let c=0;c<3;c++)data[k+c]=rgb[c]*g;data[k+3]=255;}
 await fs.mkdir(path.join(root,'textures/item/reveal'),{recursive:true});await sharp(data,{raw:{width:32,height:32,channels:4}}).png().toFile(path.join(root,`textures/item/reveal/${id}.png`));
}
const models={};
models.key=[box([7.4,.5,7.2],[8.6,9,8.8]),box([8,.7,7.1],[11,2,8.9]),box([8,3,7.1],[10.5,4.3,8.9]),box([6.7,7.8,6.8],[9.3,8.7,9.2])];
for(let i=0;i<24;i++){let a=i*Math.PI/12,x=8+3.2*Math.cos(a),y=11.6+3.2*Math.sin(a);models.key.push(box([x-.5,y-.5,7],[x+.5,y+.5,9]));}
models.key.push(box([7.1,10.7,6.4],[8.9,12.5,9.6],'gem'));for(const x of [5.7,9.7])models.key.push(box([x,9.9,6.9],[x+.6,13.5,9.1]));
models.vault_frame=[box([-4,8,4],[0,26,16],'steel'),box([16,8,4],[20,26,16],'steel'),box([0,24,4],[16,28,16],'steel'),box([-4,8,4],[20,10,16],'steel'),box([0,10,14],[16,24,16],'steel')];
for(const x of [-4,17])models.vault_frame.push(box([x,8,3.5],[x+3,27,4.5]));
models.vault_frame.push(box([-4,26,3.5],[20,28,4.5]));
for(const x of [-2,18])for(const y of [11,15,19,23])models.vault_frame.push(box([x-.5,y-.5,3],[x+.5,y+.5,4.6],'gem'));
models.vault_door=[box([8,8,4],[24,24,7],'steel'),box([9,9,3.5],[23,23,4]),box([10,10,3.1],[22,22,3.5],'steel')];
for(const x of [9,22])for(const y of [10,14,18,22])models.vault_door.push(box([x-.4,y-.4,2.8],[x+.4,y+.4,4]));
models.vault_door.push(box([15,14,2.4],[17,18,3.2],'gem'),box([15.6,14.2,2.1],[16.4,16.5,2.4],'steel'));
models.vault_wheel=[];for(let i=0;i<24;i++){let a=i*Math.PI/12,x=8+3*Math.cos(a),y=8+3*Math.sin(a);models.vault_wheel.push(box([x-.4,y-.4,7.5],[x+.4,y+.4,8.5]));}
models.vault_wheel.push(box([4.5,7.7,7.4],[11.5,8.3,8.6]),box([7.7,4.5,7.4],[8.3,11.5,8.6]),box([7,7,7],[9,9,9],'gem'));
for(const [id,elements]of Object.entries(models)) {
 await write(path.join(root,`models/item/reveal/${id}.json`),{ambientocclusion:false,textures:{gold:'viksstuff:item/reveal/gold',steel:'viksstuff:item/reveal/steel',gem:'viksstuff:item/reveal/gem',particle:'viksstuff:item/reveal/gold'},elements,display:{fixed:{rotation:[0,0,0],translation:[0,0,0],scale:[1,1,1]},gui:{rotation:[0,0,-35],scale:[.9,.9,.9]},firstperson_righthand:{rotation:[0,-90,20],translation:[1,2,1],scale:[.9,.9,.9]},thirdperson_righthand:{rotation:[0,-90,0],translation:[0,2,0],scale:[.8,.8,.8]}}});
 await write(path.join(root,`items/reveal/${id}.json`),{model:{type:'minecraft:model',model:`viksstuff:item/reveal/${id}`}});
}
await fs.mkdir(path.join(root,'textures/font'),{recursive:true});
await sharp(path.join(pack,'source-art/strength-reveal/logo-transparent.png')).resize({width:1024}).png().toFile(path.join(root,'textures/font/strength-logo.png'));
await write(path.join(root,'font/reveal.json'),{providers:[{type:'bitmap',file:'viksstuff:font/strength-logo.png',height:48,ascent:0,chars:['\ue700']}]});
const sounds=JSON.parse(await fs.readFile(path.join(root,'sounds.json'),'utf8'));const durations={};
const captions={};
await fs.mkdir(path.join(root,'sounds/reveal'),{recursive:true});
for(const variant of ['rain','generic']) {
 let out=path.join(root,`sounds/reveal/narration_${variant}.ogg`);
 execFileSync('ffmpeg',['-v','error','-y','-i',path.join(pack,`source-art/strength-reveal/narration-${variant}.mp3`),'-af','atempo=0.9,highpass=f=80,lowpass=f=5500,equalizer=f=180:t=q:w=1:g=3,aecho=0.8:0.88:85|145:0.12|0.07,loudnorm=I=-15:TP=-1.5:LRA=8','-ar','48000','-ac','1','-c:a','libvorbis','-q:a','5',out]);
 durations[variant]=Math.ceil(Number(execFileSync('ffprobe',['-v','error','-show_entries','format=duration','-of','csv=p=0',out]))*20)+6;
 const timing=JSON.parse(await fs.readFile(path.join(pack,`source-art/strength-reveal/narration-${variant}-timing.json`),'utf8'));
 let index=0;captions[variant]=timing.phrases.map(text=>{
  if(text.length>36)throw new Error('Caption exceeds the short action-bar width');
  let chars=0;const words=text.split(' ').map(token=>{
   const word=timing.words[index++];
   if(!word||word.text.toLowerCase()!==token.replace(/[.,!?]/g,'').toLowerCase())throw new Error(`Speech word mismatch: ${token}`);
   const from=chars;chars+=token.length;
   // Service offsets are 100ns units; match the final track's 0.9 tempo.
   const result={start:Math.round(word.offset/10000/.9),end:Math.round((word.offset+word.duration)/10000/.9),from,to:chars};chars++;return result;
  });return {text,words};
 });if(index!==timing.words.length)throw new Error('Unused speech word timestamps');
 sounds[`reveal.narration_${variant}`]={sounds:[{name:`viksstuff:reveal/narration_${variant}`,stream:true}]};
}
await write(path.join(root,'sounds.json'),sounds);
let config=`# Generated from encoded audio and service word boundaries; times in milliseconds.\nnarration-rain-ticks: ${durations.rain}\nnarration-generic-ticks: ${durations.generic}\n`;
for(const variant of ['rain','generic']){config+=`captions-${variant}:\n`;for(const phrase of captions[variant]){config+=`  - text: ${JSON.stringify(phrase.text)}\n    words:\n`;for(const word of phrase.words)config+=`      - {start: ${word.start}, end: ${word.end}, from: ${word.from}, to: ${word.to}}\n`;}}
await fs.writeFile('src/main/resources/strength-reveal.yml',config);
await fs.writeFile(path.join(pack,'source-art/strength-reveal/PROVENANCE.md'),'Logo supplied by user; transparent edit by image generation. Original gold key and vault geometry authored for this project. Narration generated using Microsoft Edge ThomasNeural via edge-tts 7.2.8, rate -17%, pitch -20Hz; final pacing, EQ and restrained echo processed with FFmpeg. Voice source documentation: https://github.com/rany2/edge-tts\nScript: Hi there, Rain Dynasty. I have been expecting you. You have come very far, and I have a gift for you. Take this key and enjoy.\nGeneric variant omits the name for test recipients.\n');
console.log('REVEAL ASSETS PASS: four original 3D models, transparent title logo, two neural narration tracks',durations);
