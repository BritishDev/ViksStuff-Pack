import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import assert from 'node:assert/strict';
import sharp from 'sharp';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../overlay/assets/viksstuff');
let elements=0;
for(const color of ['white','red','dark_red'])for(const kind of ['core','shell','ring','node','shard','beam','sigil','cradle']) {
  const id=`orb/${kind}_${color}`;
  const item=JSON.parse(await fs.readFile(path.join(root,'items',id+'.json'),'utf8'));
  assert.equal(item.model.model,'viksstuff:item/'+id);
  const model=JSON.parse(await fs.readFile(path.join(root,'models/item',id+'.json'),'utf8'));
  assert.equal(model.ambientocclusion,false);assert.equal(model.display.fixed.scale[0],1);
  for(const element of model.elements) {
    assert.ok(element.light_emission>=0&&element.light_emission<=15);
    assert.equal(element.shade,false);assert.equal(element.from.length,3);assert.equal(element.to.length,3);
    for(let i=0;i<3;i++){assert.ok(Number.isFinite(element.from[i]));assert.ok(element.from[i]<element.to[i]);assert.ok(element.from[i]>=-16&&element.to[i]<=32);}
    for(const face of Object.values(element.faces)) {
      const texture=model.textures[face.texture.slice(1)]; assert.ok(texture);
      await fs.access(path.join(root,'textures',texture.replace('viksstuff:','')+'.png'));
    }
    elements++;
  }
}
for(const color of ['white','red','dark_red'])for(const kind of ['energy','metal','sigil']) {
  const file=path.join(root,`textures/item/orb/${kind}_${color}`);
  const albedo=await sharp(file+'.png').metadata();
  for(const suffix of ['_n','_s']) {
    const meta=await sharp(file+suffix+'.png').metadata();assert.equal(meta.width,albedo.width);assert.equal(meta.height,albedo.height);assert.equal(meta.channels,4);
  }
  const spec=await sharp(file+'_s.png').raw().toBuffer();let emissive=0;
  for(let k=3;k<spec.length;k+=4){assert.ok(spec[k]<255,'255 disables LabPBR emission');if(spec[k]>0)emissive++;}
  assert.ok(emissive>0);
  if(kind==='energy')for(const suffix of ['','_n','_s']) {
    const animation=JSON.parse(await fs.readFile(file+suffix+'.png.mcmeta','utf8')).animation;
    assert.equal(animation.width,32);assert.equal(animation.height,32);assert.equal(animation.frametime,2);assert.equal(albedo.height/32,16);
  }
}
const sounds=JSON.parse(await fs.readFile(path.join(root,'sounds.json'),'utf8'));
for(const id of ['hum','charge','release','reveal']) {assert.ok(sounds['orb.'+id]);assert.ok((await fs.stat(path.join(root,'sounds/orb',id+'.ogg'))).size>1000);}
console.log(`ORB ASSETS PASS: 24 models, ${elements} elements, nine PBR materials, synchronized animation maps, four sounds.`);
