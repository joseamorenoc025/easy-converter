"""Adapter: IConverter → EasyConverter"""
from pathlib import Path
from typing import Tuple
from core.interfaces import IConverter
from core.converter import EasyConverter


class ConverterAdapter(IConverter):
    def __init__(self):
        self._cancelled = False

    def convert_pdf_to_word(self, pdf_path: Path, output_path: Path) -> Tuple[bool, str]:
        self._cancelled = False
        success, result = EasyConverter.pdf_to_docx(str(pdf_path), str(output_path))
        if self._cancelled:
            return False, "Cancelado por el usuario"
        return success, result

    def convert_word_to_pdf(self, word_path: Path, output_path: Path) -> Tuple[bool, str]:
        self._cancelled = False
        success, result = EasyConverter.docx_to_pdf(str(word_path), str(output_path))
        if self._cancelled:
            return False, "Cancelado por el usuario"
        return success, result

    def cancel_current_conversion(self) -> bool:
        self._cancelled = True
        return True
