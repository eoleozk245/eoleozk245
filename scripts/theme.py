"""Paleta e fontes compartilhadas pelos SVGs do perfil (tema azul claro, igual ao banner).

Mexer aqui muda a cara de TODOS os SVGs gerados pelos scripts desta pasta.
"""
from xml.sax.saxutils import escape

# --- cores -----------------------------------------------------------------
BG0 = "#eaf6ff"      # fundo mais claro
BG1 = "#f2f9ff"      # fundo azul bem clarinho
PANEL = "#e4f3ff"    # painéis / cards
PANEL_2 = "#f2f9ff"  # janelas internas
HEADER = "#cdeaff"   # pílulas e barras
BORDER = "#9fd4f5"   # bordas discretas
GRID = "#c3e3f8"     # linhas da grade
CYAN = "#0f7fcb"     # cor principal (azul legível sobre fundo claro)
BLUE = "#55c7ff"     # cor secundária (azul claro do banner)
ELECTRIC = "#2ea8f0"
TEXT = "#0c0c0c"
SOFT = "#1d2b3a"
MUTED = "#4a6076"
DIM = "#6b8199"

# --- fontes (o SVG usa as fontes instaladas no aparelho de quem vê) ---------
MONO = ("'JetBrains Mono','Fira Code','SFMono-Regular',Consolas,"
        "'DejaVu Sans Mono','Liberation Mono',Menlo,monospace")
SANS = ("'Segoe UI',Inter,system-ui,-apple-system,'Helvetica Neue',"
        "Arial,sans-serif")

BASE_CSS = (
    f".m{{font-family:{MONO}}}"
    f".s{{font-family:{SANS}}}"
    "text{white-space:pre}"
)


def esc(value) -> str:
    """Escapa texto para uso seguro dentro de SVG/XML."""
    return escape(str(value), {'"': "&quot;"})


def fade_in(delay: float, dur: float) -> str:
    """Entrada suave (SMIL). O estado base do elemento continua visível, então
    se o visualizador não suportar animação o conteúdo aparece normalmente."""
    total = round(delay + dur, 3)
    if delay <= 0:
        return (f'<animate attributeName="opacity" from="0" to="1" dur="{dur}s" '
                f'begin="0s" fill="freeze"/>')
    k = delay / total
    return (f'<animate attributeName="opacity" values="0;0;1" keyTimes="0;{k:.4f};1" '
            f'dur="{total}s" begin="0s" fill="freeze"/>')


def svg_open(width: int, height: int, title: str, desc: str) -> str:
    """Abre o <svg> já com título/descrição acessíveis."""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}" role="img" aria-labelledby="t d">'
        f'<title id="t">{esc(title)}</title><desc id="d">{esc(desc)}</desc>'
        f"<style>{BASE_CSS}</style>"
    )
