"""Tests para single instance lock."""
import pytest
import sys
import os
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

_saved_modules = {}
_added_modules = []

@pytest.fixture(autouse=True)
def _isolate_main_module():
    """Guarda y restaura sys.modules para no contaminar otros tests."""
    keys_to_save = [k for k in sys.modules if k in ('main', 'ui.main_window')]
    for k in keys_to_save:
        _saved_modules[k] = sys.modules.pop(k)
    yield
    for k, v in _saved_modules.items():
        sys.modules[k] = v
    for k in _added_modules:
        sys.modules.pop(k, None)
    _saved_modules.clear()
    _added_modules.clear()


def _import_main_with_mocks():
    """Importa main.py evitando que se cargue customtkinter/ui.main_window."""
    mock_main_window = MagicMock()
    mock_main_window.App = MagicMock
    if 'ui.main_window' not in sys.modules:
        _added_modules.append('ui.main_window')
    sys.modules['ui.main_window'] = mock_main_window
    sys.modules.pop('main', None)
    import main
    return main


class TestSingleInstance:
    def test_first_instance_returns_true(self):
        mod = _import_main_with_mocks()
        with patch('ctypes.windll') as mock_windll:
            mock_windll.kernel32.CreateMutexW.return_value = 12345
            mock_windll.kernel32.GetLastError.return_value = 0
            result = mod.check_single_instance()
            assert result is True

    def test_duplicate_instance_returns_false(self):
        mod = _import_main_with_mocks()
        with patch('ctypes.windll') as mock_windll:
            mock_windll.kernel32.CreateMutexW.return_value = 12345
            mock_windll.kernel32.GetLastError.return_value = 183
            with patch.object(mod, '_focus_existing_window'):
                result = mod.check_single_instance()
                assert result is False

    def test_mutex_name_is_unique(self):
        mod = _import_main_with_mocks()
        assert "EasyConverter" in mod.MUTEX_NAME

    def test_focus_function_exists(self):
        mod = _import_main_with_mocks()
        assert callable(mod._focus_existing_window)
