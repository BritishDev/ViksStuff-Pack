import sharp from 'sharp';
import {writeFile,mkdir} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
const root=fileURLToPath(new URL('../',import.meta.url));
const dir=`${root}overlay/assets/viksstuff/textures/training/aim`;
await mkdir(dir,{recursive:true});
const providers=[];
// Remove only the dark exterior connected to crop edges; preserve enclosed plaque interiors.
async function transparentCrop(input, region, width) {
 const {data,info}=await sharp(input).extract(region).ensureAlpha().raw().toBuffer({resolveWithObject:true});
 const seen=new Uint8Array(info.width*info.height),queue=[];
 const add=(x,y)=>{if(x<0||y<0||x>=info.width||y>=info.height)return;const i=y*info.width+x;if(seen[i])return;seen[i]=1;const k=i*4;if(region.width>1000 && x>80 && x<info.width-80 && y>45 && y<info.height-45)return;if(Math.max(data[k],data[k+1],data[k+2])>45)return;queue.push(i);};
 for(let x=0;x<info.width;x++){add(x,0);add(x,info.height-1);}for(let y=0;y<info.height;y++){add(0,y);add(info.width-1,y);}
 for(let q=0;q<queue.length;q++){const i=queue[q],x=i%info.width,y=Math.floor(i/info.width);data[i*4+3]=0;add(x-1,y);add(x+1,y);add(x,y-1);add(x,y+1);}
 return sharp(data,{raw:{width:info.width,height:info.height,channels:4}}).resize({width,kernel:'lanczos3'}).png();
}
for(const [n,col,top] of [[5,0,150],[4,1,150],[3,2,150],[2,0,560],[1,1,560],[0,2,560]]) {
 await (await transparentCrop(`${root}source-art/training/aim-countdown.png`,{left:col*512,top,width:512,height:260},256)).toFile(`${dir}/${n}.png`);
 providers.push({type:'bitmap',file:`viksstuff:training/aim/${n}.png`,height:14,ascent:11,chars:[String.fromCharCode(0xE300+n)]});
}
await (await transparentCrop(`${root}source-art/training/good-luck.png`,{left:8,top:350,width:1520,height:260},768)).toFile(`${dir}/select.png`);
providers.push({type:'bitmap',file:'viksstuff:training/aim/select.png',height:10,ascent:8,chars:['\uE306']});
await writeFile(`${root}overlay/assets/viksstuff/font/training_aim.json`,JSON.stringify({providers},null,2));

