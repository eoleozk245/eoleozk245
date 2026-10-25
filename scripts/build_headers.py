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
    ("stack", [("Minhas ", False), ("tecnologias", True)], "03"),
    ("projetos", [("Projetos em ", False), ("destaque", True)], "04"),
    ("dashboard", [("Dashboard do ", False), ("GitHub", True)], "05"),
    ("contatos", [("Fale ", False), ("comigo", True)], "02"),
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


def section(parts, num, H=46, W=620):
    serif = "".join(t for t, _ in parts); fs = 24
    fonts = fonts_css(serif, num)
    cy = H / 2
    tspans = "".join(f'<tspan font-style="{"italic" if it else "normal"}" font-weight="{700 if it else 800}">{t}</tspan>' for t, it in parts)
    pw = 44
    body = (f'<rect x="20" y="{cy - 10}" width="{pw}" height="20" rx="10" fill="{INK}"/>'
            f'<circle cx="33" cy="{cy}" r="2.6" fill="{ACC}"/>'
            f'<text x="41" y="{cy + 3.3}" font-family="JK" font-weight="700" font-size="9" fill="{ACC}">{num}</text>'
            f'<text x="{20 + pw + 12}" y="{cy + fs * .33:.1f}" font-family="PF" font-size="{fs}" letter-spacing="-.6" fill="{INK}">{tspans}</text>'
            + arrow(W - 20 - 12, cy, 12))
    return frame(W, H, 16, body, fonts=fonts, seed=int(num), label=serif)


def footer(W=620, H=46):
    parts = [("Obrigado por ", False), ("passar por aqui", True)]
    serif = "".join(t for t, _ in parts)
    fonts = fonts_css(serif, "")
    tspans = "".join(f'<tspan font-style="{"italic" if it else "normal"}" font-weight="{700 if it else 800}">{t}</tspan>' for t, it in parts)
    body = (f'<text x="{W / 2}" y="{H / 2 + 6}" text-anchor="middle" font-family="PF" font-size="18" letter-spacing="-.5" fill="{INK}">{tspans}</text>')
    return frame(W, H, 16, body, fonts=fonts, seed=3, label="Obrigado por passar por aqui")


# ---------------------------------------------------------------------------
# painéis claros que ficam logo abaixo das barras (contatos e tecnologias)
# ---------------------------------------------------------------------------
PW = 620
PANEL_FILL, PANEL_STROKE = "#f4faff", "#b9ddf6"


def icon_img(name, x, y, size=48):
    b64 = base64.b64encode((HERE.parent / "assets" / "icons" / f"{name}.svg").read_bytes()).decode()
    return f'<image x="{x}" y="{y}" width="{size}" height="{size}" href="data:image/svg+xml;base64,{b64}"/>'


def panel_bg(H):
    return (f'<defs><linearGradient id="pg" x1="0" y1="0" x2="1" y2="0.6"><stop offset="0" stop-color="#b9e0ff"/><stop offset=".5" stop-color="#d2ecff"/><stop offset="1" stop-color="#bfe3ff"/></linearGradient></defs>'
            f'<rect x="1" y="1" width="{PW - 2}" height="{H - 2}" rx="14" fill="url(#pg)" stroke="#8fcbf3" stroke-width="1.5"/>')


def pill(cx, y, text):
    w = len(text) * 8.2 + 44
    return (f'<rect x="{cx - w / 2:.1f}" y="{y}" width="{w:.1f}" height="26" rx="13" fill="{INK}"/>'
            f'<circle cx="{cx - w / 2 + 15:.1f}" cy="{y + 13}" r="3.4" fill="{ACC}"/>'
            f'<text x="{cx - w / 2 + 26:.1f}" y="{y + 17.5}" font-family="JK" font-weight="700" font-size="13" fill="#fff">{text}</text>')


def svg_wrap(vb_x, vb_w, H, inner, fonts, label):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb_x} 0 {vb_w} {H}" width="{vb_w}" height="{H}" role="img" aria-label="{label}">'
            f'<defs><style>{fonts}</style></defs>{inner}</svg>')


def contact_slices():
    H = 88
    items = [("instagram", "Instagram"), ("whatsapp", "WhatsApp"), ("gmail", "E-mail")]
    edges = [0, 207, 413, PW]
    fonts = fonts_css("", "".join(l for _, l in items))
    out = {}
    for i, (ic, label) in enumerate(items):
        cx = PW / 6 + i * PW / 3
        inner = (panel_bg(H) + icon_img(ic, round(cx - 20), 12, 40)
                 + f'<text x="{cx:.1f}" y="{H - 13}" text-anchor="middle" font-family="JK" font-weight="700" font-size="12" fill="{INK}">{label}</text>')
        out[f"contato-{ic}.svg"] = svg_wrap(edges[i], edges[i + 1] - edges[i], H, inner, fonts, label)
    return out


def stack_panel():
    H = 188
    rows = [("Linguagens", ["html", "css", "js"]), ("Ferramentas", ["supabase", "vscode", "git", "github"])]
    fonts = fonts_css("", "LinguagensFerramentas")
    inner, y = panel_bg(H), 14
    for title, icons in rows:
        inner += pill(PW / 2, y, title)
        n, size, gap = len(icons), 40, 16
        x0 = (PW - (n * size + (n - 1) * gap)) / 2
        for k, ic in enumerate(icons):
            inner += icon_img(ic, round(x0 + k * (size + gap)), y + 34, size)
        y += 86
    return svg_wrap(0, PW, H, inner, fonts, "Linguagens: HTML, CSS, JavaScript. Ferramentas: Supabase, VS Code, Git, GitHub")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(HERE.parent / "assets"))
    out = Path(ap.parse_args().out)
    files = {f"section-{slug}.svg" if slug != "contatos" else "contatos.svg": section(parts, num) for slug, parts, num in SECTIONS}
    files["footer.svg"] = footer()
    files.update(contact_slices())
    files["stack-panel.svg"] = stack_panel()
    for n, c in files.items():
        (out / n).write_text(c + "\n", encoding="utf-8"); print("ok", n, f"{len(c) // 1024} KB")


if __name__ == "__main__":
    main()
