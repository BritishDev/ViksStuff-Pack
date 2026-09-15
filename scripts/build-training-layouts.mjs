import sharp from 'sharp';
import {mkdir,readFile,writeFile,copyFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
const root=fileURLToPath(new URL('../',import.meta.url)),base=`${root}overlay/assets/viksstuff`,preview=`${root}previews/training`;
const names=['Classic Medallions','Segmented Meter','Two-Row Scoreboard','Arc of Diamonds','Split Wings','Hanging Pennants','Ticket Strip'];
const svg=body=>`<svg xmlns="http://www.w3.org/2000/svg" width="720" height="144"><defs><linearGradient id="r" x2="0" y2="1"><stop stop-color="#ff6572"/><stop offset="1" stop-color="#650b20"/></linearGradient></defs>${body}</svg>`;
const path=(d,fill='#10080c')=>`<path d="${d}" fill="${fill}" stroke="url(#r)" stroke-width="3"/>`;
function frame(id){
 if(id===2)return path('M 4 40 H 686 V 52 H 716 V 92 H 686 V 104 H 4 Z')+'<path d="M 14 33 H 677 M 14 112 H 677" stroke="#ff344f" stroke-width="2"/>';
 if(id===3)return path('M 10 7 H 710 V 137 H 10 Z')+'<path d="M 14 72 H 706" stroke="#a62338" stroke-width="3"/>';
 if(id===4)return '<path d="M 14 108 Q 360 -65 706 108" fill="none" stroke="#a31b32" stroke-width="6"/>';
 if(id===5)return path('M 4 26 H 303 L 342 72 303 118 H 4 L 24 72 Z')+path('M 716 26 H 417 L 378 72 417 118 H 716 L 696 72 Z')+path('M 360 37 L 392 72 360 107 328 72 Z','#8e1128');
 if(id===6)return '<path d="M 8 16 H 712" stroke="#ff5268" stroke-width="7"/><circle cx="9" cy="16" r="6" fill="#ff8591"/><circle cx="711" cy="16" r="6" fill="#ff8591"/>';
 return path('M 5 25 H 715 V 51 Q 686 72 715 93 V 119 H 5 V 93 Q 34 72 5 51 Z')+'<path d="M 38 34 H 682 M 38 110 H 682" stroke="#86152a" stroke-width="2" stroke-dasharray="6 5"/>';
}
function tile(id,i,state){
 const color=state===1?'#41f591':state===2?'#ff425c':'#231019';
 let x,y,w,h,body;
 if(id===2){x=20+i*66;y=50;w=58;h=44;body=path(`M ${x+7} ${y} H ${x+w} L ${x+w-7} ${y+h} H ${x} Z`,color);}
 else if(id===3){x=22+(i%5)*138;y=i<5?14:80;w=124;h=50;body=path(`M ${x} ${y} H ${x+w} V ${y+h} H ${x} Z`)+`<text x="${x+15}" y="${y+31}" fill="#b55566" font-family="Arial" font-size="16">${i+1}</text>`;}
 else if(id===4){x=13+i*70;y=55-48*Math.sin(i*Math.PI/9);w=64;h=64;body=path(`M ${x+32} ${y} L ${x+64} ${y+32} ${x+32} ${y+64} ${x} ${y+32} Z`);}
 else if(id===5){x=i<5?33+i*54:423+(i-5)*54;y=46;w=42;h=52;body=path(`M ${x} ${y} H ${x+w} V ${y+h-12} L ${x+w/2} ${y+h} ${x} ${y+h-12} Z`);}
 else if(id===6){x=18+i*69;y=27;w=59;h=i%2?96:80;body=`<path d="M ${x+12} 16 V 27 M ${x+w-12} 16 V 27" stroke="#ff7182" stroke-width="3"/>`+path(`M ${x} ${y} H ${x+w} V ${y+h-16} L ${x+w/2} ${y+h} ${x} ${y+h-16} Z`);}
 else{x=40+i*64;y=42;w=56;h=59;body=`<path d="M ${x-4} 32 V 112" stroke="#751229" stroke-dasharray="3 4"/>`+`<text x="${x+w/2}" y="${y+12}" text-anchor="middle" font-family="Arial" font-size="13" fill="#cf6576">${String(i+1).padStart(2,'0')}</text>`;}
 if(id!==2){const cx=x+w/2,cy=y+h*.53,sz=Math.min(w,h)*.22;body+=state===1?`<path d="M ${cx-sz} ${cy} l ${sz*.7} ${sz*.7} ${sz*1.5} ${-sz*1.6}" fill="none" stroke="${color}" stroke-width="5" stroke-linecap="round"/>`:state===2?`<path d="M ${cx-sz} ${cy-sz} l ${sz*2} ${sz*2} M ${cx+sz} ${cy-sz} l ${-sz*2} ${sz*2}" stroke="${color}" stroke-width="5"/>`:`<circle cx="${cx}" cy="${cy}" r="4" fill="#984354"/>`;}
 return body;
}
const advance=async(buffer)=>{const {data,info}=await sharp(buffer).ensureAlpha().raw().toBuffer({resolveWithObject:true});let right=0;for(let y=0;y<info.height;y++)for(let x=0;x<info.width;x++)if(data[(y*info.width+x)*4+3])right=Math.max(right,x+1);return Math.floor(right/4+.5)+1;};
for(let id=2;id<=7;id++){
 const dir=`${base}/textures/training/d${id}`;await mkdir(dir,{recursive:true});
 const bg=await sharp(Buffer.from(svg(frame(id)))).png().toBuffer();await writeFile(`${dir}/layout.png`,bg);
 const providers=[{type:'bitmap',file:`viksstuff:training/d${id}/layout.png`,height:36,ascent:4,chars:['\uE106']}];
 const advances={'\uE107':-await advance(bg),'\uE108':180};
 for(let i=0;i<10;i++)for(let state=0;state<3;state++){
  const bytes=await sharp(Buffer.from(svg(tile(id,i,state)))).png().toBuffer();await writeFile(`${dir}/slot_${i}_${state}.png`,bytes);
  providers.push({type:'bitmap',file:`viksstuff:training/d${id}/slot_${i}_${state}.png`,height:36,ascent:4,chars:[String.fromCharCode(0xE200+i*3+state)]});advances[String.fromCharCode(0xE240+i*3+state)]=-await advance(bytes);
 }
 providers.push({type:'space',advances});await writeFile(`${base}/font/training_d${id}_clutch.json`,JSON.stringify({providers},null,2));
 for(const f of ['success','failed'])await copyFile(`${base}/textures/training/${f}.png`,`${dir}/${f}.png`);
 await writeFile(`${base}/font/training_d${id}_result.json`,await readFile(`${base}/font/training_result.json`));
 await sharp(Buffer.from(svg(frame(id)+Array.from({length:10},(_,i)=>tile(id,i,i<5?1:i<7?2:0)).join('')))).png().toFile(`${preview}/bar${id}.png`);
}
let rows='';for(let id=1;id<=7;id++){const b64=(await readFile(`${preview}/bar${id}.png`)).toString('base64');rows+=`<text x="24" y="${(id-1)*195+30}" fill="white" font-family="Arial" font-size="22">${id}. ${names[id-1]}</text><image href="data:image/png;base64,${b64}" x="24" y="${(id-1)*195+45}" width="720" height="144"/>`;}
await sharp(Buffer.from(`<svg xmlns="http://www.w3.org/2000/svg" width="768" height="1370"><rect width="768" height="1370" fill="#121219"/>${rows}</svg>`)).png().toFile(`${preview}/seven-designs.png`);
await writeFile(`${preview}/index.html`,`<!doctype html><meta charset="utf-8"><title>Seven layouts</title><body style="background:#121219;color:white;font:20px system-ui"><h1>Seven different layouts</h1><p>Switch live: /training mode design 1 through 7. Success and failure artwork is identical for every mode.</p><img style="max-width:100%" src="seven-designs.png"></body>`);
console.log('Built six structurally different layouts; preserved classic and shared outcome artwork.');
