import unittest
import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from utils.config import ConfigManager

class TestConfigManager(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.config_manager = ConfigManager(app_name="TestApp")
        self.config_manager.config_file = Path(self.test_dir) / "config.json"
        self.config_manager.config = self.config_manager._get_defaults()
        self.config_manager._save_config()
        
    def tearDown(self):
        shutil.rmtree(self.test_dir)
        
    def test_default_values(self):
        # Empty config should return defaults
        self.assertEqual(self.config_manager.get("theme"), "dark")
        self.assertEqual(self.config_manager.get("output_mode"), "same_folder")
        
    def test_save_load(self):
        self.config_manager.set("theme", "light")
        self.assertEqual(self.config_manager.get("theme"), "light")
        
        # Create a new instance to test loading from disk
        new_manager = ConfigManager(app_name="TestApp")
        new_manager.config_file = Path(self.test_dir) / "config.json"
        new_manager.config = new_manager._load_config()
        self.assertEqual(new_manager.get("theme"), "light")
        
    def test_recent_paths(self):
        self.config_manager.add_recent_path("path1")
        self.config_manager.add_recent_path("path2")
        self.config_manager.add_recent_path("path1") # Should move to front
        
        recent = self.config_manager.get("recent_paths")
        self.assertEqual(recent[0], "path1")
        self.assertEqual(recent[1], "path2")

if __name__ == '__main__':
    unittest.main()
