"""Проверка: чирканье спички об себя — кадры до/во время/после поджига."""
import asyncio, base64, json, subprocess, sys, time, urllib.request
from pathlib import Path

ROOT = Path(r"C:\Users\Ali PC\3DAngen")
sys.path.insert(0, str(ROOT / "tools"))
from render import find_browsers, free_port  # noqa

FILE = ROOT / "dist" / "matchbox.html"
OUT = Path(r"C:\Users\Ali PC\AppData\Local\Temp\3dangen")
OUT.mkdir(parents=True, exist_ok=True)

SHOTS = [(0.0, "before"), (0.35, "rake"), (0.55, "spark"), (1.2, "lit"), (2.2, "burning")]


async def main():
    import websockets
    port = free_port(9888)
    profile = OUT / "prof_strike"
    profile.mkdir(parents=True, exist_ok=True)
    proc = None
    for browser in find_browsers():
        cand = subprocess.Popen([browser, "--headless=new", f"--remote-debugging-port={port}",
                                 f"--user-data-dir={profile}", "--no-first-run", "--no-default-browser-check",
                                 "--enable-unsafe-swiftshader", "--hide-scrollbars",
                                 "--window-size=620,760", "about:blank"],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        t0 = time.time()
        ok = False
        while time.time() - t0 < 12:
            try:
                tabs = json.loads(urllib.request.urlopen(f"http://127.0.0.1:{port}/json/list", timeout=2).read())
                if any(t.get("type") == "page" for t in tabs):
                    ok = True
                    break
            except Exception:
                pass
            await asyncio.sleep(0.4)
        if ok:
            proc = cand
            break
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
                       {"width": 620, "height": 760, "deviceScaleFactor": 1, "mobile": False})
            await call("Page.navigate", {"url": FILE.as_uri()})
            await asyncio.sleep(2.0)

            shot = await call("Page.captureScreenshot", {"format": "png"})
            (OUT / "strike_before.png").write_bytes(base64.b64decode(shot["result"]["data"]))
            print("снято before")

            await call("Runtime.evaluate", {"expression": "document.querySelector('[data-act=strike]').click()"})

            prev = 0.0
            for t, name in SHOTS[1:]:
                await asyncio.sleep(max(0.0, t - prev))
                prev = t
                shot = await call("Page.captureScreenshot", {"format": "png"})
                (OUT / f"strike_{name}.png").write_bytes(base64.b64decode(shot["result"]["data"]))
                print("снято", name)
    finally:
        proc.kill()


asyncio.run(main())
