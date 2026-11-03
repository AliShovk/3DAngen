import io, os, shutil, sys

src = 'src/table/index.html'
dst_dir = 'src/story'
os.makedirs(dst_dir, exist_ok=True)
dst = os.path.join(dst_dir, 'index.html')

s = io.open(src, encoding='utf-8').read()
block = io.open('tools/story_block.js', encoding='utf-8').read()

# 1) заголовок
s = s.replace('<title>Стол со спичкой · 3D</title>', '<title>Спич и таракан · фильм</title>', 1)

# 2) HTML занавеса
s = s.replace('<canvas id="c"></canvas>', '<canvas id="c"></canvas>\n<div id="curtain"><span></span><span></span></div>', 1)

# 3) CSS занавеса
css = """  /* занавес */
  #curtain{position:fixed;inset:0;z-index:9;pointer-events:none;display:flex}
  #curtain span{flex:1;background:#7d0f18;transform:translateX(-101%);transition:transform 1.4s cubic-bezier(.5,.05,.2,1);
    box-shadow:inset -40px 0 70px rgba(0,0,0,.75), inset 40px 0 70px rgba(0,0,0,.55);
    background-image:repeating-linear-gradient(90deg,#8e1420 0 22px,#6d0c14 22px 46px,#8e1420 46px 68px,#5e0a12 68px 92px)}
  #curtain span:last-child{transform:translateX(101%)}
  #curtain.closed span:first-child{transform:translateX(0)}
  #curtain.closed span:last-child{transform:translateX(0)}

  @media (max-width:760px){"""
s = s.replace("  @media (max-width:760px){", css, 1)

# 4) блок сценария внутрь IIFE, перед финальным запуском
block = block.replace("document.body.classList.add('film');", "document.body.classList.add('story');", 1)
s = s.replace("setBg('cream');", block + "\nsetBg('cream');", 1)

# 5) главный цикл не должен спорить со сценарием
s = s.replace("""function frame(){
  const dt = Math.min(clock.getDelta(), .05);""",
"""function frame(){
  if (window.__STORY){ requestAnimationFrame(frame); return; }
  const dt = Math.min(clock.getDelta(), .05);""", 1)

# 6) флаг для главного цикла
s = s.replace("if (qs.get('story') === '1'){\n  STORY.on = true;",
              "if (qs.get('story') === '1'){\n  STORY.on = true;\n  window.__STORY = true;", 1)

io.open(dst, 'w', encoding='utf-8', newline='\n').write(s)
print('story scene:', dst, len(s), 'bytes')
