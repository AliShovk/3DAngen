import io, sys

p = 'src/table/index.html'
s = io.open(p, encoding='utf-8').read()

start = s.index("const SHOTS = [")
end = s.index("const FILM_TOTAL")

new = r'''const SHOTS = [
  // 1. кран сверху вниз: открываем кухню и находим крошечного героя
  {name:'crane down', dur:1.3, cam:function(u, h){
    const k = smooth(u);
    return {az:.22, pol:lerp(.92, 1.27, k), rad:lerp(9.4, 6.3, k),
            tx:lerp(.2, h.x * .7, k), ty:lerp(1.30, .46, k), tz:lerp(.4, h.z * .7, k), fov:38, roll:0, shake:0};
  }},
  // 2. медленный наезд (push in) — напряжение
  {name:'push in', dur:1.0, cam:function(u, h){
    const k = smooth(u);
    return {az:.30, pol:1.27, rad:lerp(6.3, 3.2, k), tx:h.x, ty:.42, tz:h.z, fov:lerp(38, 30, k), roll:0, shake:0};
  }},
  // 3. резкий панорамный мах (whip pan) — следим за бегом
  {name:'whip pan', dur:.75, cam:function(u, h){
    const k = smooth(u);
    return {az:lerp(-.62, .62, k), pol:1.30, rad:3.9, tx:h.x, ty:.40, tz:h.z,
            fov:34, roll:lerp(-.05, .06, k), shake:.004};
  }},
  // 4. низкий облёт по дуге (arc) — герой крупно
  {name:'low arc', dur:1.1, cam:function(u, h){
    const k = smooth(u);
    return {az:lerp(.62, 1.16, k), pol:1.40, rad:2.60, tx:h.x, ty:.34, tz:h.z,
            fov:42, roll:lerp(.05, -.04, k), shake:.0025};
  }},
  // 5. crash zoom — мгновенный наезд на чирканье
  {name:'crash zoom', dur:.85, cam:function(u, h){
    const k = u < .32 ? easeOut(u / .32) : 1;
    return {az:1.10, pol:1.36, rad:lerp(3.0, 2.05, k), tx:h.x, ty:.38, tz:h.z,
            fov:lerp(44, 15, k), roll:lerp(-.02, .03, k), shake:.006 * (1 - k) + .002};
  }},
  // 6. dolly zoom (эффект «Вертиго») — вспышка огня
  {name:'dolly zoom', dur:1.1, cam:function(u, h){
    const k = smooth(u);
    return {az:1.10, pol:1.34, rad:lerp(5.2, 2.4, k), tx:h.x, ty:.40, tz:h.z,
            fov:lerp(20, 54, k), roll:.02, shake:.0015};
  }},
  // 7. голландский угол + ручная камера — хаос
  {name:'dutch handheld', dur:1.2, cam:function(u, h){
    const k = smooth(u);
    return {az:lerp(1.10, .45, k), pol:lerp(1.34, 1.42, k), rad:2.45, tx:h.x, ty:.36, tz:h.z,
            fov:34, roll:lerp(.10, .26, k), shake:.012};
  }},
  // 8. кран вверх — финальный отъезд
  {name:'crane up', dur:1.3, cam:function(u, h){
    const k = smooth(u);
    return {az:lerp(.45, .30, k), pol:lerp(1.42, .55, k), rad:lerp(3.6, 9.2, k),
            tx:h.x * .5, ty:lerp(.36, 1.05, k), tz:h.z * .5, fov:38, roll:lerp(.26, 0, k), shake:.002 * (1 - k)};
  }}
];

'''

s = s[:start] + new + s[end:]
io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('shots fixed')
