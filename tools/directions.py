import sys, json
sys.path.insert(0, "tools")
from textpath import text_d, text_bounds, glyph_d, font
from fontTools.pens.boundsPen import BoundsPen

ACCENT = "#C8FF3D"   # placeholder accent for exploration (acid lime)

def svg(w, h, body, bg="#000"):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.0f} {h:.0f}" width="{w:.0f}" height="{h:.0f}">'
            f'<rect width="100%" height="100%" fill="{bg}"/>{body}</svg>')

# ---------- Direction A: statement wordmark  POJO BOYS;
def dir_a(size=100, accent=ACCENT, ink="#fff"):
    f = "unbounded"; tr = -0.015
    d_word, adv = text_d(f, "POJO BOYS", size, 0, 0, tr)
    x0, y0, x1, y1 = text_bounds(f, "POJO BOYS", size, tr)
    # semicolon from mono, sized to cap height
    sc, sadv = glyph_d("mono", ";", size * 1.05, adv + size * 0.02, 0)
    sx0, sy0, sx1, sy1 = text_bounds("mono", ";", size * 1.05)
    pad = size * 0.3
    W = adv + size * 0.02 + sx1 + pad * 2
    H = (y1 - y0) + pad * 2
    tx = pad - x0; ty = pad - y0
    body = (f'<g transform="translate({tx:.2f},{ty:.2f})">'
            f'<path fill="{ink}" d="{d_word}"/>'
            f'<path fill="{accent}" d="{sc}"/></g>')
    return W, H, body

# ---------- Direction B: the empty object mark  {}  + grotesk wordmark
def mark_b(size=100, ink="#fff"):
    d1, a1 = glyph_d("unbounded", "{", size, 0, 0)
    gap = size * 0.12
    d2, a2 = glyph_d("unbounded", "}", size, a1 + gap, 0)
    bx0, by0, bx1, by1 = text_bounds("unbounded", "{", size)
    cx0, cy0, cx1, cy1 = text_bounds("unbounded", "}", size)
    x0 = bx0; x1 = a1 + gap + cx1; y0 = min(by0, cy0); y1 = max(by1, cy1)
    return f'<path fill="{ink}" d="{d1} {d2}"/>', (x0, y0, x1, y1)

def dir_b(size=100, accent=ACCENT, ink="#fff"):
    msize = size * 1.15
    mpath, (mx0, my0, mx1, my1) = mark_b(msize, accent)
    f = "grotesk"; tr = 0.06
    d_word, adv = text_d(f, "POJO BOYS", size * 0.78, 0, 0, tr)
    wx0, wy0, wx1, wy1 = text_bounds(f, "POJO BOYS", size * 0.78, tr)
    pad = size * 0.3
    gapx = size * 0.22
    mh = my1 - my0; wh = wy1 - wy0
    H = max(mh, wh) + pad * 2
    cy = H / 2
    W = pad + (mx1 - mx0) + gapx + (wx1 - wx0) + pad
    body = (f'<g transform="translate({pad - mx0:.2f},{cy - (my0 + my1) / 2:.2f})">{mpath}</g>'
            f'<g transform="translate({pad + (mx1 - mx0) + gapx - wx0:.2f},{cy - (wy0 + wy1) / 2:.2f})">'
            f'<path fill="{ink}" d="{d_word}"/></g>')
    return W, H, body

# ---------- Direction C: the brace-P monogram  {P
_cid = [0]
def mark_c(size=100, ink="#fff", accent=None):
    """P whose stem is a curly brace (Unbounded brace fused to Unbounded P bowl)."""
    _cid[0] += 1; cid = f"pc{_cid[0]}"
    d1, a1 = glyph_d("unbounded", "{", size, 0, 0)
    bx0, by0, bx1, by1 = text_bounds("unbounded", "{", size)
    px0, py0, px1, py1 = text_bounds("unbounded", "P", size)
    stem_w = (px1 - px0) * 0.32
    px = bx1 - px0 - stem_w * 0.5
    d2, a2 = glyph_d("unbounded", "P", size, px, 0)
    cx = bx1 - size * 0.012
    body = (f'<clipPath id="{cid}"><rect x="{cx:.2f}" y="{by0 - 10:.2f}" width="{size * 2:.0f}" height="{by1 - by0 + 20:.2f}"/></clipPath>'
            f'<path fill="{ink}" d="{d1}"/><path fill="{accent or ink}" clip-path="url(#{cid})" d="{d2}"/>')
    return body, (bx0, min(by0, py0), px + px1, max(by1, py1))

def dir_c(size=100, accent=ACCENT, ink="#fff"):
    mpath, (mx0, my0, mx1, my1) = mark_c(size * 1.25, ink, None)
    f = "unbounded800"; tr = 0.02
    d_word, adv = text_d(f, "POJO BOYS", size * 0.62, 0, 0, tr)
    wx0, wy0, wx1, wy1 = text_bounds(f, "POJO BOYS", size * 0.62, tr)
    pad = size * 0.3; gapx = size * 0.26
    mh = my1 - my0; wh = wy1 - wy0
    H = mh + pad * 2
    cy = H / 2
    W = pad + (mx1 - mx0) + gapx + (wx1 - wx0) + pad
    body = (f'<g transform="translate({pad - mx0:.2f},{cy - (my0 + my1) / 2:.2f})">{mpath}</g>'
            f'<g transform="translate({pad + (mx1 - mx0) + gapx - wx0:.2f},{cy - (wy0 + wy1) / 2:.2f})">'
            f'<path fill="{ink}" d="{d_word}"/></g>')
    return W, H, body

def avatar(mark_fn, size=512, ink="#fff", bg="#000"):
    body, (x0, y0, x1, y1) = mark_fn(size * 0.55, ink)
    w = x1 - x0; h = y1 - y0
    s = min(size * 0.62 / w, size * 0.62 / h)
    tx = size / 2 - (x0 + x1) / 2 * s; ty = size / 2 - (y0 + y1) / 2 * s
    return svg(size, size, f'<g transform="translate({tx:.2f},{ty:.2f}) scale({s:.4f})">{body}</g>', bg)

if __name__ == "__main__":
    out = {}
    for name, fn in [("a", dir_a), ("b", dir_b), ("c", dir_c)]:
        W, H, body = fn(100)
        out[name] = svg(W, H, body)
        W, H, body = fn(100, accent="#fff")
        out[name + "_mono"] = svg(W, H, body)
    # avatars for B and C; A gets a "P;" crop
    out["b_avatar"] = avatar(lambda s, ink: mark_b(s, ink))
    out["c_avatar"] = avatar(lambda s, ink: mark_c(s, ink))
    def a_mark(s, ink):
        d, adv = text_d("unbounded", "P", s, 0, 0)
        sc, _ = glyph_d("mono", ";", s * 1.05, adv + s * 0.02, 0)
        x0, y0, x1, y1 = text_bounds("unbounded", "P", s)
        sx0, sy0, sx1, sy1 = text_bounds("mono", ";", s * 1.05)
        return f'<path fill="{ink}" d="{d}"/><path fill="{ACCENT}" d="{sc}"/>', (x0, min(y0, sy0), adv + s * 0.02 + sx1, max(y1, sy1))
    out["a_avatar"] = avatar(a_mark)
    json.dump(out, open("build/directions.json", "w"))
    print({k: len(v) for k, v in out.items()})
