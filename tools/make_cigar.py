import io, os, re, sys

src = 'src/mascot/index.html'
dst = 'src/cigar/index.html'
os.makedirs('src/cigar', exist_ok=True)
s = io.open(src, encoding='utf-8').read()

reps = []

# --- фон: белая студия ---
reps.append(("    --bg1:#ffe9c7;\n    --bg2:#ffe0ef;\n    --bg3:#dfe8ff;",
             "    --bg1:#ffffff;\n    --bg2:#fbf9f5;\n    --bg3:#efeae1;"))

# --- заголовок ---
reps.append(('<div class="title">Персонаж <em>3D</em></div>',
             '<div class="title">Сигара <em>3D</em></div>'))
reps.append(('<div class="sub">Мультяшный маскот · toon-шейдинг</div>',
             '<div class="sub">Мультяшный маскот · табачный лист, пепел, toon-шейдинг</div>'))

# --- текстура: табачная обёртка вместо бумаги ---
reps.append(("""  const grd = g.createLinearGradient(0, 0, 512, 0);
  grd.addColorStop(0, '#ffe86a'); grd.addColorStop(.45, '#ffcb33');
  grd.addColorStop(.75, '#ffa81a'); grd.addColorStop(1, '#f2870c');""",
"""  const grd = g.createLinearGradient(0, 0, 512, 0);
  grd.addColorStop(0, '#9c4d0e'); grd.addColorStop(.16, '#f0911c');
  grd.addColorStop(.42, '#ffcb4d'); grd.addColorStop(.58, '#ffe37f');
  grd.addColorStop(.8, '#ffa428'); grd.addColorStop(1, '#a4510c');"""))
reps.append(("    g.strokeStyle = 'rgba(' + (Math.random() < .5 ? '150,80,8,' : '255,252,230,') + (.06 + Math.random() * .2) + ')';",
             "    g.strokeStyle = 'rgba(' + (Math.random() < .5 ? '112,56,6,' : '255,240,190,') + (.08 + Math.random() * .22) + ')';"))

# --- палитра: пепел вместо «бошки» ---
reps.append(("""  cherryA: toon(0x4a2a1c),
  cherryB: toon(0x33203a),
  cherryC: toon(0x5c3320),
  cherryD: toon(0x3b1f28),""",
"""  cherryA: toon(0x2c1a2e),
  cherryB: toon(0x170f19),
  cherryC: toon(0x3d2431),
  cherryD: toon(0x5a3018),"""))
reps.append(("  shoe:    toon(0x1c1b22),", "  shoe:    toon(0x2b1b12),"))

# --- тело: сигара (выше, меньше конусность) ---
reps.append(("const bodyGeo = new THREE.CylinderGeometry(.185, .112, 1.05, 30, 12);",
             "const bodyGeo = new THREE.CylinderGeometry(.178, .120, 1.14, 34, 16);"))
reps.append(("""    const y = p.getY(i);
    const t = (y + .525) / 1.05;
    p.setX(i, p.getX(i) + Math.sin(t * Math.PI) * .014);
    p.setZ(i, p.getZ(i) * (.93 + .07 * t));""",
"""    const y = p.getY(i);
    const t = (y + .57) / 1.14;
    p.setX(i, p.getX(i) + Math.sin(t * Math.PI) * .010);
    p.setZ(i, p.getZ(i) * (.965 + .035 * t));"""))
reps.append(("body.position.y = .925;", "body.position.y = .955;"))
reps.append(("""function bodyRadius(y){
  const t = Math.min(1, Math.max(0, (y - .40) / 1.05));
  return .112 + (.185 - .112) * t;
}""",
"""function bodyRadius(y){
  const t = Math.min(1, Math.max(0, (y - .385) / 1.14));
  return .120 + (.178 - .120) * t;
}"""))

# --- пепел: купол выше, мелкие поры ---
reps.append(("cherry.position.y = 1.44;", "cherry.position.y = 1.525;"))
reps.append(("const dome = new THREE.Mesh(new THREE.SphereGeometry(.188, 26, 14, 0, Math.PI * 2, 0, Math.PI * .58), M.cherryA);",
             "const dome = new THREE.Mesh(new THREE.SphereGeometry(.176, 30, 16, 0, Math.PI * 2, 0, Math.PI * .62), M.cherryA);"))
