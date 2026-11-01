"""Print/embroidery-ready merch layouts in mm. Logo paths are the real outlines; notes are plain SVG text."""
import sys, re
sys.path.insert(0, "tools")
from build_brand import mark_svg_body, word_body, place, lockup_h, lockup_stacked, blocks, CHALK, ORANGE, BLACK, ASH

NOTE_FONT = 'font-family="Inter, Helvetica, Arial, sans-serif"'

def inner(svg_text):
    """strip outer <svg> wrapper and <title>, return (body, w, h)"""
    m = re.search(r'viewBox="0 0 (\d+) (\d+)"', svg_text)
    w, h = float(m.group(1)), float(m.group(2))
    body = re.sub(r'^<svg[^>]*>', '', svg_text).replace('</svg>', '')
    body = re.sub(r'<title>.*?</title>', '', body)
    body = re.sub(r'<rect width="\d+" height="\d+" fill="#[0-9A-Fa-f]+"/>', '', body, count=1)
    return body, w, h

def fit(svg_text, x, y, w_mm):
    body, w, h = inner(svg_text); s = w_mm / w
    return f'<g transform="translate({x:.2f},{y:.2f}) scale({s:.5f})">{body}</g>', h * s

def note(x, y, lines, size=3.2, col=ASH, anchor="start"):
    out = ""
    for i, l in enumerate(lines):
        out += f'<text x="{x}" y="{y + i * size * 1.45:.2f}" font-size="{size}" fill="{col}" {NOTE_FONT} text-anchor="{anchor}">{l}</text>'
    return out

def dim(x1, y1, x2, y2, label, col=ORANGE):
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{col}" stroke-width="0.4" stroke-dasharray="1.5 1.5"/>'
            f'<text x="{(x1+x2)/2:.1f}" y="{(y1+y2)/2 - 1.5:.1f}" font-size="3" fill="{col}" {NOTE_FONT} text-anchor="middle">{label}</text>')

def sheet(w, h, body, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}mm" height="{h}mm">'
            f'<title>{title}</title><rect width="{w}" height="{h}" fill="#1a1a1a"/>{body}</svg>')

# ---------- CAP FRONT ----------
def cap_front():
    W, H = 297, 210
    # cap silhouette (generic 6-panel front view, crown + brim)
    cap = ('<path d="M60,135 C60,70 110,40 150,40 C190,40 240,70 240,135 Z" fill="#0A0A0A"/>'
           '<path d="M150,40 L150,135" stroke="#222" stroke-width="0.6"/>'
           '<path d="M95,52 C100,90 100,120 102,135" stroke="#222" stroke-width="0.6" fill="none"/>'
           '<path d="M205,52 C200,90 200,120 198,135" stroke="#222" stroke-width="0.6" fill="none"/>'
           '<path d="M40,135 L260,135 C262,152 238,168 150,168 C62,168 38,152 40,135 Z" fill="#111"/>')
    # embroidery: horizontal lockup 95mm wide, centred, bottom edge 20mm above brim seam (y=135)
    lk = lockup_h(100, CHALK, None, None)  # mono white
    body_g, hh = fit(lk, 0, 0, 95)
    # lockup svg has padding; compute placement: centre x=150, bottom ink ~ y=115
    g, hh = fit(lk, 150 - 95 / 2, 115 - hh, 95)
    body = cap + g
    body += dim(102.5, 120, 197.5, 120, "95 mm")
    body += dim(250, 115 - hh, 250, 135, "")
    body += note(42, 182, [
        "CAP FRONT - embroidery spec",
        "Art: pojoboys-lockup-mono.svg (reversed, single thread). 95 mm wide x ~22 mm tall, centred across the two front panels.",
        "Position: bottom of the wordmark 20 mm above the brim seam. Mark cap-height ~22 mm, stroke min 1.6 mm - safe for satin stitch.",
        "Threads: 1 colour = white (Madeira Classic 40 #1001 / Isacord 0015). Optional 2nd: Kit Orange for the bowl only (Madeira 1278 / Isacord 1306).",
        "Alt front: crest at 58 mm diameter, same centre, 1 or 2 threads. Density 0.40 mm satin, no fill-stitch areas below 2 mm.",
    ])
    return sheet(W, H, body, "POJO BOYS cap front")

