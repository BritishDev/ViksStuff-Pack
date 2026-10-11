"""Generate narration and word timestamps together (pip install edge-tts==7.2.8)."""
import asyncio
import json
from pathlib import Path

import edge_tts

DEST = Path(__file__).resolve().parents[1] / "source-art/strength-reveal"
PHRASES = {
    "rain": ["Hi there, Rain Dynasty.", "I have been expecting you.",
             "You have come very far,", "and I have a gift for you.", "Take this key and enjoy."],
    "generic": ["Hi there.", "I have been expecting you.", "You have come very far,",
                "and I have a gift for you.", "Take this key and enjoy."],
}


async def generate(variant, phrases):
    audio, words = bytearray(), []
    voice = edge_tts.Communicate(" ".join(phrases), "en-GB-ThomasNeural",
                                rate="-17%", pitch="-20Hz", boundary="WordBoundary")
    async for event in voice.stream():
        if event["type"] == "audio":
            audio.extend(event["data"])
        elif event["type"] == "WordBoundary":
            words.append({k: event[k] for k in ("text", "offset", "duration")})
    if not audio or not words:
        raise RuntimeError("Speech service returned incomplete audio/timestamps")
    DEST.mkdir(parents=True, exist_ok=True)
    # Publish only after the complete response has arrived.
    (DEST / f"narration-{variant}.mp3").write_bytes(audio)
    (DEST / f"narration-{variant}-timing.json").write_text(
        json.dumps({"phrases": phrases, "words": words}, indent=2) + "\n", encoding="utf-8")
    print(f"{variant}: {len(audio)} audio bytes, {len(words)} timed words")


async def main():
    for variant, phrases in PHRASES.items():
        await generate(variant, phrases)


if __name__ == "__main__":
    asyncio.run(main())
