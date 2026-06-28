"""Adapter: IConfigManager → ConfigManager"""
from core.interfaces import IConfigManager
from utils.config import ConfigManager


class ConfigAdapter(IConfigManager):
    def __init__(self):
        self._config = ConfigManager()

    def get(self, key: str, default=None):
        return self._config.get(key, default)

    def set(self, key: str, value):
        self._config.set(key, value)

    def save(self) -> bool:
        return True

    def get_all(self) -> dict:
        return self._config.config