# ---------- TEE FRONT ----------
def tee(w=297, h=420):
    # generic t-shirt outline at 1:2 (size M, chest ~460 mm, length ~400 mm)
    t = ('<path d="M85,45 L120,38 C130,52 170,52 180,38 L215,45 L260,105 L228,118 L228,245 L72,245 L72,118 L40,105 Z" fill="#0A0A0A" stroke="#2a2a2a" stroke-width="0.6"/>'
         '<path d="M120,38 C130,52 170,52 180,38" fill="none" stroke="#2a2a2a" stroke-width="0.6"/>')
    return t

def tee_front():
    W, H = 297, 300
    body = tee()
    # scale: 1:2. Left chest logo: mark 40 mm tall real = 20 units; centre at 100 mm left of... wearer's left = viewer's right
    mk = __import__("build_brand").mark_only(100, CHALK, None, None)
    g, hh = fit(mk, 0, 0, 1)  # dummy
    # real: mark 36 mm tall -> at 1:2 = 18 units; place centre x=150+45 (90 mm right of centre), y=40+ (85mm below collar)/2
    from build_brand import mark_only
    mk = mark_only(100, CHALK, None, None)
    _, w0, h0 = inner(mk); s = 18 / h0
    g = f'<g transform="translate({195 - w0*s/2:.2f},{50 + 42 - h0*s/2:.2f}) scale({s:.5f})">{inner(mk)[0]}</g>'
    body += g
    body += dim(150, 55, 150, 245, "centre line")
    body += dim(150, 92, 195 - w0*s/2, 92, "90 mm")
    body += note(20, 262, [
        "TEE FRONT - left chest (wearer's left)",
        "Art: pojoboys-mark-mono.svg, 36 mm tall (~30 mm wide). Centre 90 mm from centre line, 85 mm below the collar seam.",
        "Print: white screen print or DTF; or embroider with the cap spec. Diagram is 1:2 scale.",
        "Optional 2-colour: bowl in Kit Orange (Pantone 1655 C / #FF5A1F).",
    ])
    return sheet(W, H, body, "POJO BOYS tee front")

def tee_back():
    W, H = 297, 300
    body = tee()
    bl = blocks(20, CHALK, ORANGE, None)[0]
    # back graphic: block mark 240 mm tall real -> 120 units; centred, top 90 mm below collar -> y=40+45
    _, w0, h0 = inner(bl); s = 100 / h0
    body += f'<g transform="translate({150 - w0*s/2:.2f},{92:.2f}) scale({s:.5f})">{inner(bl)[0]}</g>'
    wb, wbd = word_body(100, CHALK, 0.08)
    ww = wbd[2] - wbd[0]; s2 = 100 / ww   # wordmark 200 mm wide real -> 100 units
    body += f'<g transform="translate({150 - ww*s2/2 - wbd[0]*s2:.2f},{92 + 100 + 12 - wbd[1]*s2:.2f}) scale({s2:.5f})">{wb}</g>'
    body += dim(150, 92, 150, 192, "200 mm")
    body += note(20, 262, [
        "TEE BACK - large graphic, centred",
        "Art: pojoboys-mark-blocks-colour.svg at 200 mm tall + wordmark 200 mm wide, 24 mm below the mark. Top of mark 90 mm below the collar seam.",
        "Print: 2-colour screen print, white + Kit Orange (Pantone 1655 C), or DTF. Diagram is 1:2 scale.",
        "Kit-number variant: replace wordmark with first name + number (e.g. MAAN 7 / AVIR 11) in Unbounded 800, 200 mm wide, same position.",
    ])
    return sheet(W, H, body, "POJO BOYS tee back")

if __name__ == "__main__":
    open("dist/merch/cap-front.svg", "w").write(cap_front())
    open("dist/merch/tee-front.svg", "w").write(tee_front())
    open("dist/merch/tee-back.svg", "w").write(tee_back())
    print("merch ok")
