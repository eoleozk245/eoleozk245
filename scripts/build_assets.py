#!/usr/bin/env python3
"""Gera os SVGs estáticos do perfil: banner, cabeçalhos de seção, cards de
projeto e rodapé.

Uso:
    python3 scripts/build_assets.py                 # escreve em assets/
    python3 scripts/build_assets.py --static        # sem animação (pré-visualização)
    python3 scripts/build_assets.py --out /tmp/x    # outra pasta de saída

Para adicionar um projeto novo, edite a lista PROJECTS mais abaixo e rode o
script de novo. Só entram dados que você consegue comprovar no repositório.
"""
import argparse
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from theme import (BG0, BG1, BLUE, BORDER, CYAN, DIM, ELECTRIC, GRID, HEADER,  # noqa: E402
                   MUTED, PANEL, PANEL_2, SOFT, TEXT, esc, fade_in, svg_open)

USER = "eoleozk245"


# ---------------------------------------------------------------------------
# utilidades
# ---------------------------------------------------------------------------
class Anim:
    """Gera tags de animação SMIL; em modo estático não gera nada."""

    def __init__(self, static: bool):
        self.static = static

    def tag(self, markup: str) -> str:
        return "" if self.static else markup


def typing_plan(phrases, type_s=0.06, hold_s=1.9, erase_step=0.035, gap_s=0.4):
    """Linha do tempo do efeito de digitação.

    Retorna (eventos_por_frase, duracao_total). Cada evento é (tempo_s,
    caracteres_visiveis).
    """
    t = 0.0
    plans = []
    for phrase in phrases:
        n = len(phrase)
        events = [(round(t, 4), 0)]
        for k in range(1, n + 1):
            events.append((round(t + k * type_s, 4), k))
        t_erase = t + n * type_s + hold_s
        k, step = n, 0
        while k > 0:
            step += 1
            k = max(0, k - 2)
            events.append((round(t_erase + step * erase_step, 4), k))
        t = events[-1][0] + gap_s
        plans.append(events)
    return plans, round(t, 4)


def discrete(values, times, total):
    """Monta os atributos values/keyTimes de uma animação discreta."""
    vals = ";".join(str(v) for v in values)
    keys = ";".join(f"{t / total:.6f}" for t in times)
    return (f'values="{vals}" keyTimes="{keys}" dur="{total}s" '
            f'calcMode="discrete" repeatCount="indefinite"')


# ---------------------------------------------------------------------------
# banner
# ---------------------------------------------------------------------------
PHRASES = [
    "Estudante de Informática para Internet",
    "HTML · CSS · JavaScript",
    "Construindo interfaces responsivas",
    "Curioso por IA e cibersegurança",
    "Aprendendo com projetos reais",
]

CODE = [
    (0, [("const", "kw"), (" leonardo", "id"), (" = ", "pn"), ("{", "pn")]),
    (1, [("curso", "pr"), (": ", "pn"), ('"Informática para Internet"', "st"), (",", "pn")]),
    (1, [("foco", "pr"), (": [", "pn"), ('"HTML"', "st"), (", ", "pn"), ('"CSS"', "st"),
         (", ", "pn"), ('"JavaScript"', "st"), ("],", "pn")]),
    (1, [("interesses", "pr"), (": [", "pn"), ('"IA"', "st"), (", ", "pn"),
         ('"Cibersegurança"', "st"), ("],", "pn")]),
    (1, [("status", "pr"), (": ", "pn"), ('"construindo projetos"', "st"), (",", "pn")]),
    (0, [("};", "pn")]),
    (0, [("// sempre evoluindo", "cm")]),
]
TOKEN_COLORS = {"kw": "#6ea8ff", "id": CYAN, "pr": "#9ecbff", "st": "#7ee7d9",
                "pn": MUTED, "cm": "#5b6b82"}


