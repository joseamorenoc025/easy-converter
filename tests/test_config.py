"""Tests para ConfigManager."""
import pytest
import tempfile
import threading
from pathlib import Path
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from utils.config import ConfigManager


@pytest.fixture
def temp_config():
    with tempfile.TemporaryDirectory() as tmpdir:
        config = ConfigManager.__new__(ConfigManager)
        config.config_dir = Path(tmpdir)
        config.config_file = Path(tmpdir) / "config.json"
        config._lock = threading.Lock()
        config.config = config._get_defaults()
        yield config


class TestConfigManager:
    def test_defaults_loaded(self, temp_config):
        defaults = temp_config._get_defaults()
        assert "output_mode" in defaults
        assert defaults["output_mode"] == "same_folder"
        assert defaults["theme"] == "dark"

    def test_get_existing_key(self, temp_config):
        temp_config.set("theme", "light")
        assert temp_config.get("theme") == "light"

    def test_get_missing_key_returns_default(self, temp_config):
        assert temp_config.get("nonexistent", "fallback") == "fallback"

    def test_set_and_persist(self, temp_config):
        temp_config.set("output_mode", "custom")
        assert temp_config.config["output_mode"] == "custom"

    def test_recent_paths_add(self, temp_config):
        temp_config.add_recent_path("C:/test/file.pdf")
        recent = temp_config.get("recent_paths")
        assert "C:/test/file.pdf" in recent

    def test_recent_paths_dedup(self, temp_config):
        temp_config.add_recent_path("C:/test/file.pdf")
        temp_config.add_recent_path("C:/test/file.pdf")
        recent = temp_config.get("recent_paths")
        assert recent.count("C:/test/file.pdf") == 1

    def test_recent_paths_max_5(self, temp_config):
        for i in range(10):
            temp_config.add_recent_path(f"C:/test/file{i}.pdf")
        assert len(temp_config.get("recent_paths")) == 5

    def test_save_creates_file(self, temp_config):
        temp_config.set("theme", "high_contrast")
        assert temp_config.config_file.exists()
