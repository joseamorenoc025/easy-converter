"""
Temas visuales cyber/neon para Easy Converter.
Centraliza colores y estilos para mantener consistencia en toda la UI.
"""

# Paleta cyber/neon dark theme
NEON_CYAN = "#00E5FF"
NEON_MAGENTA = "#FF00E5"
NEON_GREEN = "#00FF9F"
NEON_ORANGE = "#FF8C00"
NEON_RED = "#FF0033"
NEON_YELLOW = "#FFEA00"

BG_PRIMARY = "#0D0D0D"
BG_SECONDARY = "#1A1A1A"
BG_TERTIARY = "#1E1E24"
BG_DROPZONE = "#1A1A1A"

BORDER_NEON = NEON_CYAN
TEXT_PRIMARY = "#E0E0E0"
TEXT_SECONDARY = "gray70"
TEXT_DIM = "gray60"

ACCENT_SUCCESS = NEON_GREEN
ACCENT_WARNING = NEON_ORANGE
ACCENT_ERROR = NEON_RED

# Espaciado y border radius
PADDING_SM = 5
PADDING_MD = 10
PADDING_LG = 20
CORNER_RADIUS = 10
BORDER_WIDTH = 1

# Tamaños de fuente
FONT_TITLE = 20
FONT_SUBTITLE = 14
FONT_BODY = 12
FONT_SMALL = 11

def get_dropzone_style():
    """Estilo para la zona de drop cyber."""
    return {
        "fg_color": BG_DROPZONE,
        "border_width": 2,
        "border_color": NEON_CYAN,
        "corner_radius": 15,
    }

def get_dashboard_style():
    """Estilo para frames de dashboard futurista."""
    return {
        "fg_color": BG_TERTIARY,
        "border_width": 1,
        "border_color": NEON_CYAN,
        "corner_radius": CORNER_RADIUS,
    }

def get_status_color(status: str) -> str:
    """Retorna el color neon según el estado."""
    return {
        "pending": TEXT_SECONDARY,
        "running": NEON_ORANGE,
        "success": ACCENT_SUCCESS,
        "failed": ACCENT_ERROR,
    }.get(status, TEXT_SECONDARY)

def get_progress_color(percent: int) -> str:
    """Color del progreso basado en porcentaje."""
    if percent < 30:
        return NEON_CYAN
    elif percent < 70:
        return NEON_ORANGE
    else:
        return NEON_GREEN