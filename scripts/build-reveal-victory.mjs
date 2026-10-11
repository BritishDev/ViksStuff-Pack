import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {execFileSync} from 'node:child_process';
import {createHash} from 'node:crypto';

export async function buildRevealVictory() {
 const pack=path.resolve('ViksStuff-Pack'),source=path.join(pack,'source-art/strength-reveal/victory-original.mp3');
 const provenance=JSON.parse(await fs.readFile(path.join(pack,'source-art/strength-reveal/victory-source.json'),'utf8'));
 if(createHash('sha256').update(await fs.readFile(source)).digest('hex')!==provenance.sha256)throw new Error('Victory source hash differs from licensed source');
 const root=path.join(pack,'overlay/assets/viksstuff'),output=path.join(root,'sounds/reveal/victory.ogg');
 await fs.mkdir(path.dirname(output),{recursive:true});
 execFileSync('ffmpeg',['-v','error','-y','-i',source,'-af','highpass=f=55,lowpass=f=7500,aecho=0.8:0.88:90|190:0.10|0.05,loudnorm=I=-17:TP=-2:LRA=7,afade=t=in:d=0.025,afade=t=out:st=5.25:d=0.5','-ar','48000','-ac','1','-c:a','libvorbis','-q:a','5',output]);
 const file=path.join(root,'sounds.json'),sounds=JSON.parse(await fs.readFile(file,'utf8'));
 sounds['reveal.victory']={subtitle:'viksstuff.subtitle.reveal_victory',sounds:[{name:'viksstuff:reveal/victory',stream:false}]};
 await fs.writeFile(file,JSON.stringify(sounds,null,2)+'\n');
 const languageFile=path.join(root,'lang/en_us.json'),language=JSON.parse(await fs.readFile(languageFile,'utf8'));
 language['viksstuff.subtitle.reveal_victory']='Strength SMP victory fanfare';
 await fs.writeFile(languageFile,JSON.stringify(language,null,2)+'\n');
 console.log('CUSTOM VICTORY PASS: licensed CC0 fanfare, mono 48kHz Vorbis');
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url))await buildRevealVictory();
