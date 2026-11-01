"""Convert text to SVG path data using fontTools (no font dependency in output)."""
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen

FONTS = {
    "unbounded": "node_modules/@fontsource/unbounded/files/unbounded-latin-900-normal.woff",
    "unbounded800": "node_modules/@fontsource/unbounded/files/unbounded-latin-800-normal.woff",
    "syne": "node_modules/@fontsource/syne/files/syne-latin-800-normal.woff",
    "grotesk": "node_modules/@fontsource/space-grotesk/files/space-grotesk-latin-700-normal.woff",
    "mono": "node_modules/@fontsource/jetbrains-mono/files/jetbrains-mono-latin-800-normal.woff",
    "inter": "node_modules/@fontsource/inter/files/inter-latin-700-normal.woff",
}
_cache = {}

def font(name):
    if name not in _cache:
        _cache[name] = TTFont(FONTS[name])
    return _cache[name]

def glyph_d(fname, ch, size, x, y):
    """Return (path d, advance) for one glyph placed at baseline origin (x,y) at given px size."""
    f = font(fname)
    cmap = f.getBestCmap()
    gs = f.getGlyphSet()
    upm = f["head"].unitsPerEm
    s = size / upm
    gname = cmap[ord(ch)]
    g = gs[gname]
    pen = SVGPathPen(gs, ntos=lambda v: f"{v:.2f}")
    tpen = TransformPen(pen, (s, 0, 0, -s, x, y))
    g.draw(tpen)
    return pen.getCommands(), g.width * s

def text_d(fname, text, size, x=0, y=0, tracking=0.0):
    """Path d for a string. tracking is in em (e.g. -0.02)."""
    parts = []
    cx = x
    for ch in text:
        if ch == " ":
            cx += size * 0.28
            continue
        d, adv = glyph_d(fname, ch, size, cx, y)
        parts.append(d)
        cx += adv + tracking * size
    return " ".join(parts), cx - x

def text_bounds(fname, text, size, tracking=0.0):
    """Approximate ink bounds (xmin, ymin, xmax, ymax) relative to baseline origin, y up = negative."""
    f = font(fname)
    cmap = f.getBestCmap(); gs = f.getGlyphSet(); upm = f["head"].unitsPerEm; s = size / upm
    cx = 0; xmin = ymin = 1e9; xmax = ymax = -1e9
    for ch in text:
        if ch == " ":
            cx += size * 0.28; continue
        g = gs[cmap[ord(ch)]]
        bp = BoundsPen(gs); g.draw(bp)
        if bp.bounds:
            bx0, by0, bx1, by1 = bp.bounds
            xmin = min(xmin, cx + bx0 * s); xmax = max(xmax, cx + bx1 * s)
            ymin = min(ymin, -by1 * s); ymax = max(ymax, -by0 * s)
        cx += g.width * s + tracking * size
    return xmin, ymin, xmax, ymax
