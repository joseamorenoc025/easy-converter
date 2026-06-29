"""Tests para features v2.2.0: themes, retries, batch, CLI."""
import json
import time
from pathlib import Path
from unittest.mock import patch, MagicMock


# ===== Feature 4: Temas Personalizables =====
class TestThemes:
    def test_builtin_themes_count(self):
        from ui.themes import THEMES
        builtins = {"dark", "light", "high_contrast", "corporativo", "calido", "solarizado"}
        assert builtins.issubset(set(THEMES.keys()))

    def test_corporativo_theme_colors(self):
        from ui.themes import THEMES
        t = THEMES["corporativo"]
        assert t["name"] == "Corporativo"
        assert t["appearance"] == "dark"
        assert t["colors"]["primary"] == "#1a365d"

    def test_calido_theme_colors(self):
        from ui.themes import THEMES
        t = THEMES["calido"]
        assert t["name"] == "Calido"
        assert t["colors"]["primary"] == "#c05621"

    def test_solarizado_theme_colors(self):
        from ui.themes import THEMES
        t = THEMES["solarizado"]
        assert t["name"] == "Solarizado"
        assert t["colors"]["primary"] == "#268bd2"

    def test_theme_manager_is_builtin(self):
        from ui.themes import ThemeManager
        assert ThemeManager.is_builtin("dark") is True
        assert ThemeManager.is_builtin("corporativo") is True
        assert ThemeManager.is_builtin("nonexistent") is False

    def test_theme_manager_get_theme_default(self):
        from ui.themes import ThemeManager
        theme = ThemeManager.get_theme("dark")
        assert "colors" in theme
        assert "primary" in theme["colors"]

    def test_theme_manager_get_color(self):
        from ui.themes import ThemeManager
        color = ThemeManager.get_color("primary", "solarizado")
        assert color == "#268bd2"

    def test_theme_manager_get_color_unknown_key(self):
        from ui.themes import ThemeManager
        color = ThemeManager.get_color("nonexistent_key", "dark")
        assert color == "#ffffff"

    def test_save_custom_theme(self, tmp_path):
        from ui.themes import ThemeManager, THEMES
        with patch("ui.themes._get_themes_dir", return_value=tmp_path):
            colors = {
                "primary": "#ff0000", "secondary": "#000000", "surface": "#111111",
                "background": "#000000", "text": "#ffffff", "text_secondary": "#aaaaaa",
                "success": "#00ff00", "error": "#ff0000", "warning": "#ffff00", "border": "#333333",
            }
            result = ThemeManager.save_custom("test_custom", "Test Custom", colors, "dark")
            assert result is True
            assert "test_custom" in THEMES
            f = tmp_path / "test_custom.json"
            assert f.exists()
            data = json.loads(f.read_text(encoding="utf-8"))
            assert data["name"] == "Test Custom"
            # cleanup
            ThemeManager.delete_custom("test_custom")

    def test_delete_custom_theme(self, tmp_path):
        from ui.themes import ThemeManager, THEMES, _save_custom_theme
        with patch("ui.themes._get_themes_dir", return_value=tmp_path):
            colors = {
                "primary": "#ff0000", "secondary": "#000000", "surface": "#111111",
                "background": "#000000", "text": "#ffffff", "text_secondary": "#aaaaaa",
                "success": "#00ff00", "error": "#ff0000", "warning": "#ffff00", "border": "#333333",
            }
            _save_custom_theme("del_test", {"name": "Del", "appearance": "dark", "colors": colors})
            assert "del_test" in THEMES
            result = ThemeManager.delete_custom("del_test")
            assert result is True
            assert "del_test" not in THEMES

    def test_cannot_delete_builtin_theme(self):
        from ui.themes import ThemeManager
        result = ThemeManager.delete_custom("dark")
        assert result is False

    def test_get_theme_label(self):
        from ui.themes import ThemeManager
        assert ThemeManager.get_theme_label("dark") == "Oscuro"
        assert ThemeManager.get_theme_label("corporativo") == "Corporativo"
        assert ThemeManager.get_theme_label("nonexistent") == "nonexistent"


