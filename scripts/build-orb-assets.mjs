// Original deterministic voxel geometry and animated emissive materials.
// No vanilla textures/shaders are replaced. Re-run before build-pack.ps1.
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import sharp from 'sharp';
import {execFileSync} from 'node:child_process';
import os from 'node:os';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../overlay/assets/viksstuff');
const json = async (file, value) => { const target=path.join(root,file); await fs.mkdir(path.dirname(target),{recursive:true}); await fs.writeFile(target,JSON.stringify(value,null,2)+'\n'); };
const cube=(from,to,texture='energy',emission=15)=>({from,to,shade:false,light_emission:emission,faces:Object.fromEntries(['up','down','north','south','east','west'].map(face=>[face,{texture:'#'+texture,uv:[0,0,16,16]}]))});
const pbr=async(dir,id,albedo,width,height,smoothness)=>{
  const spec=Buffer.alloc(albedo.length),normal=Buffer.alloc(albedo.length);
  for(let k=0;k<albedo.length;k+=4){
    spec[k]=smoothness;spec[k+1]=10;spec[k+2]=0;
    spec[k+3]=albedo[k+3]===0?0:Math.min(254,Math.round(Math.max(albedo[k],albedo[k+1],albedo[k+2])*.88));
    normal[k]=128;normal[k+1]=128;normal[k+2]=255;normal[k+3]=255;
  }
  for(const [suffix,bytes] of [['_s',spec],['_n',normal]])await sharp(bytes,{raw:{width,height,channels:4}}).png().toFile(path.join(dir,id+suffix+'.png'));
};
const models={};
// A stepped ellipsoid, not three overlapping cubes: 11 bands form a luminous sphere.
models.core=Array.from({length:11},(_,i)=>{const y=-5.5+i, r=Math.sqrt(Math.max(0,36-(y+.5)**2));return cube([8-r,8+y,8-r],[8+r,9+y,8+r]);});
models.shell=[];
for(let i=0;i<72;i++){const y=1-2*(i+.5)/72,a=i*2.3999632297,r=Math.sqrt(1-y*y),p=[8+6*r*Math.cos(a),8+6*y,8+6*r*Math.sin(a)];models.shell.push(cube(p.map(v=>v-.5),p.map(v=>v+.5)));}
models.ring=[];
for(let i=0;i<64;i++){const a=i*Math.PI/32,x=8+6.4*Math.cos(a),z=8+6.4*Math.sin(a);models.ring.push(cube([x-.34,7.78,z-.34],[x+.34,8.22,z+.34]));}
for(let i=0;i<12;i++){const a=i*Math.PI/6,x=8+7.1*Math.cos(a),z=8+7.1*Math.sin(a);models.ring.push(cube([x-.20,7.68,z-.20],[x+.20,8.32,z+.20],'metal',4));}
models.node=[cube([5,5,5],[11,11,11]),cube([6,3.5,6],[10,12.5,10],'metal',6)];
models.shard=[cube([6.6,3,6.6],[9.4,13,9.4]),cube([7.1,1,7.1],[8.9,15,8.9]),cube([5.3,6,5.3],[10.7,10,10.7],'metal',6)];
models.beam=[cube([7.72,0,7.72],[8.28,16,8.28])];
models.sigil=[{from:[0,7.99,0],to:[16,8.01,16],shade:false,light_emission:15,faces:{up:{texture:'#sigil',uv:[0,0,16,16]},down:{texture:'#sigil',uv:[0,0,16,16]}}}];
for(const color of ['white','red']) {
  const width=32,frames=16,height=width*frames,bytes=Buffer.alloc(width*height*4);
  const rgb=color==='white'?[242,247,255]:[255,36,61];
  for(let f=0;f<frames;f++)for(let y=0;y<width;y++)for(let x=0;x<width;x++){
    const seam=x%8===0||y%8===0,flow=(x+y-f*2+64)%16<2;
    const gain=flow?1:seam?.72:.42+.12*Math.sin((x-y)*.5+f*Math.PI/8);
    const k=((f*width+y)*width+x)*4;
    for(let c=0;c<3;c++)bytes[k+c]=Math.round(rgb[c]*gain);bytes[k+3]=249; // Reserved orb shader tag.
  }
  const textures=path.join(root,'textures/item/orb');await fs.mkdir(textures,{recursive:true});
  await sharp(bytes,{raw:{width,height,channels:4}}).png().toFile(path.join(textures,`energy_${color}.png`));
  await pbr(textures,`energy_${color}`,bytes,width,height,170);
  await json(`textures/item/orb/energy_${color}.png.mcmeta`,{animation:{frametime:2,interpolate:true,width:32,height:32}});
  for(const suffix of ['_s','_n'])await json(`textures/item/orb/energy_${color}${suffix}.png.mcmeta`,{animation:{frametime:2,interpolate:true,width:32,height:32}});
  const metal=Buffer.alloc(16*16*4);
  for(let y=0;y<16;y++)for(let x=0;x<16;x++){const k=(y*16+x)*4,edge=x<2||y<2||x>13||y>13;for(let c=0;c<3;c++)metal[k+c]=edge?rgb[c]:Math.round(rgb[c]*.22);metal[k+3]=249;}
  await sharp(metal,{raw:{width:16,height:16,channels:4}}).png().toFile(path.join(textures,`metal_${color}.png`));
  await pbr(textures,`metal_${color}`,metal,16,16,220);
  const w=128,sigil=Buffer.alloc(w*w*4);
  for(let y=0;y<w;y++)for(let x=0;x<w;x++){const dx=(x+.5-w/2)/(w/2),dy=(y+.5-w/2)/(w/2),r=Math.hypot(dx,dy),a=Math.atan2(dy,dx);
    const rings=Math.abs(r-.88)<.013||Math.abs(r-.70)<.009||Math.abs(r-.46)<.008;
    const ticks=r>.74&&r<.82&&Math.abs(Math.sin(a*24))<.13;
    const lattice=r<.60&&r>.20&&(Math.abs(dx)<.012||Math.abs(dy)<.012||Math.abs(dx-dy)<.017||Math.abs(dx+dy)<.017);
    const k=(y*w+x)*4;for(let c=0;c<3;c++)sigil[k+c]=rgb[c];sigil[k+3]=(rings||ticks||lattice)?249:0;
  }
  await sharp(sigil,{raw:{width:w,height:w,channels:4}}).png().toFile(path.join(textures,`sigil_${color}.png`));
  await pbr(textures,`sigil_${color}`,sigil,w,w,100);
  for(const [model,elements] of Object.entries(models)){
    const id=`orb/${model}_${color}`;
    await json(`models/item/${id}.json`,{ambientocclusion:false,textures:{energy:`viksstuff:item/orb/energy_${color}`,metal:`viksstuff:item/orb/metal_${color}`,sigil:`viksstuff:item/orb/sigil_${color}`,particle:`viksstuff:item/orb/energy_${color}`},display:{fixed:{rotation:[0,0,0],translation:[0,0,0],scale:[1,1,1]}},elements});
    await json(`items/${id}.json`,{model:{type:'minecraft:model',model:`viksstuff:item/${id}`}});
  }
}
// Original sound design: quiet harmonic idle, rising charge, and resonant release.
const soundsFile=path.join(root,'sounds.json');
const sounds=JSON.parse(await fs.readFile(soundsFile,'utf8'));
const soundDir=path.join(root,'sounds/orb');await fs.mkdir(soundDir,{recursive:true});
const temp=await fs.mkdtemp(path.join(os.tmpdir(),'viks-orb-audio-'));
try {
  for(const [id,duration] of [['hum',4],['charge',3],['release',2.5]]) {
    const rate=24000,count=Math.round(rate*duration),wav=Buffer.alloc(44+count*2);
    wav.write('RIFF');wav.writeUInt32LE(36+count*2,4);wav.write('WAVEfmt ',8);wav.writeUInt32LE(16,16);
    wav.writeUInt16LE(1,20);wav.writeUInt16LE(1,22);wav.writeUInt32LE(rate,24);wav.writeUInt32LE(rate*2,28);
    wav.writeUInt16LE(2,32);wav.writeUInt16LE(16,34);wav.write('data',36);wav.writeUInt32LE(count*2,40);
    let phase=0,seed=8827;
    for(let i=0;i<count;i++) {
      const t=i/rate,u=t/duration,fade=Math.min(1,t/.12)*Math.min(1,(duration-t)/.35);
      const frequency=id==='charge'?65+210*u*u:id==='release'?130:55;
      phase+=2*Math.PI*frequency/rate;
      seed=(Math.imul(seed,1664525)+1013904223)>>>0;const noise=seed/4294967296*2-1;
      let value=id==='release'?(Math.sin(phase)+.35*Math.sin(phase*1.5)+.2*Math.sin(phase*3))*Math.exp(-t*1.4):
        (Math.sin(phase)+.25*Math.sin(phase*2)+.10*Math.sin(phase*3))*(id==='charge'?.3+.7*u:.8+.1*Math.sin(t*2));
      if(id==='charge')value+=noise*.07*u;
      wav.writeInt16LE(Math.round(Math.max(-1,Math.min(1,value*.35*fade))*32767),44+i*2);
    }
    const source=path.join(temp,id+'.wav');await fs.writeFile(source,wav);
    execFileSync('ffmpeg',['-v','error','-y','-i',source,'-c:a','libvorbis','-q:a','4',path.join(soundDir,id+'.ogg')]);
    sounds['orb.'+id]={sounds:[{name:'viksstuff:orb/'+id,stream:false,attenuation_distance:24}]};
  }
  await json('sounds.json',sounds);
} finally {await fs.rm(temp,{recursive:true,force:true});}
console.log('Generated 14 orb models, animated emissive/PBR materials and three original sounds.');
