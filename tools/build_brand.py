"""Build the POJO BOYS logo set. Output: dist/logo/*.svg, dist/merch/*.svg"""
import sys, os, math, json
sys.path.insert(0, "tools")
from textpath import text_d, text_bounds, glyph_d, font
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen
import pathops

BLACK = "#0A0A0A"; CHALK = "#F4F4F2"; ORANGE = "#FF5A1F"; ASH = "#8A8A8A"
os.makedirs("dist/logo", exist_ok=True); os.makedirs("dist/merch", exist_ok=True)

# ---------- path helpers (skia pathops) ----------
def glyph_path(fname, ch, size, x=0, y=0):
    f = font(fname); gs = f.getGlyphSet(); cmap = f.getBestCmap(); s = size / f["head"].unitsPerEm
    p = pathops.Path(); pen = TransformPen(p.getPen(), (s, 0, 0, -s, x, y))
    gs[cmap[ord(ch)]].draw(pen); return p

def rect_path(x, y, w, h):
    p = pathops.Path(); pen = p.getPen(); pen.moveTo((x, y)); pen.lineTo((x + w, y)); pen.lineTo((x + w, y + h)); pen.lineTo((x, y + h)); pen.closePath(); return p

def path_d(p):
    pen = SVGPathPen(None, ntos=lambda v: f"{v:.2f}"); p.draw(pen); return pen.getCommands()

def pbounds(p):
    return p.bounds  # (xmin, ymin, xmax, ymax)

# ---------- the mark: brace-P, flattened to two clean fills (brace, bowl) ----------
def mark_paths(size=100):
    """Returns dict with 'brace' and 'bowl' pathops paths, mark bounds. Origin: baseline of P at y=0."""
    br = glyph_path("unbounded", "{", size)
    bx0, by0, bx1, by1 = br.bounds
    P = glyph_path("unbounded", "P", size)
    px0, py0, px1, py1 = P.bounds
    stem_w = (px1 - px0) * 0.32
    dx = bx1 - px0 - stem_w * 0.5
    P.transform(1, 0, 0, 1, dx, 0)  # shift P so its stem sits inside the brace arm
    cut = rect_path(bx1 - size * 0.012, by0 - 20, size * 3, by1 - by0 + 40)
    bowl = pathops.op(P, cut, pathops.PathOp.INTERSECTION)
    bowl.simplify()
    allp = pathops.op(br, bowl, pathops.PathOp.UNION); allp.simplify()
    return {"brace": br, "bowl": bowl, "all": allp, "bounds": allp.bounds}

def mark_svg_body(size, ink, bowl_col=None, x=0, y=0):
    m = mark_paths(size)
    if bowl_col and bowl_col != ink:
        return (f'<g transform="translate({x:.2f},{y:.2f})"><path fill="{ink}" d="{path_d(m["brace"])}"/>'
                f'<path fill="{bowl_col}" d="{path_d(m["bowl"])}"/></g>'), m["bounds"]
    return f'<g transform="translate({x:.2f},{y:.2f})"><path fill="{ink}" d="{path_d(m["all"])}"/></g>', m["bounds"]

def word_body(size, ink, tracking=0.02, fname="unbounded800"):
    d, adv = text_d(fname, "POJO BOYS", size, 0, 0, tracking)
    b = text_bounds(fname, "POJO BOYS", size, tracking)
    return f'<path fill="{ink}" d="{d}"/>', b

def svg(w, h, body, bg=None, extra=""):
    bgr = f'<rect width="{w:.0f}" height="{h:.0f}" fill="{bg}"/>' if bg else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.0f} {h:.0f}" width="{w:.0f}" height="{h:.0f}"{extra}>'
            f'<title>POJO BOYS</title>{bgr}{body}</svg>')

def place(body, bounds, tx, ty):
    """translate body so its bounds' top-left lands at tx,ty"""
    return f'<g transform="translate({tx - bounds[0]:.2f},{ty - bounds[1]:.2f})">{body}</g>'

# ---------- lockups ----------
def lockup_h(size=100, ink=CHALK, bowl=None, bg=None):
    mb, mbd = mark_svg_body(size * 1.25, ink, bowl)
    wb, wbd = word_body(size * 0.62, ink)
    pad = size * 0.4; gap = size * 0.28
    mh = mbd[3] - mbd[1]; wh = wbd[3] - wbd[1]
    H = mh + pad * 2; W = pad + (mbd[2] - mbd[0]) + gap + (wbd[2] - wbd[0]) + pad
    # optical: wordmark centred on the mark's cap zone (ignore brace descender)
    cap_mid = pad + (mh - (size * 1.25 * 0.116)) / 2
    body = place(mb, mbd, pad, pad) + place(wb, wbd, pad + (mbd[2] - mbd[0]) + gap, cap_mid - wh / 2)
    return svg(W, H, body, bg)

