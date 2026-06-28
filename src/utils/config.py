import json
import sys
import threading
from pathlib import Path
from appdirs import user_config_dir


def _get_app_base_dir():
    """Obtiene el directorio base del executable o script."""
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent.parent


def _is_portable_mode():
    """Detecta si la app esta en modo portable (USB, Downloads, etc.)."""
    base = _get_app_base_dir()
    program_files = Path.home().parent / "Program Files"
    program_files_x86 = Path.home().parent / "Program Files (x86)"
    app_data = Path.home() / "AppData"

    try:
        base_resolved = base.resolve()
    except OSError:
        return False

    non_portable_parents = [
        program_files.resolve(),
        program_files_x86.resolve(),
        app_data.resolve(),
    ]
    for parent in non_portable_parents:
        try:
            base_resolved.relative_to(parent)
            return False
        except ValueError:
            continue
    return True


def get_data_dir(subfolder="EasyConverter"):
    """Retorna el directorio donde guardar datos (config, logs).
    
    Modo portable: junto al executable.
    Modo normal: usa appdirs.
    """
    if _is_portable_mode():
        return _get_app_base_dir() / subfolder.lower()
    return Path(user_config_dir(subfolder, "GeminiCLI"))


class ConfigManager:
    """
    Gestiona la persistencia de configuracion y preferencias del usuario.
    Soporta modo portable (config junto al .exe) y modo normal (appdirs).
    """
    def __init__(self, app_name="EasyConverter"):
        self.config_dir = get_data_dir(app_name)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.config_dir / "config.json"
        self._lock = threading.Lock()
        self.config = self._load_config()

    def _load_config(self):
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return self._get_defaults()
        return self._get_defaults()

    def _get_defaults(self):
        return {
            "output_mode": "same_folder",
            "custom_path": "",
            "recent_paths": [],
            "open_folder_on_finish": True,
            "theme": "dark",
            "use_ocr": False,
            "first_run_complete": False,
            "workflow_profiles": []
        }

    def get(self, key, default=None):
        return self.config.get(key, default if default is not None else self._get_defaults().get(key))

    def set(self, key, value):
        self.config[key] = value
        self._save_config()

    def _save_config(self):
        with self._lock:
            try:
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(self.config, f, indent=4)
            except Exception as e:
                print(f"Error guardando configuracion: {e}")

    def add_recent_path(self, path):
        recent = self.get("recent_paths", [])
        path_str = str(path)
        if path_str in recent:
            recent.remove(path_str)
        recent.insert(0, path_str)
        self.set("recent_paths", recent[:5])
