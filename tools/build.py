#!/usr/bin/env python3
"""3DAngen — сборщик однофайловых HTML-сцен.

Встраивает vendor/three.min.js в src/<scene>/index.html вместо маркера
`/*__THREE__*/` и кладёт готовый файл в dist/<scene>.html.

Использование:
    python tools/build.py                 # собрать все сцены
    python tools/build.py gas-stove       # собрать одну сцену
    python tools/build.py --list          # список сцен
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MARKER = "/*__THREE__*/"


def scenes() -> list[str]:
    return sorted(p.name for p in (ROOT / "src").iterdir() if (p / "index.html").is_file())


def three_source() -> str:
    vendor = ROOT / "vendor" / "three.min.js"
    if not vendor.is_file():
        sys.exit("ошибка: нет vendor/three.min.js (скачайте three r158 build/three.min.js)")
    return vendor.read_text(encoding="utf-8")


def build_one(name: str, three: str) -> tuple[Path, int]:
    src = ROOT / "src" / name / "index.html"
    if not src.is_file():
        sys.exit(f"ошибка: нет сцены «{name}» ({src})")
    html = src.read_text(encoding="utf-8")
    if MARKER not in html:
        sys.exit(f"ошибка: в {src} нет маркера {MARKER}")
    out_html = html.replace(MARKER, three, 1)

    # проверка, что внешних зависимостей не осталось
    ext = re.findall(r"<script[^>]+src=", out_html)
    if ext:
        sys.exit(f"ошибка: в {src} остались внешние скрипты: {len(ext)}")

    dist = ROOT / "dist" / f"{name}.html"
    dist.parent.mkdir(exist_ok=True)
    dist.write_text(out_html, encoding="utf-8", newline="\n")
    return dist, dist.stat().st_size


def main() -> int:
    ap = argparse.ArgumentParser(description="Сборка однофайловых HTML-сцен 3DAngen")
    ap.add_argument("scene", nargs="?", help="имя сцены (по умолчанию все)")
    ap.add_argument("--list", action="store_true", help="показать сцены")
    args = ap.parse_args()

    names = scenes()
    if args.list:
        print("\n".join(names))
        return 0
    if args.scene:
        names = [args.scene]

    three = three_source()
    total = 0
    for name in names:
        dist, size = build_one(name, three)
        total += 1
        print(f"  {name:20s} -> {dist.relative_to(ROOT)}  ({size / 1024:.0f} KB)")
    print(f"готово: {total} сцен(а) в dist/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
