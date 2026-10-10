"""Compile/link actual pack shaders against the installed 1.21.11 include files."""
from pathlib import Path
import re, subprocess, sys, zipfile
from PIL import Image
import io

root = Path(__file__).resolve().parents[1]
client = Path(sys.argv[1])
compiler = Path(sys.argv[2])
output = root.parent / '.tools/orb-shader-validation'
output.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(client) as jar:
    def expand(source, seen):
        source = re.sub(r'^\s*#version[^\n]*\n', '', source, flags=re.M)
        def include(match):
            identifier = match.group(1)
            namespace, name = identifier.split(':', 1) if ':' in identifier else ('minecraft', identifier)
            filename = f'assets/{namespace}/shaders/include/{name}'
            if filename in seen: return ''
            seen.add(filename)
            local = root / 'overlay' / filename
            data = local.read_text() if local.exists() else jar.read(filename).decode()
            return expand(data, seen)
        return re.sub(r'#moj_import\s+<([^>]+)>', include, source)
    shader_dir=root/'overlay/1_21_6/assets/minecraft/shaders/core'
    for source, extension in [('entity.vsh','vert'),('entity.fsh','frag')]:
        (output/('entity.'+extension)).write_text('#version 330\n'+expand((shader_dir/source).read_text(),set()))

variants = [[],['ALPHA_CUTOUT=0.1'],['ALPHA_CUTOUT=0.1','PER_FACE_LIGHTING'],
            ['ALPHA_CUTOUT=0.1','EMISSIVE'],['ALPHA_CUTOUT=0.1','NO_OVERLAY'],
            ['ALPHA_CUTOUT=0.1','APPLY_TEXTURE_MATRIX'],['NO_CARDINAL_LIGHTING'],
            ['PER_FACE_LIGHTING'],['EMISSIVE','NO_OVERLAY','APPLY_TEXTURE_MATRIX']]
for defines in variants:
    command=[str(compiler),'-l']+['-D'+define for define in defines]+[str(output/'entity.vert'),str(output/'entity.frag')]
    result=subprocess.run(command, text=True, capture_output=True)
    if result.returncode:
        print(result.stdout,result.stderr);raise SystemExit(f'Shader variant failed: {defines}')

# Demonstrate tag isolation against every existing pack texture, not merely a shader claim.
collisions=[]
with zipfile.ZipFile(root/'ViksStuff-Pack.zip') as pack:
    for file in pack.namelist():
        if not file.endswith('.png') or '/textures/item/orb/' in file: continue
        image=Image.open(io.BytesIO(pack.read(file))).convert('RGBA')
        for r,g,b,a in image.getdata():
            if a!=249: continue
            top=max(r,g,b)
            if top<13: continue
            chroma=[r/top,g/top,b/top]
            matches=any(sum((c-v)**2 for c,v in zip(chroma,ref))<tolerance**2
                        for ref,tolerance in [([242/255,247/255,1],.025),([1,36/255,61/255],.025),([1,.08,.20],.055)])
            if matches: collisions.append(file);break
if collisions: raise SystemExit('Orb marker collisions: '+str(collisions))
print(f'ORB SHADERS PASS: {len(variants)} linked pipeline variants; zero existing texture tag collisions; native 1.21.11 includes.')
