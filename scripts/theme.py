"""Paleta e fontes compartilhadas pelos SVGs do perfil (tema Dark Tech).

Mexer aqui muda a cara de TODOS os SVGs gerados pelos scripts desta pasta.
"""
from xml.sax.saxutils import escape

# --- cores -----------------------------------------------------------------
BG0 = "#05070d"      # fundo mais escuro
BG1 = "#0a1020"      # fundo azul-marinho
PANEL = "#0b1220"    # painéis / cards
PANEL_2 = "#070b14"  # janelas internas
HEADER = "#0d1627"   # barra de título das janelas
BORDER = "#12304f"   # bordas discretas
GRID = "#0f2038"     # linhas da grade
CYAN = "#00e5ff"     # cor principal
BLUE = "#2f81f7"     # cor secundária
ELECTRIC = "#1f6feb"
TEXT = "#e6edf3"
SOFT = "#c9d1d9"
MUTED = "#8b949e"
DIM = "#4b5a70"

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
