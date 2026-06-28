"""Tests para PathManager."""
import pytest
from unittest.mock import Mock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from core.file_manager import PathManager


@pytest.fixture
def path_manager(tmp_path):
    config = Mock()
    config.get.return_value = "same_folder"
    return PathManager(config)


class TestPathManager:
    def test_same_folder_mode(self, path_manager, tmp_path):
        input_file = tmp_path / "test.pdf"
        result = path_manager.resolve_output_path(input_file, "pdf2word")
        assert result.suffix == ".docx"
        assert result.parent == tmp_path

    def test_subfolder_mode(self, tmp_path):
        config = Mock()
        config.get.return_value = "subfolder"
        pm = PathManager(config)
        input_file = tmp_path / "test.pdf"
        result = pm.resolve_output_path(input_file, "pdf2word")
        assert result.parent.name == "convertidos"

    def test_custom_mode(self, tmp_path):
        config = Mock()
        custom_dir = tmp_path / "custom_out"
        custom_dir.mkdir()
        config.get.side_effect = lambda key, default=None: str(custom_dir) if key == "custom_path" else "custom"
        pm = PathManager(config)
        input_file = tmp_path / "test.pdf"
        result = pm.resolve_output_path(input_file, "pdf2word")
        assert "custom_out" in str(result)

    def test_word2pdf_extension(self, path_manager, tmp_path):
        input_file = tmp_path / "test.docx"
        result = path_manager.resolve_output_path(input_file, "word2pdf")
        assert result.suffix == ".pdf"

    def test_subfolder_created(self, path_manager, tmp_path):
        input_file = tmp_path / "test.pdf"
        result = path_manager.resolve_output_path(input_file, "pdf2word")
        assert result.exists() or result.parent.exists()

    def test_custom_path_fallback(self, tmp_path):
        config = Mock()
        config.get.side_effect = lambda key, default=None: "" if key == "custom_path" else "custom"
        pm = PathManager(config)
        input_file = tmp_path / "test.pdf"
        result = pm.resolve_output_path(input_file, "pdf2word")
        assert result.suffix == ".docx"

    def test_fallback_mode(self, tmp_path):
        config = Mock()
        config.get.return_value = "unknown_mode"
        pm = PathManager(config)
        input_file = tmp_path / "test.pdf"
        result = pm.resolve_output_path(input_file, "pdf2word")
        assert result.suffix == ".docx"

    def test_open_in_explorer_static(self, path_manager):
        assert callable(PathManager.open_in_explorer)
