#!/usr/bin/env python3
"""3DAngen — покадровый рендер сцены в набор картинок.

Как это работает:
  1. поднимается локальный WebSocket-сервер, который принимает кадры;
  2. запускается headless Chromium (Edge / Chrome / Brave / Chromium) с CDP;
  3. страница открывается с `?frames=1&fps=..&sec=..&port=..` — сцена сама
     прогоняет фиксированный таймлайн (dt = 1/120) и отдаёт кадры;
  4. кадры сохраняются в out/f_000.jpg, out/f_001.jpg, ...

Требования к сцене: у неё должен быть режим `?frames=1` (см.
src/mascot-on-stove — там объект `renderFrames`, который дергает
`canvas.toDataURL()` и отправляет кадр по WebSocket).

Использование:
    python tools/render.py dist/mascot-on-stove.html
    python tools/render.py dist/mascot-on-stove.html --fps 30 --sec 5 --w 1920 --h 1080
    python tools/render.py dist/mascot-on-stove.html --out frames --keep-browser
"""
from __future__ import annotations

import argparse
import asyncio
import base64
import json
import os
import shutil
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

BROWSER_CANDIDATES = [
    os.environ.get("CHROME_PATH", ""),
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
]


def find_browsers() -> list[str]:
    seen, out = set(), []
    for path in BROWSER_CANDIDATES:
        if path and path not in seen and Path(path).is_file():
            seen.add(path)
            out.append(path)
    if not out:
        sys.exit("ошибка: не найден Chromium-браузер. Укажите путь через CHROME_PATH.")
    return out


async def cdp_alive(debug_port: int, tries: int = 25) -> bool:
    for _ in range(tries):
        try:
            tabs = json.loads(urllib.request.urlopen(f"http://127.0.0.1:{debug_port}/json/list", timeout=2).read())
            if any(t.get("type") == "page" for t in tabs):
                return True
        except Exception:  # noqa: BLE001
            pass
        await asyncio.sleep(0.4)
    return False


def free_port(start: int) -> int:
    for port in range(start, start + 40):
        with socket.socket() as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    sys.exit("ошибка: не удалось найти свободный порт")


class FrameSink:
    """WebSocket-сервер, принимающий кадры вида `FRAME <i> data:image/jpeg;base64,...`."""

    def __init__(self, port: int, out_dir: Path):
        self.port = port
        self.out_dir = out_dir
        self.count = 0
        self.hello = False

    async def handle(self, ws):
        try:
            async for msg in ws:
                if isinstance(msg, bytes):
                    msg = msg.decode("utf-8", "ignore")
                if msg.startswith("HELLO"):
                    self.hello = True
                elif msg.startswith("FRAME "):
                    _, idx, payload = msg.split(" ", 2)
                    head, _, b64 = payload.partition(",")
                    ext = ".jpg" if "jpeg" in head else ".png"
                    (self.out_dir / f"f_{int(idx):03d}{ext}").write_bytes(base64.b64decode(b64))
                    self.count = max(self.count, int(idx) + 1)
        except Exception as exc:  # noqa: BLE001
            print(f"  ws: {exc!r}")

    async def serve(self, stop: asyncio.Future):
        import websockets

        async with websockets.serve(self.handle, "127.0.0.1", self.port, max_size=64 * 1024 * 1024):
            await stop


async def cdp_wait(debug_port: int, file_url: str, sink: FrameSink, deadline_s: float) -> bool:
    import websockets

    ws_url = None
    t0 = time.time()
    while time.time() - t0 < 30:
        try:
            tabs = json.loads(urllib.request.urlopen(f"http://127.0.0.1:{debug_port}/json/list", timeout=3).read())
            pages = [t for t in tabs if t.get("type") == "page"]
            if pages:
                ws_url = pages[0]["webSocketDebuggerUrl"]
                break
        except Exception:  # noqa: BLE001
            pass
        await asyncio.sleep(0.4)
    if not ws_url:
        print("ошибка: CDP не поднялся (браузер не отдаёт remote debugging)")
        return False

    mid = 0
    async with websockets.connect(ws_url, max_size=None, open_timeout=20) as ws:
        async def call(method: str, params: dict | None = None):
            nonlocal mid
            mid += 1
            await ws.send(json.dumps({"id": mid, "method": method, "params": params or {}}))
            while True:
                msg = json.loads(await ws.recv())
                if msg.get("id") == mid:
                    return msg

        await call("Page.enable")
        await call("Runtime.enable")
        await call("Page.navigate", {"url": file_url})

        t0 = time.time()
        while time.time() - t0 < deadline_s:
            res = await call("Runtime.evaluate", {"expression": "document.title", "returnByValue": True})
            title = res.get("result", {}).get("result", {}).get("value", "")
            if title.startswith("FRAMES_DONE"):
                return True
            if title.startswith("FRAME_ERR") or title.startswith("WS_FAIL"):
                print(f"  сцена сообщила: {title}")
                return False
            await asyncio.sleep(0.5)
    print("  таймаут ожидания кадров")
    return False


