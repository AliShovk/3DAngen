import io, sys

p = 'src/table/index.html'
s = io.open(p, encoding='utf-8').read()

# ---------- 1. кинематографичные движения камеры ----------
film = r'''
/* ---------------------------------------------------------------- кино: движения камеры */
const FILM = {on: false, t: 0, dur: 8.0, fps: 24};

function clamp01(x){ return x < 0 ? 0 : x > 1 ? 1 : x; }
function smooth(x){ x = clamp01(x); return x * x * (3 - 2 * x); }
function easeOut(x){ x = clamp01(x); return 1 - Math.pow(1 - x, 3); }
function easeIn(x){ x = clamp01(x); return x * x * x; }
function lerp(a, b, k){ return a + (b - a) * k; }
function nz(t, f, p){ return Math.sin(t * f + p) * .5 + Math.sin(t * f * 2.17 + p * 1.7) * .3 + Math.sin(t * f * 3.31 + p * 2.9) * .2; }

// положение героя как чистая функция времени — для детерминированного рендера
function heroAt(t){
  const speed = .11;
  let acc = 0, i = 0;
  const per = [];
  for (let k = 0; k < path.length; k++){
    const a = path[k], b = path[(k + 1) % path.length];
    per.push(a.distanceTo(b) / speed);
  }
  const total = per.reduce(function(a, b){ return a + b; }, 0);
  let tt = (t % total);
  let idx = 0;
  while (tt > per[idx]){ tt -= per[idx]; idx = (idx + 1) % path.length; }
  const a = path[idx], b = path[(idx + 1) % path.length];
  const k = tt / per[idx];
  return {x: lerp(a.x, b.x, k), z: lerp(a.y, b.y, k), heading: Math.atan2(b.x - a.x, b.y - a.y)};
}

/* Шоты: каждый возвращает параметры камеры в момент u (0..1 внутри шота) */
const SHOTS = [
  // 1. кран сверху вниз: открываем кухню и находим крошечного героя
  {name:'crane down', dur:1.3, cam:function(u, h){
    const k = smooth(u);
    return {az:.30, pol:lerp(.52, 1.26, k), rad:lerp(9.2, 6.2, k),
            ty:lerp(1.35, .48, k), tx:lerp(0, h.x * .6, k), tz:lerp(-.1, h.z * .6, k), fov:38, roll:0, shake:0};
  }},
  // 2. медленный наезд (push in) — напряжение
  {name:'push in', dur:1.0, cam:function(u, h){
    const k = smooth(u);
    return {az:.32, pol:1.27, rad:lerp(6.2, 3.3, k), tx:h.x, ty:.42, tz:h.z, fov:lerp(38, 31, k), roll:0, shake:0};
  }},
  // 3. резкий панорамный мах (whip pan) — следим за бегом
  {name:'whip pan', dur:.75, cam:function(u, h){
    const k = easeIn(u < .5 ? u * 2 : 1) * .5 + smooth(u) * .5;
    return {az:lerp(-.35, 1.55, k), pol:1.30, rad:4.0, tx:h.x, ty:.40, tz:h.z, fov:34, roll:lerp(-.05, .06, k), shake:.004};
  }},
  // 4. низкий облёт по дуге (arc) — герой крупно, стол в размытии перспективы
  {name:'low arc', dur:1.1, cam:function(u, h){
    const k = smooth(u);
    return {az:lerp(1.55, 2.75, k), pol:1.42, rad:2.55, tx:h.x, ty:.34, tz:h.z, fov:42, roll:lerp(.05, -.04, k), shake:.0025};
  }},
  // 5. crash zoom — мгновенный наезд на чирканье
  {name:'crash zoom', dur:.85, cam:function(u, h){
    const k = u < .32 ? easeOut(u / .32) : 1;
    return {az:2.75, pol:1.36, rad:lerp(3.0, 2.1, k), tx:h.x, ty:.38, tz:h.z,
            fov:lerp(44, 15, k), roll:lerp(-.02, .03, k), shake:.006 * (1 - k) + .002};
  }},
  // 6. dolly zoom (эффект «Вертиго») — вспышка огня
  {name:'dolly zoom', dur:1.1, cam:function(u, h){
    const k = smooth(u);
    return {az:2.75, pol:1.34, rad:lerp(5.4, 2.5, k), tx:h.x, ty:.40, tz:h.z, fov:lerp(20, 54, k), roll:.02, shake:.0015};
  }},
  // 7. голландский угол + ручная камера — хаос
  {name:'dutch handheld', dur:1.2, cam:function(u, h){
    const k = smooth(u);
    return {az:lerp(2.75, 3.5, k), pol:lerp(1.34, 1.44, k), rad:2.45, tx:h.x, ty:.36, tz:h.z,
            fov:34, roll:lerp(.10, .26, k), shake:.012};
  }},
  // 8. кран вверх — финальный отъезд
  {name:'crane up', dur:1.3, cam:function(u, h){
    const k = smooth(u);
    return {az:lerp(3.5, 3.9, k), pol:lerp(1.44, .38, k), rad:lerp(4.2, 9.4, k),
            tx:h.x * .5, ty:lerp(.36, 1.15, k), tz:h.z * .5, fov:38, roll:lerp(.26, 0, k), shake:.002 * (1 - k)};
  }}
];

const FILM_TOTAL = SHOTS.reduce(function(a, s2){ return a + s2.dur; }, 0);

function filmCamera(t){
  const h = heroAt(t);
  let acc = 0, shot = SHOTS[SHOTS.length - 1], u = 0;
  for (let i = 0; i < SHOTS.length; i++){
    if (t < acc + SHOTS[i].dur || i === SHOTS.length - 1){
      shot = SHOTS[i];
      u = clamp01((t - acc) / SHOTS[i].dur);
      break;
    }
    acc += SHOTS[i].dur;
  }
  const c = shot.cam(u, h);
  const sh = c.shake || 0;
  return {
    az: c.az + nz(t, 7.3, .7) * sh,
    pol: c.pol + nz(t, 5.9, 2.1) * sh * .6,
    rad: c.rad + nz(t, 4.7, 3.3) * sh * 1.6,
    tx: c.tx + nz(t, 6.1, 1.2) * sh * .8,
    ty: c.ty + nz(t, 8.3, 2.6) * sh * .6,
    tz: c.tz + nz(t, 5.3, 4.1) * sh * .8,
    fov: c.fov,
    roll: c.roll + nz(t, 9.1, 1.9) * sh * .5
  };
}

function applyFilm(t){
  const c = filmCamera(t);
  const sp = Math.sin(c.pol), cp = Math.cos(c.pol);
  camera.position.set(
    c.tx + c.rad * sp * Math.sin(c.az),
    c.ty + c.rad * cp,
    c.tz + c.rad * sp * Math.cos(c.az)
  );
  camera.fov = c.fov;
  camera.updateProjectionMatrix();
  camera.up.set(Math.sin(c.roll), Math.cos(c.roll), 0);
  camera.lookAt(c.tx, c.ty, c.tz);

  // герой идёт по маршруту синхронно с плёнкой
  const h = heroAt(t);
  hero.position.x = h.x;
  hero.position.z = h.z;
}
'''

