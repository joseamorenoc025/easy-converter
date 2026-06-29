import json
import customtkinter
from pathlib import Path

THEMES = {
    "dark": {
        "name": "Oscuro",
        "appearance": "dark",
        "colors": {
            "primary": "#1f538d",
            "secondary": "#2b2b2b",
            "surface": "#1e1e1e",
            "background": "#141414",
            "text": "#ffffff",
            "text_secondary": "#a0a0a0",
            "success": "#2ea043",
            "error": "#f85149",
            "warning": "#d29922",
            "border": "#333333",
            "sidebar_bg": "#1a1a2e",
            "sidebar_section": "#16213e",
            "card_bg": "#1e1e2e",
            "card_hover": "#252540",
            "drop_zone_bg": "#1a1a2e",
            "drop_zone_border": "#333355",
            "drop_zone_hover": "#1a3a5c",
            "queue_row": "#1e1e2e",
            "queue_row_alt": "#22223a",
            "tab_active": "#1f538d",
            "badge_pdf": "#e74c3c",
            "badge_docx": "#2980b9",
            "accent": "#4fc3f7",
        }
    },
    "light": {
        "name": "Claro",
        "appearance": "light",
        "colors": {
            "primary": "#1f538d",
            "secondary": "#e8e8e8",
            "surface": "#ffffff",
            "background": "#f5f5f5",
            "text": "#1f1f1f",
            "text_secondary": "#656565",
            "success": "#1a7f37",
            "error": "#cf222e",
            "warning": "#9a6700",
            "border": "#d0d7de",
            "sidebar_bg": "#eef2f7",
            "sidebar_section": "#dde5ef",
            "card_bg": "#ffffff",
            "card_hover": "#f0f4f8",
            "drop_zone_bg": "#f8fafc",
            "drop_zone_border": "#c8d6e5",
            "drop_zone_hover": "#d4e6f1",
            "queue_row": "#ffffff",
            "queue_row_alt": "#f8f9fa",
            "tab_active": "#1f538d",
            "badge_pdf": "#e74c3c",
            "badge_docx": "#2980b9",
            "accent": "#1565c0",
        }
    },
    "high_contrast": {
        "name": "Alto Contraste",
        "appearance": "dark",
        "colors": {
            "primary": "#00ffff",
            "secondary": "#000000",
            "surface": "#0a0a0a",
            "background": "#000000",
            "text": "#ffffff",
            "text_secondary": "#cccccc",
            "success": "#00ff00",
            "error": "#ff0000",
            "warning": "#ffff00",
            "border": "#ffffff",
            "sidebar_bg": "#000000",
            "sidebar_section": "#0a0a0a",
            "card_bg": "#0a0a0a",
            "card_hover": "#1a1a1a",
            "drop_zone_bg": "#000000",
            "drop_zone_border": "#ffffff",
            "drop_zone_hover": "#1a1a1a",
            "queue_row": "#0a0a0a",
            "queue_row_alt": "#111111",
            "tab_active": "#00ffff",
            "badge_pdf": "#ff0000",
            "badge_docx": "#00ffff",
            "accent": "#00ffff",
        }
    },
    "corporativo": {
        "name": "Corporativo",
        "appearance": "dark",
        "colors": {
            "primary": "#1a365d",
            "secondary": "#1e3a5f",
            "surface": "#152238",
            "background": "#0f1923",
            "text": "#e8ecf1",
            "text_secondary": "#8899aa",
            "success": "#38a169",
            "error": "#e53e3e",
            "warning": "#d69e2e",
            "border": "#2d4a6f",
            "sidebar_bg": "#0d1b2a",
            "sidebar_section": "#1b2838",
            "card_bg": "#152238",
            "card_hover": "#1c2d45",
            "drop_zone_bg": "#0d1b2a",
            "drop_zone_border": "#2d4a6f",
            "drop_zone_hover": "#1a365d",
            "queue_row": "#152238",
            "queue_row_alt": "#1a2d45",
            "tab_active": "#1a365d",
            "badge_pdf": "#e53e3e",
            "badge_docx": "#2b6cb0",
            "accent": "#63b3ed",
        }
    },
    "calido": {
        "name": "Calido",
        "appearance": "dark",
        "colors": {
            "primary": "#c05621",
            "secondary": "#2d2420",
            "surface": "#1e1714",
            "background": "#14100d",
            "text": "#fef3c7",
            "text_secondary": "#a08060",
            "success": "#38a169",
            "error": "#e53e3e",
            "warning": "#d69e2e",
            "border": "#5c3a1e",
            "sidebar_bg": "#1a1410",
            "sidebar_section": "#2a1f18",
            "card_bg": "#1e1714",
            "card_hover": "#2a2018",
            "drop_zone_bg": "#1a1410",
            "drop_zone_border": "#5c3a1e",
            "drop_zone_hover": "#7a4a2a",
            "queue_row": "#1e1714",
            "queue_row_alt": "#252018",
            "tab_active": "#c05621",
            "badge_pdf": "#e53e3e",
            "badge_docx": "#c05621",
            "accent": "#ed8936",
        }
    },
    "solarizado": {
        "name": "Solarizado",
        "appearance": "dark",
        "colors": {
            "primary": "#268bd2",
            "secondary": "#073642",
            "surface": "#002b36",
            "background": "#001e27",
            "text": "#fdf6e3",
            "text_secondary": "#93a1a1",
            "success": "#859900",
            "error": "#dc322f",
            "warning": "#b58900",
            "border": "#586e75",
            "sidebar_bg": "#001e27",
            "sidebar_section": "#073642",
            "card_bg": "#002b36",
            "card_hover": "#073642",
            "drop_zone_bg": "#001e27",
            "drop_zone_border": "#586e75",
            "drop_zone_hover": "#073642",
            "queue_row": "#002b36",
            "queue_row_alt": "#073642",
            "tab_active": "#268bd2",
            "badge_pdf": "#dc322f",
            "badge_docx": "#268bd2",
            "accent": "#2aa198",
        }
    },
}