def banner(static=False) -> str:
    W, H = 1000, 320
    an = Anim(static)
    CW = 12                 # largura de cada caractere da frase (fonte 20px mono)
    TX, TY = 84, 252        # início e linha-base da frase digitada
    plans, total = typing_plan(PHRASES)
    o = [svg_open(W, H, "Leonardo — Desenvolvimento Web e Tecnologia",
                  "Banner com o nome Leonardo, a área Desenvolvimento Web e Tecnologia, "
                  "frases animadas sobre meus estudos e uma janela de código.")]

    # --- defs ---------------------------------------------------------------
    o.append(f"""<defs>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{BG0}"/><stop offset="1" stop-color="{BG1}"/></linearGradient>
<radialGradient id="gc" cx="0.2" cy="0.3" r="0.55"><stop offset="0" stop-color="{CYAN}" stop-opacity="0.22"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0"/></radialGradient>
<radialGradient id="gb" cx="0.85" cy="0.9" r="0.6"><stop offset="0" stop-color="{BLUE}" stop-opacity="0.26"/><stop offset="1" stop-color="{BLUE}" stop-opacity="0"/></radialGradient>
<linearGradient id="gn" gradientUnits="userSpaceOnUse" x1="52" y1="0" x2="396" y2="0"><stop offset="0" stop-color="{CYAN}"/><stop offset="1" stop-color="{BLUE}"/></linearGradient>
<linearGradient id="gl" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{CYAN}"/><stop offset="1" stop-color="{BLUE}"/></linearGradient>
<linearGradient id="gs" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{CYAN}" stop-opacity="0"/><stop offset="0.5" stop-color="{CYAN}"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0"/></linearGradient>
<pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0H0V40" fill="none" stroke="{GRID}" stroke-width="1"/></pattern>
<filter id="glow" x="-20%" y="-40%" width="140%" height="180%"><feGaussianBlur stdDeviation="9"/></filter>
<clipPath id="round"><rect width="{W}" height="{H}" rx="16"/></clipPath>
""")
    # clipPaths da digitação (sem animação, a 1ª frase aparece completa)
    if static:
        o.append(f'<clipPath id="tc0"><rect x="{TX}" y="{TY - 24}" width="{len(PHRASES[0]) * CW}" height="32"/></clipPath>')
    else:
        for i, events in enumerate(plans):
            pts = events if events[0][0] == 0 else [(0.0, 0)] + events
            base_w = len(PHRASES[0]) * CW if i == 0 else 0
            o.append(
                f'<clipPath id="tc{i}"><rect x="{TX}" y="{TY - 24}" width="{base_w}" height="32">'
                f'<animate attributeName="width" {discrete([w * CW for _, w in pts], [t for t, _ in pts], total)}/>'
                f"</rect></clipPath>")
    o.append("</defs>")

    # --- fundo --------------------------------------------------------------
    o.append('<g clip-path="url(#round)">')
    o.append(f'<rect width="{W}" height="{H}" fill="url(#bg)"/>')
    o.append(f'<rect width="{W}" height="{H}" fill="url(#grid)" opacity="0.55"/>')
    o.append(f'<rect width="{W}" height="{H}" fill="url(#gc)"/>')
    o.append(f'<rect width="{W}" height="{H}" fill="url(#gb)"/>')
    o.append(an.tag(
        f'<rect x="0" y="-6" width="{W}" height="3" fill="url(#gs)" opacity="0.3">'
        f'<animate attributeName="y" from="-6" to="{H + 6}" dur="7s" repeatCount="indefinite"/></rect>'))
    particles = [(140, 40, 1.6, 5.0), (300, 96, 1.2, 6.5), (470, 60, 1.8, 4.2), (520, 292, 1.4, 5.6),
                 (90, 296, 1.4, 6.1), (420, 304, 1.2, 4.8), (540, 150, 1.6, 5.3), (30, 150, 1.2, 6.8),
                 (968, 304, 1.6, 4.5), (984, 120, 1.2, 5.9)]
    for i, (cx, cy, r, d) in enumerate(particles):
        a_op = an.tag(f'<animate attributeName="opacity" values="0.1;0.85;0.1" dur="{d}s" begin="{i * 0.7:.1f}s" repeatCount="indefinite"/>')
        a_cy = an.tag(f'<animate attributeName="cy" values="{cy};{cy - 7};{cy}" dur="{d + 2}s" repeatCount="indefinite"/>')
        o.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{CYAN}" opacity="0.4">{a_op}{a_cy}</circle>')
    o.append("</g>")
    o.append(f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="16" fill="none" stroke="{CYAN}" stroke-opacity="0.28"/>')
    for d in (f"M20 44V20H44", f"M{W - 44} 20H{W - 20}V44", f"M20 {H - 44}V{H - 20}H44", f"M{W - 44} {H - 20}H{W - 20}V{H - 44}"):
        o.append(f'<path d="{d}" fill="none" stroke="{CYAN}" stroke-opacity="0.55" stroke-width="1.6" stroke-linecap="round"/>')

    # --- coluna esquerda ----------------------------------------------------
    o.append(f'<text class="m" x="56" y="72" font-size="15" fill="{MUTED}">'
             f'<tspan fill="{BLUE}">~/leonardo</tspan> <tspan fill="{CYAN}">$</tspan> <tspan fill="{SOFT}">whoami</tspan></text>')
    o.append(f'<text class="s" x="52" y="152" font-size="76" font-weight="800" fill="{CYAN}" opacity="0.35" '
             f'filter="url(#glow)" textLength="344" lengthAdjust="spacingAndGlyphs">Leonardo</text>')
    o.append(f'<text class="s" x="52" y="152" font-size="76" font-weight="800" fill="url(#gn)" '
             f'textLength="344" lengthAdjust="spacingAndGlyphs">Leonardo{an.tag(fade_in(0.1, 0.7))}</text>')
    o.append(f'<text class="s" x="56" y="194" font-size="24" font-weight="500" fill="{TEXT}" '
             f'textLength="396" lengthAdjust="spacingAndGlyphs">Desenvolvimento Web &amp; Tecnologia{an.tag(fade_in(0.35, 0.7))}</text>')
    w_line = 132
    grow = an.tag(f'<animate attributeName="width" values="0;0;{w_line}" keyTimes="0;0.4;1" dur="1.5s" begin="0s" fill="freeze"/>')
    o.append(f'<rect x="56" y="210" width="{w_line}" height="3" rx="1.5" fill="url(#gl)">{grow}</rect>')

    # frase digitada
    o.append(f'<text class="m" x="56" y="{TY}" font-size="20" fill="{BLUE}">&gt;</text>')
    if static:
        o.append(f'<g clip-path="url(#tc0)"><text class="m" x="{TX}" y="{TY}" font-size="20" fill="{TEXT}" '
                 f'textLength="{len(PHRASES[0]) * CW}" lengthAdjust="spacing">{esc(PHRASES[0])}</text></g>')
        o.append(f'<rect x="{TX + len(PHRASES[0]) * CW}" y="{TY - 20}" width="9" height="24" fill="{CYAN}"/>')
    else:
        for i, phrase in enumerate(PHRASES):
            o.append(f'<g clip-path="url(#tc{i})"><text class="m" x="{TX}" y="{TY}" font-size="20" fill="{TEXT}" '
                     f'textLength="{len(phrase) * CW}" lengthAdjust="spacing">{esc(phrase)}</text></g>')
        cur = [(0.0, 0)] + [e for events in plans for e in events if e[0] > 0]
        # remove tempos repetidos mantendo o último valor
        dedup = {}
        for t, w in cur:
            dedup[t] = w
        times = sorted(dedup)
        o.append(
            f'<rect x="{TX + len(PHRASES[0]) * CW}" y="{TY - 20}" width="9" height="24" fill="{CYAN}">'
            f'<animate attributeName="x" {discrete([TX + dedup[t] * CW for t in times], times, total)}/>'
            f'<animate attributeName="opacity" values="1;0" dur="1s" calcMode="discrete" repeatCount="indefinite"/></rect>')

    # --- janela de código ---------------------------------------------------
    wx, wy, ww, wh = 560, 44, 388, 232
    o.append(f'<rect x="{wx}" y="{wy}" width="{ww}" height="{wh}" rx="12" fill="{PANEL_2}" fill-opacity="0.92" '
             f'stroke="{CYAN}" stroke-opacity="0.3"/>')
    o.append(f'<path d="M{wx} {wy + 34}V{wy + 12}a12 12 0 0 1 12 -12H{wx + ww - 12}a12 12 0 0 1 12 12V{wy + 34}Z" fill="{HEADER}"/>')
    o.append(f'<path d="M{wx} {wy + 34}H{wx + ww}" stroke="{BORDER}"/>')
    for i, c in enumerate((ELECTRIC, "#00a8c4", "#2a3b52")):
        o.append(f'<circle cx="{wx + 20 + i * 18}" cy="{wy + 17}" r="5" fill="{c}"/>')
    o.append(f'<text class="m" x="{wx + ww // 2}" y="{wy + 21}" font-size="12" fill="{MUTED}" text-anchor="middle">perfil.js</text>')
    cx0, cy0, step, fs = wx + 24, wy + 64, 24, 13.5
    cwc = fs * 0.6
    for i, (indent, tokens) in enumerate(CODE):
        y = cy0 + i * step
        x = cx0 + indent * 2 * cwc
        spans = "".join(f'<tspan fill="{TOKEN_COLORS[k]}">{esc(txt)}</tspan>' for txt, k in tokens)
        reveal = an.tag(fade_in(round(0.6 + i * 0.45, 2), 0.35))
        o.append(f'<g><text class="m" x="{x:.1f}" y="{y}" font-size="{fs}">{spans}</text>{reveal}</g>')
    last_y = cy0 + (len(CODE) - 1) * step
    cursor_x = cx0 + len("// sempre evoluindo") * cwc + 6
    blink = an.tag('<animate attributeName="opacity" values="1;0" dur="1s" calcMode="discrete" repeatCount="indefinite"/>')
    o.append(f'<rect x="{cursor_x:.1f}" y="{last_y - 12}" width="7" height="15" fill="{CYAN}">{blink}</rect>')

    o.append("</svg>")
    return "".join(o)


# ---------------------------------------------------------------------------
# cabeçalhos de seção (estilo prompt de terminal)
# ---------------------------------------------------------------------------
SECTIONS = [
    ("sobre", "Sobre mim"),
    ("stack", "Tecnologias"),
    ("projetos", "Projetos"),
    ("dashboard", "Dashboard"),
]


def _text_width(s: str, fs: float) -> float:
    """Estima a largura de um texto sans-serif em negrito (px) para centralizar a cápsula."""
    w = 0.0
    for ch in s:
        if ch == " ":
            w += 0.30
        elif ch in "ilj":
            w += 0.28
        elif ch in "tfr":
            w += 0.36
        elif ch in "mw":
            w += 0.86
        elif ch.isupper():
            w += 0.68
        else:
            w += 0.58
    return w * fs


def section_header(title: str, static=False, size=24) -> str:
    """Título de seção centralizado: cápsula escura com borda em gradiente, linhas
    que somem nas pontas, losangos e um pontinho viajando em direção ao título."""
    W = 1000
    fs = size
    tw = _text_width(title, fs)
    cap_h = round(fs * 1.9)
    cap_w = tw + fs * 2.4
    H = cap_h + 20
    cx, cy = W / 2, H / 2
    x0, x1 = cx - cap_w / 2, cx + cap_w / 2
    le, rs = x0 - 16, x1 + 16                      # fim da linha esquerda / início da direita
    margin = 48
    an = Anim(static)
    o = [svg_open(W, H, f"Seção: {title}", f"Título da seção {title}")]
    o.append(f'''<defs>
<linearGradient id="bd" gradientUnits="userSpaceOnUse" x1="{x0:.1f}" y1="0" x2="{x1:.1f}" y2="0"><stop offset="0" stop-color="{CYAN}"/><stop offset="1" stop-color="{BLUE}"/></linearGradient>
<linearGradient id="tx" gradientUnits="userSpaceOnUse" x1="{cx - tw / 2:.1f}" y1="0" x2="{cx + tw / 2:.1f}" y2="0"><stop offset="0" stop-color="{CYAN}"/><stop offset="1" stop-color="#5aa2ff"/></linearGradient>
<linearGradient id="ll" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{CYAN}" stop-opacity="0"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0.85"/></linearGradient>
<linearGradient id="lr" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{BLUE}" stop-opacity="0.85"/><stop offset="1" stop-color="{BLUE}" stop-opacity="0"/></linearGradient>
<filter id="glow" x="-30%" y="-80%" width="160%" height="260%"><feGaussianBlur stdDeviation="9"/></filter>
</defs>''')
    # brilho suave atrás da cápsula
    o.append(f'<rect x="{x0:.1f}" y="{cy - cap_h / 2:.1f}" width="{cap_w:.1f}" height="{cap_h}" rx="{cap_h / 2}" '
             f'fill="{CYAN}" opacity="0.13" filter="url(#glow)"/>')
    # linhas laterais que somem nas pontas
    o.append(f'<rect x="{margin}" y="{cy - 1}" width="{le - margin:.1f}" height="2" rx="1" fill="url(#ll)"/>')
    o.append(f'<rect x="{rs:.1f}" y="{cy - 1}" width="{W - margin - rs:.1f}" height="2" rx="1" fill="url(#lr)"/>')
    # losangos nas pontas internas + pontinho viajando em direção ao título
    for x_end, x_start, col in ((le, margin, CYAN), (rs, W - margin, BLUE)):
        travel = an.tag(f'<animate attributeName="cx" values="{x_start};{x_end:.1f}" dur="3s" repeatCount="indefinite"/>'
                        f'<animate attributeName="opacity" values="0;0.9;0.9;0" keyTimes="0;0.2;0.8;1" dur="3s" repeatCount="indefinite"/>')
        o.append(f'<circle cx="{x_end:.1f}" cy="{cy}" r="2.4" fill="{col}" opacity="0">{travel}</circle>')
        o.append(f'<rect x="{x_end - 3.5:.1f}" y="{cy - 3.5}" width="7" height="7" rx="1" fill="{col}" '
                 f'transform="rotate(45 {x_end:.1f} {cy})"/>')
    # cápsula com borda em gradiente (respira de leve)
    pulse = an.tag('<animate attributeName="stroke-opacity" values="0.55;1;0.55" dur="3.5s" repeatCount="indefinite"/>')
    o.append(f'<rect x="{x0:.1f}" y="{cy - cap_h / 2:.1f}" width="{cap_w:.1f}" height="{cap_h}" rx="{cap_h / 2}" '
             f'fill="{BG1}" stroke="url(#bd)" stroke-width="1.5" stroke-opacity="0.8">{pulse}</rect>')
    o.append(f'<text class="s" x="{cx}" y="{cy + fs * 0.36:.1f}" font-size="{fs}" font-weight="700" text-anchor="middle" '
             f'fill="url(#tx)" textLength="{tw:.1f}" lengthAdjust="spacingAndGlyphs">{esc(title)}</text>')
    o.append("</svg>")
    return "".join(o)


# ---------------------------------------------------------------------------
# cards de projetos
#   Preencha APENAS com o que dá para comprovar no repositório.
# ---------------------------------------------------------------------------
PROJECTS = [
    {
        "slug": "sustentabilidade",
        "repo": "Site-SUSTENTABILIDADE-FETEC",
        "lines": ["Vitrine com 14 projetos de sustentabilidade",
                  "e tecnologia da turma, em 5 categorias, com",
                  "busca, favoritos e tema claro/escuro."],
        "techs": ["HTML", "CSS", "JavaScript"],
    },
    {
        "slug": "barbearia",
        "repo": "BARBEARIA-Daniel",
        "lines": ["Sistema de barbearia com agendamento online,",
                  "QR Code por agendamento e painéis para",
                  "barbeiro e administrador."],
        "techs": ["HTML", "CSS", "JavaScript", "Supabase"],
    },
    {
        "slug": "jogos",
        "repo": "SITE-JOGOS-FETEC",
        "lines": ["Galeria com 14 jogos em JavaScript criados",
                  "pelos alunos do 1º ano de Informática",
                  "para Internet da ETEC."],
        "techs": ["HTML", "CSS", "JavaScript"],
    },
    {
        "slug": "fetec-2026",
        "repo": "FETEC-2026",
        "lines": ["Plataforma de jogos Scratch da FETEC 2026:",
                  "catálogo, busca, filtros, favoritos e",
                  "acesso administrativo com Supabase."],
        "techs": ["HTML", "JavaScript", "Tailwind", "Supabase"],
    },
    {
        "slug": "ecocity",
        "repo": "ecocity-os-core",
        "lines": ["EcoCity OS: site sobre cidades inteligentes e",
                  "sustentáveis, com visual de painel de sistema",
                  "operacional. Criado com Lovable."],
        "techs": ["TypeScript", "Lovable"],
    },
]


def _pills(techs, x, y):
    parts, cx = [], x
    for tech in techs:
        w = len(tech) * 7 + 18
        parts.append(f'<rect x="{cx}" y="{y}" width="{w}" height="22" rx="11" fill="{HEADER}" stroke="{BORDER}"/>'
                     f'<text class="m" x="{cx + w / 2:.1f}" y="{y + 15}" font-size="11" fill="{CYAN}" text-anchor="middle">{esc(tech)}</text>')
        cx += w + 8
    return "".join(parts)


def project_card(p: dict, static=False) -> str:
    W, H = 400, 200
    an = Anim(static)
    o = [svg_open(W, H, f"Projeto {p['repo']}", " ".join(p["lines"]))]
    o.append(f'<defs><linearGradient id="ac" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{CYAN}"/>'
             f'<stop offset="1" stop-color="{BLUE}"/></linearGradient></defs>')
    pulse = an.tag('<animate attributeName="stroke-opacity" values="0.55;1;0.55" dur="4s" repeatCount="indefinite"/>')
    o.append(f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="14" fill="{PANEL}" stroke="{BORDER}" stroke-opacity="0.8">{pulse}</rect>')
    o.append(f'<rect x="24" y="1" width="96" height="3" rx="1.5" fill="url(#ac)"/>')
    o.append(f'<path d="M24 31h8l3 3h11a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H26a2 2 0 0 1-2-2V33a2 2 0 0 1 2-2z" fill="none" '
             f'stroke="{CYAN}" stroke-width="1.6" stroke-linejoin="round"/>')
    name = p["repo"]
    o.append(f'<text class="m" x="58" y="47" font-size="15" font-weight="700" fill="{TEXT}">{esc(name)}</text>')
    for i, line in enumerate(p["lines"]):
        o.append(f'<text class="s" x="24" y="{82 + i * 20}" font-size="13.5" fill="{SOFT}">{esc(line)}</text>')
    o.append(_pills(p["techs"], 24, 142))
    o.append(f'<text class="m" x="24" y="186" font-size="11" fill="{MUTED}">↗ github.com/{USER}/{esc(name)}</text>')
    o.append("</svg>")
    return "".join(o)


def placeholder_card(static=False) -> str:
    W, H = 400, 200
    an = Anim(static)
    o = [svg_open(W, H, "Espaço para o próximo projeto", "Espaço reservado para novos projetos.")]
    dash = an.tag('<animate attributeName="stroke-dashoffset" from="0" to="-24" dur="3s" repeatCount="indefinite"/>')
    o.append(f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="14" fill="{BG1}" stroke="{DIM}" '
             f'stroke-width="1.5" stroke-dasharray="6 6">{dash}</rect>')
    o.append(f'<circle cx="200" cy="82" r="22" fill="none" stroke="{CYAN}" stroke-width="1.6"/>')
    o.append(f'<path d="M200 71V93M189 82H211" stroke="{CYAN}" stroke-width="2" stroke-linecap="round"/>')
    o.append(f'<text class="m" x="200" y="136" font-size="15" font-weight="700" fill="{TEXT}" text-anchor="middle">próximo projeto</text>')
    o.append(f'<text class="s" x="200" y="160" font-size="13" fill="{MUTED}" text-anchor="middle">espaço reservado para o que vem por aí</text>')
    o.append("</svg>")
    return "".join(o)


# ---------------------------------------------------------------------------
# rodapé
# ---------------------------------------------------------------------------
def footer(static=False) -> str:
    """Ondas preenchidas em camadas, com degradê de ciano para azul, se movendo devagar. Sem texto."""
    W, H = 1000, 100
    an = Anim(static)
    o = [svg_open(W, H, "Rodapé", "Ondas animadas em degradê de ciano e azul")]
    o.append(f'''<defs>
<linearGradient id="bgf" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{BG0}"/><stop offset="1" stop-color="{BG1}"/></linearGradient>
<linearGradient id="wf" gradientUnits="userSpaceOnUse" x1="0" y1="30" x2="0" y2="{H}"><stop offset="0" stop-color="{CYAN}" stop-opacity="0.8"/><stop offset="1" stop-color="{BLUE}" stop-opacity="0.1"/></linearGradient>
<linearGradient id="wl" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{CYAN}"/><stop offset="1" stop-color="{BLUE}"/></linearGradient>
<clipPath id="fr"><rect width="{W}" height="{H}" rx="16"/></clipPath>
</defs>''')
    o.append(f'<rect width="{W}" height="{H}" rx="16" fill="url(#bgf)"/>')
    o.append('<g clip-path="url(#fr)">')
    # (período, amplitude, linha-base, opacidade, duração, fase): do fundo para a frente
    layers = [(330, 9, 42, 0.30, 14, 0.0), (250, 8, 54, 0.45, 10, 1.7), (190, 7, 66, 0.70, 7, 3.1)]
    for i, (period, amp, base, op, dur, phase) in enumerate(layers):
        xs = list(range(0, W + period * 2 + 1, 8))
        top = [f"{x},{base + amp * math.sin(2 * math.pi * x / period + phase):.1f}" for x in xs]
        d_fill = "M" + " L".join(top) + f" L{xs[-1]},{H} L0,{H} Z"
        move = an.tag(f'<animateTransform attributeName="transform" type="translate" from="0 0" to="-{period} 0" '
                      f'dur="{dur}s" repeatCount="indefinite"/>')
        o.append(f'<path d="{d_fill}" fill="url(#wf)" opacity="{op}">{move}</path>')
        if i == len(layers) - 1:                   # linha de crista só na onda da frente
            d_line = "M" + " L".join(top)
            o.append(f'<path d="{d_line}" fill="none" stroke="url(#wl)" stroke-width="1.6" opacity="0.9">{move}</path>')
    o.append("</g>")
    o.append(f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="16" fill="none" stroke="{BORDER}"/>')
    o.append("</svg>")
    return "".join(o)


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=str(Path(__file__).resolve().parent.parent / "assets"))
    ap.add_argument("--static", action="store_true", help="gera sem animações (pré-visualização)")
    args = ap.parse_args()
    out = Path(args.out)
    (out / "cards").mkdir(parents=True, exist_ok=True)

    # banner.svg e os títulos/rodapé agora vêm de scripts/build_headers.py (e do banner animado), não daqui
    files = {"cards/placeholder.svg": placeholder_card(args.static)}
    for p in PROJECTS:
        files[f"cards/{p['slug']}.svg"] = project_card(p, args.static)

    for name, content in files.items():
        (out / name).write_text(content + "\n", encoding="utf-8")
        print(f"ok  {out / name}  ({len(content):,} bytes)")


if __name__ == "__main__":
    main()
