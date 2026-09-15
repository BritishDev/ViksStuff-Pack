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
  await sharp(`${root}source-art/training/attempts.png`)
    .extract({left:i*512,top:250,width:512,height:490})
    .resize(32,32,{kernel:'nearest'}).png().toFile(`${textures}/${name}.png`);
}
await writeFile(`${fonts}/training_clutch.json`, JSON.stringify({providers:[
  provider('pending','\uE103',12,-3),provider('hit','\uE104',12,-3),provider('miss','\uE105',12,-3)
]},null,2));
// Purple is reserved for this image-only HUD; no other workspace bar uses it.
const bars = `${root}overlay/assets/minecraft/textures/gui/sprites/boss_bar`;
await mkdir(bars,{recursive:true});
for (const name of ['purple_background','purple_progress']) {
  await sharp({create:{width:182,height:5,channels:4,background:{r:0,g:0,b:0,alpha:0}}})
    .png().toFile(`${bars}/${name}.png`);
}
