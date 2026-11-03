"""Печатает мировые координаты кисти и головки спички, чтобы понять фактическое направление."""
import asyncio, json, subprocess, sys, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "3DAngen" / "tools"))
from render import find_browsers, free_port  # noqa

FILE = Path(r"C:\Users\Ali PC\3DAngen\dist\matchbox.html")


async def main():
    import websockets
    port = free_port(9855)
    profile = Path(r"C:\Users\Ali PC\AppData\Local\Temp\3dangen\prof2")
    profile.mkdir(parents=True, exist_ok=True)
    proc = None
    for browser in find_browsers():
        cand = subprocess.Popen([browser, "--headless=new", f"--remote-debugging-port={port}",
                                 f"--user-data-dir={profile}", "--no-first-run", "--no-default-browser-check",
                                 "--enable-unsafe-swiftshader", "--hide-scrollbars",
                                 "--window-size=900,1000", "about:blank"],
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
            await call("Page.navigate", {"url": FILE.as_uri()})
            await asyncio.sleep(2.0)
            expr = """(() => {
              const d = window.__dbg; if (!d) return 'no dbg';
              const out = {};
              ['handR','heldMatch','heldHead'].forEach(n => {
                const o = d.scene.getObjectByName(n);
                if (!o) { out[n] = null; return; }
                const p = new d.THREE.Vector3(); o.getWorldPosition(p);
                out[n] = [ +p.x.toFixed(3), +p.y.toFixed(3), +p.z.toFixed(3) ];
              });
              const h = d.scene.getObjectByName('heldMatch');
              if (h){
                const a = new d.THREE.Vector3(), b = new d.THREE.Vector3();
                h.getWorldPosition(a);
                const hd = h.getObjectByName('heldHead');
                if (hd){ hd.getWorldPosition(b); out.dir = [ +(b.x-a.x).toFixed(3), +(b.y-a.y).toFixed(3), +(b.z-a.z).toFixed(3) ]; }
              }
              return JSON.stringify(out);
            })()"""
            r = await call("Runtime.evaluate", {"expression": expr, "returnByValue": True})
            print(r["result"]["result"].get("value"))
    finally:
        proc.kill()

asyncio.run(main())
