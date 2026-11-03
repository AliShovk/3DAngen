#!/usr/bin/env python3
"""3DAngen — стоп-кадр сцены (постер) через headless Chromium + CDP.

    python tools/still.py dist/cigar.html --out examples/cigar-poster.png
    python tools/still.py dist/cigar.html --w 1600 --h 1000 --wait 3.5
"""
from __future__ import annotations

import argparse
import asyncio
import base64
import json
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

from render import find_browsers, free_port  # noqa: E402


async def shoot(args) -> int:
    file = Path(args.file)
    if not file.is_absolute():
        file = (ROOT / file).resolve()
    if not file.is_file():
        sys.exit(f"ошибка: нет файла {file}")
    out = Path(args.out)
    if not out.is_absolute():
        out = (ROOT / out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    import websockets

    proc = None
    port = 0
    for browser in find_browsers():
        port = free_port(args.debug_port)
        profile = out.parent / f".still-profile-{port}"
        profile.mkdir(parents=True, exist_ok=True)
        cand = subprocess.Popen([
            browser, "--headless=new", f"--remote-debugging-port={port}",
            f"--user-data-dir={profile}", "--no-first-run", "--no-default-browser-check",
            "--enable-unsafe-swiftshader", "--hide-scrollbars",
            f"--window-size={args.w},{args.h}", "about:blank",
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        ok = False
        t0 = time.time()
        while time.time() - t0 < 12:
            try:
                tabs = json.loads(urllib.request.urlopen(f"http://127.0.0.1:{port}/json/list", timeout=2).read())
                if any(t.get("type") == "page" for t in tabs):
                    ok = True
                    break
            except Exception:  # noqa: BLE001
                pass
            await asyncio.sleep(0.4)
        if ok:
            proc = cand
            break
        cand.kill()

    if proc is None:
        sys.exit("ошибка: ни один браузер не отдал DevTools-порт")

    try:
        tabs = json.loads(urllib.request.urlopen(f"http://127.0.0.1:{port}/json/list", timeout=5).read())
        page = [t for t in tabs if t.get("type") == "page"][0]
        mid = 0
        errs = []
        async with websockets.connect(page["webSocketDebuggerUrl"], max_size=None) as ws:
            async def call(method, params=None):
                nonlocal mid
                mid += 1
                await ws.send(json.dumps({"id": mid, "method": method, "params": params or {}}))
                while True:
                    msg = json.loads(await ws.recv())
                    if msg.get("id") == mid:
                        return msg
                    m = msg.get("method")
                    if m == "Runtime.exceptionThrown":
                        det = msg["params"]["exceptionDetails"]
                        errs.append("JS: " + str(det.get("text")) + " " +
                                    str((det.get("exception") or {}).get("description", ""))[:400])
                    elif m == "Log.entryAdded" and msg["params"]["entry"].get("level") in ("error", "warning"):
                        errs.append("LOG: " + msg["params"]["entry"].get("text", "")[:300])

            await call("Page.enable")
            await call("Runtime.enable")
            await call("Log.enable")
            await call("Emulation.setDeviceMetricsOverride",
                       {"width": args.w, "height": args.h, "deviceScaleFactor": 1, "mobile": False})
            await call("Page.navigate", {"url": file.as_uri()})
            await asyncio.sleep(args.wait)
            shot = await call("Page.captureScreenshot", {"format": "png", "captureBeyondViewport": False})
            data = shot["result"]["data"]
            out.write_bytes(base64.b64decode(data))
    finally:
        proc.kill()

    if errs:
        print("ошибки страницы:")
        for e in errs[:12]:
            print("  " + e)

    print(f"готово: {out} ({out.stat().st_size / 1024:.0f} KB, {args.w}×{args.h})")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="3DAngen: стоп-кадр сцены")
    ap.add_argument("file")
    ap.add_argument("--out", default="examples/poster.png")
    ap.add_argument("--w", type=int, default=1280)
    ap.add_argument("--h", type=int, default=960)
    ap.add_argument("--wait", type=float, default=3.0, help="секунд до снимка (анимация/прогрев)")
    ap.add_argument("--debug-port", type=int, default=9811)
    return asyncio.run(shoot(ap.parse_args()))


if __name__ == "__main__":
    raise SystemExit(main())
