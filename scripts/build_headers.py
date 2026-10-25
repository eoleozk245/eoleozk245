"""Gera os títulos de seção e o rodapé do perfil (estilo do banner: azul claro, preto, serifa + sans).

Uso: python3 scripts/build_headers.py [--out assets]
As fontes (Playfair Display e Plus Jakarta Sans) são recortadas só com os caracteres usados
e embutidas no SVG, porque o GitHub não carrega fontes externas dentro de <img>.
"""
import argparse, base64, io
from pathlib import Path
from fontTools import subset
from fontTools.ttLib import TTFont

HERE = Path(__file__).resolve().parent
FONTS = HERE / "fonts"
INK, ACC, ACC2 = "#0c0c0c", "#55c7ff", "#2ea8f0"

# (slug, [(texto, itálico?)...], número)
SECTIONS = [
    ("sobre", [("Sobre ", False), ("mim", True)], "01"),
    ("stack", [("Minhas ", False), ("tecnologias", True)], "02"),
    ("projetos", [("Projetos em ", False), ("destaque", True)], "03"),
    ("dashboard", [("Dashboard do ", False), ("GitHub", True)], "04"),
    ("contatos", [("Fale ", False), ("comigo", True)], "05"),
]


def font_face(family, file, weight, style, text):
    opts = subset.Options(); opts.flavor = "woff2"; opts.layout_features = ["kern", "liga"]
    f = TTFont(FONTS / file)
    s = subset.Subsetter(opts); s.populate(text=text); s.subset(f)
    buf = io.BytesIO(); f.flavor = "woff2"; f.save(buf)
    b64 = base64.b64encode(buf.getvalue()).decode()
    return (f"@font-face{{font-family:'{family}';font-weight:{weight};font-style:{style};"
            f"src:url(data:font/woff2;base64,{b64}) format('woff2')}}")


def fonts_css(serif_text, sans_text):
    return (font_face("PF", "playfair-display-latin-800-normal.woff2", 800, "normal", serif_text)
            + font_face("PF", "playfair-display-latin-700-italic.woff2", 700, "italic", serif_text)
            + font_face("JK", "plus-jakarta-sans-latin-700-normal.woff2", 700, "normal", sans_text))


SP = 'calcMode="spline" keyTimes="0;.25;.5;.75;1" keySplines=".45 .05 .55 .95;.45 .05 .55 .95;.45 .05 .55 .95;.45 .05 .55 .95"'


def blobs(W, H, seed=0):
    def b(fill, r, xs, ys, dur, op):
        return (f'<circle r="{r}" fill="{fill}" opacity="{op}">'
                f'<animate attributeName="cx" values="{";".join(map(str, xs))}" dur="{dur}s" repeatCount="indefinite" {SP}/>'
                f'<animate attributeName="cy" values="{";".join(map(str, ys))}" dur="{dur}s" repeatCount="indefinite" {SP}/></circle>')
    o = seed
    return "".join([
        b(ACC, H * 1.1, [W * .15, W * .45, W * .7, W * .3, W * .15], [H * .8, H * .2, H * .9, H * .6, H * .8], 19 + o, .9),
        b(ACC2, H * .9, [W * .9, W * .6, W * .35, W * .8, W * .9], [H * .9, H * .6, H * 1.0, H * .2, H * .9], 23 + o, .6),
        b("#9fe0ff", H * 1.0, [W * .55, W * .85, W * .1, W * .4, W * .55], [0, H * .1, 0, H * .1, 0], 27 + o, .9),
    ])


def frame(W, H, rx, body, defs_extra="", fonts="", seed=0, label=""):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{label}">
<defs><style>{fonts}</style>
<linearGradient id="base" x1="0" y1="0" x2="1" y2="0.4"><stop offset="0" stop-color="#b4e1ff"/><stop offset=".55" stop-color="#d4efff"/><stop offset="1" stop-color="#e9f6ff"/></linearGradient>
<filter id="bl" x="-30%" y="-80%" width="160%" height="260%"><feGaussianBlur stdDeviation="{H * .42:.0f}"/></filter>
<clipPath id="c"><rect width="{W}" height="{H}" rx="{rx}"/></clipPath>{defs_extra}</defs>
<g clip-path="url(#c)"><rect width="{W}" height="{H}" fill="url(#base)"/>
<g filter="url(#bl)">{blobs(W, H, seed)}</g>{body}</g></svg>'''


def arrow(cx, cy, r):
    s = r * .42
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{ACC}" stroke="{INK}" stroke-width="1.5"/>'
            f'<path d="M{cx - s} {cy + s} L{cx + s} {cy - s} M{cx - s * .15} {cy - s} H{cx + s} V{cy + s * .15}" fill="none" '
            f'stroke="{INK}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>')


def section(parts, num, H=60, W=1000):
    serif = "".join(t for t, _ in parts); fs = 31
    fonts = fonts_css(serif, num)
    cy = H / 2
    tspans = "".join(f'<tspan font-style="{"italic" if it else "normal"}" font-weight="{700 if it else 800}">{t}</tspan>' for t, it in parts)
    pw = 54
    body = (f'<rect x="26" y="{cy - 13}" width="{pw}" height="26" rx="13" fill="{INK}"/>'
            f'<circle cx="40" cy="{cy}" r="3.2" fill="{ACC}"/>'
            f'<text x="49" y="{cy + 4}" font-family="JK" font-weight="700" font-size="11" fill="{ACC}">{num}</text>'
            f'<text x="{26 + pw + 16}" y="{cy + fs * .33:.1f}" font-family="PF" font-size="{fs}" letter-spacing="-.6" fill="{INK}">{tspans}</text>'
            + arrow(W - 26 - 15, cy, 15))
    return frame(W, H, 22, body, fonts=fonts, seed=int(num), label=serif)


def footer(W=1000, H=64):
    parts = [("Obrigado por ", False), ("passar por aqui", True)]
    serif = "".join(t for t, _ in parts)
    fonts = fonts_css(serif, "")
    tspans = "".join(f'<tspan font-style="{"italic" if it else "normal"}" font-weight="{700 if it else 800}">{t}</tspan>' for t, it in parts)
    body = (f'<text x="{W / 2}" y="{H / 2 + 8}" text-anchor="middle" font-family="PF" font-size="23" letter-spacing="-.5" fill="{INK}">{tspans}</text>')
    return frame(W, H, 22, body, fonts=fonts, seed=3, label="Obrigado por passar por aqui")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(HERE.parent / "assets"))
    out = Path(ap.parse_args().out)
    files = {f"section-{slug}.svg" if slug != "contatos" else "contatos.svg": section(parts, num) for slug, parts, num in SECTIONS}
    files["footer.svg"] = footer()
    for n, c in files.items():
        (out / n).write_text(c + "\n", encoding="utf-8"); print("ok", n, f"{len(c) // 1024} KB")


if __name__ == "__main__":
    main()
