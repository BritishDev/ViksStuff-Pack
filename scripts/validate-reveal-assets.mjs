import fs from 'node:fs/promises';import path from 'node:path';import assert from 'node:assert/strict';import sharp from 'sharp';import {execFileSync}from'node:child_process';
const root=path.resolve('ViksStuff-Pack/overlay/assets/viksstuff');let elements=0;
for(const id of ['key','vault_frame','vault_door','vault_wheel']){
 let model=JSON.parse(await fs.readFile(path.join(root,`models/item/reveal/${id}.json`),'utf8'));
 let item=JSON.parse(await fs.readFile(path.join(root,`items/reveal/${id}.json`),'utf8'));assert.equal(item.model.model,`viksstuff:item/reveal/${id}`);
 for(let e of model.elements){for(let axis=0;axis<3;axis++){assert.ok(e.from[axis]<e.to[axis]);assert.ok(e.from[axis]>=-16&&e.to[axis]<=32);}for(let face of Object.values(e.faces)){let t=model.textures[face.texture.slice(1)];await fs.access(path.join(root,'textures',t.slice('viksstuff:'.length)+'.png'));}elements++;}
}
const logo=await sharp(path.join(root,'textures/font/strength-logo.png')).ensureAlpha().raw().toBuffer();let transparent=0,opaque=0;for(let i=3;i<logo.length;i+=4){if(logo[i]===0)transparent++;if(logo[i]>200)opaque++;}assert.ok(transparent>logo.length/16);assert.ok(opaque>logo.length/16);
const font=JSON.parse(await fs.readFile(path.join(root,'font/reveal.json'),'utf8'));assert.equal(font.providers[0].chars[0],'\ue700');assert.equal(font.providers[0].height,48);
const config=await fs.readFile('src/main/resources/strength-reveal.yml','utf8');for(let variant of ['rain','generic']){let file=path.join(root,`sounds/reveal/narration_${variant}.ogg`);let duration=Number(execFileSync('ffprobe',['-v','error','-show_entries','format=duration','-of','csv=p=0',file]));let ticks=Number(config.match(new RegExp(`narration-${variant}-ticks: (\\d+)`))[1]);assert.ok(ticks/20>=duration&&ticks/20<duration+1);assert.ok(duration>10&&duration<30);}
let timedWords=0;
for(const variant of ['rain','generic']){
 const source=JSON.parse(await fs.readFile(`ViksStuff-Pack/source-art/strength-reveal/narration-${variant}-timing.json`,'utf8'));
 const section=config.split(`captions-${variant}:\n`)[1].split('captions-')[0];
 const phrases=[...section.matchAll(/  - text: (.+)\n/g)].map(m=>JSON.parse(m[1]));assert.deepEqual(phrases,source.phrases);assert.ok(phrases.every(p=>p.length<=36));
 const words=[...section.matchAll(/\{start: (\d+), end: (\d+), from: (\d+), to: (\d+)\}/g)];assert.equal(words.length,source.words.length);
 let previousEnd=-1;const duration=Number(execFileSync('ffprobe',['-v','error','-show_entries','format=duration','-of','csv=p=0',path.join(root,`sounds/reveal/narration_${variant}.ogg`)]))*1000;
 words.forEach((word,i)=>{const start=Number(word[1]),end=Number(word[2]),raw=source.words[i];assert.equal(start,Math.round(raw.offset/10000/.9));assert.equal(end,Math.round((raw.offset+raw.duration)/10000/.9));assert.ok(start>=previousEnd&&end>start&&end<duration);previousEnd=end;timedWords++;});
}
console.log(`REVEAL VALIDATION PASS: 4 models, ${elements} elements, transparent logo, valid font, duration-aligned narration, ${timedWords} synchronized word timestamps.`);
