import threading
from queue import Queue
from dataclasses import dataclass
from typing import List, Callable
from pathlib import Path

@dataclass
class QueueItem:
    file_path: Path
    mode: str  # 'pdf2word' o 'word2pdf'
    status: str = "pending"  # pending, running, success, failed
    progress: int = 0
    message: str = "En cola"
    result_path: str = None
    workflow_profile: str = None
    use_ocr: bool = False

class ConversionQueue:
    def __init__(self, worker_func: Callable, on_queue_update: Callable = None):
        self.queue = Queue()
        self.items: List[QueueItem] = []
        self.worker_func = worker_func
        self.on_queue_update = on_queue_update
        self.is_running = False
        self._lock = threading.Lock()

    def add_item(self, file_path: Path, mode: str, workflow_profile: str = None, use_ocr: bool = False):
        with self._lock:
            item = QueueItem(file_path=file_path, mode=mode, workflow_profile=workflow_profile, use_ocr=use_ocr)
            self.items.append(item)
            self.queue.put(item)
            
            if self.on_queue_update:
                self.on_queue_update()
            
            if not self.is_running:
                self.is_running = True
                thread = threading.Thread(target=self._process_queue, daemon=True)
                thread.start()

    def _process_queue(self):
        while True:
            with self._lock:
                if self.queue.empty():
                    self.is_running = False
                    break
            
            item = self.queue.get()
            
            with self._lock:
                item.status = "running"
                item.message = "Iniciando..."
            
            if self.on_queue_update:
                self.on_queue_update()

            try:
                self.worker_func(item)
                with self._lock:
                    item.status = "success"
                    item.progress = 100
                    item.message = "Completado"
            except Exception as e:
                with self._lock:
                    item.status = "failed"
                    item.message = f"Error: {str(e)}"
            
            if self.on_queue_update:
                self.on_queue_update()
            
            self.queue.task_done()
        
        if self.on_queue_update:
            self.on_queue_update()

    def clear_completed(self):
        with self._lock:
            self.items = [item for item in self.items if item.status not in ["success", "failed"]]
        if self.on_queue_update:
            self.on_queue_update()

    def get_all_items(self):
        with self._lock:
            return list(self.items)