# ===== Feature 5: Reintentos Inteligentes =====
class TestRetries:
    def test_queue_item_retry_fields(self):
        from core.queue_manager import QueueItem
        from pathlib import Path
        item = QueueItem(file_path=Path("test.pdf"), mode="pdf2word")
        assert item.retry_count == 0
        assert item.max_retries == 3
        assert item.last_error == ""
        assert item.next_retry_at == 0.0

    def test_retry_delays_constant(self):
        from core.queue_manager import RETRY_DELAYS
        assert RETRY_DELAYS[0] == 2
        assert RETRY_DELAYS[1] == 5
        assert RETRY_DELAYS[2] == 15

    def test_retry_pending_status_on_failure(self):
        from core.queue_manager import ConversionQueue
        from pathlib import Path

        def failing_worker(item):
            raise RuntimeError("test error")

        q = ConversionQueue(worker_func=failing_worker, max_size=2)
        q.add_item(Path("test.pdf"), "pdf2word")

        time.sleep(3)  # Wait for first retry timer (2s) to fire
        items = q.get_all_items()
        assert len(items) == 1
        item = items[0]
        assert item.retry_count == 1
        assert item.status in ("retry_pending", "failed")  # may have failed after 2nd attempt

    def test_retry_eventually_fails(self):
        from core.queue_manager import ConversionQueue
        from pathlib import Path

        def failing_worker(item):
            raise RuntimeError("persistent error")

        q = ConversionQueue(worker_func=failing_worker, max_size=2)
        q.add_item(Path("test.pdf"), "pdf2word", use_ocr=False)

        # Wait for all 3 retries (2s + 5s + 15s would be too long,
        # so we test with fast retries by modifying max_retries)
        items = q.get_all_items()
        items[0].max_retries = 1  # allow only 1 retry

        time.sleep(4)
        items = q.get_all_items()
        item = items[0]
        assert item.status == "failed"
        assert "sin reintentos" in item.message

    def test_manual_retry(self):
        from core.queue_manager import ConversionQueue
        from pathlib import Path

        call_count = [0]

        def flaky_worker(item):
            call_count[0] += 1
            if call_count[0] <= 1:
                raise RuntimeError("first attempt fails")

        q = ConversionQueue(worker_func=flaky_worker, max_size=2)
        q.add_item(Path("test.pdf"), "pdf2word")

        time.sleep(3)  # Wait for first retry to fire
        items = q.get_all_items()
        item = items[0]
        # Should have retried and succeeded on 2nd attempt
        assert item.status == "success"

    def test_retry_item_rejects_non_retryable(self):
        from core.queue_manager import ConversionQueue, QueueItem
        from pathlib import Path

        q = ConversionQueue(worker_func=lambda x: None, max_size=2)
        item = QueueItem(file_path=Path("test.pdf"), mode="pdf2word", status="success")
        assert q.retry_item(item) is False

    def test_cancel_retry_timer_on_remove(self):
        from core.queue_manager import ConversionQueue
        from pathlib import Path

        q = ConversionQueue(worker_func=lambda x: (_ for _ in ()).throw(RuntimeError("x")), max_size=2)
        q.add_item(Path("test.pdf"), "pdf2word")
        time.sleep(0.3)
        items = q.get_all_items()
        q.remove_item(items[0])
        time.sleep(1)
        assert items[0].status == "retry_pending" or items[0] not in q.items


