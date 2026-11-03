/* ================= СЦЕНАРИЙ: «Спич и таракан» ================= */
(function(){
"use strict";

const STORY = {on:false, t:0, dur:19.0};

/* ---- таракан ---- */
function makeRoach(sc){
  const g = new THREE.Group();
  const dark = new THREE.MeshStandardMaterial({color:0x2a1a10, roughness:.55, metalness:.05});
  const shell = new THREE.MeshStandardMaterial({color:0x4a2f18, roughness:.32, metalness:.12});
  const body = new THREE.Mesh(new THREE.SphereGeometry(.17, 22, 14), shell);
  body.scale.set(1, .40, 1.55); body.position.y = .07; body.castShadow = true; g.add(body);
  const pron = new THREE.Mesh(new THREE.SphereGeometry(.105, 16, 10), shell);
  pron.scale.set(1, .38, .85); pron.position.set(0, .085, -.20); pron.castShadow = true; g.add(pron);
  const head = new THREE.Mesh(new THREE.SphereGeometry(.062, 14, 10), dark);
  head.position.set(0, .075, -.30); head.castShadow = true; g.add(head);
  const eyeMat = new THREE.MeshStandardMaterial({color:0x0a0a0a, roughness:.15});
  [-1, 1].forEach(function(s){
    const e = new THREE.Mesh(new THREE.SphereGeometry(.015, 8, 6), eyeMat);
    e.position.set(s * .036, .088, -.345); g.add(e);
  });
  const antMat = new THREE.MeshStandardMaterial({color:0x241610, roughness:.6});
  const ants = [];
  [-1, 1].forEach(function(s){
    const a = new THREE.Mesh(new THREE.CylinderGeometry(.006, .0035, .30, 6), antMat);
    a.position.set(s * .032, .105, -.44);
    a.rotation.set(-.45, 0, s * .28);
    g.add(a); ants.push({m:a, s:s});
  });
  const legs = [];
  for (let i = 0; i < 3; i++){
    [-1, 1].forEach(function(s){
      const l = new THREE.Mesh(new THREE.CylinderGeometry(.0095, .006, .21, 6), antMat);
      l.position.set(s * .125, .055, -.09 + i * .10);
      l.rotation.set(0, 0, s * .95);
      l.castShadow = true;
      g.add(l); legs.push({m:l, s:s, i:i});
    });
  }
  g.scale.setScalar(sc);
  scene.add(g);
  return {g:g, legs:legs, ants:ants, sc:sc};
}

const roachA = makeRoach(.55);   // мелкий
const roachB = makeRoach(1.0);   // крупный
roachB.g.visible = false;

/* ---- рассыпанный сахар ---- */
const SUGAR = {a:new THREE.Vector3(-.95, 0, .58), b:new THREE.Vector3(1.05, 0, -.18), n:64, items:[]};
(function sugar(){
  const mat = new THREE.MeshStandardMaterial({color:0xfdf9f0, roughness:.2, metalness:.05});
  for (let i = 0; i < SUGAR.n; i++){
    const k = i / (SUGAR.n - 1);
    const p = new THREE.Vector3().lerpVectors(SUGAR.a, SUGAR.b, k);
    p.x += Math.sin(k * Math.PI * 2.4) * .085;
    p.z += Math.cos(k * Math.PI * 3.1) * .045;
    const c = new THREE.Mesh(new THREE.BoxGeometry(.05, .045, .05), mat.clone());
    c.position.set(p.x, .024, p.z);
    c.rotation.set(Math.random() * 3, Math.random() * 3, Math.random() * 3);
    c.castShadow = true;
    scene.add(c);
    SUGAR.items.push({m:c, k:k, p:p});
  }
})();

function sugarPoint(k){
  const p = new THREE.Vector3().lerpVectors(SUGAR.a, SUGAR.b, k);
  p.x += Math.sin(k * Math.PI * 2.4) * .085;
  p.z += Math.cos(k * Math.PI * 3.1) * .045;
  p.y = 0;
  return p;
}

/* ---- огонь по сахару (бикфордов шнур) ---- */
const fuseLight = new THREE.PointLight(0xff8a22, 0, 1.4, 2);
scene.add(fuseLight);
const fuseGlow = new THREE.Sprite(new THREE.SpriteMaterial({
  map: (function(){
    const c = document.createElement('canvas'); c.width = c.height = 64;
    const g = c.getContext('2d');
    const grd = g.createRadialGradient(32, 32, 0, 32, 32, 32);
    grd.addColorStop(0, 'rgba(255,240,190,1)');
    grd.addColorStop(.4, 'rgba(255,170,60,.9)');
    grd.addColorStop(1, 'rgba(255,120,20,0)');
    g.fillStyle = grd; g.fillRect(0, 0, 64, 64);
    const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
  })(),
  transparent:true, blending:THREE.AdditiveBlending, depthWrite:false, opacity:1
}));
fuseGlow.scale.setScalar(.5);
fuseGlow.visible = false;
scene.add(fuseGlow);

/* ---- взрыв ---- */
const boom = {t:-1, done:false};
const boomFlash = new THREE.Sprite(new THREE.SpriteMaterial({
  map: fuseGlow.material.map, transparent:true, blending:THREE.AdditiveBlending, depthWrite:false, opacity:0
}));
boomFlash.visible = false;
scene.add(boomFlash);

const boomRing = new THREE.Mesh(
  new THREE.TorusGeometry(.35, .035, 8, 40),
  new THREE.MeshBasicMaterial({color:0xffd9a0, transparent:true, opacity:0, depthWrite:false})
);
boomRing.rotation.x = Math.PI / 2;
boomRing.visible = false;
scene.add(boomRing);

const smokeMat = new THREE.SpriteMaterial({
  map: (function(){
    const c = document.createElement('canvas'); c.width = c.height = 128;
    const g = c.getContext('2d');
    const grd = g.createRadialGradient(64, 64, 0, 64, 64, 64);
    grd.addColorStop(0, 'rgba(120,110,100,.85)');
    grd.addColorStop(.6, 'rgba(90,82,74,.45)');
    grd.addColorStop(1, 'rgba(70,64,58,0)');
    g.fillStyle = grd; g.fillRect(0, 0, 128, 128);
    const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
  })(),
  transparent:true, depthWrite:false, opacity:0
});
const smoke = [];
for (let i = 0; i < 7; i++){
  const s = new THREE.Sprite(smokeMat.clone());
  s.visible = false;
  scene.add(s);
  smoke.push({s:s, vx:(Math.random() - .5) * .5, vy:.35 + Math.random() * .35, vz:(Math.random() - .5) * .5, sz:.35 + Math.random() * .35});
}
const boomLight = new THREE.PointLight(0xffcf8a, 0, 5, 2);
scene.add(boomLight);

/* ---- лицо «удивление» ---- */
let surpriseReady = false;
function faceSurprise(){
  if (surpriseReady) return;
  const cvs = M.label.map && M.label.map.image;
  if (!cvs) return;
  const g = cvs.getContext('2d');
  g.clearRect(0, 0, 1024, 1024);
  g.fillStyle = '#f7efdc'; g.fillRect(0, 0, 1024, 1024);
  [{x:90,y:190,r:210,col:'#2ec4c0'},{x:860,y:120,r:175,col:'#ff9a1f'},
   {x:60,y:860,r:200,col:'#ffc61e'},{x:930,y:900,r:195,col:'#ff6fa5'},
   {x:500,y:60,r:120,col:'#7fe0d8'}].forEach(function(a){
    g.fillStyle = a.col; g.beginPath(); g.arc(a.x, a.y, a.r, 0, Math.PI * 2); g.fill();
  });
  g.strokeStyle = '#1d1512'; g.lineWidth = 26; g.strokeRect(34, 34, 956, 956);
  g.strokeStyle = '#f7efdc'; g.lineWidth = 12; g.strokeRect(62, 62, 900, 900);
  const eyeY = 430, dx = 200;
  [-1, 1].forEach(function(s2){
    const cx = 512 + s2 * dx;
    g.fillStyle = '#fff'; g.strokeStyle = '#1d1512'; g.lineWidth = 18;
    g.beginPath(); g.ellipse(cx, eyeY, 128, 178, 0, 0, Math.PI * 2); g.fill(); g.stroke();
    g.fillStyle = '#1d1512';
    g.beginPath(); g.ellipse(cx + s2 * 6, eyeY + 6, 50, 60, 0, 0, Math.PI * 2); g.fill();
    g.fillStyle = '#fff';
    g.beginPath(); g.ellipse(cx + s2 * 6 - 18, eyeY - 18, 18, 24, -.4, 0, Math.PI * 2); g.fill();
    g.strokeStyle = '#1d1512'; g.lineWidth = 16;
    g.beginPath(); g.arc(cx, eyeY - 186, 104, Math.PI * 1.16, Math.PI * 1.84); g.stroke();
  });
  g.fillStyle = '#1d1512';
  g.beginPath(); g.ellipse(512, 752, 58, 76, 0, 0, Math.PI * 2); g.fill();
  g.fillStyle = 'rgba(242,160,181,.5)';
  [-1, 1].forEach(function(s2){ g.beginPath(); g.ellipse(512 + s2 * 250, 720, 62, 40, 0, 0, Math.PI * 2); g.fill(); });
  M.label.map.needsUpdate = true;
  surpriseReady = true;
}

/* ---- занавес ---- */
function curtainAt(t){
  const c = document.getElementById('curtain');
  if (!c) return;
  const k = Math.max(0, Math.min(1, (t - 17.3) / 1.25));
  const e = k * k * (3 - 2 * k);
  const a = c.children[0], b = c.children[1];
  if (a) a.style.transform = 'translateX(' + (-101 + e * 101) + '%)';
  if (b) b.style.transform = 'translateX(' + (101 - e * 101) + '%)';
}

/* ---- сценарий по времени ---- */
const HERO = {x:0, z:0, rot:0};
function storySetHero(t){
  const h = {x:-1.55, z:.82, rot:0};
  if (t < 2.2){ h.x = -1.55; h.z = .82; }
  else if (t < 5.0){ const k = smooth((t - 2.2) / 2.8); h.x = lerp(-1.55, .55, k); h.z = lerp(.82, .58, k); }
  else if (t < 5.9){ h.x = .55; h.z = .58; }
  else if (t < 8.3){ const k = smooth((t - 5.9) / 2.4); h.x = lerp(.55, .95, k); h.z = lerp(.58, .18, k); }
  else if (t < 9.7){ const k = smooth((t - 8.3) / 1.4); h.x = lerp(.95, .15, k); h.z = lerp(.18, .52, k); }
  else if (t < 11.2){ const k = smooth((t - 9.7) / 1.5); h.x = lerp(.15, -.95, k); h.z = lerp(.52, .58, k); }
  else { h.x = -.95; h.z = .58; }
  HERO.x = h.x; HERO.z = h.z;
  hero.position.x = h.x; hero.position.z = h.z;
}

function storySetRoaches(t){
  // мелкий: сидит у тарелки, потом убегает
  if (t < 5.0){ roachA.g.visible = false; }
  else {
    roachA.g.visible = true;
    let x = 1.15, z = .22;
    if (t > 5.9){
      const k = Math.min(1, (t - 5.9) / 2.2);
      x = lerp(1.15, -.55, k);
      z = lerp(.22, -.30, k) + Math.sin(k * 9) * .12;
    }
    if (t > 8.3){ x = -.55 - (t - 8.3) * .12; }
    roachA.g.position.set(x, 0, z);
    roachA.g.rotation.y = Math.atan2(hero.position.x - x, hero.position.z - z) + Math.PI;
  }

  // крупный: появляется из-за посуды и гонится
  if (t < 8.3){ roachB.g.visible = false; }
  else if (t < 14.6){
    roachB.g.visible = true;
    roachB.g.scale.setScalar(1.0 * Math.min(1, (t - 8.3) * 3));
    let x = lerp(-1.35, -.15, Math.min(1, (t - 8.3) / 1.3));
    let z = .35;
    if (t > 9.7){
      const k = Math.min(1, (t - 9.7) / 1.5);
      x = lerp(-.15, -.55, k);
      z = lerp(.35, .42, k);
    }
    if (t > 11.2){
      const k = Math.min(1, (t - 11.2) / 3.2);
      x = lerp(-.55, 1.0, k);
      z = lerp(.42, -.16, k);
    }
    roachB.g.position.set(x, 0, z);
    roachB.g.rotation.y = Math.atan2(hero.position.x - x, hero.position.z - z) + Math.PI;
  } else {
    roachB.g.visible = t < 14.75;
    const s = Math.max(0, 1 - (t - 14.6) * 6);
    roachB.g.scale.setScalar(Math.max(.001, s));
  }
}

function storyFuse(t){
  // 12.0 — поджиг, 12.4..14.5 — фронт идёт по сахару
  const front = t < 12.0 ? -1 : Math.min(1, (t - 12.0) / 2.4);
  for (let i = 0; i < SUGAR.items.length; i++){
    const it = SUGAR.items[i];
    const burnt = front >= 0 && it.k <= front;
    const heat = burnt ? 1 : 0;
    it.m.material.color.setRGB(lerp(1, .07, heat), lerp(.97, .06, heat), lerp(.94, .05, heat));
    it.m.material.emissive = it.m.material.emissive || new THREE.Color(0);
    it.m.material.emissive.setRGB(heat * .55, heat * .18, 0);
  }
  if (front >= 0 && front < 1){
    const p = sugarPoint(front);
    fuseGlow.visible = true;
    fuseGlow.position.set(p.x, .07, p.z);
    fuseGlow.scale.setScalar(.45 + Math.sin(t * 30) * .06);
    fuseLight.position.set(p.x, .12, p.z);
    fuseLight.intensity = 2.6;
  } else {
    fuseGlow.visible = false;
    fuseLight.intensity = 0;
  }
  return front;
}

function storyBoom(t){
  const T0 = 14.5;
  if (t < T0){
    boomFlash.visible = false; boomRing.visible = false; boomLight.intensity = 0;
    smoke.forEach(function(s){ s.s.visible = false; });
    return;
  }
  const k = t - T0;
  boomFlash.visible = k < .45;
  boomFlash.material.opacity = Math.max(0, 1 - k / .45);
  boomFlash.scale.setScalar(1.2 + k * 5.5);
  boomFlash.position.set(1.0, .35, -.16);

  boomRing.visible = k < .8;
  boomRing.material.opacity = Math.max(0, .9 - k / .8);
  boomRing.scale.setScalar(1 + k * 6);
  boomRing.position.set(1.0, .06, -.16);

  boomLight.position.set(1.0, .4, -.16);
  boomLight.intensity = Math.max(0, 9 * (1 - k / .6));

  smoke.forEach(function(s, i){
    s.s.visible = k < 2.2;
    const kk = Math.min(1, k / 2.2);
    s.s.position.set(1.0 + s.vx * kk * 1.6, .2 + s.vy * kk * 1.4, -.16 + s.vz * kk * 1.6);
    s.s.scale.setScalar(s.sz * (.5 + kk * 1.4));
    s.s.material.opacity = Math.max(0, .55 * (1 - kk));
  });
}

/* ---- камера фильма (вертикаль 9:16) ---- */
function storyCam(t){
  const h = hero.position;
  // 1. тьма, общий план
  if (t < 2.2){
    const k = smooth(t / 2.2);
    return {az:.34, pol:lerp(1.20, 1.36, k), rad:lerp(4.6, 3.5, k), tx:h.x * .5, ty:.35, tz:h.z * .5, fov:40, roll:0, shake:0};
  }
  // 2. идёт и стучит по посуде
  if (t < 5.0){
    const k = smooth((t - 2.2) / 2.8);
    return {az:.30, pol:1.28, rad:lerp(3.5, 2.6, k), tx:h.x, ty:.42, tz:h.z, fov:36, roll:0, shake:.0015};
  }
  // 3. увидел таракана — наезд
  if (t < 5.9){
    const k = smooth((t - 5.0) / .9);
    return {az:.18, pol:1.22, rad:lerp(2.6, 1.9, k), tx:lerp(h.x, .95, k * .6), ty:.36, tz:lerp(h.z, .2, k * .6), fov:lerp(36, 30, k), roll:0, shake:0};
  }
  // 4. погоня
  if (t < 8.3){
    return {az:.40, pol:1.30, rad:2.9, tx:(h.x + roachA.g.position.x) / 2, ty:.32,
            tz:(h.z + roachA.g.position.z) / 2, fov:34, roll:.03, shake:.006};
  }
  // 5. второй таракан — мах камеры
  if (t < 9.7){
    const k = smooth((t - 8.3) / 1.4);
    return {az:lerp(.40, -.35, k), pol:1.32, rad:2.7, tx:(h.x + roachB.g.position.x) / 2, ty:.34,
            tz:(h.z + roachB.g.position.z) / 2, fov:36, roll:lerp(.03, -.10, k), shake:.012};
  }
  // 6. к сахару
  if (t < 12.0){
    const k = smooth((t - 9.7) / 2.3);
    return {az:lerp(-.35, .10, k), pol:1.26, rad:2.5, tx:lerp(h.x, -.9, k * .5), ty:.34, tz:h.z,
            fov:38, roll:0, shake:.003};
  }
  // 7. вдоль шнура
  if (t < 14.5){
    const front = Math.min(1, Math.max(0, (t - 12.0) / 2.4));
    const p = sugarPoint(front);
    return {az:.24, pol:1.40, rad:1.85, tx:lerp(h.x, p.x, .55), ty:.22, tz:lerp(h.z, p.z, .55),
            fov:40, roll:.02, shake:.004};
  }
  // 8. взрыв
  if (t < 16.0){
    const k = smooth((t - 14.5) / 1.5);
    return {az:lerp(.24, .55, k), pol:lerp(1.40, 1.24, k), rad:lerp(1.8, 3.3, k), tx:1.0, ty:.35, tz:-.16,
            fov:40, roll:lerp(.02, -.06, k), shake:.02 * (1 - k) + .004};
  }
  // 9. крупно лицо — удивление
  if (t < 17.3){
    const k = smooth((t - 16.0) / 1.3);
    const fast = easeOut(Math.min(1, (t - 16.0) / .55));
    return {az:lerp(.55, .30, k), pol:1.20, rad:lerp(3.3, 1.15, fast), tx:lerp(1.0, hero.position.x, fast),
            ty:lerp(.35, .60, fast), tz:lerp(-.16, hero.position.z, fast), fov:lerp(40, 29, fast), roll:0, shake:.002};
  }
  // 10. отъезд, занавес
  const k = smooth((t - 17.3) / 1.5);
  return {az:.30, pol:1.26, rad:lerp(1.15, 3.4, k), tx:hero.position.x, ty:lerp(.58, .4, k), tz:hero.position.z,
          fov:lerp(30, 38, k), roll:0, shake:0};
}

function applyStoryCamera(t){
  const c = storyCam(t);
  c.pol = Math.max(.9, Math.min(1.5, c.pol));
  const sp = Math.sin(c.pol), cp = Math.cos(c.pol);
  camera.position.set(
    c.tx + c.rad * sp * Math.sin(c.az),
    c.ty + c.rad * cp,
    c.tz + c.rad * sp * Math.cos(c.az)
  );
  camera.fov = c.fov;
  camera.updateProjectionMatrix();
  const sh = c.shake || 0;
  const nx = Math.sin(t * 7.1) * .5 + Math.sin(t * 13.3) * .3;
  const ny = Math.sin(t * 5.7 + 1.1) * .5 + Math.sin(t * 11.9 + 2.2) * .3;
  camera.position.x += nx * sh * .5;
  camera.position.y += ny * sh * .4;
  camera.up.set(Math.sin(c.roll), Math.cos(c.roll), 0);
  camera.lookAt(c.tx, c.ty, c.tz);
}

/* ---- анимация персонажа в сцене ---- */
function storyHeroAnim(t){
  const walking = (t > 2.2 && t < 5.0) || (t > 5.9 && t < 11.2);
  const running = (t > 5.9 && t < 11.2);
  const sp = running ? 9.5 : 5.2;
  const phase = t * sp;
  const s = Math.sin(phase);
  legPivots.L.rotation.x = walking ? s * .42 : 0;
  legPivots.R.rotation.x = walking ? -s * .42 : 0;
  armPivots.R.rotation.z = armDeg * Math.PI / 180;
  armPivots.L.rotation.z = -armDeg * Math.PI / 180;
  armPivots.R.rotation.x = walking ? Math.sin(phase + Math.PI) * .2 : 0;
  armPivots.L.rotation.x = walking ? Math.sin(phase) * .2 : 0;

  // стук по посуде: 2.4..5.0 — рука «стучит» каждые 0.45 с
  if (t > 2.4 && t < 5.0){
    const tap = Math.max(0, Math.sin((t - 2.4) / .45 * Math.PI * 2));
    armPivots.R.rotation.x += Math.pow(tap, 6) * 1.1;
  }
  hero.position.y = Math.abs(s) * .03 + (walking ? 0 : Math.sin(t * 1.6) * .006);
  hero.rotation.z = -.02 + (walking ? -Math.cos(phase) * .05 : 0);
  hero.rotation.y = Math.atan2(camera.position.x - hero.position.x, camera.position.z - hero.position.z);
}

/* ---- включение режима ---- */
const qs = new URLSearchParams(location.search);
if (qs.get('story') === '1'){
  STORY.on = true;
  document.body.classList.add('film');
  document.querySelector('.bar').style.display = 'none';
  document.querySelector('.hint').style.display = 'none';
  document.querySelector('.hud').style.display = 'none';
  hero.scale.setScalar(.42);

  // тьма
  scene.traverse(function(o){
    if (o.isHemisphereLight) o.intensity = .07;
    if (o.isDirectionalLight) o.intensity = o.intensity > 1.5 ? .10 : .04;
    if (o.isPointLight) o.intensity = 0;
  });
  scene.fog = new THREE.Fog(0x05070a, 5.5, 15);
  // убираем свет окружения — комната должна быть тёмной
  scene.environment = null;
  scene.traverse(function(o){
    if (!o.isMesh || !o.material) return;
    (Array.isArray(o.material) ? o.material : [o.material]).forEach(function(m){
      if (m && m.isMeshStandardMaterial){ m.envMapIntensity = 0; m.needsUpdate = true; }
    });
  });
  renderer.toneMappingExposure = 1.15;

  // подсветка от спички
  if (heldRef && heldRef.userData && heldRef.userData.light){
    const l = heldRef.userData.light;
    l.distance = 7; l.decay = 1.4;
  }

  window.__seek = function(t){
    STORY.t = t;
    storySetHero(t);
    storySetRoaches(t);
    storyFuse(t);
    storyBoom(t);
    applyStoryCamera(t);
    storyHeroAnim(t);
    // огонёк спички
    const litNow = t > 1.55;
    if (heldRef && heldRef.userData){
      const u = heldRef.userData;
      u.flame.visible = litNow;
      u.light.intensity = litNow ? 2.4 + Math.sin(t * 24) * .3 : 0;
      const fl = 1 + Math.sin(t * 26) * .08;
      u.flame.scale.set(litNow ? 1 : .001, litNow ? fl : .001, litNow ? 1 : .001);
    }
    // занавес
    curtainAt(t);
    // лицо
    if (t > 15.75) faceSurprise();
    renderer.render(scene, camera);
  };
}
})();
