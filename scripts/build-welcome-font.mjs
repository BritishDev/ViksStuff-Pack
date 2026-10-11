import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

export async function buildWelcomeFont() {
 // Reuse Minecraft's own ASCII texture, at a deliberately small title height.
 // Its printable ASCII glyphs occupy their Unicode positions in the 16x16 grid.
 const chars=Array.from({length:16},(_,row)=>Array.from({length:16},(_,column)=>{
  const letter=String.fromCodePoint(row*16+column);
  return 'Welcomt'.includes(letter)?letter:'\u0000';
 }).join(''));
 const font={providers:[
  {type:'space',advances:{' ':1.5}},
  {type:'bitmap',file:'minecraft:font/ascii.png',height:3,ascent:2,chars}
 ]};
 const output=path.resolve('ViksStuff-Pack/overlay/assets/viksstuff/font/reveal_welcome.json');
 await fs.mkdir(path.dirname(output),{recursive:true});
 await fs.writeFile(output,JSON.stringify(font,null,2)+'\n');
 console.log('WELCOME FONT PASS: small vanilla pixel letters, 12-pixel title height');
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url))await buildWelcomeFont();
