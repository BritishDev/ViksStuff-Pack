import fs from 'node:fs/promises';
import path from 'node:path';
import {buildRevealNarration} from './build-reveal-narration.mjs';
import sharp from 'sharp';
import {buildRevealFont} from './build-reveal-font.mjs';
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
 // ItemDisplayRenderer adds a Y half-turn; cancel it before the authored geometry.
 await write(path.join(root,`models/item/reveal/${id}.json`),{ambientocclusion:false,textures:{gold:'viksstuff:item/reveal/gold',steel:'viksstuff:item/reveal/steel',gem:'viksstuff:item/reveal/gem',particle:'viksstuff:item/reveal/gold'},elements,display:{fixed:{rotation:[0,180,0],translation:[0,0,0],scale:[1,1,1]},gui:{rotation:[0,0,-35],scale:[.9,.9,.9]},firstperson_righthand:{rotation:[0,-90,20],translation:[1,2,1],scale:[.9,.9,.9]},thirdperson_righthand:{rotation:[0,-90,0],translation:[0,2,0],scale:[.8,.8,.8]}}});
 await write(path.join(root,`items/reveal/${id}.json`),{model:{type:'minecraft:model',model:`viksstuff:item/reveal/${id}`}});
}
await buildRevealFont();
await buildRevealNarration();
console.log('REVEAL ASSETS PASS: four original 3D models, transparent title logo, narration');