# вставляем перед "/* ---------------------------------------------------------------- маршрут */"
s = s.replace("/* ---------------------------------------------------------------- маршрут */", film + "\n/* ---------------------------------------------------------------- маршрут */", 1)

# ---------- 2. режим фильма в цикле ----------
s = s.replace("""  if (spin && !dragging) cam.taz += dt * .28;
  cam.az += (cam.taz - cam.az) * ck;
  cam.pol += (cam.tpol - cam.pol) * ck;
  cam.rad += (cam.trad - cam.rad) * ck;
  applyCamera();""",
"""  if (FILM.on){
    FILM.t += dt;
    if (FILM.t > FILM_TOTAL) FILM.t = 0;
    applyFilm(FILM.t);
  } else {
    if (spin && !dragging) cam.taz += dt * .28;
    cam.az += (cam.taz - cam.az) * ck;
    cam.pol += (cam.tpol - cam.pol) * ck;
    cam.rad += (cam.trad - cam.rad) * ck;
    applyCamera();
  }""", 1)

# в режиме фильма не двигаем героя инкрементально
s = s.replace("  let moving = 0;\n  if (walkOn){", "  let moving = 0;\n  if (walkOn && !FILM.on){", 1)
s = s.replace("  hero.rotation.y = heading;", "  if (!FILM.on) hero.rotation.y = heading;\n  else hero.rotation.y = Math.atan2(camera.position.x - hero.position.x, camera.position.z - hero.position.z);", 1)

# ---------- 3. запуск/UI/кадры ----------
s = s.replace("""let strikeT = -1, lit = false, litT = 0, flashT = 0;""",
"""let strikeT = -1, lit = false, litT = 0, flashT = 0;

// режим съёмки: ?film=1 (для покадрового рендера) или кнопка
const params = new URLSearchParams(location.search);
if (params.get('film') === '1'){
  FILM.on = true;
  document.body.classList.add('film');
  document.querySelector('.bar').style.display = 'none';
  document.querySelector('.hint').style.display = 'none';
  document.querySelector('.hud').style.display = 'none';
  // в кадре 8 секунд: чирканье примерно на 4.0
  setTimeout(function(){ strike(); }, 4000);
}
window.__seek = function(t){
  FILM.on = true;
  FILM.t = t;
  if (t > 4.0 && !lit) { lit = true; litT = 1; }
  if (t < 4.0) { lit = false; litT = 0; }
  applyFilm(t);
  renderer.render(scene, camera);
};""", 1)

# кинематографичные полосы + затемнение UI в режиме фильма
s = s.replace("  @media (max-width:760px){", """  /* кинокадр 2.39:1 */
  body.film::before, body.film::after{
    content:'';position:fixed;left:0;right:0;height:calc((100vh - 100vw / 2.39) / 2);
    background:#0a0806;z-index:5;pointer-events:none;
  }
  body.film::before{top:0}
  body.film::after{bottom:0}

  @media (max-width:760px){""", 1)

io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('film rig ok')