async def run(args) -> int:
    file = Path(args.file)
    if not file.is_absolute():
        file = (ROOT / file).resolve()
    if not file.is_file():
        sys.exit(f"ошибка: нет файла {file}")

    out_dir = Path(args.out)
    if not out_dir.is_absolute():
        out_dir = (ROOT / out_dir).resolve()
    if out_dir.exists() and args.clean:
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    ws_port = free_port(args.ws_port)
    browser_list = find_browsers()

    url = (
        file.as_uri()
        + f"?frames=1&fps={args.fps}&sec={args.sec}&port={ws_port}"
        + f"&w={args.w}&h={args.h}"
    )
    total = int(args.fps * args.sec)
    print(f"3DAngen render → {out_dir}")
    print(f"  сцена:   {file.name}")
    print(f"  кадров:  {total} ({args.fps} fps × {args.sec} c, {args.w}×{args.h})")
    print(f"  браузеры: {', '.join(Path(b).name for b in browser_list)}  (ws {ws_port})")

    sink = FrameSink(ws_port, out_dir)
    stop = asyncio.get_running_loop().create_future()
    server = asyncio.create_task(sink.serve(stop))

    proc = None
    debug_port = 0
    # перебираем браузеры: некоторые сборки (корпоративные политики) не отдают CDP
    for browser in browser_list:
        debug_port = free_port(args.debug_port)
        profile = out_dir / f".browser-profile-{debug_port}"
        profile.mkdir(exist_ok=True)
        cand = subprocess.Popen(
            [
                browser,
                "--headless=new",
                f"--remote-debugging-port={debug_port}",
                f"--user-data-dir={profile}",
                "--no-first-run",
                "--no-default-browser-check",
                "--enable-unsafe-swiftshader",
                "--disable-background-timer-throttling",
                "--disable-renderer-backgrounding",
                "--hide-scrollbars",
                f"--window-size={args.w},{args.h}",
                "about:blank",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if await cdp_alive(debug_port):
            proc = cand
            print(f"  CDP:     {Path(browser).name} (порт {debug_port})")
            break
        cand.kill()
        print(f"  CDP:     {Path(browser).name} — недоступен, пробуем следующий")

    ok = False
    try:
        if proc is not None:
            ok = await cdp_wait(debug_port, url, sink, deadline_s=args.timeout)
    finally:
        if proc is not None and not args.keep_browser:
            proc.kill()
            try:
                proc.wait(timeout=10)
            except Exception:  # noqa: BLE001
                pass
        stop.set_result(True)
        await asyncio.sleep(0.2)
        server.cancel()

    print(f"  получено кадров: {sink.count} / {total}")
    if not ok or sink.count < total:
        print("  рендер неполный — проверьте сцену и консоль браузера")
        return 1
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="3DAngen: рендер сцены в кадры")
    ap.add_argument("file", help="путь к собранной сцене (dist/*.html)")
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--sec", type=float, default=5.0)
    ap.add_argument("--w", type=int, default=1280)
    ap.add_argument("--h", type=int, default=720)
    ap.add_argument("--out", default="frames")
    ap.add_argument("--ws-port", type=int, default=8766)
    ap.add_argument("--debug-port", type=int, default=9777)
    ap.add_argument("--timeout", type=float, default=600)
    ap.add_argument("--clean", action="store_true", default=True)
    ap.add_argument("--keep-browser", action="store_true")
    return asyncio.run(run(ap.parse_args()))


if __name__ == "__main__":
    raise SystemExit(main())
