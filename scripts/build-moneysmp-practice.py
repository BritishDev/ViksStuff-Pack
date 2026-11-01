from pathlib import Path
import hashlib, zipfile
root = Path(__file__).resolve().parents[1]
source = root / "source-art/moneysmp-practice"
output = root / "releases/MoneySMPPractice-artwork.zip"
output.parent.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
    for file in sorted(source.rglob("*")):
        if file.is_file():
            info = zipfile.ZipInfo(file.relative_to(source).as_posix(), (2026, 11, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            data = file.read_bytes()
            if file.suffix in (".json", ".mcmeta"):
                data = data.replace(b"\r\n", b"\n")
            archive.writestr(info, data)
print(hashlib.sha1(output.read_bytes()).hexdigest())
