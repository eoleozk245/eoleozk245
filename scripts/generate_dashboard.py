#!/usr/bin/env python3
"""Gera os SVGs que dependem de dados REAIS do GitHub (rodado pelo workflow).

Subcomandos:
    dashboard --out dist        Cria overview.svg e activity.svg a partir da
                                API GraphQL do GitHub (precisa de GITHUB_TOKEN
                                e PROFILE_USER no ambiente).
    snake ARQUIVO.svg           Coloca um fundo escuro no SVG da cobrinha, para
                                ele ficar bom tanto no tema claro quanto no escuro.

Nada aqui inventa dados: se a API falhar, o script termina com erro e o
workflow para (os arquivos antigos continuam publicados).
"""
import argparse
import json
import math
import os
import re
import sys
import urllib.request
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from theme import (BLUE, BORDER, CYAN, DIM, GRID, MUTED, PANEL, PANEL_2,  # noqa: E402
                   SOFT, esc, fade_in, svg_open)

QUERY = """
query($login: String!) {
  user(login: $login) {
    repositories(privacy: PUBLIC, ownerAffiliations: OWNER) { totalCount }
    contributionsCollection {
      totalCommitContributions
      totalPullRequestContributions
      contributionCalendar {
        totalContributions
        weeks { firstDay contributionDays { contributionCount } }
      }
    }
  }
}
"""
MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]


def br(n: int) -> str:
    """Formata número no padrão brasileiro (1.234)."""
    return f"{n:,}".replace(",", ".")


# ---------------------------------------------------------------------------
# dados
# ---------------------------------------------------------------------------
def fetch_stats(login: str, token: str) -> dict:
    body = json.dumps({"query": QUERY, "variables": {"login": login}}).encode()
    req = urllib.request.Request(
        "https://api.github.com/graphql", data=body,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json",
                 "User-Agent": "profile-assets-script"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.load(resp)
    if data.get("errors"):
        raise SystemExit(f"Erro na API do GitHub: {data['errors']}")
    user = (data.get("data") or {}).get("user")
    if not user:
        raise SystemExit(f"Usuário '{login}' não encontrado na API.")
    return summarize(user)


def summarize(user: dict) -> dict:
    cc = user["contributionsCollection"]
    cal = cc["contributionCalendar"]
    weeks = [{"first": w["firstDay"],
              "total": sum(d["contributionCount"] for d in w["contributionDays"])}
             for w in cal["weeks"]]
    return {"repos": user["repositories"]["totalCount"],
            "contributions": cal["totalContributions"],
            "commits": cc["totalCommitContributions"],
            "prs": cc["totalPullRequestContributions"],
            "weeks": weeks}


# ---------------------------------------------------------------------------
# overview.svg
# ---------------------------------------------------------------------------
def render_overview(stats: dict) -> str:
    W, H = 1000, 120
    tiles = [("REPOSITÓRIOS PÚBLICOS", stats["repos"], "na minha conta"),
             ("CONTRIBUIÇÕES", stats["contributions"], "últimos 12 meses"),
             ("COMMITS", stats["commits"], "últimos 12 meses"),
             ("PULL REQUESTS", stats["prs"], "últimos 12 meses")]
    tw, gap = 232, 24
    o = [svg_open(W, H, "Visão geral do GitHub", "Números reais da conta no GitHub: repositórios públicos, "
                  "contribuições, commits e pull requests.")]
    o.append(f'<defs><linearGradient id="gv" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{CYAN}"/>'
             f'<stop offset="1" stop-color="{BLUE}"/></linearGradient></defs>')
    for i, (label, value, sub) in enumerate(tiles):
        x = i * (tw + gap)
        o.append(f'<g>{fade_in(round(i * 0.15, 2), 0.6)}')
        o.append(f'<rect x="{x + 0.5}" y="0.5" width="{tw - 1}" height="{H - 1}" rx="12" fill="{PANEL}" stroke="{BORDER}"/>')
        o.append(f'<rect x="{x + 20}" y="0.5" width="64" height="3" rx="1.5" fill="url(#gv)"/>')
        o.append(f'<text class="m" x="{x + 20}" y="34" font-size="12" fill="{MUTED}">{esc(label)}</text>')
        o.append(f'<text class="s" x="{x + 20}" y="82" font-size="42" font-weight="800" fill="url(#gv)">{br(value)}</text>')
        o.append(f'<text class="m" x="{x + 20}" y="104" font-size="11" fill="{DIM}">{esc(sub)}</text>')
        o.append("</g>")
    o.append("</svg>")
    return "".join(o)


# ---------------------------------------------------------------------------
# activity.svg
# ---------------------------------------------------------------------------
def smooth_path(pts, top, bottom):
    """Curva suave (Catmull-Rom → Bézier) sem passar dos limites do gráfico.

    Retorna (atributo d do path, comprimento aproximado em px). O comprimento
    é usado na animação de "desenhar a linha".
    """
    d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
    length, prev = 0.0, pts[0]
    for i in range(len(pts) - 1):
        p0 = pts[i - 1] if i > 0 else pts[i]
        p1, p2 = pts[i], pts[i + 1]
        p3 = pts[i + 2] if i + 2 < len(pts) else pts[i + 1]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, min(max(p1[1] + (p2[1] - p0[1]) / 6, top), bottom))
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, min(max(p2[1] - (p3[1] - p1[1]) / 6, top), bottom))
        d += f" C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}"
        for s in range(1, 13):  # amostra a curva para medir o comprimento
            t = s / 12
            u = 1 - t
            x = u**3 * p1[0] + 3 * u * u * t * c1[0] + 3 * u * t * t * c2[0] + t**3 * p2[0]
            y = u**3 * p1[1] + 3 * u * u * t * c1[1] + 3 * u * t * t * c2[1] + t**3 * p2[1]
            length += math.hypot(x - prev[0], y - prev[1])
            prev = (x, y)
    return d, length