_DEFAULT_THEME = {
    "name": "Unknown",
    "appearance": "dark",
    "colors": {
        "primary": "#1f538d",
        "secondary": "#2b2b2b",
        "surface": "#1e1e1e",
        "background": "#141414",
        "text": "#ffffff",
        "text_secondary": "#a0a0a0",
        "success": "#2ea043",
        "error": "#f85149",
        "warning": "#d29922",
        "border": "#333333",
        "sidebar_bg": "#1a1a2e",
        "sidebar_section": "#16213e",
        "card_bg": "#1e1e2e",
        "card_hover": "#252540",
        "drop_zone_bg": "#1a1a2e",
        "drop_zone_border": "#333355",
        "drop_zone_hover": "#1a3a5c",
        "queue_row": "#1e1e2e",
        "queue_row_alt": "#22223a",
        "tab_active": "#1f538d",
        "badge_pdf": "#e74c3c",
        "badge_docx": "#2980b9",
        "accent": "#4fc3f7",
    }
}


def _load_custom_themes():
    """Carga temas personalizados desde themes_dir si existen."""
    try:
        themes_dir = _get_themes_dir()
        if not themes_dir.exists():
            return
        for f in themes_dir.glob("*.json"):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                if "name" in data and "colors" in data:
                    key = f.stem
                    data.setdefault("appearance", "dark")
                    base = dict(_DEFAULT_THEME["colors"])
                    base.update(data.get("colors", {}))
                    data["colors"] = base
                    THEMES[key] = data
            except (json.JSONDecodeError, OSError):
                continue
    except Exception:
        pass


def _get_themes_dir() -> Path:
    """Retorna el directorio de temas personalizados junto al .exe."""
    import sys
    if getattr(sys, 'frozen', False):
        base = Path(sys.executable).parent
    else:
        base = Path(__file__).parent.parent
    return base / "themes"


def _save_custom_theme(key: str, theme_data: dict) -> bool:
    """Guarda un tema personalizado como JSON."""
    try:
        themes_dir = _get_themes_dir()
        themes_dir.mkdir(parents=True, exist_ok=True)
        out = themes_dir / f"{key}.json"
        out.write_text(json.dumps(theme_data, indent=2, ensure_ascii=False), encoding="utf-8")
        THEMES[key] = theme_data
        return True
    except Exception:
        return False


def _delete_custom_theme(key: str) -> bool:
    """Elimina un tema personalizado."""
    if key not in THEMES:
        return False
    if key in ("dark", "light", "high_contrast", "corporativo", "calido", "solarizado"):
        return False
    themes_dir = _get_themes_dir()
    f = themes_dir / f"{key}.json"
    if f.exists():
        try:
            f.unlink()
        except OSError:
            return False
    del THEMES[key]
    return True


_load_custom_themes()


class ThemeManager:
    _current = "dark"
    _registered_widgets: list = []

    @classmethod
    def get_theme(cls, name=None):
        return THEMES.get(name or cls._current, _DEFAULT_THEME)

    @classmethod
    def get_color(cls, key, theme_name=None):
        theme = cls.get_theme(theme_name)
        return theme["colors"].get(key, "#ffffff")

    @classmethod
    def apply(cls, theme_name):
        if theme_name not in THEMES:
            return
        cls._current = theme_name
        theme = THEMES[theme_name]
        customtkinter.set_appearance_mode(theme["appearance"])

    @classmethod
    def get_theme_names(cls):
        return list(THEMES.keys())

    @classmethod
    def get_theme_label(cls, theme_name):
        theme = THEMES.get(theme_name)
        return theme["name"] if theme else theme_name

    @classmethod
    def is_builtin(cls, theme_name):
        builtins = {"dark", "light", "high_contrast", "corporativo", "calido", "solarizado"}
        return theme_name in builtins

    @classmethod
    def save_custom(cls, key, name, colors, appearance="dark"):
        theme_data = {
            "name": name,
            "appearance": appearance,
            "colors": colors,
        }
        return _save_custom_theme(key, theme_data)

    @classmethod
    def delete_custom(cls, key):
        return _delete_custom_theme(key)

    @classmethod
    def get_sidebar_bg(cls):
        return cls.get_color("sidebar_bg")

    @classmethod
    def get_sidebar_section(cls):
        return cls.get_color("sidebar_section")

    @classmethod
    def get_card_bg(cls):
        return cls.get_color("card_bg")

    @classmethod
    def get_card_hover(cls):
        return cls.get_color("card_hover")
