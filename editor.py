import argparse
import asyncio
import os
import subprocess
import tempfile
from pathlib import Path

import edge_tts
import urllib.request


def duration(path):
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(path)]
    return float(subprocess.check_output(cmd, text=True).strip())


async def synthesize(text, voice, output):
    try:
        communicate = edge_tts.Communicate(text, voice=voice, rate="+0%")
        await communicate.save(str(output))
        return
    except Exception as exc:
        print(f"Edge TTS indisponível ({type(exc).__name__}). Usando Piper offline.", flush=True)

    # Alternativa offline em português brasileiro: não depende do serviço Microsoft.
    model_dir = output.parent / "piper_model"
    model_dir.mkdir(exist_ok=True)
    base = "https://huggingface.co/rhasspy/piper-voices/resolve/main/pt/pt_BR/faber/medium/"
    model = model_dir / "pt_BR-faber-medium.onnx"
    config = model_dir / "pt_BR-faber-medium.onnx.json"
    for target in (model, config):
        if not target.exists():
            urllib.request.urlretrieve(base + target.name, target)
    wav = output.with_suffix(".wav")
    subprocess.run(["piper", "--model", str(model), "--output_file", str(wav)],
                   input=text, text=True, check=True)
    subprocess.run(["ffmpeg", "-y", "-i", str(wav), "-codec:a", "libmp3lame", "-qscale:a", "3", str(output)], check=True)



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", required=True)
    parser.add_argument("--text", required=True)
    parser.add_argument("--voice", default="pt-BR-ThalitaMultilingualNeural")
    parser.add_argument("--output", default="output/short-final.mp4")
    args = parser.parse_args()

    video = Path(args.video).resolve()
    if not video.is_file() or video.suffix.lower() != ".mp4":
        raise SystemExit("Vídeo MP4 não encontrado: " + str(video))
    output = Path(args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        speech = Path(tmp) / "voz.mp3"
        asyncio.run(synthesize(args.text, args.voice, speech))
        vd = duration(video)
        ad = duration(speech)
        # atempo accepts factors 0.5 to 100; limit speed adjustment to avoid unnaturally fast speech
        factor = ad / vd
        if factor > 1.35:
            raise SystemExit(f"Narração longa demais ({ad:.1f}s) para vídeo de {vd:.1f}s. Encurte o roteiro.")
        filter_chain = f"atempo={max(0.5, factor):.5f},apad,atrim=duration={vd:.5f}"
        subprocess.run([
            "ffmpeg", "-y", "-i", str(video), "-i", str(speech),
            "-map", "0:v:0", "-map", "1:a:0",
            "-filter:a", filter_chain,
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
            "-t", str(vd), "-movflags", "+faststart", str(output)
        ], check=True)
        print(f"Vídeo gerado: {output} ({vd:.1f}s), voz {ad:.1f}s")


if __name__ == "__main__":
    main()
