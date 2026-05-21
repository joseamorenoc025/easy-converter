import json
import os
from pathlib import Path
from appdirs import user_config_dir

class ConfigManager:
    """
    Gestiona la persistencia de configuración y preferencias del usuario.
    """
    def __init__(self, app_name="EasyConverter"):
        self.config_dir = Path(user_config_dir(app_name, "GeminiCLI"))
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.config_dir / "config.json"
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
            "output_mode": "same_folder", # same_folder, subfolder, custom
            "custom_path": "",
            "recent_paths": [],
            "open_folder_on_finish": True,
            "theme": "dark",
            "workflow_profiles": []
        }

    def get(self, key, default=None):
        return self.config.get(key, default if default is not None else self._get_defaults().get(key))

    def set(self, key, value):
        self.config[key] = value
        self._save_config()

    def _save_config(self):
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Error guardando configuración: {e}")

    def add_recent_path(self, path):
        recent = self.get("recent_paths", [])
        path_str = str(path)
        if path_str in recent:
            recent.remove(path_str)
        recent.insert(0, path_str)
        self.set("recent_paths", recent[:5]) # Mantener solo los últimos 5
