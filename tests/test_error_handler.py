"""Tests para ErrorHandler."""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from core.error_handler import (
    ErrorHandler, EasyConverterError, WordMissingError,
    FileCorruptedError, PermissionDeniedError
)


@pytest.fixture
def handler():
    return ErrorHandler(app_name="TestEasyConverter")


class TestErrorHandler:
    def test_handle_word_missing(self, handler):
        msg = handler.handle(WordMissingError("Word not found"))
        assert "Microsoft Word" in msg

    def test_handle_file_corrupted(self, handler):
        msg = handler.handle(FileCorruptedError("Bad file"))
        assert "dañado" in msg

    def test_handle_permission_denied(self, handler):
        msg = handler.handle(PermissionDeniedError("No access"))
        assert "permisos" in msg

    def test_handle_comtypes_error(self, handler):
        msg = handler.handle(Exception("comtypes dispatch failed"))
        assert "Word" in msg

    def test_handle_generic_error(self, handler):
        msg = handler.handle(Exception("Something weird"))
        assert "inesperado" in msg

    def test_handle_with_context(self, handler):
        msg = handler.handle(Exception("err"), context={"file": "test.pdf"})
        assert "inesperado" in msg
        log_content = handler.log_file.read_text(encoding='utf-8')
        assert "test.pdf" in log_content

    def test_log_file_created(self, handler):
        handler.handle(Exception("test error"))
        assert handler.log_file.exists()

    def test_retry_decorator_success(self):
        counter = {"calls": 0}

        @ErrorHandler.get_retry_decorator(max_attempts=3, base_delay=0.01)
        def flaky():
            counter["calls"] += 1
            if counter["calls"] < 3:
                raise Exception("fail")
            return "ok"

        result = flaky()
        assert result == "ok"
        assert counter["calls"] == 3

    def test_retry_decorator_exhausted(self):
        @ErrorHandler.get_retry_decorator(max_attempts=2, base_delay=0.01)
        def always_fail():
            raise Exception("always")

        with pytest.raises(Exception):
            always_fail()

    def test_easy_converter_error_is_exception(self):
        assert issubclass(EasyConverterError, Exception)