def render_activity(stats: dict) -> str:
    weeks = stats["weeks"]
    if len(weeks) < 2:
        raise SystemExit("Poucos dados de contribuição para montar o gráfico.")
    vals = [w["total"] for w in weeks]
    W, H = 1000, 300
    x0, x1, top, base = 64, 960, 78, 244
    ymax = int(math.ceil(max(4, max(vals)) / 4) * 4)
    n = len(vals)
    pts = [(x0 + i * (x1 - x0) / (n - 1), base - (v / ymax) * (base - top)) for i, v in enumerate(vals)]
    line, length = smooth_path(pts, top, base)
    dash = math.ceil(length) + 12
    area = f"{line} L{pts[-1][0]:.1f},{base} L{pts[0][0]:.1f},{base} Z"

    o = [svg_open(W, H, "Atividade de contribuições",
                  f"Gráfico de contribuições por semana nos últimos 12 meses, total de {stats['contributions']}.")]
    o.append(f'<defs>'
             f'<linearGradient id="ln" gradientUnits="userSpaceOnUse" x1="{x0}" y1="0" x2="{x1}" y2="0"><stop offset="0" stop-color="{CYAN}"/><stop offset="1" stop-color="{BLUE}"/></linearGradient>'
             f'<linearGradient id="ar" gradientUnits="userSpaceOnUse" x1="0" y1="{top}" x2="0" y2="{base}"><stop offset="0" stop-color="{CYAN}" stop-opacity="0.32"/><stop offset="1" stop-color="{BLUE}" stop-opacity="0"/></linearGradient>'
             f'</defs>')
    o.append(f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="14" fill="{PANEL}" stroke="{BORDER}"/>')
    o.append(f'<text class="m" x="28" y="42" font-size="14" fill="{SOFT}">contribuições por semana '
             f'<tspan fill="{MUTED}">· últimos 12 meses</tspan></text>')
    o.append(f'<text class="m" x="972" y="42" font-size="14" fill="{MUTED}" text-anchor="end">total '
             f'<tspan fill="{CYAN}" font-weight="700">{br(stats["contributions"])}</tspan></text>')
    # grade e eixo Y
    for k in range(5):
        y = base - k * (base - top) / 4
        o.append(f'<line x1="{x0}" y1="{y:.1f}" x2="{x1}" y2="{y:.1f}" stroke="{GRID}" stroke-width="1"/>')
        o.append(f'<text class="m" x="{x0 - 12}" y="{y + 4:.1f}" font-size="11" fill="{DIM}" text-anchor="end">{int(ymax * k / 4)}</text>')
    # eixo X (rótulos de mês, com espaço mínimo entre eles)
    last_label_x, last_month = -999, None
    for i, w in enumerate(weeks):
        month = int(w["first"][5:7])
        if month != last_month:
            last_month = month
            if pts[i][0] - last_label_x >= 48:
                o.append(f'<text class="m" x="{pts[i][0]:.1f}" y="{base + 24}" font-size="11" fill="{MUTED}">{MESES[month - 1]}</text>')
                last_label_x = pts[i][0]
    o.append(f'<path d="{area}" fill="url(#ar)">{fade_in(1.2, 1.2)}</path>')
    o.append(f'<path d="{line}" fill="none" stroke="url(#ln)" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" '
             f'stroke-dasharray="{dash}"><animate attributeName="stroke-dashoffset" from="{dash}" to="0" dur="2.2s" begin="0s" fill="freeze"/></path>')
    for (px, py), v in zip(pts, vals):
        if v > 0:
            o.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="2.4" fill="{PANEL_2}" stroke="{CYAN}" stroke-width="1.4"/>')
    lx, ly = pts[-1]
    o.append(f'<circle cx="{lx:.1f}" cy="{ly:.1f}" r="4" fill="{CYAN}"><animate attributeName="r" values="4;9;4" dur="2.4s" repeatCount="indefinite"/>'
             f'<animate attributeName="opacity" values="1;0.25;1" dur="2.4s" repeatCount="indefinite"/></circle>')
    o.append(f'<text class="m" x="28" y="{H - 14}" font-size="10" fill="{DIM}">dados da API do GitHub · atualizado em {date.today().strftime("%d/%m/%Y")}</text>')
    o.append("</svg>")
    return "".join(o)


# ---------------------------------------------------------------------------
# cobrinha: fundo escuro
# ---------------------------------------------------------------------------
def style_snake(path: Path) -> None:
    svg = path.read_text(encoding="utf-8")
    root = re.search(r"<svg\b[^>]*>", svg)
    vb = re.search(r'viewBox="\s*(-?[\d.]+)[\s,]+(-?[\d.]+)[\s,]+([\d.]+)[\s,]+([\d.]+)\s*"', root.group(0)) if root else None
    if not vb:
        raise SystemExit(f"Não achei o viewBox em {path}; o formato do SVG da cobrinha mudou?")
    x, y, w, h = (float(v) for v in vb.groups())
    bg = (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{PANEL_2}"/>'
          f'<rect x="{x + 0.5}" y="{y + 0.5}" width="{w - 1}" height="{h - 1}" rx="14" fill="none" '
          f'stroke="{BORDER}"/>')
    path.write_text(svg[:root.end()] + bg + svg[root.end():], encoding="utf-8")
    print(f"ok  fundo escuro aplicado em {path}")


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("dashboard")
    d.add_argument("--out", default="dist")
    s = sub.add_parser("snake")
    s.add_argument("file")
    args = ap.parse_args()

    if args.cmd == "snake":
        style_snake(Path(args.file))
        return
    token, login = os.environ.get("GITHUB_TOKEN"), os.environ.get("PROFILE_USER")
    if not token or not login:
        raise SystemExit("Defina GITHUB_TOKEN e PROFILE_USER no ambiente.")
    stats = fetch_stats(login, token)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "overview.svg").write_text(render_overview(stats) + "\n", encoding="utf-8")
    (out / "activity.svg").write_text(render_activity(stats) + "\n", encoding="utf-8")
    print(f"ok  overview.svg e activity.svg gerados para {login}: "
          f"{stats['repos']} repos, {stats['contributions']} contribuições")


if __name__ == "__main__":
    main()
