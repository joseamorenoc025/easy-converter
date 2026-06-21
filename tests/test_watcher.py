from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from core.watcher import SmartFolderHandler, SmartWatcher


class TestSmartFolderHandler:
    @pytest.fixture
    def handler(self):
        callback = MagicMock()
        return SmartFolderHandler(callback=callback)

    @patch.object(SmartFolderHandler, "_wait_until_ready", return_value=True)
    def test_ignores_directories(self, mock_wait, handler):
        mock_event = MagicMock()
        mock_event.is_directory = True
        mock_event.src_path = "/some/dir"
        handler.on_created(mock_event)
        handler.callback.assert_not_called()

    @patch.object(SmartFolderHandler, "_wait_until_ready", return_value=True)
    def test_ignores_temp_word_files(self, mock_wait, handler):
        mock_event = MagicMock()
        mock_event.is_directory = False
        mock_event.src_path = "/path/~$document.docx"
        handler.on_created(mock_event)
        handler.callback.assert_not_called()

    @patch.object(SmartFolderHandler, "_wait_until_ready", return_value=True)
    def test_ignores_converted_flag_files(self, mock_wait, handler):
        mock_event = MagicMock()
        mock_event.is_directory = False
        mock_event.src_path = "/path/doc_CONVERTIDO_2024.pdf"
        handler.on_created(mock_event)
        handler.callback.assert_not_called()

    @patch.object(SmartFolderHandler, "_wait_until_ready", return_value=True)
    def test_processes_pdf_files(self, mock_wait, handler):
        mock_event = MagicMock()
        mock_event.is_directory = False
        mock_event.src_path = "/path/test.pdf"
        handler.on_created(mock_event)
        handler.callback.assert_called_once_with(Path("/path/test.pdf"))

    @patch.object(SmartFolderHandler, "_wait_until_ready", return_value=True)
    def test_processes_docx_files(self, mock_wait, handler):
        mock_event = MagicMock()
        mock_event.is_directory = False
        mock_event.src_path = "/path/test.docx"
        handler.on_created(mock_event)
        handler.callback.assert_called_once()

    @patch.object(SmartFolderHandler, "_wait_until_ready", return_value=True)
    def test_debounce_suppresses_duplicate_events(self, mock_wait, handler):
        mock_event = MagicMock()
        mock_event.is_directory = False
        mock_event.src_path = "/path/test.pdf"
        handler.on_created(mock_event)
        handler.on_created(mock_event)
        assert handler.callback.call_count == 1

    @patch.object(SmartFolderHandler, "_wait_until_ready", return_value=True)
    @patch("core.watcher.time.monotonic")
    def test_debounce_allows_after_window(self, mock_time, mock_wait, handler):
        mock_time.side_effect = [100.0, 103.0]
        mock_event = MagicMock()
        mock_event.is_directory = False
        mock_event.src_path = "/path/test.pdf"
        handler.on_created(mock_event)
        handler.on_created(mock_event)
        assert handler.callback.call_count == 2


class TestSmartWatcher:
    def test_add_watch(self):
        callback = MagicMock()
        watcher = SmartWatcher(callback=callback)
        watcher.add_watch("/test/path")
        assert "/test/path" in watcher.watch_paths

    def test_remove_watch(self):
        callback = MagicMock()
        watcher = SmartWatcher(callback=callback)
        watcher.add_watch("/test/path")
        watcher.remove_watch("/test/path")
        assert "/test/path" not in watcher.watch_paths

    def test_add_same_path_twice_does_not_duplicate(self):
        callback = MagicMock()
        watcher = SmartWatcher(callback=callback)
        watcher.add_watch("/test/path")
        watcher.add_watch("/test/path")
        assert len(watcher.watch_paths) == 1

    def test_remove_nonexistent_path_does_not_error(self):
        callback = MagicMock()
        watcher = SmartWatcher(callback=callback)
        watcher.remove_watch("/no/exist")
