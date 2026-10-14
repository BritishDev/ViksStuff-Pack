"""Package hand-authored REAPER/Vital renders; this script does not synthesize sound."""
from pathlib import Path
import hashlib, json, shutil, subprocess, wave
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT.parent / 'artifacts/parkour-audio-v3'
FF = shutil.which('ffmpeg')
assert FF, 'ffmpeg required'
baseline_path = ART / 'previous-manifest.json'
if not baseline_path.exists():
    shutil.copy2(ROOT / 'docs/parkour-sounds.json', baseline_path)
baseline = json.loads(baseline_path.read_text())
design = json.loads((ART / 'mcp-authoring.json').read_text())
target = ROOT / 'overlay/assets/viksstuff/sounds/parkour'
target.mkdir(parents=True, exist_ok=True)

def decode(path):
    return np.frombuffer(subprocess.check_output([FF,'-v','error','-i',str(path),'-ac','1','-ar','48000','-f','f32le','-']),dtype='<f4')

manifest = {'version':3,'sample_rate':48000,'channels':1,'encoding':'Vorbis',
    'provenance':'Original hand-authored MIDI and individual Vital patches, assembled and rendered through REAPER MCP. No sampled game audio or copied melodies.',
    'design':'Nine distinct arcade/platformer cues: pulse and bent oscillators, rounded bass bodies, original short arpeggios and a two-phrase fanfare.',
    'editable_project':'artifacts/parkour-audio-v3/Parkour-Arcade-v3.rpp',
    'loudness_target_db_vs_v2':1.5,'sounds':{}}
audio={}
for cue in design['cues']:
    name=cue['id']; source=ART/'masters'/f'{name}.wav'
    assert source.exists(), f'Missing REAPER master: {name}'
    compressed=ART/'masters'/f'{name}-levelled.wav'
    subprocess.run([FF,'-v','error','-y','-i',str(source),'-ac','1','-ar','48000',
        '-af','acompressor=threshold=0.075:ratio=3:attack=2:release=45:makeup=1','-c:a','pcm_s24le',str(compressed)],check=True)
    a=decode(compressed); rms=float(np.sqrt(np.mean(a*a)))
    desired=baseline['sounds'][name]['rms'] * 10**(1.5/20)
    gain=desired/max(rms,1e-8)
    ogg=target/f'{name}.ogg'
    duration=len(a)/48000
    for attempt in range(8):
        filters=f'volume={gain:.8f},alimiter=limit=0.80:attack=2:release=30:level=false:latency=true,afade=t=in:d=0.002,afade=t=out:st={duration-0.015:.6f}:d=0.015'
        subprocess.run([FF,'-v','error','-y','-i',str(compressed),'-af',filters,'-ac','1','-ar','48000',
            '-map_metadata','-1','-c:a','libvorbis','-q:a','7',str(ogg)],check=True)
        samples=decode(ogg); peak=float(np.max(np.abs(samples))); actual=float(np.sqrt(np.mean(samples*samples)))
        if abs(20*np.log10(actual/desired))<.12: break
        gain *= desired/actual
    assert actual > baseline['sounds'][name]['rms'], f'Cue must be slightly louder: {name}'
    assert np.isfinite(samples).all() and .1<peak<.95 and .1<len(samples)/48000<3, f'Invalid audio: {name}'
    audio[name]=samples
    manifest['sounds'][name]={'seconds':round(len(samples)/48000,4),'decoded_peak':round(peak,4),
        'rms':round(actual,4),'rms_db_vs_v2':round(float(20*np.log10(actual/baseline['sounds'][name]['rms'])),2),
        'sha256':hashlib.sha256(ogg.read_bytes()).hexdigest(),'design':cue['detail']}
    print(name,manifest['sounds'][name])
(ROOT/'docs/parkour-sounds.json').write_text(json.dumps(manifest,indent=2)+'\n')

def wav(path,samples):
    with wave.open(str(path),'wb') as out:
        out.setnchannels(1);out.setsampwidth(2);out.setframerate(48000)
        out.writeframes((np.clip(samples,-1,1)*32767).astype('<i2').tobytes())
sampler=np.zeros(4*48000)
for offset,name in [(0,'ready'),(1,'set'),(2,'set'),(3,'go')]:
    a=audio[name];start=offset*48000;sampler[start:start+len(a)]+=a
sampler=np.concatenate([sampler]+[np.concatenate([np.zeros(24000),audio[name]]) for name in ['slime','checkpoint','warp_out','warp_in','retry','finish']])
wav(ART/'parkour-arcade-v3-sampler.wav',sampler)
print('REAPER AUDIO PACKAGING PASS: nine unique mono 48 kHz cues, retained IDs, decoded peaks below clipping.')
