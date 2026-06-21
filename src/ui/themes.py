import customtkinter

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
        }
    }
}

class ThemeManager:
    _current = "dark"

    @classmethod
    def get_theme(cls, name=None):
        return THEMES.get(name or cls._current, THEMES["dark"])

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
