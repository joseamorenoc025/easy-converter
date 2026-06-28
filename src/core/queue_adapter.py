"""Adapter: IQueueManager → ConversionQueue"""
import time
from typing import Optional, Callable, Dict
from pathlib import Path
from core.interfaces import IQueueManager, ConversionJob, ConversionStatus
from core.queue_manager import ConversionQueue, QueueItem


class QueueAdapter(IQueueManager):
    def __init__(self, max_size: int = 10):
        self._queue = ConversionQueue(
            worker_func=self._process_item,
            max_size=max_size
        )
        self._job_map: Dict[int, ConversionJob] = {}
        self._progress_callback: Optional[Callable] = None
        self._converter = None

    def set_converter(self, converter):
        self._converter = converter

    def _process_item(self, queue_item: QueueItem):
        """Worker: adapta QueueItem a ConversionJob y ejecuta."""
        job = self._job_map.get(id(queue_item))
        if not job or not self._converter:
            return

        job.status = ConversionStatus.PROCESSING
        output_path = queue_item.result_path or str(
            Path(queue_item.file_path).with_suffix(
                '.docx' if queue_item.mode == 'pdf2word' else '.pdf'
            )
        )
        output = Path(output_path)

        try:
            if queue_item.mode == 'pdf2word':
                success, result = self._converter.convert_pdf_to_word(
                    Path(queue_item.file_path), output
                )
            else:
                success, result = self._converter.convert_word_to_pdf(
                    Path(queue_item.file_path), output
                )

            if success:
                job.status = ConversionStatus.COMPLETED
                job.target_path = Path(result)
                queue_item.status = "success"
                queue_item.result_path = str(result)
            else:
                job.status = ConversionStatus.FAILED
                job.error_message = result
                queue_item.status = "failed"
                queue_item.message = result
        except Exception as e:
            job.status = ConversionStatus.FAILED
            job.error_message = str(e)
            queue_item.status = "failed"
            queue_item.message = str(e)

        job.completed_at = time.time()

    def add_job(self, job: ConversionJob) -> bool:
        mode = 'pdf2word' if job.conversion_type == 'pdf2word' else 'word2pdf'
        success, _ = self._queue.add_item(
            Path(job.source_path), mode
        )
        if success:
            items = self._queue.get_all_items()
            for item in items:
                if item.file_path == Path(job.source_path) and item.status in ("pending", "waiting_secondary"):
                    self._job_map[id(item)] = job
                    break
        return success

    def get_next_job(self) -> Optional[ConversionJob]:
        return None

    def mark_job_completed(self, job_id: str, success: bool, error_msg: Optional[str] = None):
        pass

    def get_stats(self) -> dict:
        return self._queue.get_queue_stats()

    def register_progress_callback(self, callback: Callable[[str, float], None]):
        self._progress_callback = callback
