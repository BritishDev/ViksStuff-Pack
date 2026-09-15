import sharp from 'sharp';
import {writeFile,mkdir} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
const root=fileURLToPath(new URL('../',import.meta.url));
const dir=`${root}overlay/assets/viksstuff/textures/training/aim`;
await mkdir(dir,{recursive:true});
const providers=[];
for(const [n,col,top] of [[5,0,150],[4,1,150],[3,2,150],[2,0,560],[1,1,560],[0,2,560]]) {
 await sharp(`${root}source-art/training/aim-countdown.png`).extract({left:col*512,top,width:512,height:260}).resize(256,130,{kernel:'lanczos3'}).png().toFile(`${dir}/${n}.png`);
 providers.push({type:'bitmap',file:`viksstuff:training/aim/${n}.png`,height:14,ascent:11,chars:[String.fromCharCode(0xE300+n)]});
}
await sharp(`${root}source-art/training/good-luck.png`).extract({left:8,top:350,width:1520,height:260}).resize({width:768,kernel:'lanczos3'}).png().toFile(`${dir}/select.png`);
providers.push({type:'bitmap',file:'viksstuff:training/aim/select.png',height:16,ascent:13,chars:['\uE306']});
await writeFile(`${root}overlay/assets/viksstuff/font/training_aim.json`,JSON.stringify({providers},null,2));

