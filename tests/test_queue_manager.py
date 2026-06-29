import time
import threading
from pathlib import Path
from unittest.mock import MagicMock


from core.queue_manager import ConversionQueue, QueueItem


class TestConversionQueue:
    def test_add_item_creates_queue_item(self):
        queue = ConversionQueue(worker_func=lambda x: None)
        queue.add_item(Path("/test/file.pdf"), "pdf2word")
        assert len(queue.items) == 1
        assert queue.items[0].file_path == Path("/test/file.pdf")
        assert queue.items[0].mode == "pdf2word"
        assert queue.items[0].status == "pending"

    def test_add_item_with_ocr(self):
        queue = ConversionQueue(worker_func=lambda x: None)
        queue.add_item(Path("/test/file.pdf"), "pdf2word", use_ocr=True)
        assert queue.items[0].use_ocr is True

    def test_add_item_with_workflow(self):
        queue = ConversionQueue(worker_func=lambda x: None)
        queue.add_item(Path("/test/file.pdf"), "pdf2word", workflow_profile="perfil1")
        assert queue.items[0].workflow_profile == "perfil1"

    def test_get_all_items_returns_copy(self):
        queue = ConversionQueue(worker_func=lambda x: None)
        queue.add_item(Path("/test/file.pdf"), "pdf2word")
        items = queue.get_all_items()
        items.append(QueueItem(Path("/fake.pdf"), "pdf2word"))
        assert len(queue.items) == 1

    def test_worker_processes_item(self):
        results = {}

        def worker(item):
            results["processed"] = item.file_path.name

        queue = ConversionQueue(worker_func=worker)
        queue.add_item(Path("/test/file.pdf"), "pdf2word")
        time.sleep(0.2)
        assert results.get("processed") == "file.pdf"

    def test_item_status_becomes_success(self):
        def worker(item):
            pass

        queue = ConversionQueue(worker_func=worker)
        queue.add_item(Path("/test/file.pdf"), "pdf2word")
        time.sleep(0.3)
        assert queue.items[0].status == "success"
        assert queue.items[0].progress == 100

    def test_item_status_becomes_failed_on_error(self):
        def worker(item):
            raise ValueError("Error de prueba")

        queue = ConversionQueue(worker_func=worker)
        queue.add_item(Path("/test/file.pdf"), "pdf2word")
        time.sleep(0.3)
        # With retries enabled, first failure goes to retry_pending
        assert queue.items[0].status in ("failed", "retry_pending")
        assert "Error de prueba" in queue.items[0].last_error

    def test_clear_completed_removes_success_and_failed(self):
        queue = ConversionQueue(worker_func=lambda x: None)
        queue.items = [
            QueueItem(Path("/test/success.pdf"), "pdf2word", status="success"),
            QueueItem(Path("/test/failed.pdf"), "pdf2word", status="failed"),
            QueueItem(Path("/test/pending.pdf"), "pdf2word", status="pending"),
            QueueItem(Path("/test/running.pdf"), "pdf2word", status="running"),
        ]
        queue.clear_completed()
        assert len(queue.items) == 2
        assert queue.items[0].status == "pending"
        assert queue.items[1].status == "running"

    def test_multiple_items_process_sequentially(self):
        processed = []

        def worker(item):
            processed.append(item.file_path.name)

        queue = ConversionQueue(worker_func=worker)
        queue.add_item(Path("/test/a.pdf"), "pdf2word")
        queue.add_item(Path("/test/b.pdf"), "pdf2word")
        time.sleep(0.5)
        assert processed == ["a.pdf", "b.pdf"]

    def test_is_running_flag(self):
        def slow_worker(item):
            time.sleep(0.2)

        queue = ConversionQueue(worker_func=slow_worker)
        assert queue.is_running is False
        queue.add_item(Path("/test/file.pdf"), "pdf2word")
        time.sleep(0.05)
        assert queue.is_running is True
        time.sleep(0.3)
        assert queue.is_running is False

    def test_on_queue_update_callback(self):
        callback = MagicMock()
        queue = ConversionQueue(worker_func=lambda x: None, on_queue_update=callback)
        queue.add_item(Path("/test/file.pdf"), "pdf2word")
        time.sleep(0.3)
        assert callback.call_count >= 1

    def test_queue_uses_lock(self):
        queue = ConversionQueue(worker_func=lambda x: None)
        assert hasattr(queue, "_lock")
        assert isinstance(queue._lock, type(threading.Lock()))
