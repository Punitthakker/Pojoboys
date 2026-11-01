# POJO BOYS

Family brand for two brothers. Name from Java's Plain Old Java Object.

- `site/index.html` - pojoboys.com. One self-contained file (fonts inlined), no build step, no tracking, no forms.
- `brand/logo/` - logo set as outlined SVG (colour, mono, reversed, stacked, mark, crest, block variant, avatar, favicon).
- `brand/merch/` - cap and tee spec sheets with placement, sizes and thread references.
- `brand/brand-system.html` - palette, type, voice and rules.
- `tools/` - generators. `npm i` then `python3 tools/build_brand.py && python3 tools/build_merch.py && python3 tools/build_site.py` (needs `fonttools` and `skia-pathops`).

Deploys to Netlify from `site/` (see `netlify.toml`).
