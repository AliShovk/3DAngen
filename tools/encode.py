#!/usr/bin/env python3
"""3DAngen — сборка кадров в видео через ffmpeg.

Использование:
    python tools/encode.py                       # frames/ -> dist/video.mp4
    python tools/encode.py --fps 60 --crf 17
    python tools/encode.py --out dist/scene.mp4 --gif
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def frames_in(folder: Path) -> tuple[Path, str]:
    for ext in ("jpg", "png"):
        files = sorted(folder.glob(f"f_*.{ext}"))
        if files:
            return folder / f"f_%03d.{ext}", ext
    sys.exit(f"ошибка: в {folder} нет кадров f_*.jpg / f_*.png")


def main() -> int:
    ap = argparse.ArgumentParser(description="3DAngen: кадры -> mp4")
    ap.add_argument("--frames", default="frames")
    ap.add_argument("--out", default="dist/video.mp4")
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--crf", type=int, default=19)
    ap.add_argument("--gif", action="store_true", help="дополнительно собрать GIF")
    args = ap.parse_args()

    if not shutil.which("ffmpeg"):
        sys.exit("ошибка: ffmpeg не найден в PATH")

    folder = Path(args.frames)
    if not folder.is_absolute():
        folder = ROOT / folder
    pattern, ext = frames_in(folder)
    out = Path(args.out)
    if not out.is_absolute():
        out = ROOT / out
    out.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "image2", "-framerate", str(args.fps), "-i", str(pattern),
        "-c:v", "libx264", "-preset", "slow", "-crf", str(args.crf),
        "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(out),
    ]
    print(" ".join(cmd))
    subprocess.run(cmd, check=True)
    size = out.stat().st_size / 1024 / 1024
    print(f"готово: {out} ({size:.1f} МБ, {ext}-кадры)")

    if args.gif:
        gif = out.with_suffix(".gif")
        subprocess.run([
            "ffmpeg", "-y", "-loglevel", "error", "-i", str(out),
            "-vf", "fps=20,scale=640:-1:flags=lanczos,split[a][b];[a]palettegen[p];[b][p]paletteuse",
            str(gif),
        ], check=True)
        print(f"gif:  {gif}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
