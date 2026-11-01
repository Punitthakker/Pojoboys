import sys, json, re, urllib.parse
sys.path.insert(0, "tools")
from build_brand import crest, avatar, lockup_h, mark_only, CHALK, ORANGE, BLACK
from build_merch import inner, tee

a = json.load(open("build/site_assets.json"))
t = open("tools/site-template.html").read().replace("__FONTS__", open("tools/fonts.css").read())

b = a["bounds"]; wb = a["word_bounds"]
markvb = f"{b[0]:.2f} {b[1]:.2f} {b[2]-b[0]:.2f} {b[3]-b[1]:.2f}"
markpaths = f'<path fill="#F4F4F2" d="{a["brace"]}"/><path fill="#FF5A1F" d="{a["bowl"]}"/>'
wordvb = f"{wb[0]:.2f} {wb[1]:.2f} {wb[2]-wb[0]:.2f} {wb[3]-wb[1]:.2f}"
wordpath = f'<path d="{a["word"]}"/>'

grid = a["grid"]; cell = 24; g = cell * 0.10
rects = ""
for r, row in enumerate(grid):
    for c, v in enumerate(row):
        if v:
            col = "#FF5A1F" if v == 2 else "#F4F4F2"
            rects += f'<rect x="{c*cell+g/2:.1f}" y="{r*cell+g/2:.1f}" width="{cell-g:.1f}" height="{cell-g:.1f}" rx="2" fill="{col}"/>'
blockvb = f"0 0 {len(grid[0])*cell} {len(grid)*cell}"

navmark = f'<svg viewBox="{markvb}" aria-hidden="true"><path fill="#F4F4F2" d="{a["all"]}"/></svg>'
fav = avatar(64).replace('<title>POJO BOYS</title>', '')
favicon = urllib.parse.quote(fav, safe="")

cr = crest(400, CHALK, ORANGE, None)
cr = re.sub(r'width="\d+" height="\d+"', 'aria-hidden="true"', cr, count=1)

# merch illustrations (no notes)
def capsvg():
    cap = ('<path d="M60,135 C60,70 110,40 150,40 C190,40 240,70 240,135 Z" fill="#0A0A0A" stroke="#242424" stroke-width="0.8"/>'
           '<path d="M150,40 L150,135 M95,52 C100,90 100,120 102,135 M205,52 C200,90 200,120 198,135" stroke="#222" stroke-width="0.8" fill="none"/>'
           '<path d="M40,135 L260,135 C262,152 238,168 150,168 C62,168 38,152 40,135 Z" fill="#111" stroke="#242424" stroke-width="0.8"/>')
    lk = lockup_h(100, CHALK, None, None); body, w, h = inner(lk); s = 95 / w
    cap += f'<g transform="translate({150-95/2:.2f},{115-h*s:.2f}) scale({s:.5f})">{body}</g>'
    return f'<svg viewBox="30 -8 240 225" aria-label="Black cap with POJO BOYS embroidery">{cap}</svg>'

def teesvg():
    body = tee()
    mk = mark_only(100, CHALK, None, None); mb, w0, h0 = inner(mk); s = 18 / h0
    body += f'<g transform="translate({195 - w0*s/2:.2f},{92 - h0*s/2:.2f}) scale({s:.5f})">{mb}</g>'
    return f'<svg viewBox="30 30 240 225" aria-label="Black tee with small chest mark">{body}</svg>'

out = (t.replace("__FAVICON__", favicon).replace("__NAVMARK__", navmark)
        .replace("__BLOCKVB__", blockvb).replace("__BLOCKRECTS__", rects)
        .replace("__MARKVB__", markvb).replace("__MARKPATHS__", markpaths)
        .replace("__WORDVB__", wordvb).replace("__WORDPATH__", wordpath)
        .replace("__CREST__", cr).replace("__CAP__", capsvg()).replace("__TEE__", teesvg()))
open("dist/site/index.html", "w").write(out)
print("site", len(out), "bytes")
