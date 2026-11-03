import io, sys

p = 'src/table/index.html'
s = io.open(p, encoding='utf-8').read()

start = s.index("/* ---------------------------------------------------------------- стол */")
end = s.index("/* ---------------------------------------------------------------- еда */")

new = r'''/* ---------------------------------------------------------------- текстуры окружения */
function woodTableTex(){
  const {c, g} = cv(1024, 1024);
  g.fillStyle = '#b8814a'; g.fillRect(0, 0, 1024, 1024);
  const plank = 1024 / 5;
  for (let i = 0; i < 5; i++){
    const y0 = i * plank;
    g.fillStyle = i % 2 ? '#b07a44' : '#bf8a54';
    g.fillRect(0, y0, 1024, plank - 3);
    g.strokeStyle = 'rgba(56,32,12,.5)'; g.lineWidth = 3;
    g.strokeRect(0, y0, 1024, plank - 3);
    for (let k = 0; k < 90; k++){
      g.strokeStyle = 'rgba(88,54,24,' + (.035 + Math.random() * .09) + ')';
      g.lineWidth = 1 + Math.random() * 2.4;
      g.beginPath();
      const yy = y0 + Math.random() * plank;
      g.moveTo(0, yy);
      g.bezierCurveTo(300, yy + (Math.random() - .5) * 14, 700, yy + (Math.random() - .5) * 14, 1024, yy);
      g.stroke();
    }
    for (let k = 0; k < 3; k++){
      g.strokeStyle = 'rgba(70,42,16,.25)'; g.lineWidth = 2;
      g.beginPath(); g.ellipse(Math.random() * 1024, y0 + Math.random() * plank, 16 + Math.random() * 26, 5 + Math.random() * 6, 0, 0, Math.PI * 2); g.stroke();
    }
  }
  const grd = g.createLinearGradient(0, 0, 0, 1024);
  grd.addColorStop(0, 'rgba(255,235,205,.22)');
  grd.addColorStop(.45, 'rgba(255,255,255,0)');
  grd.addColorStop(1, 'rgba(60,35,12,.18)');
  g.fillStyle = grd; g.fillRect(0, 0, 1024, 1024);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  t.anisotropy = 8;
  return t;
}
function marbleTex(){
  const {c, g} = cv(1024, 512);
  g.fillStyle = '#efe9df'; g.fillRect(0, 0, 1024, 512);
  for (let i = 0; i < 26; i++){
    g.strokeStyle = 'rgba(' + (150 + Math.random() * 40 | 0) + ',' + (140 + Math.random() * 30 | 0) + ',' + (128 + Math.random() * 26 | 0) + ',' + (.12 + Math.random() * .28) + ')';
    g.lineWidth = .6 + Math.random() * 2.4;
    g.beginPath();
    let x = Math.random() * 1024, y = Math.random() * 512;
    g.moveTo(x, y);
    for (let k = 0; k < 6; k++){
      x += (Math.random() - .5) * 260; y += (Math.random() - .5) * 150;
      g.lineTo(x, y);
    }
    g.stroke();
  }
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.repeat.set(3, 1);
  t.anisotropy = 8;
  return t;
}
function tileTex(){
  const {c, g} = cv(512, 512);
  g.fillStyle = '#dfe6e2'; g.fillRect(0, 0, 512, 512);
  const n = 4, cell = 512 / n;
  for (let i = 0; i < n; i++){
    for (let j = 0; j < n; j++){
      const shade = 236 + Math.random() * 14 | 0;
      g.fillStyle = 'rgb(' + shade + ',' + (shade - 4) + ',' + (shade - 10) + ')';
      g.fillRect(i * cell + 3, j * cell + 3, cell - 6, cell - 6);
      g.fillStyle = 'rgba(255,255,255,.5)';
      g.fillRect(i * cell + 3, j * cell + 3, cell - 6, 6);
    }
  }
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.repeat.set(6, 2);
  t.anisotropy = 8;
  return t;
}
function parquetTex(){
  const {c, g} = cv(512, 512);
  g.fillStyle = '#9a6b40'; g.fillRect(0, 0, 512, 512);
  const row = 512 / 8;
  for (let i = 0; i < 8; i++){
    g.fillStyle = i % 2 ? '#8f6038' : '#a07246';
    g.fillRect(0, i * row, 512, row - 2);
    g.strokeStyle = 'rgba(50,30,12,.45)'; g.lineWidth = 2;
    g.strokeRect(0, i * row, 512, row - 2);
    g.beginPath(); g.moveTo(((i * 97) % 512), i * row); g.lineTo(((i * 97) % 512), i * row + row); g.stroke();
  }
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.repeat.set(6, 6);
  return t;
}
function skyTex(){
  const {c, g} = cv(256, 256);
  const grd = g.createLinearGradient(0, 0, 0, 256);
  grd.addColorStop(0, '#cfe8ff');
  grd.addColorStop(.55, '#eaf4ff');
  grd.addColorStop(1, '#fdf6e6');
  g.fillStyle = grd; g.fillRect(0, 0, 256, 256);
  for (let i = 0; i < 8; i++){
    g.fillStyle = 'rgba(255,255,255,' + (.25 + Math.random() * .3) + ')';
    g.beginPath(); g.ellipse(Math.random() * 256, 60 + Math.random() * 90, 40 + Math.random() * 40, 14 + Math.random() * 12, 0, 0, Math.PI * 2); g.fill();
  }
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}
function envTexture(){
  const {c, g} = cv(512, 256);
  const grd = g.createLinearGradient(0, 0, 0, 256);
  grd.addColorStop(0, '#fff6e6');
  grd.addColorStop(.45, '#efe3d1');
  grd.addColorStop(1, '#8d8072');
  g.fillStyle = grd; g.fillRect(0, 0, 512, 256);
  g.fillStyle = '#fffdf2'; g.fillRect(50, 54, 130, 96);
  g.fillStyle = 'rgba(255,238,205,.9)'; g.fillRect(300, 40, 90, 60);
  const t = new THREE.CanvasTexture(c);
  t.mapping = THREE.EquirectangularReflectionMapping;
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

/* ---------------------------------------------------------------- материалы окружения (реализм) */
const R = {
  tableTop:  new THREE.MeshStandardMaterial({map: woodTableTex(), roughness:.42, metalness:0}),
  tableEdge: new THREE.MeshStandardMaterial({color:0x7d4f22, roughness:.55, metalness:0}),
  marble:    new THREE.MeshStandardMaterial({map: marbleTex(), roughness:.26, metalness:0}),
  cabinet:   new THREE.MeshStandardMaterial({color:0x2c6a6b, roughness:.52, metalness:0}),
  cabinetDoor: new THREE.MeshStandardMaterial({color:0x347b7c, roughness:.42, metalness:0}),
  handle:    new THREE.MeshStandardMaterial({color:0xd0a94e, roughness:.28, metalness:.9}),
  wall:      new THREE.MeshStandardMaterial({color:0xf2e9dd, roughness:.95, metalness:0}),
  tile:      new THREE.MeshStandardMaterial({map: tileTex(), roughness:.55, metalness:0}),
  floor:     new THREE.MeshStandardMaterial({map: parquetTex(), roughness:.6, metalness:0}),
  metal:     new THREE.MeshStandardMaterial({color:0xc3cad1, roughness:.3, metalness:.85}),
  fridge:    new THREE.MeshStandardMaterial({color:0xf3f5f6, roughness:.35, metalness:.15}),
  window:    new THREE.MeshBasicMaterial({map: skyTex()}),
  frame:     new THREE.MeshStandardMaterial({color:0xf6f1e6, roughness:.6}),
  lamp:      new THREE.MeshStandardMaterial({color:0x2b3a3a, roughness:.35, metalness:.7})
};
Object.keys(R).forEach(function(k){ if (R[k].isMeshStandardMaterial) R[k].envMapIntensity = .75; });

/* ---------------------------------------------------------------- стол */
const TABLE = {w: 3.4, d: 2.3, t: .09, h: 1.02};
const tableTop = 0;

const table = new THREE.Group();
scene.add(table);

const slab = new THREE.Mesh(new THREE.BoxGeometry(TABLE.w, TABLE.t, TABLE.d, 2, 1, 2), R.tableTop);
slab.position.y = -TABLE.t / 2;
slab.castShadow = true; slab.receiveShadow = true;
table.add(slab);

const trim = new THREE.Mesh(new THREE.BoxGeometry(TABLE.w + .03, .05, TABLE.d + .03), R.tableEdge);
trim.position.y = -TABLE.t - .022;
trim.castShadow = true; trim.receiveShadow = true;
table.add(trim);

(function legs(){
  const pts = [];
  for (let i = 0; i <= 14; i++){
    const t = i / 14;
    const r = .055 + Math.sin(t * Math.PI * 2.1) * .022 + (t < .12 ? .018 : 0) + (t > .88 ? .022 : 0);
    pts.push(new THREE.Vector2(r, -t * TABLE.h));
  }
  const geo = new THREE.LatheGeometry(pts, 18);
  [[-1, -1], [1, -1], [-1, 1], [1, 1]].forEach(function(c){
    const leg = new THREE.Mesh(geo, R.tableEdge);
    leg.position.set(c[0] * (TABLE.w / 2 - .20), -TABLE.t - .04, c[1] * (TABLE.d / 2 - .18));
    leg.castShadow = true; leg.receiveShadow = true;
    table.add(leg);
  });
})();

[[-1], [1]].forEach(function(v){
  const bar = new THREE.Mesh(new THREE.BoxGeometry(TABLE.w - .5, .055, .055), R.tableEdge);
  bar.position.set(0, -TABLE.t - TABLE.h + .22, v[0] * (TABLE.d / 2 - .18));
  bar.castShadow = true;
  table.add(bar);
});

/* ---------------------------------------------------------------- кухня */
const kitchen = new THREE.Group();
scene.add(kitchen);

const floor = new THREE.Mesh(new THREE.PlaneGeometry(16, 16), R.floor);
floor.rotation.x = -Math.PI / 2;
floor.position.y = -TABLE.t - TABLE.h;
floor.receiveShadow = true;
scene.add(floor);

const wall = new THREE.Mesh(new THREE.PlaneGeometry(10, 3.6), R.wall);
wall.position.set(0, .8, -2.05);
wall.receiveShadow = true;
scene.add(wall);

const splash = new THREE.Mesh(new THREE.PlaneGeometry(6.4, 1.05), R.tile);
splash.position.set(0, 1.42, -2.03);
splash.receiveShadow = true;
scene.add(splash);

(function counter(){
  const body = new THREE.Mesh(new THREE.BoxGeometry(6.4, .86, .64), R.cabinet);
  body.position.set(0, .47, -1.72);
  body.castShadow = true; body.receiveShadow = true;
  kitchen.add(body);

  const top = new THREE.Mesh(new THREE.BoxGeometry(6.5, .07, .70), R.marble);
  top.position.set(0, .93, -1.70);
  top.castShadow = true; top.receiveShadow = true;
  kitchen.add(top);

  for (let i = 0; i < 6; i++){
    const door = new THREE.Mesh(new THREE.BoxGeometry(.96, .74, .03), R.cabinetDoor);
    door.position.set(-2.6 + i * 1.04, .47, -1.395);
    door.castShadow = true; door.receiveShadow = true;
    kitchen.add(door);
    const handle = new THREE.Mesh(new THREE.CylinderGeometry(.012, .012, .26, 10), R.handle);
    handle.position.set(-2.6 + i * 1.04 + .34, .60, -1.36);
    kitchen.add(handle);
  }
})();

(function upper(){
  const body = new THREE.Mesh(new THREE.BoxGeometry(4.2, .80, .36), R.cabinet);
  body.position.set(-.4, 2.30, -1.90);
  body.castShadow = true; body.receiveShadow = true;
  kitchen.add(body);
  for (let i = 0; i < 4; i++){
    const door = new THREE.Mesh(new THREE.BoxGeometry(.98, .70, .03), R.cabinetDoor);
    door.position.set(-1.88 + i * 1.02, 2.30, -1.715);
    door.castShadow = true;
    kitchen.add(door);
    const handle = new THREE.Mesh(new THREE.CylinderGeometry(.010, .010, .22, 10), R.handle);
    handle.position.set(-1.88 + i * 1.02 + .36, 2.12, -1.69);
    kitchen.add(handle);
  }
})();

(function windowUnit(){
  const frame = new THREE.Mesh(new THREE.BoxGeometry(1.55, 1.15, .09), R.frame);
  frame.position.set(-3.4, 1.75, -1.98);
  frame.castShadow = true;
  kitchen.add(frame);
  const glass = new THREE.Mesh(new THREE.PlaneGeometry(1.36, .96), R.window);
  glass.position.set(-3.4, 1.75, -1.925);
  kitchen.add(glass);
  const barV = new THREE.Mesh(new THREE.BoxGeometry(.05, .98, .05), R.frame);
  barV.position.set(-3.4, 1.75, -1.92);
  kitchen.add(barV);
  const sill = new THREE.Mesh(new THREE.BoxGeometry(1.7, .06, .22), R.marble);
  sill.position.set(-3.4, 1.16, -1.90);
  sill.castShadow = true;
  kitchen.add(sill);
})();

(function fridge(){
  const body = new THREE.Mesh(new THREE.BoxGeometry(.92, 2.0, .70), R.fridge);
  body.position.set(2.55, 1.0, -1.6);
  body.castShadow = true; body.receiveShadow = true;
  kitchen.add(body);
  const seam = new THREE.Mesh(new THREE.BoxGeometry(.93, .015, .71), R.metal);
  seam.position.set(2.55, 1.36, -1.6);
  kitchen.add(seam);
  const h1 = new THREE.Mesh(new THREE.CylinderGeometry(.014, .014, .34, 10), R.metal);
  h1.position.set(2.92, 1.62, -1.24);
  kitchen.add(h1);
  const h2 = new THREE.Mesh(new THREE.CylinderGeometry(.014, .014, .34, 10), R.metal);
  h2.position.set(2.92, 1.10, -1.24);
  kitchen.add(h2);
})();

(function kettle(){
  const mat = new THREE.MeshStandardMaterial({color:0xd94f3d, roughness:.3, metalness:.2});
  const body = cyl(.16, .19, .26, mat, 26);
  body.position.set(-1.9, 1.10, -1.66);
  body.castShadow = true;
  kitchen.add(body);
  const lid = ball(.10, R.metal, 16);
  lid.position.set(-1.9, 1.24, -1.66);
  lid.scale.y = .6;
  kitchen.add(lid);
})();

(function lamp(){
  const rod = new THREE.Mesh(new THREE.CylinderGeometry(.012, .012, .55, 8), R.lamp);
  rod.position.set(0, 2.42, 0);
  kitchen.add(rod);
  const shade = new THREE.Mesh(new THREE.ConeGeometry(.28, .24, 24, 1, true), R.lamp);
  shade.position.set(0, 2.12, 0);
  shade.rotation.x = Math.PI;
  shade.castShadow = true;
  kitchen.add(shade);
  const bulb = ball(.06, new THREE.MeshBasicMaterial({color:0xfff0c0}), 12);
  bulb.position.set(0, 2.04, 0);
  kitchen.add(bulb);
  const l = new THREE.PointLight(0xffd9a0, 9, 6, 2);
  l.position.set(0, 2.0, 0);
  kitchen.add(l);
})();

/* ---------------------------------------------------------------- еда */'''

s = s[:start] + new + s[end:]

s = s.replace("const camera = new THREE.PerspectiveCamera(36, 1, .05, 60);",
              "const camera = new THREE.PerspectiveCamera(38, 1, .05, 60);\nscene.fog = new THREE.Fog(0xf2e7d6, 9, 20);", 1)
s = s.replace("/* ---------------------------------------------------------------- свет */",
              "/* ---------------------------------------------------------------- окружение */\n(function env(){\n  const pmrem = new THREE.PMREMGenerator(renderer);\n  scene.environment = pmrem.fromEquirectangular(envTexture()).texture;\n})();\n\n/* ---------------------------------------------------------------- свет */", 1)

io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('kitchen ok')
