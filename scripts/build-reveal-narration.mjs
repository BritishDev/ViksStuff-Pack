import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {execFileSync} from 'node:child_process';

export async function buildRevealNarration() {
 const pack=path.resolve('ViksStuff-Pack'),root=path.join(pack,'overlay/assets/viksstuff');
 const sounds=JSON.parse(await fs.readFile(path.join(root,'sounds.json'),'utf8'));
 const durations={},captions={};
 await fs.mkdir(path.join(root,'sounds/reveal'),{recursive:true});
 for(const variant of ['rain','generic']) {
  const out=path.join(root,`sounds/reveal/narration_${variant}.ogg`);
  execFileSync('ffmpeg',['-v','error','-y','-i',path.join(pack,`source-art/strength-reveal/narration-${variant}.mp3`),'-af','atempo=0.9,highpass=f=80,lowpass=f=5500,equalizer=f=180:t=q:w=1:g=3,aecho=0.8:0.88:85|145:0.12|0.07,loudnorm=I=-15:TP=-1.5:LRA=8,volume=4dB,alimiter=limit=0.841395:level=false:latency=true','-ar','48000','-ac','1','-c:a','libvorbis','-q:a','5',out]);
  durations[variant]=Math.ceil(Number(execFileSync('ffprobe',['-v','error','-show_entries','format=duration','-of','csv=p=0',out]))*20)+6;
  const timing=JSON.parse(await fs.readFile(path.join(pack,`source-art/strength-reveal/narration-${variant}-timing.json`),'utf8'));
  let index=0;
  captions[variant]=timing.phrases.map(text=>{
   if(text.length>36)throw new Error('Caption exceeds the short action-bar width');
   let chars=0;
   const words=text.split(' ').map(token=>{
    const word=timing.words[index++];
    if(!word||word.text.toLowerCase()!==token.replace(/[.,!?]/g,'').toLowerCase())throw new Error(`Speech word mismatch: ${token}`);
    const from=chars;chars+=token.length;
    // Service offsets are 100ns units; match the final track's 0.9 tempo.
    const result={start:Math.round(word.offset/10000/.9),end:Math.round((word.offset+word.duration)/10000/.9),from,to:chars};
    chars++;return result;
   });
   return {text,words};
  });
  if(index!==timing.words.length)throw new Error('Unused speech word timestamps');
  sounds[`reveal.narration_${variant}`]={sounds:[{name:`viksstuff:reveal/narration_${variant}`,stream:true}]};
 }
 // A separate quiet bed can duck independently of narration and stop at its last cue.
 const bed=path.join(root,'sounds/reveal/narration_bed.ogg');
 execFileSync('ffmpeg',['-v','error','-y','-stream_loop','-1','-i',path.join(root,'sounds/orb/hum.ogg'),'-t',String(Math.max(...Object.values(durations))/20),'-af','afade=t=in:d=0.3','-ar','48000','-ac','1','-c:a','libvorbis','-q:a','5',bed]);
 sounds['reveal.narration_bed']={sounds:[{name:'viksstuff:reveal/narration_bed',stream:true}]};
 await fs.writeFile(path.join(root,'sounds.json'),JSON.stringify(sounds,null,2)+'\n');
 let config=`# Generated from encoded audio and service word boundaries; times in milliseconds.\nnarration-rain-ticks: ${durations.rain}\nnarration-generic-ticks: ${durations.generic}\n`;
 for(const variant of ['rain','generic']){
  config+=`captions-${variant}:\n`;
  for(const phrase of captions[variant]){
   config+=`  - text: ${JSON.stringify(phrase.text)}\n    words:\n`;
   for(const word of phrase.words)config+=`      - {start: ${word.start}, end: ${word.end}, from: ${word.from}, to: ${word.to}}\n`;
  }
 }
 await fs.writeFile('src/main/resources/strength-reveal.yml',config);
 await fs.writeFile(path.join(pack,'source-art/strength-reveal/PROVENANCE.md'),`Logo supplied by user; transparent edit by image generation. Original gold key and vault geometry authored for this project. Narration generated using Microsoft Edge ThomasNeural via edge-tts 7.2.8, rate -17%, pitch -20Hz; final pacing, EQ and restrained echo processed with FFmpeg. The original -15 LUFS normalization is followed by a 4 dB gain and a -1.5 dB peak limiter with latency compensation, giving a modest audible boost without shifting the captions. Voice source documentation: https://github.com/rany2/edge-tts

Script:
Hello there Rain Dynasty
I have been expecting you
I have been watching you closely and have liked what I have seen.
I have a gift, but make sure to listen closely
[one-second pause]
Take this key, and when you see a vault, right click it

The pause is inserted into decoded audio and accounts for the final 0.9 tempo and the instruction's lead-in. Word timestamps include the pause and drive the gold action-bar captions. Generic variant omits the name for test recipients. A separate narration bed reuses the licensed orb hum at 0.24 playback volume, 20 percent below the normal 0.30 distant bed. The custom victory fanfare source and CC0 license are recorded in victory-source.json.
`);
 console.log('REVEAL NARRATION PASS: two neural tracks and synchronized captions',durations);
}

if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url))await buildRevealNarration();