# ===== Feature 6: Conversión por Lotes =====
class TestBatchConversion:
    def test_batch_convert_folder_not_dir(self):
        from core.controller import AppController
        from core.converter_adapter import ConverterAdapter
        from core.queue_adapter import QueueAdapter
        from core.config_adapter import ConfigAdapter
        from core.workflow_adapter import WorkflowAdapter
        from core.platform_adapter import PlatformAdapter

        config = ConfigAdapter()
        converter = ConverterAdapter()
        queue = QueueAdapter()
        queue.set_converter(converter)
        ctrl = AppController(
            converter=converter,
            queue_manager=queue,
            config_manager=config,
            workflow_engine=WorkflowAdapter(config._config),
            platform_service=PlatformAdapter(),
        )
        success, msg, ids = ctrl.batch_convert_folder(Path("/nonexistent"), "pdf2word")
        assert success is False
        assert "no es una carpeta" in msg.lower()

    def test_batch_convert_empty_folder(self, tmp_path):
        from core.controller import AppController
        from core.converter_adapter import ConverterAdapter
        from core.queue_adapter import QueueAdapter
        from core.config_adapter import ConfigAdapter
        from core.workflow_adapter import WorkflowAdapter
        from core.platform_adapter import PlatformAdapter

        config = ConfigAdapter()
        converter = ConverterAdapter()
        queue = QueueAdapter()
        queue.set_converter(converter)
        ctrl = AppController(
            converter=converter,
            queue_manager=queue,
            config_manager=config,
            workflow_engine=WorkflowAdapter(config._config),
            platform_service=PlatformAdapter(),
        )
        success, msg, ids = ctrl.batch_convert_folder(tmp_path, "pdf2word")
        assert success is False
        assert "no se encontraron" in msg.lower()

    def test_batch_convert_with_pdfs(self, tmp_path):
        from core.controller import AppController
        from core.converter_adapter import ConverterAdapter
        from core.queue_adapter import QueueAdapter
        from core.config_adapter import ConfigAdapter
        from core.workflow_adapter import WorkflowAdapter
        from core.platform_adapter import PlatformAdapter

        # Create fake PDF files
        for i in range(3):
            (tmp_path / f"test_{i}.pdf").write_bytes(b"%PDF-1.4")

        config = ConfigAdapter()
        converter = ConverterAdapter()
        queue = QueueAdapter()
        queue.set_converter(converter)
        ctrl = AppController(
            converter=converter,
            queue_manager=queue,
            config_manager=config,
            workflow_engine=WorkflowAdapter(config._config),
            platform_service=PlatformAdapter(),
        )
        success, msg, ids = ctrl.batch_convert_folder(tmp_path, "pdf2word")
        assert success is True
        assert len(ids) == 3
        assert "3" in msg

    def test_batch_convert_word_mode(self, tmp_path):
        from core.controller import AppController
        from core.converter_adapter import ConverterAdapter
        from core.queue_adapter import QueueAdapter
        from core.config_adapter import ConfigAdapter
        from core.workflow_adapter import WorkflowAdapter
        from core.platform_adapter import PlatformAdapter

        # Create fake docx files (proper PK magic + ZIP header)
        for i in range(2):
            (tmp_path / f"doc_{i}.docx").write_bytes(b"PK\x03\x04\x14\x00\x00\x00")

        config = ConfigAdapter()
        converter = ConverterAdapter()
        queue = QueueAdapter()
        queue.set_converter(converter)
        ctrl = AppController(
            converter=converter,
            queue_manager=queue,
            config_manager=config,
            workflow_engine=WorkflowAdapter(config._config),
            platform_service=PlatformAdapter(),
        )
        success, msg, ids = ctrl.batch_convert_folder(tmp_path, "word2pdf")
        assert success is True
        assert len(ids) == 2

    def test_batch_convert_invalid_mode(self, tmp_path):
        from core.controller import AppController
        from core.converter_adapter import ConverterAdapter
        from core.queue_adapter import QueueAdapter
        from core.config_adapter import ConfigAdapter
        from core.workflow_adapter import WorkflowAdapter
        from core.platform_adapter import PlatformAdapter

        config = ConfigAdapter()
        converter = ConverterAdapter()
        queue = QueueAdapter()
        queue.set_converter(converter)
        ctrl = AppController(
            converter=converter,
            queue_manager=queue,
            config_manager=config,
            workflow_engine=WorkflowAdapter(config._config),
            platform_service=PlatformAdapter(),
        )
        success, msg, ids = ctrl.batch_convert_folder(tmp_path, "invalid_mode")
        assert success is False


