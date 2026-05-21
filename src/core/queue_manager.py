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
    workflow_profile: str = None # Nombre del perfil a aplicar al finalizar

class ConversionQueue:
    def __init__(self, worker_func: Callable, on_queue_update: Callable = None):
        self.queue = Queue()
        self.items: List[QueueItem] = []
        self.worker_func = worker_func
        self.on_queue_update = on_queue_update
        self.is_running = False
        self._lock = threading.Lock()

    def add_item(self, file_path: Path, mode: str, workflow_profile: str = None):
        with self._lock:
            item = QueueItem(file_path=file_path, mode=mode, workflow_profile=workflow_profile)
            self.items.append(item)
            self.queue.put(item)
        
        if self.on_queue_update:
            self.on_queue_update()
            
        if not self.is_running:
            self._start_worker()

    def _start_worker(self):
        self.is_running = True
        thread = threading.Thread(target=self._process_queue, daemon=True)
        thread.start()

    def _process_queue(self):
        while not self.queue.empty():
            item = self.queue.get()
            item.status = "running"
            item.message = "Iniciando..."
            
            if self.on_queue_update:
                self.on_queue_update()

            try:
                # La worker_func debe manejar el progreso del item
                self.worker_func(item)
                item.status = "success"
                item.progress = 100
                item.message = "Completado"
            except Exception as e:
                item.status = "failed"
                item.message = f"Error: {str(e)}"
            
            if self.on_queue_update:
                self.on_queue_update()
            
            self.queue.task_done()
        
        self.is_running = False
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
