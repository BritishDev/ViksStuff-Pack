import fs from 'node:fs/promises';import path from 'node:path';import assert from 'node:assert/strict';import sharp from 'sharp';import {execFileSync}from'node:child_process';
const root=path.resolve('ViksStuff-Pack/overlay/assets/viksstuff');let elements=0;
for(const id of ['key','vault_frame','vault_door','vault_wheel']){
 let model=JSON.parse(await fs.readFile(path.join(root,`models/item/reveal/${id}.json`),'utf8'));
 let item=JSON.parse(await fs.readFile(path.join(root,`items/reveal/${id}.json`),'utf8'));assert.equal(item.model.model,`viksstuff:item/reveal/${id}`);
 assert.deepEqual(model.display.fixed.rotation,[0,180,0]);
 for(let e of model.elements){for(let axis=0;axis<3;axis++){assert.ok(e.from[axis]<e.to[axis]);assert.ok(e.from[axis]>=-16&&e.to[axis]<=32);}for(let face of Object.values(e.faces)){let t=model.textures[face.texture.slice(1)];await fs.access(path.join(root,'textures',t.slice('viksstuff:'.length)+'.png'));}elements++;}
}
const logo=await sharp(path.join(root,'textures/font/strength-logo.png')).ensureAlpha().raw().toBuffer();let transparent=0,opaque=0;for(let i=3;i<logo.length;i+=4){if(logo[i]===0)transparent++;if(logo[i]>200)opaque++;}assert.ok(transparent>logo.length/16);assert.ok(opaque>logo.length/16);
const font=JSON.parse(await fs.readFile(path.join(root,'font/reveal.json'),'utf8'));assert.equal(font.providers[0].chars[0],'\ue700\ue702\ue703\ue704');assert.equal(font.providers[0].height,28);assert.equal(font.providers[1].chars[0],'\ue701');assert.equal(font.providers[1].height,1024);
for(const provider of font.providers.filter(p=>p.type==='bitmap')){
 const size=await sharp(path.join(root,'textures',provider.file.slice('viksstuff:'.length))).metadata();
 const columns=[...provider.chars[0]].length,rows=provider.chars.length;
 assert.ok(provider.chars.every(row=>[...row].length===columns),'Bitmap glyph rows must have equal length');
 assert.equal(size.width%columns,0);assert.equal(size.height%rows,0);
 assert.ok(size.width/columns<=256&&size.height/rows<=256,'Native Minecraft font atlas silently rejects bitmap cells larger than 256x256; display height does not shrink the uploaded bitmap');
}
const spacing=font.providers.find(p=>p.type==='space');
const logoRaw=await sharp(path.join(root,'textures/font/strength-logo.png')).ensureAlpha().raw().toBuffer({resolveWithObject:true});
const cellWidth=logoRaw.info.width/4,scale=28/logoRaw.info.height;let logoAdvance=0;
for(let tile=0;tile<4;tile++){
 let actualWidth=0;for(let x=cellWidth-1;x>=0&&!actualWidth;x--)for(let y=0;y<logoRaw.info.height;y++)if(logoRaw.data[(y*logoRaw.info.width+tile*cellWidth+x)*4+3]){actualWidth=x+1;break;}
 const advance=Math.trunc(.5+actualWidth*scale)+1;assert.ok(advance<=32,'Individual logo tiles must retain safe font advances');logoAdvance+=advance;
 if(tile<3){const compensation=spacing.advances[String.fromCodePoint(0xe710+tile)];assert.equal(advance+compensation,cellWidth*scale,'Logo tiles must meet without seams or overlap');logoAdvance+=compensation;}
}
assert.ok(logoAdvance*4<320,'Composed logo must fit the minimum Minecraft title width');
const logoSize=await sharp(path.join(root,'textures/font/strength-logo.png')).metadata();assert.ok((logoSize.width/logoSize.height*font.providers[0].height+1)*4<320,'Logo must fit the minimum Minecraft GUI width as a main title');
const flash=await sharp(path.join(root,'textures/font/reveal-flash.png')).ensureAlpha().raw().toBuffer();assert.ok(flash.every(b=>b===255));
const variants=['rain','generic','rain_v2','generic_v2'];
const config=await fs.readFile('src/main/resources/strength-reveal.yml','utf8');for(let variant of variants){let file=path.join(root,`sounds/reveal/narration_${variant}.ogg`);let duration=Number(execFileSync('ffprobe',['-v','error','-show_entries','format=duration','-of','csv=p=0',file]));let ticks=Number(config.match(new RegExp(`narration-${variant}-ticks: (\\d+)`))[1]);assert.ok(ticks/20>=duration&&ticks/20<duration+1);assert.ok(duration>10&&duration<40);}
const welcome=JSON.parse(await fs.readFile(path.join(root,'font/reveal_welcome.json'),'utf8'));
const welcomeBitmap=welcome.providers.find(p=>p.type==='bitmap');
assert.equal(welcomeBitmap.file,'minecraft:font/ascii.png');assert.equal(welcomeBitmap.height,3);assert.equal(welcomeBitmap.ascent,2);
assert.equal(welcomeBitmap.chars.length,16);assert.ok(welcomeBitmap.chars.every(row=>row.length===16));
for(const letter of 'Welcomt')assert.equal(welcomeBitmap.chars[Math.floor(letter.charCodeAt(0)/16)][letter.charCodeAt(0)%16],letter);
assert.equal(welcome.providers.find(p=>p.type==='space').advances[' '],1.5);
const sounds=JSON.parse(await fs.readFile(path.join(root,'sounds.json'),'utf8'));
for(const id of ['victory','narration_bed']){
 assert.equal(sounds[`reveal.${id}`].sounds[0].name,`viksstuff:reveal/${id}`);
 const info=JSON.parse(execFileSync('ffprobe',['-v','error','-show_entries','stream=codec_name,sample_rate,channels:format=duration','-of','json',path.join(root,`sounds/reveal/${id}.ogg`)]));
 assert.equal(info.streams[0].codec_name,'vorbis');assert.equal(info.streams[0].sample_rate,'48000');assert.equal(info.streams[0].channels,1);
 const duration=Number(info.format.duration);const longestNarrationTicks=Math.max(...variants.map(variant=>Number(config.match(new RegExp(`narration-${variant}-ticks: (\\d+)`))[1])));assert.ok(id==='victory'?duration>5&&duration<7:Math.abs(duration-longestNarrationTicks/20)<.01);
}
let timedWords=0;
for(const variant of variants){
 const source=JSON.parse(await fs.readFile(`ViksStuff-Pack/source-art/strength-reveal/narration-${variant}-timing.json`,'utf8'));
 const expected=variant.endsWith('_v2')?['Hello',variant==='rain_v2'?'I have been expecting you Rain Dynasty':'I have been expecting you','I have been watching you, and I have liked what I have seen','I am here to congratulate you, but first you must do something for me','Take this key, and when you see a vault, right click it from where you are standing','Best of luck']:[variant==='rain'?'Hello there Rain Dynasty':'Hello there','I have been expecting you','I have been watching you closely and have liked what I have seen.','I have a gift, but make sure to listen closely','Take this key. When the vault appears, look at it and right click from where you are.'];
 assert.deepEqual(source.script_lines,expected);
 assert.equal(source.pause.after_line,4);assert.equal(source.pause.duration_ms,1000);assert.equal(source.pause.end_ms-source.pause.start_ms,1000);
 const section=config.split(`captions-${variant}:\n`)[1].split('captions-')[0];
 const phrases=[...section.matchAll(/  - text: (.+)\n/g)].map(m=>JSON.parse(m[1]));assert.deepEqual(phrases,source.phrases);assert.ok(phrases.every(p=>p.length<=36));
 const words=[...section.matchAll(/\{start: (\d+), end: (\d+), from: (\d+), to: (\d+)\}/g)];assert.equal(words.length,source.words.length);
 let previousEnd=-1;const duration=Number(execFileSync('ffprobe',['-v','error','-show_entries','format=duration','-of','csv=p=0',path.join(root,`sounds/reveal/narration_${variant}.ogg`)]))*1000;
 words.forEach((word,i)=>{const start=Number(word[1]),end=Number(word[2]),raw=source.words[i];assert.equal(start,Math.round(raw.offset/10000/.9));assert.equal(end,Math.round((raw.offset+raw.duration)/10000/.9));assert.ok(start>=previousEnd&&end>start&&end<duration);previousEnd=end;timedWords++;});
 const instructionPhrase=source.phrases.findIndex(phrase=>phrase.startsWith('Take this key'));
 assert.ok(instructionPhrase>0);
 const instructionIndex=source.phrases.slice(0,instructionPhrase).reduce((count,phrase)=>count+phrase.split(' ').length,0);
 assert.equal(Number(words[instructionIndex-1][2]),source.pause.start_ms);
 assert.equal(Number(words[instructionIndex][1]),source.pause.end_ms);
 // Verify the delivered OGG contains silence, allowing the existing short echo tail.
 const audio=execFileSync('ffmpeg',['-v','error','-i',path.join(root,`sounds/reveal/narration_${variant}.ogg`),'-f','f32le','-ac','1','-ar','48000','pipe:1'],{maxBuffer:16*1024*1024});
 const quietStart=Math.round((source.pause.start_ms+250)*48),quietEnd=Math.round((source.pause.end_ms-100)*48);
 assert.ok(quietEnd*4<audio.length);
 let peak=0;for(let i=quietStart;i<quietEnd;i++)peak=Math.max(peak,Math.abs(audio.readFloatLE(i*4)));
 assert.ok(peak<0.001,`${variant}: requested pause must be audible silence`);
}
console.log(`REVEAL VALIDATION PASS: 4 models, ${elements} elements, transparent logo, valid font, exact script, encoded one-second pauses, ${timedWords} synchronized word timestamps.`);