reps.append(("""for (let i = 0; i < 20; i++){
  const a = i / 20 * Math.PI * 2 + Math.random() * .4;
  const rad = .19 * (.35 + Math.random() * .62);
  const h = .19 * Math.sqrt(Math.max(0, 1 - Math.pow(rad / .19, 2))) * .95;
  const b = ball(.028 + Math.random() * .036, budMats[i % budMats.length], 12);
  b.position.set(Math.cos(a) * rad, h * (.6 + Math.random() * .5), Math.sin(a) * rad);
  add(b, cherry);
}""",
"""for (let i = 0; i < 34; i++){
  const a = i / 34 * Math.PI * 2 + Math.random() * .5;
  const rad = .175 * (.25 + Math.random() * .72);
  const h = .175 * Math.sqrt(Math.max(0, 1 - Math.pow(rad / .175, 2))) * .95;
  const b = ball(.018 + Math.random() * .030, budMats[i % budMats.length], 12);
  b.position.set(Math.cos(a) * rad, h * (.55 + Math.random() * .55), Math.sin(a) * rad);
  add(b, cherry);
}
// поры в пепле
for (let i = 0; i < 16; i++){
  const a = Math.random() * Math.PI * 2;
  const rad = .02 + Math.random() * .13;
  const h = .175 * Math.sqrt(Math.max(0, 1 - Math.pow(rad / .175, 2))) * .9;
  const p = ball(.008 + Math.random() * .012, M.cherryB, 8);
  p.position.set(Math.cos(a) * rad, h + .012, Math.sin(a) * rad);
  cherry.add(p);
}"""))

# --- ухмылка: шире, два ряда зубов ---
reps.append(("""  s.moveTo(-.098, .026);
  s.quadraticCurveTo(0, -.115, .098, .026);
  s.quadraticCurveTo(0, -.052, -.098, .026);""",
"""  s.moveTo(-.120, .030);
  s.quadraticCurveTo(0, -.140, .120, .026);
  s.quadraticCurveTo(0, -.060, -.120, .030);"""))
reps.append(("""  // зубы
  for (let i = 0; i < 2; i++){
    const t = rbox(.072, .042, .014, .010, M.white, (i ? 1 : -1) * .040, -.030, .014);
    t.rotation.z = (i ? -1 : 1) * .10;
    mouth.add(t);
  }""",
"""  // верхний ряд зубов
  for (let i = 0; i < 3; i++){
    const t = rbox(.054, .042, .014, .009, M.white, (i - 1) * .058, -.032, .014);
    t.rotation.z = (i - 1) * -.05;
    mouth.add(t);
  }
  // нижний ряд
  for (let i = 0; i < 2; i++){
    const b = rbox(.050, .026, .012, .008, M.white, (i ? .029 : -.029), -.086, .012);
    mouth.add(b);
  }"""))
reps.append(("  const lip = new THREE.Mesh(new THREE.TorusGeometry(.098, .010, 8, 26, Math.PI * .92), M.black);",
             "  const lip = new THREE.Mesh(new THREE.TorusGeometry(.120, .009, 8, 28, Math.PI * .94), M.black);"))

# --- кеды: три шнурка и толще подошва ---
reps.append(("  for (let i = 0; i < 4; i++){\n    const l = rbox(.128, .022, .030, .010, M.white, 0, .198 + i * .018, .092 - i * .012, g);",
             "  for (let i = 0; i < 3; i++){\n    const l = rbox(.132, .024, .032, .010, M.white, 0, .200 + i * .022, .094 - i * .014, g);"))
reps.append(("  rbox(.215, .062, .385, .032, M.cream, 0, .031, .030, g);",
             "  rbox(.220, .072, .392, .034, M.cream, 0, .036, .030, g);"))

# --- камера чуть дальше: персонаж выше ---
reps.append(("const cam = {az:.20, pol:1.36, rad:4.05, taz:.20, tpol:1.36, trad:4.05};",
             "const cam = {az:.20, pol:1.40, rad:3.95, taz:.20, tpol:1.40, trad:3.95};"))

for old, new in reps:
    if old not in s:
        sys.exit('NOT FOUND:\n' + old[:160])
    s = s.replace(old, new, 1)

io.open(dst, 'w', encoding='utf-8', newline='\n').write(s)
print('создана сцена src/cigar/index.html', len(s), 'байт')
