import io, sys

p = 'src/table/index.html'
s = io.open(p, encoding='utf-8').read()

# --- 1. текстуры еды
tex = r'''/* ---------------------------------------------------------------- текстуры еды */
function breadTex(){
  const {c, g} = cv(512, 512);
  g.fillStyle = '#d9a35c'; g.fillRect(0, 0, 512, 512);
  for (let i = 0; i < 420; i++){
    g.fillStyle = 'rgba(' + (120 + Math.random() * 60 | 0) + ',' + (78 + Math.random() * 40 | 0) + ',' + (34 + Math.random() * 26 | 0) + ',' + (.12 + Math.random() * .35) + ')';
    g.beginPath();
    g.ellipse(Math.random() * 512, Math.random() * 512, 1 + Math.random() * 4, 1 + Math.random() * 3, Math.random() * 3, 0, Math.PI * 2);
    g.fill();
  }
  for (let i = 0; i < 90; i++){
    g.fillStyle = 'rgba(255,246,224,' + (.1 + Math.random() * .25) + ')';
    g.beginPath(); g.ellipse(Math.random() * 512, Math.random() * 512, 3 + Math.random() * 8, 2 + Math.random() * 5, 0, 0, Math.PI * 2); g.fill();
  }
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}
function breadInTex(){
  const {c, g} = cv(512, 512);
  g.fillStyle = '#f4e2bb'; g.fillRect(0, 0, 512, 512);
  for (let i = 0; i < 320; i++){
    g.fillStyle = 'rgba(214,186,140,' + (.15 + Math.random() * .4) + ')';
    g.beginPath(); g.ellipse(Math.random() * 512, Math.random() * 512, 1 + Math.random() * 5, 1 + Math.random() * 4, 0, 0, Math.PI * 2); g.fill();
  }
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}
function cheeseTex(){
  const {c, g} = cv(512, 512);
  g.fillStyle = '#ffc63d'; g.fillRect(0, 0, 512, 512);
  for (let i = 0; i < 26; i++){
    g.fillStyle = 'rgba(226,158,30,.55)';
    g.beginPath(); g.ellipse(Math.random() * 512, Math.random() * 512, 6 + Math.random() * 16, 5 + Math.random() * 12, Math.random() * 3, 0, Math.PI * 2); g.fill();
  }
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}
function orangeTex(){
  const {c, g} = cv(512, 512);
  g.fillStyle = '#f79516'; g.fillRect(0, 0, 512, 512);
  for (let i = 0; i < 2600; i++){
    g.fillStyle = 'rgba(' + (200 + Math.random() * 45 | 0) + ',' + (120 + Math.random() * 50 | 0) + ',20,' + (.1 + Math.random() * .3) + ')';
    g.beginPath(); g.arc(Math.random() * 512, Math.random() * 512, .8 + Math.random() * 2.2, 0, Math.PI * 2); g.fill();
  }
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}
function coffeeTex(){
  const {c, g} = cv(256, 256);
  g.fillStyle = '#3a1f10'; g.fillRect(0, 0, 256, 256);
  const grd = g.createRadialGradient(120, 110, 20, 128, 128, 130);
  grd.addColorStop(0, 'rgba(150,96,52,.55)');
  grd.addColorStop(1, 'rgba(150,96,52,0)');
  g.fillStyle = grd; g.fillRect(0, 0, 256, 256);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

'''
s = s.replace("/* ---------------------------------------------------------------- материалы окружения (реализм) */", tex + "/* ---------------------------------------------------------------- материалы окружения (реализм) */", 1)

# --- 2. еда на PBR
reps = [
("  bread:   toon(0xdca85f),", "  bread:   new THREE.MeshStandardMaterial({map: breadTex(), roughness:.85, metalness:0}),"),
("  breadIn: toon(0xf3dcae),", "  breadIn: new THREE.MeshStandardMaterial({map: breadInTex(), roughness:.9, metalness:0}),"),
("  cheese:  toon(0xffc23c),", "  cheese:  new THREE.MeshStandardMaterial({map: cheeseTex(), roughness:.45, metalness:0}),"),
("  tomato:  toon(0xe5432f),", "  tomato:  new THREE.MeshStandardMaterial({color:0xd2352a, roughness:.24, metalness:0}),"),
("  lettuce: toon(0x64c04a),", "  lettuce: new THREE.MeshStandardMaterial({color:0x63c247, roughness:.7, metalness:0}),"),
("  apple:   toon(0xe23434),", "  apple:   new THREE.MeshStandardMaterial({color:0xc21f26, roughness:.18, metalness:0}),"),
("  orange:  toon(0xff9a1f),", "  orange:  new THREE.MeshStandardMaterial({map: orangeTex(), roughness:.5, metalness:0}),"),
("  leaf:    toon(0x3f9d3a),", "  leaf:    new THREE.MeshStandardMaterial({color:0x3f9d3a, roughness:.55, metalness:0}),"),
("  mug:     toon(0x4a7fd4),", "  mug:     new THREE.MeshStandardMaterial({color:0x2f6fb5, roughness:.16, metalness:0}),"),
("  coffee:  toon(0x4a2a16),", "  coffee:  new THREE.MeshStandardMaterial({map: coffeeTex(), roughness:.32, metalness:0}),"),
("  steel:   toon(0xc9d2da),", "  steel:   new THREE.MeshStandardMaterial({color:0xd9e0e6, roughness:.16, metalness:.95}),"),
("  bowl:    toon(0x6ec1e6),", "  bowl:    new THREE.MeshStandardMaterial({color:0x5aa9d6, roughness:.18, metalness:0}),"),
("  porcelain: toon(0xfefaf2),", "  porcelain: new THREE.MeshStandardMaterial({color:0xfdfbf6, roughness:.14, metalness:0}),"),
("  wood:    toon(0xffffff, {map: woodTexture()}),", "  wood:    new THREE.MeshStandardMaterial({map: woodTableTex(), roughness:.55, metalness:0}),"),
]
for o, n in reps:
    if o not in s:
        print('NOT FOUND:', o[:60]); sys.exit(1)
    s = s.replace(o, n, 1)

# envMapIntensity для еды
s = s.replace("Object.keys(R).forEach(function(k){ if (R[k].isMeshStandardMaterial) R[k].envMapIntensity = .75; });",
              "Object.keys(R).forEach(function(k){ if (R[k].isMeshStandardMaterial) R[k].envMapIntensity = .75; });\nObject.keys(M).forEach(function(k){ if (M[k] && M[k].isMeshStandardMaterial) M[k].envMapIntensity = .8; });", 1)

# --- 3. стол больше, камера ближе
reps2 = [
("const TABLE = {w: 3.4, d: 2.3, t: .09, h: 1.02};", "const TABLE = {w: 3.9, d: 2.55, t: .10, h: 1.02};"),
("const target = new THREE.Vector3(0, .78, 0);", "const target = new THREE.Vector3(0, .52, 0);"),
("const cam = {az:.34, pol:1.30, rad:7.6, taz:.34, tpol:1.30, trad:7.6};",
 "const cam = {az:.36, pol:1.26, rad:6.5, taz:.36, tpol:1.26, trad:6.5};"),
]
for o, n in reps2:
    if o not in s:
        print('NOT FOUND:', o[:60]); sys.exit(1)
    s = s.replace(o, n, 1)

io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('food pbr + bigger table')