def lockup_stacked(size=100, ink=CHALK, bowl=None, bg=None):
    mb, mbd = mark_svg_body(size * 1.6, ink, bowl)
    wb, wbd = word_body(size * 0.5, ink, 0.06)
    pad = size * 0.4; gap = size * 0.3
    mw = mbd[2] - mbd[0]; mh = mbd[3] - mbd[1]; ww = wbd[2] - wbd[0]; wh = wbd[3] - wbd[1]
    W = max(mw, ww) + pad * 2; H = pad + mh + gap + wh + pad
    body = place(mb, mbd, (W - mw) / 2, pad) + place(wb, wbd, (W - ww) / 2, pad + mh + gap)
    return svg(W, H, body, bg)

def mark_only(size=100, ink=CHALK, bowl=None, bg=None):
    mb, mbd = mark_svg_body(size, ink, bowl); pad = size * 0.25
    W = (mbd[2] - mbd[0]) + pad * 2; H = (mbd[3] - mbd[1]) + pad * 2
    return svg(W, H, place(mb, mbd, pad, pad), bg)

def avatar(size=512, ink=CHALK, bowl=ORANGE, bg=BLACK):
    mb, mbd = mark_svg_body(100, ink, bowl)
    mw = mbd[2] - mbd[0]; mh = mbd[3] - mbd[1]
    s = size * 0.58 / mh
    tx = size / 2 - (mbd[0] + mbd[2]) / 2 * s; ty = size / 2 - (mbd[1] + mbd[3]) / 2 * s
    return svg(size, size, f'<g transform="translate({tx:.2f},{ty:.2f}) scale({s:.4f})">{mb}</g>', bg)

# ---------- crest (roundel) ----------
def arc_text(text, fname, size, cx, cy, r, ink, top=True, tracking=0.12):
    f = font(fname); upm = f["head"].unitsPerEm; s = size / upm; gs = f.getGlyphSet(); cmap = f.getBestCmap()
    advs = []
    for ch in text:
        advs.append(size * 0.3 if ch == " " else gs[cmap[ord(ch)]].width * s + tracking * size)
    total = sum(advs) - tracking * size
    total_deg = math.degrees(total / r)
    out = ""; cur = -total_deg / 2
    for ch, adv in zip(text, advs):
        a_deg = adv / r * 180 / math.pi
        mid = cur + a_deg / 2
        if ch != " ":
            d, gadv = glyph_d(fname, ch, size, 0, 0)
            b = text_bounds(fname, ch, size)
            if top:
                rot = mid
                tr = f"rotate({rot:.3f} {cx:.2f} {cy:.2f}) translate({cx - (b[0] + b[2]) / 2:.2f},{cy - r:.2f})"
            else:
                rot = -mid
                tr = f"rotate({rot:.3f} {cx:.2f} {cy:.2f}) translate({cx - (b[0] + b[2]) / 2:.2f},{cy + r + (b[3] - b[1]) * 0 - b[1] - (b[3]-b[1]):.2f})"
            out += f'<path fill="{ink}" transform="{tr}" d="{d}"/>'
        cur += a_deg
    return out

