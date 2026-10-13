"""Original non-verbal Parkour Relay effects. No sampled audio or vanilla overrides."""
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
RNG = np.random.default_rng(73109)
FFMPEG = shutil.which("ffmpeg")
if not FFMPEG:
    raise RuntimeError("ffmpeg with libvorbis is required")


def tone(duration, start, end=None, gain=1., decay=5., harmonic=.12):
    t = np.arange(round(duration * RATE)) / RATE
    end = start if end is None else end
    f = start + (end - start) * t / duration
    phase = 2 * np.pi * np.cumsum(f) / RATE
    attack = np.minimum(t / .008, 1)
    release = np.minimum((duration - t) / .025, 1)
    envelope = attack * release * np.exp(-decay * t / duration)
    return gain * envelope * (np.sin(phase) + harmonic * np.sin(2 * phase))


def layer(duration, pieces):
    output = np.zeros(round(duration * RATE))
    for offset, value in pieces:
        a = round(offset * RATE)
        b = min(len(output), a + len(value))
        output[a:b] += value[:b-a]
    return output


def air(duration, gain=.1):
    # Filtered noise under the chirp, with faded edges to avoid clicks.
    value = RNG.normal(0, 1, round(duration * RATE))
    value = np.convolve(value, np.ones(18) / 18, mode="same")
    return gain * value * np.sin(np.linspace(0, np.pi, len(value))) ** 2


sounds = {
    "ready": layer(.38, [(0, tone(.16, 440, gain=.7, decay=1)),
                            (.20, tone(.16, 440, gain=.7, decay=1))]),
    "set": tone(.22, 660, gain=.8, decay=1.4),
    "go": layer(.55, [(0, tone(.38, 880, 1320, gain=.7, decay=2)),
                         (0, tone(.35, 1760, gain=.24, decay=2.8)),
                         (.04, air(.4, .09))]),
    "slime": layer(.37, [(0, tone(.34, 680, 150, gain=.7, decay=3, harmonic=.2)),
                            (.08, tone(.25, 200, 420, gain=.18, decay=3))]),
    "checkpoint": layer(.78, [(0, tone(.45, 1046.5, gain=.65)),
                                 (.12, tone(.55, 1568, gain=.5)),
                                 (.22, tone(.48, 2093, gain=.25))]),
    "warp_out": layer(.60, [(0, tone(.53, 1200, 160, gain=.55, decay=1.7)),
                               (.02, air(.55, .6)),
                               (0, tone(.5, 600, 80, gain=.18, decay=2))]),
    "warp_in": layer(.63, [(0, tone(.48, 180, 1300, gain=.45, decay=.2)),
                              (0, air(.5, .45)),
                              (.38, tone(.23, 1568, gain=.3))]),
    "finish": layer(1.80, [(0, tone(.35, 783.99, gain=.55)),
                             (.17, tone(.35, 1046.5, gain=.55)),
                             (.34, tone(.35, 1318.51, gain=.55)),
                             (.54, tone(1.12, 1568, gain=.55, decay=3)),
                             (.54, tone(1.12, 1046.5, gain=.28, decay=3)),
                             (.54, tone(1.12, 1318.51, gain=.22, decay=3))]),
}

target = ROOT / "overlay/assets/viksstuff/sounds/parkour"
target.mkdir(parents=True, exist_ok=True)
manifest = {"sample_rate": RATE, "channels": 1, "encoding": "Vorbis", "seed": 73109,
            "provenance": "Original procedural synthesis; no voice or third-party samples.", "sounds": {}}
with tempfile.TemporaryDirectory(prefix="viks-parkour-audio-") as temp:
    for name, value in sounds.items():
        value *= .69 / max(1e-9, np.max(np.abs(value)))
        wav_path = Path(temp) / f"{name}.wav"
        ogg_path = target / f"{name}.ogg"
        with wave.open(str(wav_path), "wb") as writer:
            writer.setnchannels(1)
            writer.setsampwidth(2)
            writer.setframerate(RATE)
            writer.writeframes(np.round(value * 32767).astype("<i2").tobytes())
        subprocess.run([FFMPEG, "-hide_banner", "-loglevel", "error", "-y", "-i", str(wav_path),
                        "-map_metadata", "-1", "-c:a", "libvorbis", "-q:a", "5", str(ogg_path)], check=True)
        decoded = subprocess.run([FFMPEG, "-hide_banner", "-loglevel", "error", "-i", str(ogg_path),
                                  "-f", "f32le", "-ac", "1", "-ar", str(RATE), "-"],
                                 capture_output=True, check=True).stdout
        samples = np.frombuffer(decoded, dtype="<f4")
        peak = float(np.max(np.abs(samples)))
        if not np.all(np.isfinite(samples)) or peak >= .95 or len(samples) < RATE / 10:
            raise RuntimeError(f"Decoded audio failed peak/length validation: {name}")
        manifest["sounds"][name] = {"seconds": round(len(samples)/RATE, 4), "decoded_peak": round(peak, 4),
                                    "rms": round(float(np.sqrt(np.mean(samples*samples))), 4),
                                    "sha256": hashlib.sha256(ogg_path.read_bytes()).hexdigest()}
        print(f"{name}: {len(samples)/RATE:.2f}s, decoded peak {peak:.3f}")

registry_path = ROOT / "overlay/assets/viksstuff/sounds.json"
registry = json.loads(registry_path.read_text(encoding="utf-8"))
for name in sounds:
    registry[f"parkour.{name}"] = {
        "sounds": [{"name": f"viksstuff:parkour/{name}", "stream": False}]
    }
registry_path.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")
(ROOT / "docs").mkdir(parents=True, exist_ok=True)
(ROOT / "docs/parkour-sounds.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
