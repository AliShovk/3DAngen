import io

p = 'tools/film_capture.py'
s = io.open(p, encoding='utf-8').read()

s = s.replace('await call("Page.navigate", {"url": file.as_uri() + "?film=1"})',
              'await call("Page.navigate", {"url": file.as_uri() + "?" + args.query})', 1)

old_args = '    ap.add_argument("--out", default=str(Path(r"C:\\Users\\Ali PC\\AppData\\Local\\Temp\\3dangen\\film")))'
new_args = (old_args +
            '\n    ap.add_argument("--query", default="film=1")'
            '\n    ap.add_argument("--times", default="")')
if old_args in s:
    s = s.replace(old_args, new_args, 1)

anchor = """            t0 = time.time()
            for i in range(args.frames):"""
insert = """            if args.times:
                times = [float(x) for x in args.times.split(",")]
                for i, tt in enumerate(times):
                    await call("Runtime.evaluate", {"expression": "window.__seek(%.3f)" % tt, "returnByValue": True})
                    shot = await call("Page.captureScreenshot", {"format": "png"})
                    (out / ("t_%02d_%.1f.png" % (i, tt))).write_bytes(base64.b64decode(shot["result"]["data"]))
                    print("t=", tt)
                return 0

""" + anchor
if anchor in s:
    s = s.replace(anchor, insert, 1)

io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('patched capture')
