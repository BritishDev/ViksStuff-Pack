"""Check encoded pack delivery and audible level of the original relay cues."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import zipfile
import numpy as np

root = Path(__file__).resolve().parents[1]
manifest = json.loads((root / "docs/parkour-sounds.json").read_text(encoding="utf-8"))
ffmpeg = shutil.which("ffmpeg")
assert ffmpeg, "ffmpeg required"
original = json.loads(subprocess.check_output(["git", "show", "HEAD:overlay/assets/viksstuff/sounds.json"], cwd=root))
with zipfile.ZipFile(root / "ViksStuff-Pack.zip") as archive:
    registry = json.loads(archive.read("assets/viksstuff/sounds.json"))
    for key, value in original.items():
        assert registry[key] == value, f"Existing sound changed: {key}"
    for cue, info in manifest["sounds"].items():
        path = f"assets/viksstuff/sounds/parkour/{cue}.ogg"
        data = archive.read(path)
        assert data[:4] == b"OggS", f"Not an Ogg container: {cue}"
        assert hashlib.sha256(data).hexdigest() == info["sha256"], f"Wrong packed bytes: {cue}"
        assert registry[f"parkour.{cue}"]["sounds"] == [{"name": f"viksstuff:parkour/{cue}", "stream": False}], f"Wrong registry: {cue}"
        decoded = subprocess.run([ffmpeg, "-hide_banner", "-loglevel", "error", "-i", "pipe:0",
                                  "-f", "f32le", "-ac", "1", "-ar", "48000", "-"],
                                 input=data, capture_output=True, check=True).stdout
        samples = np.frombuffer(decoded, dtype="<f4")
        assert np.isfinite(samples).all() and .1 < np.abs(samples).max() < .95, f"Silent/clipped audio: {cue}"
        assert .1 < len(samples) / 48000 < 3, f"Unexpected duration: {cue}"
print(f"PARKOUR AUDIO PASS: {len(manifest['sounds'])} mono 48kHz .ogg cues; decoded peaks below clipping; packed hashes and names match; existing sounds retained.")
