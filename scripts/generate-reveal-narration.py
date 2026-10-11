"""Generate narration and word timestamps together (pip install edge-tts==7.2.8)."""
import asyncio
import json
import math
import subprocess
import tempfile
import sys
import wave
from pathlib import Path

import edge_tts

DEST = Path(__file__).resolve().parents[1] / "source-art/strength-reveal"
SCRIPT = ["Hello there Rain Dynasty", "I have been expecting you",
          "I have been watching you closely and have liked what I have seen.",
          "I have a gift, but make sure to listen closely",
          "Take this key. When the vault appears, look at it and right click from where you are."]
CAPTIONS = ["Hello there Rain Dynasty", "I have been expecting you",
            "I have been watching you closely", "and have liked what I have seen.",
            "I have a gift,", "but make sure to listen closely",
            "Take this key.", "When the vault appears,",
            "look at it and right click", "from where you are."]
SCRIPT_V2 = ["Hello", "I have been expecting you Rain Dynasty",
             "I have been watching you, and I have liked what I have seen",
             "I am here to congratulate you, but first you must do something for me",
             "Take this key, and when you see a vault, right click it from where you are standing",
             "Best of luck"]
CAPTIONS_V2 = ["Hello", "I have been expecting you",
               "Rain Dynasty", "I have been watching you,",
               "and I have liked what I have seen",
               "I am here to congratulate you,",
               "but first you must do",
               "something for me", "Take this key,",
               "and when you see a vault,",
               "right click it from where",
               "you are standing", "Best of luck"]
TEMPO = .9  # The final encoder slows the voice with atempo=0.9.
SAMPLE_RATE = 48000


async def speech(text):
    for attempt in range(4):
        audio, words = bytearray(), []
        voice = edge_tts.Communicate(text, "en-GB-ThomasNeural",
                                    rate="-17%", pitch="-20Hz", boundary="WordBoundary")
        try:
            async for event in voice.stream():
                if event["type"] == "audio":
                    audio.extend(event["data"])
                elif event["type"] == "WordBoundary":
                    words.append({k: event[k] for k in ("text", "offset", "duration")})
            if not audio or not words:
                raise RuntimeError("Speech service returned incomplete audio/timestamps")
            return audio, words
        except Exception:
            if attempt == 3:
                raise
            print(f"Voice request retry {attempt + 1}", flush=True)
            await asyncio.sleep(2 ** (attempt + 1))


def pcm(directory, name, audio):
    source, target = directory / f"{name}.mp3", directory / f"{name}.wav"
    source.write_bytes(audio)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(source),
                    "-ar", str(SAMPLE_RATE), "-ac", "1", "-c:a", "pcm_s16le", str(target)], check=True)
    with wave.open(str(target), "rb") as track:
        return track.readframes(track.getnframes())


async def generate(variant):
    second = variant.endswith("_v2")
    lines, phrases = (SCRIPT_V2.copy(), CAPTIONS_V2.copy()) if second else (SCRIPT.copy(), CAPTIONS.copy())
    if variant == "generic_v2":
        lines[1] = "I have been expecting you"
        phrases.remove("Rain Dynasty")
    elif variant == "generic":
        lines[0] = phrases[0] = "Hello there"
    # Sentence punctuation shapes the spoken pauses; captions retain the supplied wording.
    intro, intro_words = await speech(" ".join(line.rstrip(".") + "." for line in lines[:4]))
    instruction, instruction_words = await speech(" ".join(line.rstrip(".") + "." for line in lines[4:]))
    DEST.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="reveal-narration-") as scratch:
        directory = Path(scratch)
        intro_pcm, key_pcm = pcm(directory, "intro", intro), pcm(directory, "key", instruction)
        last_end = intro_words[-1]["offset"] + intro_words[-1]["duration"]
        intro_samples = math.ceil(last_end / 10_000_000 * SAMPLE_RATE)
        if intro_samples * 2 > len(intro_pcm):
            raise RuntimeError("Intro word timestamps exceed decoded audio")
        # Include the instruction's existing lead-in in the requested final one-second gap.
        pause_samples = round((TEMPO - instruction_words[0]["offset"] / 10_000_000) * SAMPLE_RATE)
        if pause_samples <= 0:
            raise RuntimeError("Instruction lead-in is too long for the requested pause")
        shift = round((intro_samples + pause_samples) / SAMPLE_RATE * 10_000_000)
        words = intro_words + [{**word, "offset": word["offset"] + shift} for word in instruction_words]
        pause_start_ms = round(last_end / 10_000 / TEMPO)
        pause_end_ms = round(words[len(intro_words)]["offset"] / 10_000 / TEMPO)
        if abs(pause_end_ms - pause_start_ms - 1000) > 1:
            raise RuntimeError("Encoded speech boundaries do not preserve the one-second pause")
        assembled = directory / "assembled.wav"
        with wave.open(str(assembled), "wb") as track:
            track.setnchannels(1); track.setsampwidth(2); track.setframerate(SAMPLE_RATE)
            track.writeframes(intro_pcm[:intro_samples * 2] + bytes(pause_samples * 2) + key_pcm)
        output = directory / "narration.mp3"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(assembled),
                        "-c:a", "libmp3lame", "-b:a", "192k", str(output)], check=True)
        # Publish only after complete synthesis, audio assembly and timing verification.
        (DEST / f"narration-{variant}.mp3").write_bytes(output.read_bytes())
    (DEST / f"narration-{variant}-timing.json").write_text(
        json.dumps({"script_lines": lines, "phrases": phrases, "words": words,
                    "pause": {"after_line": 4, "start_ms": pause_start_ms,
                              "end_ms": pause_end_ms, "duration_ms": 1000}}, indent=2) + "\n", encoding="utf-8")
    print(f"{variant}: {len(words)} timed words; one-second pause at {pause_start_ms}ms")


async def main():
    variants = sys.argv[1:] or ["rain", "generic", "rain_v2", "generic_v2"]
    for variant in variants:
        if variant not in ("rain", "generic", "rain_v2", "generic_v2"):
            raise ValueError(f"Unknown narration variant: {variant}")
        await generate(variant)


if __name__ == "__main__":
    asyncio.run(main())