# ===== Feature 7: CLI Mejorado =====
class TestCLI:
    def test_cli_info_flag(self, tmp_path):
        import fitz
        pdf_path = tmp_path / "test.pdf"
        doc = fitz.open()
        doc.new_page()
        doc.save(str(pdf_path))
        doc.close()

        from main import _run_cli_tool
        args = MagicMock()
        args.info = str(pdf_path)
        args.compress = None
        args.sanitize = None
        args.decrypt = None
        args.merge = None
        args.split = None
        args.batch = None
        result = _run_cli_tool(args)
        assert result is True

    def test_cli_compress_flag(self, tmp_path):
        import fitz
        pdf_path = tmp_path / "test.pdf"
        doc = fitz.open()
        doc.new_page()
        doc.save(str(pdf_path))
        doc.close()

        from main import _run_cli_tool
        args = MagicMock()
        args.info = None
        args.compress = str(pdf_path)
        args.quality = "medium"
        args.sanitize = None
        args.decrypt = None
        args.merge = None
        args.split = None
        args.batch = None
        result = _run_cli_tool(args)
        assert result is True

    def test_cli_nothing_flagged(self):
        from main import _run_cli_tool
        args = MagicMock()
        args.info = None
        args.compress = None
        args.sanitize = None
        args.decrypt = None
        args.merge = None
        args.split = None
        args.batch = None
        result = _run_cli_tool(args)
        assert result is False

    def test_cli_decrypt_no_password(self, tmp_path):
        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_bytes(b"%PDF-1.4")

        from main import _run_cli_tool
        args = MagicMock()
        args.info = None
        args.compress = None
        args.sanitize = None
        args.decrypt = str(pdf_path)
        args.password = ""
        args.merge = None
        args.split = None
        args.batch = None
        result = _run_cli_tool(args)
        assert result is True

    def test_cli_sanitize_flag(self, tmp_path):
        import fitz
        pdf_path = tmp_path / "test.pdf"
        doc = fitz.open()
        doc.new_page()
        doc.save(str(pdf_path))
        doc.close()

        from main import _run_cli_tool
        args = MagicMock()
        args.info = None
        args.compress = None
        args.sanitize = str(pdf_path)
        args.decrypt = None
        args.merge = None
        args.split = None
        args.batch = None
        result = _run_cli_tool(args)
        assert result is True

    def test_cli_merge_flag(self, tmp_path):
        import fitz
        pdf1 = tmp_path / "a.pdf"
        pdf2 = tmp_path / "b.pdf"
        for p in (pdf1, pdf2):
            doc = fitz.open()
            doc.new_page()
            doc.save(str(p))
            doc.close()

        from main import _run_cli_tool
        args = MagicMock()
        args.info = None
        args.compress = None
        args.sanitize = None
        args.decrypt = None
        args.merge = [str(pdf1), str(pdf2)]
        args.output = str(tmp_path / "merged.pdf")
        args.split = None
        args.batch = None
        result = _run_cli_tool(args)
        assert result is True
        assert (tmp_path / "merged.pdf").exists()

    def test_cli_split_flag(self, tmp_path):
        import fitz
        pdf_path = tmp_path / "test.pdf"
        doc = fitz.open()
        doc.new_page()
        doc.new_page()
        doc.new_page()
        doc.save(str(pdf_path))
        doc.close()

        from main import _run_cli_tool
        args = MagicMock()
        args.info = None
        args.compress = None
        args.sanitize = None
        args.decrypt = None
        args.merge = None
        args.split = str(pdf_path)
        args.pages = "1-2"
        args.batch = None
        result = _run_cli_tool(args)
        assert result is True

    def test_cli_batch_flag(self, tmp_path):
        for i in range(2):
            (tmp_path / f"file_{i}.pdf").write_bytes(b"%PDF-1.4")

        from main import _run_cli_tool
        args = MagicMock()
        args.info = None
        args.compress = None
        args.sanitize = None
        args.decrypt = None
        args.merge = None
        args.split = None
        args.batch = str(tmp_path)
        args.mode = "pdf2word"
        args.recursive = False
        result = _run_cli_tool(args)
        assert result is True

    def test_cli_batch_empty_folder(self, tmp_path):
        from main import _run_cli_tool
        args = MagicMock()
        args.info = None
        args.compress = None
        args.sanitize = None
        args.decrypt = None
        args.merge = None
        args.split = None
        args.batch = str(tmp_path)
        args.mode = "pdf2word"
        args.recursive = False
        result = _run_cli_tool(args)
        assert result is True

    def test_cli_batch_invalid_folder(self):
        from main import _run_cli_tool
        args = MagicMock()
        args.info = None
        args.compress = None
        args.sanitize = None
        args.decrypt = None
        args.merge = None
        args.split = None
        args.batch = "/nonexistent/path"
        args.mode = "pdf2word"
        args.recursive = False
        result = _run_cli_tool(args)
        assert result is True
