"""Adapter: IPlatformService → WindowsPlatformService"""
from typing import Optional, Tuple
from pathlib import Path
from core.interfaces import IPlatformService
from utils.platform_service import WindowsPlatformService


class PlatformAdapter(IPlatformService):
    def __init__(self):
        self._service = WindowsPlatformService()

    def register_context_menu(self, enabled: bool) -> Tuple[bool, str]:
        return self._service.register_context_menu(enabled)

    def is_word_installed(self) -> bool:
        return self._service.is_word_installed()

    def send_notification(self, title: str, message: str) -> bool:
        return self._service.send_notification(title, message)

    def get_tesseract_path(self) -> Optional[Path]:
        return self._service.get_tesseract_path()
