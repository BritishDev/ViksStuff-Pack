// Rebuild the licensed menacing orb sounds from the preserved CC0 source.
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {execFileSync} from 'node:child_process';
import {createHash} from 'node:crypto';
const repo=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const source=path.join(repo,'source-art/orb-audio/dark-intro-original.ogg');
if(createHash('sha256').update(await fs.readFile(source)).digest('hex')!=='7bfe029fcc5cc73688e4b6ca13b8845fe80a4c73d775e5d2c52af30e7a5d75b0')throw new Error('Orb sound source hash mismatch');
const root=path.join(repo,'overlay/assets/viksstuff');
const directory=path.join(root,'sounds/orb');await fs.mkdir(directory,{recursive:true});
for(const [id,start,duration] of [['reveal',0,14],['hum',4,7.5]]) {
    const filter=`atrim=start=${start},asetpts=PTS-STARTPTS,asetrate=36162,aresample=48000,highpass=f=35,lowpass=f=4000,equalizer=f=80:t=q:w=1:g=5,loudnorm=I=-20:TP=-2:LRA=7,atrim=duration=${duration},afade=t=in:d=0.15,afade=t=out:st=${duration-.45}:d=0.45`;
    execFileSync('ffmpeg',['-v','error','-y','-i',source,'-af',filter,'-ar','48000','-ac','1','-c:a','libvorbis','-q:a','5',path.join(directory,id+'.ogg')]);
}
const soundsPath=path.join(root,'sounds.json');const sounds=JSON.parse(await fs.readFile(soundsPath,'utf8'));
sounds['orb.reveal']={subtitle:'viksstuff.subtitle.orb_reveal',sounds:[{name:'viksstuff:orb/reveal',stream:false,attenuation_distance:64}]};
sounds['orb.hum']={sounds:[{name:'viksstuff:orb/hum',stream:false,attenuation_distance:48}]};
await fs.writeFile(soundsPath,JSON.stringify(sounds,null,2)+'\n');
const langPath=path.join(root,'lang/en_us.json');let lang={};try{lang=JSON.parse(await fs.readFile(langPath,'utf8'));}catch(e){if(e.code!=='ENOENT')throw e;}
lang['viksstuff.subtitle.orb_reveal']='Orb energy awakens';await fs.mkdir(path.dirname(langPath),{recursive:true});await fs.writeFile(langPath,JSON.stringify(lang,null,2)+'\n');
console.log('ORB SOUND PASS: licensed 14-second reveal and 7.5-second ambient pulse, mono 48 kHz Vorbis.');