def crest(size=400, ink=CHALK, bowl=None, bg=None, ring_col=None):
    cx = cy = size / 2; R = size * 0.47; t = size * 0.038
    ring_col = ring_col or ink
    body = f'<circle cx="{cx}" cy="{cy}" r="{R - t / 2:.2f}" fill="none" stroke="{ring_col}" stroke-width="{t:.2f}"/>'
    # convert ring to a fill (two circles, evenodd) for embroidery-friendliness
    body = (f'<path fill="{ring_col}" fill-rule="evenodd" d="M{cx:.2f},{cy - R:.2f} a{R:.2f},{R:.2f} 0 1,0 0.01,0 Z '
            f'M{cx:.2f},{cy - R + t:.2f} a{R - t:.2f},{R - t:.2f} 0 1,0 0.01,0 Z"/>')
    mb, mbd = mark_svg_body(100, ink, bowl)
    mh = mbd[3] - mbd[1]; s = size * 0.40 / mh
    tx = cx - (mbd[0] + mbd[2]) / 2 * s; ty = cy - (mbd[1] + mbd[3]) / 2 * s + size * 0.01
    body += f'<g transform="translate({tx:.2f},{ty:.2f}) scale({s:.4f})">{mb}</g>'
    body += arc_text("POJO BOYS", "unbounded800", size * 0.075, cx, cy, R - t - size * 0.085, ink, True, 0.16)
    body += arc_text("SQUAD OF TWO", "unbounded800", size * 0.052, cx, cy, R - t - size * 0.075, ink, False, 0.18)
    # two small squares at the equator: the single pixel wink, in the accent if colour
    sq = size * 0.028; col = bowl or ink
    body += f'<rect x="{cx - R + t + size*0.06:.2f}" y="{cy - sq/2:.2f}" width="{sq:.2f}" height="{sq:.2f}" fill="{col}"/>'
    body += f'<rect x="{cx + R - t - size*0.06 - sq:.2f}" y="{cy - sq/2:.2f}" width="{sq:.2f}" height="{sq:.2f}" fill="{col}"/>'
    return svg(size, size, body, bg)

# ---------- block-built variant ----------
def blocks(cols=14, ink=CHALK, bowl=ORANGE, bg=None, cell=24, gap_ratio=0.10):
    """Rasterise the mark onto a coarse grid; returns svg of rects."""
    m = mark_paths(100); b = m["bounds"]
    W = b[2] - b[0]; H = b[3] - b[1]
    rows = round(cols * H / W)
    cw = W / cols; ch = H / rows
    out = ""; grid = []
    for r in range(rows):
        row = []
        for c in range(cols):
            # sample 3x3 points per cell for coverage
            hits_b = hits_w = 0
            for i in range(3):
                for j in range(3):
                    x = b[0] + (c + (i + 0.5) / 3) * cw; y = b[1] + (r + (j + 0.5) / 3) * ch
                    if m["bowl"].contains((x, y)): hits_w += 1
                    elif m["brace"].contains((x, y)): hits_b += 1
            tot = hits_b + hits_w
            if tot >= 4:
                col = bowl if (hits_w >= hits_b and bowl) else ink
                g = cell * gap_ratio
                out += f'<rect x="{c*cell+g/2:.2f}" y="{r*cell+g/2:.2f}" width="{cell-g:.2f}" height="{cell-g:.2f}" rx="{cell*0.08:.2f}" fill="{col}"/>'
                row.append(2 if col == bowl else 1)
            else:
                row.append(0)
        grid.append(row)
    return svg(cols * cell, rows * cell, out, bg), grid

if __name__ == "__main__":
    files = {
        "logo/pojoboys-lockup-colour.svg": lockup_h(100, CHALK, ORANGE, BLACK),
        "logo/pojoboys-lockup-mono.svg": lockup_h(100, BLACK, None, None),
        "logo/pojoboys-lockup-reversed.svg": lockup_h(100, CHALK, None, BLACK),
        "logo/pojoboys-stacked-colour.svg": lockup_stacked(100, CHALK, ORANGE, BLACK),
        "logo/pojoboys-stacked-mono.svg": lockup_stacked(100, BLACK, None, None),
        "logo/pojoboys-stacked-reversed.svg": lockup_stacked(100, CHALK, None, BLACK),
        "logo/pojoboys-mark-colour.svg": mark_only(100, CHALK, ORANGE, BLACK),
        "logo/pojoboys-mark-mono.svg": mark_only(100, BLACK, None, None),
        "logo/pojoboys-mark-reversed.svg": mark_only(100, CHALK, None, BLACK),
        "logo/pojoboys-avatar.svg": avatar(),
        "logo/pojoboys-crest-colour.svg": crest(400, CHALK, ORANGE, BLACK),
        "logo/pojoboys-crest-mono.svg": crest(400, BLACK, None, None),
        "logo/pojoboys-crest-reversed.svg": crest(400, CHALK, None, BLACK),
    }
    bsvg, grid = blocks(20, CHALK, ORANGE, BLACK)
    files["logo/pojoboys-mark-blocks-colour.svg"] = bsvg
    files["logo/pojoboys-mark-blocks-mono.svg"] = blocks(20, BLACK, None, None)[0]
    json.dump(grid, open("build/blocks_grid.json", "w"))
    for k, v in files.items():
        open(f"dist/{k}", "w").write(v)
    print(len(files), "files;", "grid", len(grid), "x", len(grid[0]))
