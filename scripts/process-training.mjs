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
await writeFile(`${fonts}/training_clutch.json`, JSON.stringify({providers:[provider('clutch','\uE100',18,13)]},null,2));
await writeFile(`${fonts}/training_result.json`, JSON.stringify({providers:[provider('failed','\uE101',24,19),provider('success','\uE102',24,19)]},null,2));
