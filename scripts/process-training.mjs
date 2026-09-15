import sharp from 'sharp';
import {mkdir, writeFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
const root = fileURLToPath(new URL('../', import.meta.url));
const textures = `${root}overlay/assets/viksstuff/textures/training`;
const fonts = `${root}overlay/assets/viksstuff/font`;
await mkdir(textures, {recursive:true});
await mkdir(fonts, {recursive:true});
// Mechanical atlas extraction for Minecraft; the generated artwork is unchanged.
for (const [name, top, left, width] of [['clutch',90,318,900], ['failed',378,318,900], ['success',670,275,990]]) {
  await sharp(`${root}source-art/training/atlas.png`)
    .extract({left,top,width,height:268}).resize({width:256,kernel:'nearest'})
    .png().toFile(`${textures}/${name}.png`);
}
const provider = (name, char, height, ascent) => ({type:'bitmap',file:`viksstuff:training/${name}.png`,height,ascent,chars:[char]});
await writeFile(`${fonts}/training_clutch.json`, JSON.stringify({providers:[provider('clutch','\uE100',12,-3)]},null,2));
await writeFile(`${fonts}/training_result.json`, JSON.stringify({providers:[provider('failed','\uE101',8,6),provider('success','\uE102',8,6)]},null,2));

for (const [i,name] of ['pending','hit','miss'].entries()) {
  await sharp(`${root}source-art/training/attempts-smooth.png`)
    .extract({left:i*512,top:230,width:512,height:512})
    .resize(128,128,{kernel:'lanczos3'}).png().toFile(`${textures}/${name}.png`);
}
await writeFile(`${fonts}/training_clutch.json`, JSON.stringify({providers:[
  provider('pending','\uE103',12,-3),provider('hit','\uE104',12,-3),provider('miss','\uE105',12,-3),
  provider('frame','\uE106',18,0),{type:'space',advances:{'\uE107':-135,'\uE108':4}}
]},null,2));
// Purple is reserved for this image-only HUD; no other workspace bar uses it.
const bars = `${root}overlay/assets/minecraft/textures/gui/sprites/boss_bar`;
await mkdir(bars,{recursive:true});
for (const name of ['purple_background','purple_progress']) {
  await sharp({create:{width:182,height:5,channels:4,background:{r:0,g:0,b:0,alpha:0}}})
    .png().toFile(`${bars}/${name}.png`);
}

// Code-native shared frame, rendered at 4x GUI resolution for smooth bevels.
const frame = `<svg width="552" height="72" xmlns="http://www.w3.org/2000/svg"><defs><linearGradient id="rim" x2="0" y2="1"><stop stop-color="#ff7777"/><stop offset=".35" stop-color="#ed182c"/><stop offset="1" stop-color="#660817"/></linearGradient></defs><rect x="2" y="2" width="548" height="68" rx="13" fill="#030202" stroke="url(#rim)" stroke-width="4"/><rect x="7" y="7" width="538" height="58" rx="9" fill="none" stroke="#420a12" stroke-width="2"/></svg>`;
await sharp(Buffer.from(frame)).png().toFile(`${textures}/frame.png`);
