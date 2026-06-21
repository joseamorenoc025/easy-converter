import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
import pytest

from core.converter import EasyConverter
from core.progress import ConversionProgress


class TestEasyConverter:
    def test_pdf_to_docx_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            EasyConverter.pdf_to_docx("/no/exist/file.pdf")

    @patch("core.converter.fitz.open")
    @patch("core.converter.Converter")
    def test_pdf_to_docx_success(self, mock_converter_cls, mock_fitz_open):
        mock_doc = MagicMock()
        mock_doc.__len__.return_value = 5
        mock_fitz_open.return_value.__enter__.return_value = mock_doc

        mock_cv = MagicMock()
        mock_converter_cls.return_value = mock_cv

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            pdf_path = f.name
        try:
            success, result = EasyConverter.pdf_to_docx(pdf_path)
            assert success is True
            assert result.endswith(".docx")
        finally:
            os.unlink(pdf_path)

    @patch("core.converter.fitz.open")
    @patch("core.converter.Converter")
    def test_pdf_to_docx_with_progress(self, mock_converter_cls, mock_fitz_open):
        mock_doc = MagicMock()
        mock_doc.__len__.return_value = 3
        mock_fitz_open.return_value.__enter__.return_value = mock_doc

        mock_cv = MagicMock()
        mock_converter_cls.return_value = mock_cv

        updates = []
        tracker = ConversionProgress(
            on_update=lambda p, m: updates.append((p, m))
        )

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            pdf_path = f.name
        try:
            success, result = EasyConverter.pdf_to_docx(pdf_path, progress_tracker=tracker)
            assert success is True
            assert len(updates) > 0
            assert updates[-1][0] == 100
        finally:
            os.unlink(pdf_path)

    @patch("core.converter.WordChecker.check_word_or_fail")
    @patch("core.converter.pythoncom")
    def test_docx_to_pdf_word_not_installed(self, mock_pythoncom, mock_check_word):
        mock_check_word.side_effect = Exception("Word no instalado")

        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
            docx_path = f.name
        try:
            with pytest.raises(Exception):
                EasyConverter.docx_to_pdf(docx_path)
        finally:
            os.unlink(docx_path)

    @patch("core.converter.pythoncom")
    @patch("core.converter.WordChecker.check_word_or_fail")
    @patch("core.converter.word_to_pdf_conv")
    def test_docx_to_pdf_file_not_found(self, mock_conv, mock_check_word, mock_pythoncom):
        with pytest.raises(FileNotFoundError):
            EasyConverter.docx_to_pdf("/no/exist/file.docx")
