import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import sharp from 'sharp';

export async function buildRevealFont() {
 const pack=path.resolve('ViksStuff-Pack'),root=path.join(pack,'overlay/assets/viksstuff');
 // Minecraft stitches each bitmap cell into a 256x256 font atlas, regardless of its display height.
 // Four adjacent cells keep substantially more detail than shrinking the entire logo to one glyph.
 const width=640,height=256,cellWidth=160,displayHeight=28;
 const logo=await sharp(path.join(pack,'source-art/strength-reveal/logo-transparent.png')).resize(width,height,{fit:'fill'}).ensureAlpha().raw().toBuffer();
 await fs.mkdir(path.join(root,'textures/font'),{recursive:true});
 await sharp(logo,{raw:{width,height,channels:4}}).png().toFile(path.join(root,'textures/font/strength-logo.png'));
 await sharp({create:{width:16,height:16,channels:4,background:{r:255,g:255,b:255,alpha:1}}}).png().toFile(path.join(root,'textures/font/reveal-flash.png'));
 const advances={};
 for(let tile=0;tile<3;tile++) {
  let actualWidth=0;
  for(let x=cellWidth-1;x>=0&&!actualWidth;x--)for(let y=0;y<height;y++)if(logo[(y*width+tile*cellWidth+x)*4+3]){actualWidth=x+1;break;}
  const nativeAdvance=Math.trunc(.5+actualWidth*displayHeight/height)+1;
  advances[String.fromCodePoint(0xe710+tile)]=cellWidth*displayHeight/height-nativeAdvance;
 }
 const font={providers:[
  {type:'bitmap',file:'viksstuff:font/strength-logo.png',height:displayHeight,ascent:7,chars:['\ue700\ue702\ue703\ue704']},
  {type:'bitmap',file:'viksstuff:font/reveal-flash.png',height:1024,ascent:512,chars:['\ue701']},
  {type:'space',advances}
 ]};
 await fs.writeFile(path.join(root,'font/reveal.json'),JSON.stringify(font,null,2)+'\n');
 console.log('REVEAL FONT BUILT: four 160x256 logo tiles, seamless native advance compensation, unchanged flash');
}

if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url))await buildRevealFont();
