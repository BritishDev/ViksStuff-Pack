"""V2 original arcade-racer effects: FM mallets, rubber impacts, tuned sweeps and short early reflections."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import tempfile
import wave
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RATE = 48000
RNG = np.random.default_rng(73110)
FFMPEG = shutil.which("ffmpeg")
if not FFMPEG:
    raise RuntimeError("ffmpeg with libvorbis is required")


def envelope(duration, decay=4, attack=.003, release=.035):
    t = np.arange(round(duration * RATE)) / RATE
    return t, np.minimum(t / attack, 1) * np.minimum((duration-t) / release, 1) * np.exp(-decay*t/duration)


def mallet(duration, frequency, gain=1, bright=1.7, decay=5):
    t, env = envelope(duration, decay)
    # Transient FM overtones relax into the fundamental instead of a plain sine beep.
    phase = 2*np.pi*frequency*t + bright*np.exp(-t/.075)*np.sin(2*np.pi*frequency*2.01*t)
    value = np.sin(phase) + .18*np.sin(2*np.pi*frequency*1.003*t) + .10*np.sin(4*np.pi*frequency*t)*np.exp(-t/.08)
    return gain*env*value


def body(duration, high, low, gain=.4):
    t, env = envelope(duration, 7, .002)
    frequency = low+(high-low)*np.exp(-t/.025)
    return gain*env*np.sin(2*np.pi*np.cumsum(frequency)/RATE)


def noise(duration, center=1200, width=600, gain=.1):
    t, env = envelope(duration, 3, .002)
    spectrum = np.fft.rfft(RNG.normal(0, 1, len(t)))
    frequencies = np.fft.rfftfreq(len(t), 1/RATE)
    spectrum *= np.exp(-.5*((frequencies-center)/width)**2)
    value = np.fft.irfft(spectrum, len(t))
    value /= max(1e-9, np.abs(value).max())
    return gain*env*value


def sweep(duration, start, end, gain=.5, ascending=False):
    t, env = envelope(duration, 1.5 if not ascending else .7, .02, .055)
    curve = (t/duration)**(.7 if ascending else 1.25)
    frequency = start*(end/start)**curve
    phase = 2*np.pi*np.cumsum(frequency)/RATE
    return gain*env*(np.sin(phase+.8*np.sin(2*phase))+.12*np.sin(phase*1.5))


def mix(duration, pieces):
    output = np.zeros(round(duration*RATE))
    for offset, value in pieces:
        a = round(offset*RATE); b = min(len(output), a+len(value))
        output[a:b] += value[:b-a]
    return output


def room(value):
    output = value.copy()
    # Low-level early reflections create space without long overlapping race cues.
    softened = np.convolve(value, np.ones(7)/7, mode="same")
    for milliseconds, gain in ((37,.13),(79,.085),(131,.04)):
        gap = round(milliseconds/1000*RATE)
        output[gap:] += gain*softened[:-gap]
    return output


c4, e4, g4, c5, e5, g5, c6 = 261.626, 329.628, 391.995, 523.251, 659.255, 783.991, 1046.502
sounds = {
    "ready": mix(.46, [(0,body(.19,190,85,.24)), (0,mallet(.23,e4,.57,.9,4)),
                       (.16,mallet(.25,e4,.5,.9,4)), (.16,body(.15,150,75,.17))]),
    "set": mix(.40, [(0,body(.15,215,100,.2)), (0,mallet(.33,g4,.7,1.3,4)),
                     (.018,mallet(.26,g5,.15,1.1,5))]),
    "go": mix(.94, [(0,body(.30,180,62,.48)), (0,noise(.14,1450,720,.09)),
                    (0,mallet(.74,c5,.48,1.2,3)), (.025,mallet(.73,e5,.33,1.3,3)),
                    (.05,mallet(.74,g5,.29,1.4,3)), (.09,sweep(.33,240,720,.17,True)),
                    (.12,mallet(.58,c6,.16,1.1,5))]),
    "slime": mix(.48, [(0,body(.24,570,125,.65)), (.035,sweep(.32,130,370,.34,True)),
                       (.004,noise(.11,850,460,.12)), (.13,mallet(.20,460,.10,2.4,6))]),
    "checkpoint": mix(.98, [(0,mallet(.40,c5,.51,2.3)), (.072,mallet(.42,e5,.43,2.2)),
                            (.144,mallet(.60,g5,.39,2.0)), (.23,mallet(.66,c6,.33,1.7,4)),
                            (0,body(.18,155,73,.13)), (.25,mallet(.42,g5*2,.075,1.0,6))]),
    "warp_out": mix(.64, [(0,sweep(.50,820,105,.48)), (.05,sweep(.46,410,80,.19)),
                          (.025,noise(.42,850,370,.16)), (0,body(.17,120,58,.2))]),
    "warp_in": mix(.76, [(0,sweep(.48,105,650,.36,True)), (.02,noise(.43,850,410,.12)),
                         (.31,mallet(.38,c5,.32,1.3,4)), (.36,mallet(.34,g5,.17,1.3,4)),
                         (.3,body(.15,140,70,.14))]),
    "retry": mix(.49, [(0,mallet(.22,e4,.37,.8,5)), (.085,mallet(.26,c4,.39,.8,4)),
                       (.17,body(.23,210,75,.31)), (.015,noise(.09,780,390,.055))]),
    "finish": mix(2.66, [(0,body(.25,180,65,.3)),
                         (0,mallet(.47,c5,.48,1.7,4)), (.13,mallet(.47,e5,.45,1.7,4)),
                         (.26,mallet(.53,g5,.43,1.7,4)), (.44,mallet(.67,c6,.42,1.6,3)),
                         (.78,mallet(.49,g5,.28,1.4,4)), (1.02,mallet(1.36,c6,.34,1.3,3)),
                         (1.02,mallet(1.36,e5,.23,1.3,3)), (1.02,mallet(1.36,g5,.21,1.3,3)),
                         (1.02,mallet(1.25,c4,.20,.7,3)),
                         (.44,noise(.20,1500,730,.065)), (1.02,noise(.25,1450,670,.07))]),
}
for name, value in sounds.items():
    value = room(value)
    value = np.tanh(value*1.15)
    value *= .59/max(1e-9,np.abs(value).max())
    sounds[name] = value


def write_wav(path, value):
    with wave.open(str(path), "wb") as writer:
        writer.setnchannels(1);writer.setsampwidth(2);writer.setframerate(RATE)
        writer.writeframes(np.round(value*32767).astype("<i2").tobytes())


target = ROOT / "overlay/assets/viksstuff/sounds/parkour"
target.mkdir(parents=True, exist_ok=True)
manifest = {"version": 2, "sample_rate": RATE, "channels": 1, "encoding": "Vorbis", "seed": 73110,
            "provenance": "Original layered arcade-racer synthesis; no voice or third-party samples.",
            "design": "FM mallets, rounded impact transients, filtered rubber/warp textures, tuned C-major family and short early reflections.",
            "sounds": {}}
with tempfile.TemporaryDirectory(prefix="viks-parkour-audio-") as temp:
    for name, value in sounds.items():
        wav_path = Path(temp)/f"{name}.wav";ogg_path = target/f"{name}.ogg"
        write_wav(wav_path,value)
        subprocess.run([FFMPEG,"-hide_banner","-loglevel","error","-y","-i",str(wav_path),
                        "-map_metadata","-1","-fflags","+bitexact","-flags:a","+bitexact",
                        "-c:a","libvorbis","-q:a","6",str(ogg_path)],check=True)
        decoded = subprocess.run([FFMPEG,"-hide_banner","-loglevel","error","-i",str(ogg_path),
                                  "-f","f32le","-ac","1","-ar",str(RATE),"-"],capture_output=True,check=True).stdout
        samples = np.frombuffer(decoded,dtype="<f4");peak = float(np.max(np.abs(samples)))
        if not np.isfinite(samples).all() or peak>=.85 or len(samples)<RATE/10:
            raise RuntimeError(f"Decoded audio failed peak/length validation: {name}")
        manifest["sounds"][name] = {"seconds":round(len(samples)/RATE,4),"decoded_peak":round(peak,4),
                                    "rms":round(float(np.sqrt(np.mean(samples*samples))),4),
                                    "sha256":hashlib.sha256(ogg_path.read_bytes()).hexdigest()}
        print(f"{name}: {len(samples)/RATE:.2f}s, decoded peak {peak:.3f}")

registry_path = ROOT/"overlay/assets/viksstuff/sounds.json"
registry = json.loads(registry_path.read_text(encoding="utf-8"))
for name in sounds:
    registry[f"parkour.{name}"] = {"sounds":[{"name":f"viksstuff:parkour/{name}","stream":False}]}
registry_path.write_text(json.dumps(registry,indent=2)+"\n",encoding="utf-8")
(ROOT/"docs").mkdir(parents=True,exist_ok=True)
(ROOT/"docs/parkour-sounds.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")

preview_dir = ROOT.parent/"artifacts/parkour-timer"
preview_dir.mkdir(parents=True,exist_ok=True)
sampler = np.concatenate([mix(4.1,[(0,sounds["ready"]),(1,sounds["set"]),(2,sounds["set"]),(3,sounds["go"])])]
                         + [np.concatenate((np.zeros(round(.45*RATE)),sounds[name])) for name in ("slime","checkpoint","warp_out","warp_in","retry","finish")])
write_wav(preview_dir/"race-sound-preview-v2.wav",sampler)
