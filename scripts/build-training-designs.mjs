import sharp from 'sharp';
import {mkdir,readFile,writeFile,copyFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
const root=fileURLToPath(new URL('../',import.meta.url));
const base=`${root}overlay/assets/viksstuff`;
const preview=`${root}previews/training`;
await mkdir(preview,{recursive:true});
const themes=[
 ['Crimson Classic','#ff3046','#650916','#090508','round'],
 ['Obsidian Edge','#ff7045','#871f15','#111016','cut'],
 ['Royal Gold','#ffdc76','#936220','#17100b','royal'],
 ['Arctic Glass','#7deeff','#166087','#061a29','hex'],
 ['Emerald Circuit','#61ffad','#146345','#061710','circuit'],
 ['Violet Orbit','#d49cff','#642fa6','#150b25','orbit'],
 ['Pearl Studio','#a92543','#69182e','#f4ece7','pearl']
];
const svg=(w,h,body)=>`<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}">${body}</svg>`;
function plate(w,h,t,inner='') {
 const [name,a,b,bg,shape]=t;
 const defs=`<defs><linearGradient id="g" x2="0" y2="1"><stop stop-color="${a}"/><stop offset="1" stop-color="${b}"/></linearGradient></defs>`;
 let border;
 if(shape==='cut') border=`<path d="M 12 2 H ${w-12} L ${w-2} 12 V ${h-12} L ${w-12} ${h-2} H 12 L 2 ${h-12} V 12 Z" fill="${bg}" stroke="url(#g)" stroke-width="3"/>`;
 else if(shape==='hex') border=`<path d="M 16 2 H ${w-16} L ${w-2} ${h/2} L ${w-16} ${h-2} H 16 L 2 ${h/2} Z" fill="${bg}" stroke="url(#g)" stroke-width="3"/>`;
 else border=`<rect x="2" y="2" width="${w-4}" height="${h-4}" rx="${shape==='orbit'?h/2:shape==='circuit'?3:12}" fill="${bg}" stroke="url(#g)" stroke-width="3"/>`;
 let deco='';
 if(shape==='royal') deco=`<path d="M ${w/2-16} 9 l 6 8 10 -12 10 12 6 -8" fill="none" stroke="${a}" stroke-width="2"/>`;
 if(shape==='circuit') deco=`<path d="M 10 ${h-10} V 10 H 26 M ${w-10} 10 v ${h-20} h -16" fill="none" stroke="${a}" stroke-width="2"/><circle cx="26" cy="10" r="3" fill="${a}"/>`;
 if(shape==='orbit') deco=`<ellipse cx="${w/2}" cy="${h/2}" rx="${w/2-9}" ry="${h/2-7}" fill="none" stroke="${a}" stroke-opacity=".25"/>`;
 if(shape==='round') deco=`<rect x="7" y="7" width="${w-14}" height="${h-14}" rx="8" fill="none" stroke="${b}"/>`;
 if(shape==='pearl') deco=`<path d="M 17 ${h-8} H ${w-17}" stroke="${a}" stroke-width="2"/>`;
 return svg(w,h,defs+border+deco+inner);
}
const text=(w,h,label,t,size)=>`<text x="${w/2}" y="${h/2}" dominant-baseline="central" text-anchor="middle" font-family="Arial, sans-serif" font-size="${size}" font-weight="800" letter-spacing="1" fill="${t[4]==='pearl'?'#53182b':t[1]}" stroke="${t[4]==='pearl'?'none':t[2]}" stroke-width=".6" paint-order="stroke">${label}</text>`;
const png=async(path,xml)=>sharp(Buffer.from(xml)).png().toFile(path);
const provider=(file,char,height,ascent)=>({type:'bitmap',file:`viksstuff:training/${file}.png`,height,ascent,chars:[char]});
for(let i=0;i<themes.length;i++) {
 const id=i+1,t=themes[i],dir=`${base}/textures/training/d${id}`;
 await mkdir(dir,{recursive:true});
 if(id===1) for(const file of ['frame','pending','hit','miss','success','failed']) await copyFile(`${base}/textures/training/${file}.png`,`${dir}/${file}.png`);
 else {
  await png(`${dir}/frame.png`,plate(720,88,t));
  for(const state of ['pending','hit','miss']) {
   const color=state==='hit'?'#5dff96':state==='miss'?'#ff4b67':t[1];
   const symbol=state==='hit'?`<path d="M 32 66 L 54 86 L 98 37" fill="none" stroke="${color}" stroke-width="11" stroke-linecap="round" stroke-linejoin="round"/>`:state==='miss'?`<path d="M 40 40 L 88 88 M 88 40 L 40 88" stroke="${color}" stroke-width="10" stroke-linecap="round"/>`:'';
   await png(`${dir}/${state}.png`,plate(128,128,t,symbol));
  }
  for(const [name,label] of [['success','SUCCESS'],['failed','FAILED']]) {
   const semantic=[...t];semantic[1]=name==='success'?'#5dff96':'#ff5d77';
   await png(`${dir}/${name}.png`,plate(320,80,semantic,text(320,80,label,semantic,38)));
  }
 }
 for(let n=0;n<=10;n++) await png(`${dir}/score_${n}.png`,plate(320,80,t,text(320,80,`${n} / 10`,t,48)));
 for(const [j,label] of ['BELOW AVERAGE','AVERAGE','ABOVE AVERAGE'].entries()) await png(`${dir}/grade_${j}.png`,plate(360,64,t,text(360,64,label,t,27)));
 const key=id===1?'training':'training_d'+id;
 if(id>1) {
  await writeFile(`${base}/font/${key}_clutch.json`,JSON.stringify({providers:[provider(`d${id}/pending`,'\uE103',16,1),provider(`d${id}/hit`,'\uE104',16,1),provider(`d${id}/miss`,'\uE105',16,1),provider(`d${id}/frame`,'\uE106',22,4),{type:'space',advances:{'\uE107':-176,'\uE108':5}}]},null,2));
  await writeFile(`${base}/font/${key}_result.json`,JSON.stringify({providers:[provider(`d${id}/failed`,'\uE101',8,6),provider(`d${id}/success`,'\uE102',8,6)]},null,2));
 }
 for(const [suffix,height,ascent] of [['score',14,11],['compact_score',8,6],['grade',8,6]]) {
  const isGrade=suffix==='grade',count=isGrade?3:11;
  await writeFile(`${base}/font/${key}_${suffix}.json`,JSON.stringify({providers:Array.from({length:count},(_,n)=>provider(`d${id}/${isGrade?'grade':'score'}_${n}`,String.fromCharCode((isGrade?0xE130:0xE120)+n),height,ascent))},null,2));
 }
 const parts=[{input:await sharp(`${dir}/frame.png`).png().toBuffer(),left:0,top:0}];
 for(let j=0;j<10;j++) parts.push({input:await sharp(`${dir}/${j<5?'hit':j<7?'miss':'pending'}.png`).resize(64,64).toBuffer(),left:20+j*68,top:12});
 await sharp({create:{width:720,height:88,channels:4,background:'#111118'}}).composite(parts).png().toFile(`${preview}/bar${id}.png`);
}
const embed=async(path)=>`data:image/png;base64,${(await readFile(path)).toString('base64')}`;
let rows='';
for(let i=0;i<7;i++) {
 const id=i+1,dir=`${base}/textures/training/d${id}`,y=i*245;
 rows+=`<g transform="translate(0 ${y})"><text x="30" y="35" fill="#eeeeff" font-family="Arial" font-size="24">${id}. ${themes[i][0]}</text><image href="${await embed(`${preview}/bar${id}.png`)}" x="30" y="55" width="720" height="88"/><image href="${await embed(`${dir}/success.png`)}" x="30" y="161" width="200" height="50"/><image href="${await embed(`${dir}/failed.png`)}" x="245" y="161" width="200" height="50"/><image href="${await embed(`${dir}/score_7.png`)}" x="790" y="55" width="320" height="80"/><image href="${await embed(`${dir}/grade_2.png`)}" x="790" y="145" width="320" height="57"/></g>`;
}
await png(`${preview}/seven-designs.png`,svg(1140,1720,`<rect width="1140" height="1720" fill="#111118"/>${rows}`));
await writeFile(`${preview}/index.html`,`<!doctype html><meta charset="utf-8"><title>Clutch designs</title><style>body{background:#111118;color:#eee;font:18px system-ui;max-width:1000px;margin:30px auto}section{border:1px solid #393944;border-radius:12px;padding:20px;margin:20px 0}img{max-width:100%}.pair img{width:220px;margin:15px}select{font-size:18px;padding:6px}</style><h1>Seven clutch designs</h1><p>Design 1 remains active. Preview with /training mode design preview 1 7. Fixed score labels: 0–4 below, 5 average, 6–10 above.</p>${themes.map((t,i)=>`<section><h2>${i+1}. ${t[0]}</h2><img src="bar${i+1}.png"><div class="pair"><img src="../../overlay/assets/viksstuff/textures/training/d${i+1}/success.png"><img src="../../overlay/assets/viksstuff/textures/training/d${i+1}/failed.png"></div><label>Score <select onchange="this.closest('section').querySelector('.score').src='../../overlay/assets/viksstuff/textures/training/d${i+1}/score_'+this.value+'.png';this.closest('section').querySelector('.grade').src='../../overlay/assets/viksstuff/textures/training/d${i+1}/grade_'+(this.value&lt;5?0:this.value==5?1:2)+'.png'">${Array.from({length:11},(_,n)=>`<option ${n===7?'selected':''}>${n}</option>`).join('')}</select></label><div class="pair"><img class="score" src="../../overlay/assets/viksstuff/textures/training/d${i+1}/score_7.png"><img class="grade" src="../../overlay/assets/viksstuff/textures/training/d${i+1}/grade_2.png"></div></section>`).join('')}`);
console.log('Built seven complete designs and preview gallery.');

await import("./build-training-layouts.mjs");
