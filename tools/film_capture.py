"""Покадровый съём фильма из сцены: tools/film_capture.py --frames 192 --fps 24"""
import argparse, asyncio, base64, json, subprocess, sys, time, urllib.request
from pathlib import Path

ROOT = Path(r"C:\Users\Ali PC\3DAngen")
sys.path.insert(0, str(ROOT / "tools"))
from render import find_browsers, free_port  # noqa


async def main(args):
    import websockets
    file = (ROOT / "dist" / args.file).resolve()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    port = free_port(9899)
    profile = out / ".profile"
    profile.mkdir(parents=True, exist_ok=True)

    proc = None
    for browser in find_browsers():
        cand = subprocess.Popen([browser, "--headless=new", f"--remote-debugging-port={port}",
                                 f"--user-data-dir={profile}", "--no-first-run", "--no-default-browser-check",
                                 "--enable-unsafe-swiftshader", "--hide-scrollbars",
                                 f"--window-size={args.w},{args.h}", "about:blank"],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        t0 = time.time(); ok = False
        while time.time() - t0 < 15:
            try:
                tabs = json.loads(urllib.request.urlopen(f"http://127.0.0.1:{port}/json/list", timeout=2).read())
                if any(t.get("type") == "page" for t in tabs):
                    ok = True; break
            except Exception:
                pass
            await asyncio.sleep(0.4)
        if ok:
            proc = cand; break
        cand.kill()
    if not proc:
        sys.exit("нет браузера")

    tabs = json.loads(urllib.request.urlopen(f"http://127.0.0.1:{port}/json/list", timeout=5).read())
    page = [t for t in tabs if t.get("type") == "page"][0]
    try:
        async with websockets.connect(page["webSocketDebuggerUrl"], max_size=None) as ws:
            mid = 0

            async def call(method, params=None):
                nonlocal mid
                mid += 1
                await ws.send(json.dumps({"id": mid, "method": method, "params": params or {}}))
                while True:
                    msg = json.loads(await ws.recv())
                    if msg.get("id") == mid:
                        return msg

            await call("Page.enable")
            await call("Runtime.enable")
            await call("Emulation.setDeviceMetricsOverride",
                       {"width": args.w, "height": args.h, "deviceScaleFactor": 1, "mobile": False})
            await call("Page.navigate", {"url": file.as_uri() + "?film=1"})
            await asyncio.sleep(2.5)

            r = await call("Runtime.evaluate", {"expression": "typeof window.__seek", "returnByValue": True})
            if r["result"]["result"].get("value") != "function":
                print("нет __seek — сцена не в режиме фильма")
                return 1

            t0 = time.time()
            for i in range(args.frames):
                await call("Runtime.evaluate",
                           {"expression": f"window.__seek({(i / args.fps):.4f})", "returnByValue": True})
                shot = await call("Page.captureScreenshot", {"format": "png"})
                (out / f"f_{i:04d}.png").write_bytes(base64.b64decode(shot["result"]["data"]))
                if i % 24 == 0:
                    print(i, "из", args.frames, "%.1f с" % (time.time() - t0))
    finally:
        proc.kill()

    print("готово:", out, args.frames, "кадров")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default="table.html")
    ap.add_argument("--frames", type=int, default=192)
    ap.add_argument("--fps", type=int, default=24)
    ap.add_argument("--w", type=int, default=1280)
    ap.add_argument("--h", type=int, default=720)
    ap.add_argument("--out", default=str(Path(r"C:\Users\Ali PC\AppData\Local\Temp\3dangen\film")))
    raise SystemExit(asyncio.run(main(ap.parse_args())))
